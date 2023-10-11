"""
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
File Name   : config.py
Author      : jinming.yang
Description : 数据库连接信息等参数配置
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
"""
from pydantic import Field
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class Configuration(BaseSettings):
    model_config = SettingsConfigDict(env_file=('.env', 'dev.env'), env_file_encoding='utf-8', extra='ignore')
    # 默认IP
    host: str = Field('127.0.0.1', env='HOST')
    # OLTP数据库相关参数
    oltp_host: str = Field(host)
    oltp_port: int = Field(5432)
    oltp_user: str = Field(alias='POSTGRESQL_USERNAME')
    oltp_pwd: str = Field(alias='POSTGRESQL_PASSWORD')
    oltp_db: str = Field(alias='POSTGRESQL_DATABASE')
    # OLAP数据库相关参数
    olap_host: str = Field(host)
    olap_port: int = Field(9000)
    olap_user: str = Field(alias='CLICKHOUSE_ADMIN_USER')
    olap_pwd: str = Field(alias='CLICKHOUSE_ADMIN_PASSWORD')
    olap_db: str = Field(alias='CLICKHOUSE_DATABASE')
    # REDIS相关参数
    redis_host: str = Field(host)
    redis_port: int = Field(6379)
    redis_password: str
    # KAFKA相关参数
    kafka_host: str = Field(host)
    kafka_port: int = Field(9092)
    kafka_consumer_timeout: int = Field(10)
    kafka_protocol: str = 'PLAINTEXT'
    kafka_message_max_bytes: int
    kafka_producer_queue_size: int = Field(100)
    kafka_group: str = Field('demo')
    # JWT
    jwt_token_expire_days = 7
    jwt_secret = Field('DEMO_KEY')

    # 拓展属性

    @property
    def oltp_uri(self):
        return f'postgresql+psycopg://{self.oltp_user}:{self.oltp_pwd}@{self.oltp_host}:{self.oltp_port}/{self.oltp_db}'

    @property
    def olap_uri(self):
        return f'clickhouse://{self.olap_user}:{self.olap_pwd}@{self.olap_host}:{self.olap_port}/{self.olap_db}'

    @property
    def kafka_server(self):
        return f'{self.kafka_host}:{self.kafka_port}'

    @property
    def kafka_producer_config(self):
        return {
            'bootstrap.servers': self.kafka_server,
            'security.protocol': self.kafka_protocol,
            'message.max.bytes': self.kafka_message_max_bytes,
            'queue.buffering.max.messages': self.kafka_producer_queue_size,
        }

    @property
    def kafka_consumer_config(self):
        return {
            'auto.offset.reset': 'earliest',
            'group.id': self.kafka_group,
            'bootstrap.servers': self.kafka_server,
        }
