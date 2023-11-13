"""
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
File Name   : kafka.py
Author      : jinming.yang@qingteng.cn
Description : Kafka相关封装
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
"""
import json

from confluent_kafka import Consumer
from confluent_kafka import Producer
from confluent_kafka import TopicPartition

from config import CONFIG
from utils import logger
from .classes import JSONExtensionEncoder


class KafkaManager:
    """
    Kafka管理器，简化生成和消费的处理
    """

    PRODUCER = Producer(CONFIG.kafka_producer_config)

    @staticmethod
    def get_consumer(*topic, group_name=None, partition=None):
        """
        创建一个消费者。

        Args:
            topic: 消费的主题都有哪些。
            group_name (str): 组名称，默认None时使用CONFIG中的默认值。
            partition (int): 指定监听的分区。

        Returns:
            Consumer: 消费者实例。
        """
        config = CONFIG.kafka_consumer_config
        if group_name:
            config['group.id'] = group_name
        consumer = Consumer(config)
        if partition is not None:
            consumer.assign([TopicPartition(t, partition) for t in topic])
        consumer.subscribe(list(topic))
        return consumer

    @staticmethod
    def delivery_report(err, msg):
        """
        回调函数，用于获取消息写入Kafka时的状态。

        Args:
            err (str): 错误消息（如果有）。
            msg (str): 发给Kafka的信息。

        Returns:
            None
        """
        logger.debug(f'Kafka Sent:{msg}')
        if err is not None:
            logger.error('Kafka发生失败', err)

    @staticmethod
    def consume(*topic, consumer=None, limit=None, need_load=True):
        """
        消费指定主题的数据。

        Args:
            topic: 需要消费的主题。
            consumer (Consumer, optional): 默认为None时会自动创建一个消费者，并在方法结束调用后取消订阅并关闭自动创建的消费者对象。
            limit (int, optional): 批处理中要使用的消息数。默认值为None，表示每次返回单个消息。
            need_load (bool, optional): 是否返回JSON解码消息, 默认为True会对订阅到的消息进行json.load。

        Returns:
            list | dict: 如果指定了“limit”，则返回JSON解码消息的列表。

        Yields:
            dict | str: 如果“limit”为None，则以生成器的方式每次返回单个JSON解码消息。

        Raises:
            ValueError: 当kafka发生错误时抛出异常。
        """

        def load(msg):
            return json.loads(msg.value().decode('utf-8'))

        if flag := consumer is None:
            consumer = KafkaManager.get_consumer(*topic)
        try:
            if limit:
                # 批量消费
                msgs = consumer.consume(num_messages=limit, timeout=CONFIG.kafka_consumer_timeout)
                return [load(msg) for msg in msgs] if need_load else [msg.value() for msg in msgs]
            else:
                # 持续轮询，返回收到的第一条非空消息
                while True:
                    msg = consumer.poll(1.0)
                    if msg is None:
                        continue
                    if msg.error():
                        raise ValueError(msg.error())
                    yield load(msg) if need_load else msg.value()
        finally:
            # 不是函数内创建的消费者不进行取消订阅以及关闭操作
            if flag:
                consumer.unsubscribe()
                consumer.close()

    @staticmethod
    async def produce(topic, data):
        """
        生成指定主题的数据。

        Args:
            topic (str): 主题的名称。
            data (dict | list | str): 要发送的数据, 建议批量发送以提高效率。

        Returns:
            None
        """

        async def produce_data(value):
            """
            单次发送指定主题的数据。

            Args:
                value (dict | str): 要发送的数据。

            Returns:
                None
            """
            if isinstance(value, dict):
                value = json.dumps(value, cls=JSONExtensionEncoder)
            KafkaManager.PRODUCER.produce(topic=topic, value=value, callback=KafkaManager.delivery_report)

        if isinstance(data, list):
            index = 1
            for item in data:
                if index >= CONFIG.kafka_producer_queue_size:
                    KafkaManager.PRODUCER.poll(0)
                    index = 1
                await produce_data(item)
                index += 1
        else:
            await produce_data(data)
        # 确保交付
        KafkaManager.PRODUCER.poll(0)
