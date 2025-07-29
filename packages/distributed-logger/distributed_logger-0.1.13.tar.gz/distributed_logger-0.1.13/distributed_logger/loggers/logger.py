from abc import ABC, abstractmethod
import json
import logging
from typing import Optional
from distributed_logger.models.log import LogInfo
from distributed_logger.models.config import KafkaConfig
from kafka import KafkaProducer
from kafka.errors import KafkaError

logger = logging.getLogger(__name__)

class Logger(ABC):
    """
    Abstract base class for logging implementations.
    Provides interface for establishing connections and publishing logs.
    """
    @abstractmethod
    def connect(self) -> None:
        """Establish connection to the logging backend"""
        raise NotImplementedError("connect must be implemented")
    
    @abstractmethod
    def publish(self, log_info: LogInfo) -> bool:
        """Publish log information to the logging backend"""
        raise NotImplementedError("publish function must be implemented")
    
    @abstractmethod
    def close(self) -> None:
        """Close any open connections"""
        raise NotImplementedError("close function must be implemented")

class KafkaLogger(Logger):
    def __init__(self, config: KafkaConfig) -> None:
        super().__init__()
        self.config = config
        self.producer: Optional[KafkaProducer] = None
        self.connect()
    
    def connect(self) -> None:
        if not isinstance(self.config, KafkaConfig):
            raise TypeError("KafkaLogger requires a KafkaConfig instance")
        
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.config.bootstrap_servers,
                client_id=self.config.client_id,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                acks='all',  # Ensure the message is fully committed
                retries=3,   # Number of retries if the initial publish fails
                max_in_flight_requests_per_connection=1,  # Preserve ordering
                enable_idempotence=True,  # Prevent duplicate messages
                compression_type='gzip',  # Compress messages for efficiency
                api_version=(2, 5, 0)  # Use modern Kafka protocol
            )
            logger.info("Successfully connected to Kafka broker(s): %s", self.config.bootstrap_servers)
        except Exception as e:
            logger.error("Failed to connect to Kafka: %s", str(e))
            self.producer = None
            raise
    
    def publish(self, log_info: LogInfo) -> bool:
        """
        Publish a log message to Kafka.
        
        Args:
            log_info: The log information to publish
            
        Returns:
            bool: True if successfully published, False otherwise
            
        Raises:
            KafkaError: If there's an error publishing to Kafka
        """
        if not self.producer:
            logger.error("Kafka producer not connected")
            return False
        
        try:
            future = self.producer.send(
                topic=self.config.topic,
                value=log_info.to_json(),
            )
            
            # Wait for the message to be delivered
            record_metadata = future.get(timeout=10)
            
            logger.debug(
                "Successfully published message to Kafka - Topic: %s, Partition: %d, Offset: %d",
                record_metadata.topic,
                record_metadata.partition,
                record_metadata.offset
            )
            return True
            
        except KafkaError as ke:
            logger.error("Failed to publish to Kafka: %s", str(ke))
            raise
        except Exception as e:
            logger.error("Unexpected error while publishing to Kafka: %s", str(e))
            raise
    
    def close(self) -> None:
        """Cleanly shut down the Kafka producer"""
        if self.producer:
            try:
                self.producer.flush()  # Ensure all messages are sent
                self.producer.close(timeout=5)  # Give 5 seconds for clean shutdown
                logger.info("Kafka producer closed successfully")
            except Exception as e:
                logger.error("Error while closing Kafka producer: %s", str(e))
            finally:
                self.producer = None