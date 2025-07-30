# lstmAtten_datautils/lstmAtten_datautils/process.py
# -*- coding: utf-8 -*-
from .base_Conf import BaseConfig, logger
from itertools import chain
import torch

def relation2id(baseconfig):
    """
    功能：读取关系数据文件，生成关系名称到ID的映射字典。
    输入：
        baseconfig: Config 对象，提供 rel_data_path
    输出：关系到ID的字典 {relation: id}
    描述：从 baseconfig.rel_data_path (relation2id.txt) 读取关系文件，每行格式为 "relation_name id"，生成映射字典。
    """
    relation2id_dict = {}
    logger.info(f"加载关系映射从: {baseconfig.rel_data_path}")
    try:
        with open(baseconfig.rel_data_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                lines = line.strip().split(" ")
                if len(lines) != 2:
                    logger.warning(f"第 {line_num} 行格式错误: {line.strip()}, 预期 'relation_name id', 跳过")
                    continue
                relation_name, relation_id = lines[0], lines[1]
                try:
                    relation2id_dict[relation_name] = int(relation_id)
                except ValueError:
                    logger.warning(f"第 {line_num} 行 ID 无效: {relation_id}, 跳过")
                    continue
        logger.info(f"关系映射加载完成，字典大小: {len(relation2id_dict)}")
    except FileNotFoundError:
        logger.error(f"关系文件 {baseconfig.rel_data_path} 未找到！请提供或创建该文件。")
        raise
    return relation2id_dict

def word2id(baseconfig):
    """
    功能：获取词到ID的映射字典。
    输入：
        baseconfig: Config 对象，提供 vocab_data_path
    输出：词到ID的字典 {word: id}
    描述：通过 baseconfig.get_word2id() 获取缓存的词表映射，避免重复加载。
    """
    return baseconfig.get_word2id()

def sent_padding(sent, word2id_dict, baseconfig):
    """
    功能：将句子中的字符转为ID，并截断或补齐到固定长度。
    输入：
        sent: 字符列表，表示句子
        word2id_dict: 词到ID映射字典
        baseconfig: Config 对象，提供 max_length
    输出：长度为 baseconfig.max_length 的ID列表
    描述：将 sent 中的每个字符转为对应的 ID，使用 'UNK' 处理未知词，超出 max_length 截断，不足则补齐 'PAD'。
    """
    ids = [word2id_dict.get(word, word2id_dict['UNK']) for word in sent]
    if len(ids) >= baseconfig.max_length:
        return ids[:baseconfig.max_length]
    return ids + [word2id_dict['PAD']] * (baseconfig.max_length - len(ids))

def pos(num, baseconfig):
    """
    功能：将相对位置差映射到非负范围，覆盖 [-pos_range, pos_range]。
    输入：
        num: 相对位置差
        baseconfig: Config 对象，提供 pos_range
    输出：映射后的非负位置ID
    描述：根据 baseconfig.pos_range（默认 max_length-1）将位置差映射到 [0, 2*pos_range]，
          num < -pos_range 返回 0，num > pos_range 返回 2*pos_range，其他情况返回 num + pos_range。
    """
    pos_range_num = baseconfig.pos_range
    if num < -pos_range_num:
        return 0
    elif num > pos_range_num:
        return 2 * pos_range_num
    return num + pos_range_num

def pos_padding(pos_ids, baseconfig):
    """
    功能：将位置序列转为非负形式，并截断或补齐到最大长度。
    输入：
        pos_ids: 位置序列
        baseconfig: Config 对象，提供 max_length 和 pos_padding_value
    输出：长度为 baseconfig.max_length 的非负位置ID列表
    描述：对 pos_ids 中的每个位置应用 pos 函数，超出 max_length 截断，不足则补齐 pos_padding_value。
    """
    pos_seq = [pos(pos_id, baseconfig) for pos_id in pos_ids]
    if len(pos_seq) >= baseconfig.max_length:
        return pos_seq[:baseconfig.max_length]
    return pos_seq + [baseconfig.pos_padding_value] * (baseconfig.max_length - len(pos_seq))

def get_data(data_path, baseconfig):
    """
    功能：读取指定路径的数据集，转换为模型需要的格式。
    输入：
        data_path: 数据集文件路径
        baseconfig: Config 对象，提供其他超参数和路径
    输出：(datas, labels, pos_e1, pos_e2, ents)
    描述：从 data_path 读取数据，每行格式为 "ent1 ent2 relation text"，生成句子、标签和位置编码。
    """
    logger.info(f"处理数据集: {data_path}")
    datas, ents, labels, pos_e1, pos_e2 = [], [], [], [], []
    relation_dict = relation2id(baseconfig)
    if not relation_dict:
        logger.error(f"关系映射字典为空，请检查 {baseconfig.rel_data_path} 内容！")
        raise ValueError("关系映射字典初始化失败")
    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            for line in f:
                line_list = line.strip().split(' ', maxsplit=3)
                if len(line_list) != 4:
                    logger.warning(f"行格式错误: {line.strip()}, 跳过")
                    continue
                ent1, ent2, relation, sentence = line_list
                if relation not in relation_dict:
                    logger.warning(f"关系 {relation} 不在映射中，跳过")
                    continue
                ents.append([ent1, ent2])
                idx1, idx2 = sentence.index(ent1), sentence.index(ent2)
                sent, pos1, pos2 = [], [], []
                for idx, word in enumerate(sentence):
                    sent.append(word)
                    pos1.append(idx - idx1)
                    pos2.append(idx - idx2)
                datas.append(sent)
                pos_e1.append(pos1)
                pos_e2.append(pos2)
                labels.append(relation_dict[relation])
        logger.info(f"数据集处理完成，数据量: {len(datas)}")
    except FileNotFoundError:
        logger.error(f"数据集文件 {data_path} 未找到！")
        raise
    return datas, labels, pos_e1, pos_e2, ents

def build_vocabulary(baseconfig):
    """
    功能：从训练数据集中提取所有字符，构建词汇表。
    输入：
        baseconfig: Config 对象，提供 train_data_path
    输出：字符列表
    描述：读取 baseconfig.train_data_path 中的文本，提取唯一字符，用于生成词表，不涉及标签或位置编码。
    """
    logger.info(f"构建词汇表从: {baseconfig.train_data_path}")
    chars = set()
    try:
        with open(baseconfig.train_data_path, 'r', encoding='utf-8') as f:
            for line in f:
                line_list = line.strip().split(' ', maxsplit=3)
                if len(line_list) >= 4:
                    sentence = line_list[3]
                    chars.update(sentence)
        logger.info(f"词汇表构建完成，字符数量: {len(chars)}")
    except FileNotFoundError:
        logger.error(f"训练数据集文件 {baseconfig.train_data_path} 未找到！")
        raise
    return ['PAD', 'UNK'] + list(chars)

def get_vocab(baseconfig):
    """
    功能：从训练数据集中提取所有字符，生成词表文件。
    输入：
        baseconfig: Config 对象，提供 train_data_path 和 vocab_data_path
    输出：生成词表文件
    描述：调用 build_vocabulary 获取字符列表，保存到 baseconfig.vocab_data_path。
    """
    data_list = build_vocabulary(baseconfig)
    logger.info(f"生成词表，保存到: {baseconfig.vocab_data_path}")
    with open(baseconfig.vocab_data_path, 'w', encoding='utf-8') as fw:
        fw.write('\n'.join(data_list))
        fw.flush()
    logger.info(f"词表已保存到 {baseconfig.vocab_data_path}")

def process_single_sample(sample, baseconfig):
    """
    功能：处理单条无标签样本数据，转换为张量格式。
    输入：
        sample: 字典，包含 "text" (句子), "ent1" (实体1), "ent2" (实体2)，无 "label" 字段
        baseconfig: Config 对象，提供 max_length 和 vocab_data_path
    输出：(sents_tensor, pos_e1_tensor, pos_e2_tensor, labels_tensor, sents, pos_e1, pos_e2, ents)
    描述：为新数据预测设计，生成与批处理一致的张量，labels_tensor 始终为 None。
    示例输入：{"text": "温暖的家歌曲...", "ent1": "温暖的家", "ent2": "余致迪"}
    注意：若 sample 包含 "label" 字段，请使用批量处理 (get_loader + collate_fn)。
    """
    logger.info(f"处理单条样本: {sample.get('text', '无文本')}")
    text = sample.get('text')
    ent1 = sample.get('ent1')
    ent2 = sample.get('ent2')

    # 验证必要字段
    if not all([text, ent1, ent2]):
        logger.error("sample 必须包含 'text', 'ent1', 'ent2' 字段！")
        raise ValueError("缺少必要字段")
    if 'label' in sample:
        logger.error("单条样本检测到 'label' 字段，请使用批量处理 (get_loader + collate_fn)！")
        raise ValueError("单条样本不支持标签，请使用批量处理")

    # 模拟批处理格式
    sents = [list(text)]
    ents = [[ent1, ent2]]
    labels = None  # 无标签
    idx1 = text.index(ent1)
    idx2 = text.index(ent2)
    pos_e1 = [[i - idx1 for i in range(len(text))]]
    pos_e2 = [[i - idx2 for i in range(len(text))]]

    # 使用现有逻辑处理
    word2id_dict = word2id(baseconfig)
    sents_ids = [sent_padding(sent, word2id_dict, baseconfig) for sent in sents]
    pos_e1_ids = [pos_padding(pos, baseconfig) for pos in pos_e1]
    pos_e2_ids = [pos_padding(pos, baseconfig) for pos in pos_e2]

    try:
        sents_tensor = torch.tensor(sents_ids, dtype=torch.long)
        pos_e1_tensor = torch.tensor(pos_e1_ids, dtype=torch.long)
        pos_e2_tensor = torch.tensor(pos_e2_ids, dtype=torch.long)
        labels_tensor = None  # 始终为 None
        logger.info(f"单条样本张量转换完成，形状: (sents: {sents_tensor.shape}, pos_e1: {pos_e1_tensor.shape})")
    except RuntimeError as e:
        logger.error(f"单条样本张量转换失败: {e}")
        raise

    return sents_tensor, pos_e1_tensor, pos_e2_tensor, labels_tensor, sents, pos_e1, pos_e2, ents