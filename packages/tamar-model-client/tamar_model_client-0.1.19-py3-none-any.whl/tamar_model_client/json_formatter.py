import json
import logging
from datetime import datetime


class JSONFormatter(logging.Formatter):
    def format(self, record):
        # log_type 只能是 request、response 或 info
        log_type = getattr(record, "log_type", "info")
        if log_type not in ["request", "response", "info"]:
            log_type = "info"
            
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "type": log_type,
            "uri": getattr(record, "uri", None),
            "request_id": getattr(record, "request_id", None),
            "data": getattr(record, "data", None),
            "message": record.getMessage(),
            "duration": getattr(record, "duration", None),
        }
        # 增加 trace 支持
        if hasattr(record, "trace"):
            log_data["trace"] = getattr(record, "trace")
        return json.dumps(log_data, ensure_ascii=False)