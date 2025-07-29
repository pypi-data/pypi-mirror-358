# lstmAtten_datautils/lstmAtten_datautils/data_loader.py
# coding: utf-8
from torch.utils.data import DataLoader, Dataset
from .process import *
import torch
from .config import logger, Config
from sklearn.model_selection import train_test_split
import os

class MyDataset(Dataset):
    def __init__(self, data_path, config):
        """
        初始化数据集。
        :param data_path: 数据集文件路径
        :param config: Config 对象，提供超参数和路径
        """
        logger.info(f"初始化数据集，加载数据: {data_path}")
        self.data = get_data(data_path, config)  # 使用特定 data_path
        logger.info(f"数据集大小: {len(self.data[0])} 条样本")

    def __len__(self):
        return len(self.data[0])

    def __getitem__(self, i):
        return self.data[0][i], self.data[1][i], self.data[2][i], self.data[3][i], self.data[4][i]

def collate_fn(batch, config):
    """
    处理批次数据。
    :param batch: 批次数据列表
    :param config: Config 对象，提供 max_length
    :return: 张量和原始数据
    """
    logger.info(f"处理批次数据，批次大小: {len(batch)}")
    sents = [data[0] for data in batch]
    labels = [data[1] for data in batch]
    pos_e1 = [data[2] for data in batch]
    pos_e2 = [data[3] for data in batch]
    ents = [data[4] for data in batch]
    sents_ids = [sent_padding(sent, word2id(config), config) for sent in sents]
    pos_e1_ids = [pos_padding(pos_ids, config) for pos_ids in pos_e1]
    pos_e2_ids = [pos_padding(pos_ids, config) for pos_ids in pos_e2]
    try:
        sents_tensor = torch.tensor(sents_ids, dtype=torch.long)
        pos_e1_tensor = torch.tensor(pos_e1_ids, dtype=torch.long)
        pos_e2_tensor = torch.tensor(pos_e2_ids, dtype=torch.long)
        labels_tensor = torch.tensor(labels, dtype=torch.long)
        logger.info(f"批次张量转换完成，形状: (sents: {sents_tensor.shape}, pos_e1: {pos_e1_tensor.shape})")
    except RuntimeError as e:
        logger.error(f"张量转换失败: {e}")
        raise
    print("当前batch原始数据:", sents, labels, pos_e1, pos_e2, ents)
    print("当前batch处理后数据:", sents_tensor, pos_e1_tensor, pos_e2_tensor, labels_tensor)
    return sents_tensor, pos_e1_tensor, pos_e2_tensor, labels_tensor, sents, labels, ents

def get_loader(config):
    """
    功能：创建数据加载器。
    输入：
        config: Config 对象，提供所有路径和超参数
        (train_data_path, test_data_path, val_data_path, vocab_path, rel_path, max_length, batch_size)
    输出：字典 {dataset_type: loader}，仅包含实际存在的加载器
    注意：config.train_data_path 和 config.test_data_path 均为必填项。
    """
    logger.info("创建数据加载器...")
    # 验证必填路径
    if not config.train_data_path or not config.test_data_path:
        logger.error("train_data_path 和 test_data_path 均为必填项！")
        raise ValueError("请提供有效的 train_data_path 和 test_data_path")
    if not os.path.exists(config.train_data_path):
        logger.error(f"训练数据集文件 {config.train_data_path} 不存在！")
        raise FileNotFoundError(f"请检查 {config.train_data_path}")
    if not os.path.exists(config.test_data_path):
        logger.error(f"测试数据集文件 {config.test_data_path} 不存在！")
        raise FileNotFoundError(f"请检查 {config.test_data_path}")

    # 自动生成词表文件
    if not os.path.exists(config.vocab_data_path):
        logger.info(f"词表文件 {config.vocab_data_path} 不存在，自动生成...")
        from .process import get_vocab
        get_vocab(config=config)
    # 检查关系文件
    if not os.path.exists(config.rel_data_path):
        logger.warning(f"关系文件 {config.rel_data_path} 不存在，请确保手动提供！")

    # 处理数据
    train_dataset = MyDataset(config.train_data_path, config)
    val_dataset = MyDataset(config.val_data_path, config) if config.val_data_path and os.path.exists(config.val_data_path) else None
    test_dataset = MyDataset(config.test_data_path, config) if config.test_data_path and os.path.exists(config.test_data_path) else None

    # 创建 DataLoader
    loaders = {}
    if train_dataset:
        train_loader = DataLoader(dataset=train_dataset,
                                  shuffle=False,
                                  batch_size=config.batch_size,
                                  drop_last=True,
                                  collate_fn=lambda x: collate_fn(x, config))
        loaders['train'] = train_loader
        logger.info(f"训练数据加载器: {len(train_loader)} 个批次 (batch_size={config.batch_size}), 样本数: {len(train_dataset)}")
    if val_dataset:
        val_loader = DataLoader(dataset=val_dataset,
                                shuffle=False,
                                batch_size=config.batch_size,
                                drop_last=True,
                                collate_fn=lambda x: collate_fn(x, config))
        loaders['val'] = val_loader
        logger.info(f"验证数据加载器: {len(val_loader)} 个批次 (batch_size={config.batch_size}), 样本数: {len(val_dataset)}")
    if test_dataset:
        test_loader = DataLoader(dataset=test_dataset,
                                 shuffle=False,
                                 batch_size=config.batch_size,
                                 drop_last=True,
                                 collate_fn=lambda x: collate_fn(x, config))
        loaders['test'] = test_loader
        logger.info(f"测试数据加载器: {len(test_loader)} 个批次 (batch_size={config.batch_size}), 样本数: {len(test_dataset)}")

    if not loaders:
        logger.error("未创建任何数据加载器，请检查路径和配置！")
        raise ValueError("无有效数据集可用")
    return loaders

if __name__ == '__main__':
    logger.info("测试数据加载流程...")
    config = Config(
        train_data_path=r"C:\Lucky_dt\2_bj\bj_23AI_KGCode\chapter4_code\BiLSTM_Attention_RE\data\train.txt",
        test_data_path=r"C:\Lucky_dt\2_bj\bj_23AI_KGCode\chapter4_code\BiLSTM_Attention_RE\data\test.txt",
        val_data_path=r"C:\Lucky_dt\2_bj\bj_23AI_KGCode\chapter4_code\BiLSTM_Attention_RE\data\val.txt",
        vocab_path=r"C:\Lucky_dt\2_bj\bj_23AI_KGCode\chapter4_code\BiLSTM_Attention_RE\data\vocab.txt",
        rel_path=r"C:\Lucky_dt\2_bj\bj_23AI_KGCode\chapter4_code\BiLSTM_Attention_RE\data\relation.txt"
    )
    loaders = get_loader(config)
    for dataset_type, loader in loaders.items():
        logger.info(f'{dataset_type}加载器批次数量: {len(loader)}')
        for index, (sents_tensor, pos_e1_tensor, pos_e2_tensor, labels_tensor, sents, labels, ents) in enumerate(loader):
            logger.info(f"{dataset_type}批次 {index}: 句子张量形状 {sents_tensor.shape}")
            logger.info(f"{dataset_type}批次 {index}: 实体1位置张量形状 {pos_e1_tensor.shape}")
            logger.info(f"{dataset_type}批次 {index}: 实体2位置张量形状 {pos_e2_tensor.shape}")
            logger.info(f"{dataset_type}批次 {index}: 标签张量形状 {labels_tensor.shape}")
            break