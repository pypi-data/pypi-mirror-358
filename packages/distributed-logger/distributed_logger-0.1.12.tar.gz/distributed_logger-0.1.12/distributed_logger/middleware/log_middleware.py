import time
import logging
import os
from typing import Any, Callable, Dict, Optional

from distributed_logger.models.log import LogInfo
from distributed_logger.loggers.factory import LoggerFactory, EnvType
from distributed_logger.models.config import ConfigFactory
from distributed_logger.loggers.logger import Logger
import json

logger = logging.getLogger(__name__)

class AuditLogMiddleware:
    """
    Middleware for auditing requests using distributed logging.
    Supports both WSGI and ASGI frameworks.
    """
    
    def __init__(self, get_response: Callable) -> None:
        """
        Initialize the middleware.
        Args:
            get_response: The next middleware or view in the chain
        """
        self.get_response = get_response
        self.logger: Optional[Logger] = None
        self._initialize_logger()

    def _initialize_logger(self) -> None:
        """Initialize the logger based on environment configuration"""
        try:
            broker_type = os.environ.get("BROKER_TYPE", "KAFKA").upper()
            env_type = EnvType.KAFKA

            config = ConfigFactory.create_config(
                config_type=broker_type,
                bootstrap_servers=os.environ.get("KAFKA_BOOTSTRAP_SERVERS"),
                topic=os.environ.get("KAFKA_TOPIC"),
                client_id=os.environ.get("KAFKA_CLIENT_ID"),
            )
            
            self.logger = LoggerFactory(env_type, config).get_logger()
            logger.info("Successfully initialized %s logger", broker_type)
        except Exception as e:
            logger.error("Failed to initialize logger: %s", str(e))
            raise

    def _extract_request_data(self, request: Any) -> Dict[str, Any]:
        """Extract relevant data from the request object, including form data."""
        data: Dict[str, Any] = {}
        try:
            # Method and path
            data['method'] = getattr(request, 'method', '')
            data['path'] = getattr(request, 'path', '')

            # Query params
            if hasattr(request, 'GET') and request.GET:
                data['query_params'] = dict(request.GET)

            # Body for POST/PUT/PATCH
            if request.method in ['POST', 'PUT', 'PATCH']:
                content_type = getattr(request, 'content_type', '')

                # Form data
                if hasattr(request, 'POST') and request.POST:
                    form_data = dict(request.POST)
                    # Exclude sensitive fields
                    form_data = {
                        k: '[REDACTED]' if k.lower() in ['password', 'token', 'secret', 'key', 'authorization']
                        else v for k, v in form_data.items()
                    }
                    data['body'] = form_data

                # JSON data
                elif 'application/json' in content_type:
                    raw = getattr(request, 'body', b'')
                    try:
                        body_data = json.loads(raw.decode('utf-8')) if raw else {}
                        if isinstance(body_data, dict):
                            body_data = {
                                k: '[REDACTED]' if k.lower() in ['password', 'token', 'secret', 'key', 'authorization']
                                else v for k, v in body_data.items()
                            }
                        data['body'] = body_data
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        data['body'] = 'Unable to decode JSON body'

                # Other types
                else:
                    raw = getattr(request, 'body', b'')
                    if raw:
                        try:
                            data['body'] = raw.decode('utf-8')
                        except UnicodeDecodeError:
                            data['body'] = 'Binary data not shown'

            # Headers
            if hasattr(request, 'headers'):
                raw_headers = dict(request.headers)
                sensitive = ['cookie', 'authorization', 'proxy-authorization', 'user-role']
                data['headers'] = {
                    k.lower(): '[REDACTED]' if k.lower() in sensitive else v
                    for k, v in raw_headers.items()
                }

            # Content type
            if hasattr(request, 'content_type'):
                data['content_type'] = request.content_type

        except Exception as e:
            logger.warning("Failed to extract request data: %s", e)
        return data

    def _get_client_ip(self, request: Any) -> str:
        """Get the client IP address from request headers or META."""
        xff = request.META.get('HTTP_X_FORWARDED_FOR')
        if xff:
            return xff.split(',')[0].strip()
        return request.META.get('HTTP_X_REAL_IP') or request.META.get('REMOTE_ADDR', '')

    def __call__(self, request: Any) -> Any:
        """Process the request, log audit info, and return response"""
        start = time.time()
        response = self.get_response(request)

        if not self.logger:
            logger.warning("Logger not initialized, skipping audit logging")
            return response

        try:
            # Build log payload
            req_data = self._extract_request_data(request)
            duration = int((time.time() - start) * 1000)
            req_data['duration_ms'] = duration
            req_data['status_code'] = getattr(response, 'status_code', None)

            if hasattr(response, 'content'):
                try:
                    req_data['response_data'] = response.content.decode('utf-8')
                except Exception:
                    req_data['response_data'] = 'Binary response data not shown'

            log_info = LogInfo(
                ip_address=self._get_client_ip(request),
                user_id=str(request.user.id) if getattr(request, 'user', None) and request.user.is_authenticated else None,
                username=request.META.get('HTTP_USER_USERNAME'),
                request_time=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start)),
                action=getattr(request, 'path', ''),
                request_data=req_data,
                headers=req_data.get('headers', {})
            )

            self.logger.publish(log_info)

        except Exception as e:
            logger.error("Error logging request: %s", e)

        return response
