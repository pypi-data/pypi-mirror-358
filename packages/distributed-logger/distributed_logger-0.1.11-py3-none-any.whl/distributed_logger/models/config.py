from dataclasses import dataclass
from typing import Dict, Optional, List


@dataclass
class KafkaConfig:
    bootstrap_servers: List[str]
    topic: str
    client_id: Optional[str] = None



class ConfigFactory:
    @staticmethod
    def create_config(config_type: str, **kwargs):
        if config_type == "KAFKA":
            return KafkaConfig(**kwargs)
        else:
            raise ValueError(f"Unknown config type: {config_type}")