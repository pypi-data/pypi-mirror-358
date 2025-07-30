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
    word2id_dict = {word.strip(): idx for idx, word in enumerate(open(baseconfig.vocab_data_path, encoding='utf-8'))}
    return word2id_dict

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
    pos_range_num = baseconfig.pos_range
    if num < -pos_range_num:
        logger.info(f"位置 {num} 越界，映射为 0")
        return 0
    elif num > pos_range_num:
        logger.info(f"位置 {num} 越界，映射为 {2 * pos_range_num}")
        return 2 * pos_range_num
    mapped_pos = num + pos_range_num
    logger.info(f"位置 {num} 映射为 {mapped_pos}")
    return mapped_pos

def pos_padding(pos_ids, baseconfig):
    pos_seq = [pos(pos_id, baseconfig) for pos_id in pos_ids]
    if len(pos_seq) >= baseconfig.max_length:
        truncated_pos = pos_seq[:baseconfig.max_length]
        logger.info(f"截断后位置序列: {truncated_pos[:10]}...")
        return truncated_pos
    pos_padding_value = baseconfig.pos_padding_value
    pos_seq.extend([pos_padding_value] * (baseconfig.max_length - len(pos_seq)))
    return pos_seq

def get_data(data_path, baseconfig):
    logger.info(f"处理数据集: {data_path}")
    datas, ents, labels, pos_e1, pos_e2 = [], [], [], [], []
    relation_dict = relation2id(baseconfig)
    if not relation_dict:
        logger.error(f"关系映射字典为空，请检查 {baseconfig.rel_data_path} 内容！")
        raise ValueError("关系映射字典初始化失败")
    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line_list = line.strip().split(' ', maxsplit=3)
                if len(line_list) != 4:
                    logger.warning(f"第 {line_num} 行格式错误: {line.strip()}, 跳过")
                    continue
                ent1, ent2, relation, sentence = line_list
                if relation not in relation_dict:
                    logger.warning(f"第 {line_num} 关系 {relation} 不在映射中，跳过")
                    continue
                if ent1 not in sentence or ent2 not in sentence:
                    logger.warning(f"第 {line_num} 实体 {ent1} 或 {ent2} 不在句子中，跳过")
                    continue
                # 选择实体第一次出现的位置
                idx1 = sentence.index(ent1)
                idx2 = sentence.index(ent2)
                logger.info(f"第 {line_num} 行: 实体1={ent1} (索引: {idx1}), 实体2={ent2} (索引: {idx2}), 关系={relation}")
                sent, pos1, pos2 = [], [], []
                for idx, word in enumerate(sentence):
                    sent.append(word)
                    pos1.append(idx - idx1)
                    pos2.append(idx - idx2)
                datas.append(sent)
                pos_e1.append(pos1)
                pos_e2.append(pos2)
                labels.append(relation_dict[relation])
                ents.append([ent1, ent2])
                logger.info(f"句子: {sent[:10]}..., 标签ID: {labels[-1]}")
        logger.info(f"数据集处理完成，数据量: {len(datas)}")
    except FileNotFoundError:
        logger.error(f"数据集文件 {data_path} 未找到！")
        raise
    return datas, labels, pos_e1, pos_e2, ents

def build_vocabulary(baseconfig):
    logger.info(f"构建词汇表从: {baseconfig.train_data_path}")
    chars = set()
    with open(baseconfig.train_data_path, 'r', encoding='utf-8') as f:
        for line in f:
            line_list = line.strip().split(' ', maxsplit=3)
            if len(line_list) >= 4:
                sentence = line_list[3]
                chars.update(sentence)
    return ['PAD', 'UNK'] + list(chars)

def get_vocab(baseconfig):
    data_list = build_vocabulary(baseconfig)
    with open(baseconfig.vocab_data_path, 'w', encoding='utf-8') as fw:
        fw.write('\n'.join(data_list))
        fw.flush()

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