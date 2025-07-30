# -*- coding: utf-8 -*-
import threading
import time
from typing import Optional

from fastboost.funboost_config_deafult import BrokerConnConfig
from fastboost.publishers.base_publisher import AbstractPublisher
from logging import getLogger

logger = getLogger(__name__)


class AliyunRocketmqPublisher(AbstractPublisher):
    _group_id__rocketmq_producer = {}
    _lock_for_create_producer = threading.Lock()

    def custom_init(self):
        try:

            from rocketmq import ClientConfiguration, Credentials, Message, Producer
        except ImportError as e:
            raise ImportError("请先安装阿里云 RocketMQ SDK: pip install alibabacloud-rocketmq") from e

        access_key = BrokerConnConfig.ALIYUN_ROCKETMQ_ACCESS_KEY
        secret_key = BrokerConnConfig.ALIYUN_ROCKETMQ_SECRET_KEY
        endpoint = BrokerConnConfig.ALIYUN_ROCKETMQ_NAMESRV_ADDR
        instance_id = getattr(BrokerConnConfig, 'ALIYUN_ROCKETMQ_INSTANCE_ID', None)

        group_id = f'GID-{self._queue_name}'  # 阿里云要求 Group ID 以 GID- 开头

        with self._lock_for_create_producer:
            if group_id not in self.__class__._group_id__rocketmq_producer:
                # 构造认证信息
                credentials = Credentials(ak=access_key, sk=secret_key)

                # 解析 endpoint host 和 port


                # 构建客户端配置
                config = ClientConfiguration(
                    endpoints=endpoint,
                    credentials=credentials,
                    namespace=instance_id or ""
                )

                # 创建生产者
                producer = Producer(config, topics=(self._queue_name,))

                try:
                    producer.startup()
                    self.__class__._group_id__rocketmq_producer[group_id] = producer
                except Exception as e:
                    logger.error(f"启动 RocketMQ Producer 失败: {e}", exc_info=True)
                    raise
            else:
                producer = self.__class__._group_id__rocketmq_producer[group_id]
            self._producer = producer

    def concrete_realization_of_publish(self, msg: str):
        try:
            from rocketmq.client import Message
        except BaseException as e:
            logger.error(f"加载 RocketMQ 模块失败: {e}")
            raise ImportError(f'阿里云 RocketMQ 包未正确安装: {str(e)}') from e

        rocket_msg = Message()
        rocket_msg.topic = self._queue_name
        rocket_msg.body = msg.encode('utf-8')

        # 设置 TAG
        if getattr(self, '_tag', None):
            rocket_msg.tag = self._tag
        else:
            rocket_msg.tag = "DEFAULT_TAG"

        # 设置 KEY
        rocket_msg.keys = "FASTBOOST_MSG"

        # 可选设置 PROPERTY
        rocket_msg.add_property("source", "fastboost")

        result = self._producer.send(rocket_msg)
        if result.status == "SEND_OK":
            logger.info(f"消息发送成功: {result.msg_id}")
        else:
            logger.error(f"消息发送失败: {result.status}, 内容: {msg}")
            raise Exception(f"消息发送失败: {result.status}")

    def clear(self):
        logger.warning('清除队列暂不支持，阿里云SDK无相关API。')

    def get_message_count(self):
        logger.warning('获取消息数量暂不支持，阿里云SDK无相关API。')
        return -1

    def close(self):
        if hasattr(self, '_producer'):
            try:
                self._producer.shutdown()
            except Exception as e:
                logger.warning(f"关闭 RocketMQ Producer 异常: {e}")
            finally:
                self._producer = None

    def __del__(self):
        self.close()