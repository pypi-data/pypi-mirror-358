import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from distributed_logger.loggers.logger import KafkaLogger, SimpleLogger, Logger
from distributed_logger.models.config import KafkaConfig, SimpleConfig
from distributed_logger.models.log import LogInfo
from unittest import TestCase
import time
import os
from distributed_logger.loggers.factory import LoggerFactory, EnvType
import json
from unittest.mock import patch


class LoggerTest(TestCase):
    @patch("distributed_logger.loggers.logger.KafkaProducer")
    def test_publish(self, mock_kafka_producer):
        config = KafkaConfig(
            broker_type="",
            bootstrap_servers=["test"],
            topic="test",
        )

        logger = KafkaLogger(config=config)
        mock_kafka_producer.return_value.send.return_value = None
        mock_kafka_producer.return_value.flush.return_value = None

        log_info = LogInfo(
            ip_address="localhost",
            user_id="",
            request_time=str(time.time()),
            request_data={},
            action=""
        )

        logger.publish(log_info=log_info)

    def test_simple_logger_publish(self):
        config = SimpleConfig(broker_type="SIMPLE")
        logger = SimpleLogger(config=config)
        log_info = LogInfo(
            ip_address="127.0.0.1",
            user_id="user1",
            request_time=str(time.time()),
            request_data={"foo": "bar"},
            action="test_action"
        )
        logger.publish(log_info=log_info)

    def test_loginfo_to_json(self):
        log_info = LogInfo(
            ip_address="1.2.3.4",
            user_id="u",
            request_time="now",
            request_data={"a": 1},
            action="act"
        )
        json_str = log_info.to_json()
        data = json.loads(json_str)
        self.assertEqual(data["ip_address"], "1.2.3.4")
        self.assertEqual(data["user_id"], "u")
        self.assertEqual(data["request_time"], "now")
        self.assertEqual(data["request_data"], {"a": 1})
        self.assertEqual(data["action"], "act")

    def test_logger_factory(self):
        os.environ["BROKER_TYPE"] = "SIMPLE"
        factory = LoggerFactory(broker_type=EnvType.SIMPLE, config=SimpleConfig(broker_type="SIMPLE"))
        logger = factory.get_logger()
        self.assertIsInstance(logger, SimpleLogger)
        os.environ["BROKER_TYPE"] = "KAFKA"
        os.environ["BROKER_SERVERS"] = "localhost:9092"
        os.environ["TOPIC"] = "test"
        factory = LoggerFactory(broker_type=EnvType.KAFKA, config=KafkaConfig(broker_type="KAFKA", bootstrap_servers=["localhost:9092"], topic="test"))
        logger = factory.get_logger()
        self.assertIsInstance(logger, KafkaLogger)

    def test_log_middleware_placeholder(self):
        from distributed_logger.middleware.log_middleware import AuditLogMiddleware
        mw = AuditLogMiddleware(
            get_response=lambda x: x,
        )
        self.assertIsInstance(mw, AuditLogMiddleware)
        self.assertIsInstance(mw.logger, Logger)

if __name__ == "__main__":
    import unittest
    unittest.main()