import os
from enum import Enum

from distributed_logger.loggers.logger import Logger, KafkaLogger
from distributed_logger.models.config import  KafkaConfig


class EnvType(Enum):
    KAFKA = "KAFKA"

class LoggerFactory:
    """
    - Reads the environment variables
    - Selects environment based on the config from the env file
    """

    def __init__(self, broker_type: EnvType, config:KafkaConfig) -> None:
        self.env_type = broker_type
        self.config = config

        if not isinstance(self.env_type, EnvType):
            raise ValueError(f"Invalid env_type: {self.env_type}. Must be an instance of EnvType Enum.")
        
        if not isinstance(self.config, KafkaConfig):
            raise ValueError(f"Invalid config: {self.config}. Must be an instance of Config.")



    def get_logger(self) -> Logger:
        config = self.config
        
        match self.env_type:
            case EnvType.KAFKA:
                if not isinstance(config, KafkaConfig):
                    raise ValueError("KafkaLogger requires a KafkaConfig instance")
                return KafkaLogger(config=config)
            case _:
                raise Exception("No matching logger found for the environment type.")