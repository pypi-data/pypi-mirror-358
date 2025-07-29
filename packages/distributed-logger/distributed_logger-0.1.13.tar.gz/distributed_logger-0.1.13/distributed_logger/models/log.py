import json
import time
from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional


@dataclass
class LogInfo:
    """
    Data class for storing log information.
    """
    ip_address: str
    user_id: Optional[str]
    username: Optional[str]
    request_time: str
    action: str
    request_data: Dict[str, Any]
    headers: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the log info to a dictionary"""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert the log info to a JSON string"""
        return json.dumps(self.to_dict())
    
    def get_timestamp(self) -> float:
        """Get the timestamp in seconds since epoch"""
        try:
            # Try to parse the request_time if it's in the format '%Y-%m-%d %H:%M:%S'
            return time.mktime(time.strptime(self.request_time, '%Y-%m-%d %H:%M:%S'))
        except ValueError:
            # If parsing fails, return current timestamp
            return time.time()
