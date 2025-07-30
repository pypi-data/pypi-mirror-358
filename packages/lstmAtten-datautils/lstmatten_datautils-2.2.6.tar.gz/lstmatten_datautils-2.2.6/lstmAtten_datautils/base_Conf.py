# lstmAtten_datautils/lstmAtten_datautils/base_Conf.py
import torch
import os
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class BaseConfig:
    def __init__(self, train_data_path, test_data_path, val_data_path=None, vocab_path=None, rel_path=None,
                 max_length=70, batch_size=2):
        """
        初始化配置类，定义数据处理和模型训练的超参数。

        :param train_data_path: 训练数据集文件路径 (必填)
        :param test_data_path: 测试数据集文件路径 (必填)
        :param val_data_path: 验证数据集文件路径 (可选)
        :param vocab_path: 词表文件路径 (可选), 若提供且文件存在则使用，否则从 train_data_path 自动生成
        :param rel_path: 关系映射文件路径 (可选), 提供 relation2id.txt
        :param max_length: 最大句子长度 (默认: 70，需为正整数)
        :param batch_size: 批次大小 (默认: 2，需为正整数)
        """
        self.train_data_path = train_data_path
        self.test_data_path = test_data_path
        self.val_data_path = val_data_path or test_data_path  # 默认使用 test_data_path
        self.vocab_data_path = vocab_path or os.path.join(os.path.dirname(train_data_path), 'vocab.txt')
        self.rel_data_path = rel_path or os.path.join(os.path.dirname(train_data_path), 'relation2id.txt')  # 明确指向 relation2id.txt
        self.word2id_dict = None  # 缓存词表

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

        # 设置 pos 非负处理映射范围
        self.pos_range = max_length - 1

        # 设置 pos 的 padding 值，目的为了补齐
        self.pos_padding_value = self.max_length * 2

        # 自动生成或加载词表
        self.get_word2id()  # 在初始化时确保词表可用

    def get_word2id(self):
        """
        获取词到ID的映射字典，缓存机制避免重复加载。
        返回：word2id_dict 字典
        描述：若 vocab_data_path 存在且有效，则加载词表；若不存在或无效，从 train_data_path 自动生成并缓存。
        """
        if self.word2id_dict is None:
            if os.path.exists(self.vocab_data_path):
                logger.info(f"使用现有词表文件: {self.vocab_data_path}")
            else:
                logger.info(f"词表文件 {self.vocab_data_path} 不存在，自动生成...")
                from .process import get_vocab
                if not os.path.exists(self.train_data_path):
                    logger.error(f"训练数据集 {self.train_data_path} 不存在，无法生成词表！")
                    raise FileNotFoundError(f"请提供有效的 train_data_path")
                get_vocab(self)
            try:
                with open(self.vocab_data_path, encoding='utf-8') as f:
                    self.word2id_dict = {word.strip(): idx for idx, word in enumerate(f)}
                logger.info(f"词表加载完成，大小: {len(self.word2id_dict)}")
            except FileNotFoundError:
                logger.error(f"词表文件 {self.vocab_data_path} 生成后仍未找到！")
                raise
            except Exception as e:
                logger.error(f"加载词表失败: {e}")
                raise
        return self.word2id_dict