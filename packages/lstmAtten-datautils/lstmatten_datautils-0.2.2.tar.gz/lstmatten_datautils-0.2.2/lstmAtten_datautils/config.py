# lstmAtten_datautils/lstmAtten_datautils/config.py
import torch
import os
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


class Config:
    def __init__(self, train_data_path, test_data_path, val_data_path=None, vocab_path=None, rel_path=None,
                 max_length=70, batch_size=2):
        """
        初始化配置类，定义数据处理和模型训练的超参数。

        :param train_data_path: 训练数据集文件路径 (必填)
        :param test_data_path: 测试数据集文件路径 (必填)
        :param val_data_path: 验证数据集文件路径 (可选)
        :param vocab_path: 词表文件路径 (可选),如果没有词表文件则需要设置用于生成vocab.txt
        :param rel_path: 关系映射文件路径 (可选)
        :param max_length: 最大句子长度 (默认: 70，需为正整数)
        :param batch_size: 批次大小 (默认: 2，需为正整数)
        """
        self.train_data_path = train_data_path
        self.test_data_path = test_data_path
        self.val_data_path = val_data_path or test_data_path  # 默认使用 test_data_path
        self.vocab_data_path = vocab_path or os.path.join(os.path.dirname(train_data_path), 'vocab.txt')
        self.rel_data_path = rel_path or os.path.join(os.path.dirname(train_data_path), 'relation.txt')

        # 验证并设置 max_length
        if not isinstance(max_length, int):
            logger.warning(f"max_length 应为整数，收到 {max_length}，使用默认值 70")
            self.max_length = 70
        elif max_length <= 0:
            logger.warning(f"max_length {max_length} 无效，使用默认值 70")
            self.max_length = 70
        else:
            self.max_length = max_length

        # 验证并设置 batch_size
        if not isinstance(batch_size, int):
            logger.warning(f"batch_size 应为整数，收到 {batch_size}，使用默认值 2")
            self.batch_size = 2
        elif batch_size <= 0:
            logger.warning(f"batch_size {batch_size} 无效，使用默认值 2")
            self.batch_size = 2
        else:
            self.batch_size = batch_size

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        # 验证检查文件路径
        for path in [self.train_data_path, self.test_data_path, self.val_data_path, self.vocab_data_path,
                     self.rel_data_path]:
            if not os.path.exists(path):
                logger.warning(f"路径 {path} 不存在，请确保文件可用或提供正确路径！")