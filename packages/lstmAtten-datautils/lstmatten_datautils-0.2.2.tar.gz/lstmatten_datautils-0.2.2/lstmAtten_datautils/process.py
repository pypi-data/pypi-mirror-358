# lstmAtten_datautils/lstmAtten_datautils/process.py
# -*- coding: utf-8 -*-
from .config import Config, logger
from itertools import chain

def relation2id(config):
    """
    功能：读取关系数据文件，生成关系名称到ID的映射字典。
    输入：
        config: Config 对象，提供 rel_data_path
    输出：关系到ID的字典 {relation: id}
    """
    relation2id_dict = {}
    logger.info("加载关系映射...")
    try:
        with open(config.rel_data_path, encoding='utf-8') as f:
            for line in f:
                lines = line.strip().split(" ")
                relation2id_dict[lines[0]] = int(lines[1])
        logger.info(f"关系映射加载完成，字典大小: {len(relation2id_dict)}")
    except FileNotFoundError:
        logger.error(f"关系文件 {config.rel_data_path} 未找到！请提供或创建该文件。")
        raise
    return relation2id_dict

def word2id(config):
    """
    功能：读取词表文件，生成词到ID的映射字典。
    输入：
        config: Config 对象，提供 vocab_data_path
    输出：词到ID的字典 {word: id}
    """
    logger.info("加载词表映射...")
    try:
        with open(config.vocab_data_path, encoding='utf-8') as f:
            word2id_dict = {word.strip(): idx for idx, word in enumerate(f)}
        logger.info(f"词表加载完成，大小: {len(word2id_dict)}")
    except FileNotFoundError:
        logger.error(f"词表文件 {config.vocab_data_path} 未找到！")
        raise
    return word2id_dict

def sent_padding(sent, word2id_dict, config):
    """
    功能：将句子中的字符转为ID，并截断或补齐到固定长度。
    输入：
        sent: 字符列表
        word2id_dict: 词到ID映射字典
        config: Config 对象，提供 max_length
    输出：长度为 config.max_length 的ID列表
    """
    ids = [word2id_dict.get(word, word2id_dict['UNK']) for word in sent]
    if len(ids) >= config.max_length:
        return ids[:config.max_length]
    return ids + [word2id_dict['PAD']] * (config.max_length - len(ids))

def pos(num, config):
    """
    功能：将相对位置差映射到 [0, 138]，覆盖 [-69, 69] 的范围。
    输入：
        num: 相对位置差
        config: Config 对象，提供 max_length
    输出：映射后的非负位置ID
    """
    if num < -69:
        return 0
    elif num > 69:
        return 138
    return num + 69

def pos_padding(pos_ids, config):
    """
    功能：将位置序列转为非负形式，并截断或补齐到最大长度。
    输入：
        pos_ids: 位置序列
        config: Config 对象，提供 max_length
    输出：长度为 config.max_length 的非负位置ID列表
    """
    pos_seq = [pos(pos_id, config) for pos_id in pos_ids]
    if len(pos_seq) >= config.max_length:
        return pos_seq[:config.max_length]
    return pos_seq + [142] * (config.max_length - len(pos_seq))

def get_data(data_path, config):
    """
    功能：读取指定路径的数据集，转换为模型需要的格式。
    输入：
        data_path: 数据集文件路径
        config: Config 对象，提供其他超参数和路径
    输出：(datas, labels, pos_e1, pos_e2, ents)
    """
    logger.info(f"处理数据集: {data_path}")
    datas, ents, labels, pos_e1, pos_e2 = [], [], [], [], []
    relation_dict = relation2id(config)
    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            for line in f:
                line_list = line.strip().split(' ', maxsplit=3)
                if len(line_list) != 4 or line_list[2] not in relation_dict:
                    continue
                ent1, ent2 = line_list[0], line_list[1]
                ents.append([ent1, ent2])
                sentence = line_list[3]
                idx1, idx2 = sentence.index(ent1), sentence.index(ent2)
                sent, pos1, pos2 = [], [], []
                for idx, word in enumerate(sentence):
                    sent.append(word)
                    pos1.append(idx - idx1)
                    pos2.append(idx - idx2)
                datas.append(sent)
                pos_e1.append(pos1)
                pos_e2.append(pos2)
                labels.append(relation_dict[line_list[2]])
        logger.info(f"数据集处理完成，数据量: {len(datas)}")
    except FileNotFoundError:
        logger.error(f"数据集文件 {data_path} 未找到！")
        raise
    return datas, labels, pos_e1, pos_e2, ents

def get_vocab(config):
    """
    功能：从训练数据集中提取所有字符，生成词表文件。
    输入：
        config: Config 对象，提供 train_data_path 和 vocab_data_path
    输出：生成词表文件
    """
    logger.info("生成词表...")
    datas = get_data(config.train_data_path, config)[0]
    data_list = ['PAD', 'UNK']
    data_list.extend(list(set(chain(*datas))))
    logger.info(f"词表大小: {len(data_list)}")
    with open(config.vocab_data_path, 'w', encoding='utf-8') as fw:
        fw.write('\n'.join(data_list))
        fw.flush()
    logger.info(f"词表已保存到 {config.vocab_data_path}")