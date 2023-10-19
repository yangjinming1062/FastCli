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
    # 日志记录
    log_dir: str = ''
    log_level: str = 'DEBUG'
    log_info_name: str = 'info.log'
    log_error_name: str = 'error.log'
    log_stdout: bool = True
    log_format: str = '{time:YYYY-MM-DD HH:mm:ss}|<level>{message}</level>'
    log_retention: str = '1 days'
    # 默认IP
    host: str = '127.0.0.1'
    # OLTP数据库相关参数
    oltp_address: str = f'{host}:5432'
    oltp_username: str = Field(alias='POSTGRESQL_USERNAME')
    oltp_password: str = Field(alias='POSTGRESQL_PASSWORD')
    oltp_db: str = Field(alias='POSTGRESQL_DATABASE')
    # OLAP数据库相关参数
    olap_address: str = f'{host}:9000'
    olap_username: str = Field(alias='CLICKHOUSE_ADMIN_USER')
    olap_password: str = Field(alias='CLICKHOUSE_ADMIN_PASSWORD')
    olap_db: str = Field(alias='CLICKHOUSE_DATABASE')
    # REDIS相关参数
    redis_host: str = host
    redis_port: int = 6379
    redis_password: str
    # KAFKA相关参数
    kafka_address: str = f'{host}:9092'
    kafka_consumer_timeout: int = 10
    kafka_protocol: str = 'PLAINTEXT'
    kafka_message_max_bytes: int
    kafka_producer_queue_size: int = 1000
    kafka_group: str = 'demo'
    # JWT
    jwt_token_expire_days: int = 7
    jwt_secret: str = 'DEMO_KEY'
    # Secret
    secret_key: bytes = b'_6TMXZCARlHQyko-3pQJLKNF_niJwDxtVzHn0BdHmlM='

    # 拓展属性

    @property
    def oltp_uri(self):
        return f'postgresql+psycopg://{self.oltp_username}:{self.oltp_password}@{self.oltp_address}/{self.oltp_db}'

    @property
    def olap_uri(self):
        return f'clickhouse://{self.olap_username}:{self.olap_password}@{self.olap_address}/{self.olap_db}'

    @property
    def kafka_producer_config(self):
        return {
            'bootstrap.servers': self.kafka_address,
            'security.protocol': self.kafka_protocol,
            'message.max.bytes': self.kafka_message_max_bytes,
            'queue.buffering.max.messages': self.kafka_producer_queue_size,
        }

    @property
    def kafka_consumer_config(self):
        return {
            'auto.offset.reset': 'earliest',
            'group.id': self.kafka_group,
            'bootstrap.servers': self.kafka_address,
        }
