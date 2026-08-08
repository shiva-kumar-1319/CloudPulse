import logging
import json
import datetime
from typing import Any, Dict


class JSONFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured CloudPulse logging.
    """
    def __init__(self, service_name: str = "cloudpulse-service"):
        super().__init__()
        self.service_name = service_name

    def format(self, record: logging.LogRecord) -> str:
        log_obj: Dict[str, Any] = {
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "service": getattr(record, "service", self.service_name),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Include request ID / correlation ID if present
        if hasattr(record, "request_id"):
            log_obj["request_id"] = record.request_id
        if hasattr(record, "event_id"):
            log_obj["event_id"] = record.event_id

        # Include exception info if present
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        # Include additional extra attributes
        if hasattr(record, "extra") and isinstance(record.extra, dict):
            for k, v in record.extra.items():
                if k not in ("password", "token", "secret", "jwt_secret"):
                    log_obj[k] = v

        return json.dumps(log_obj)


def get_logger(service_name: str, level: str = "INFO") -> logging.Logger:
    """
    Configure and return a structured JSON logger for a specific service.
    """
    logger = logging.getLogger(service_name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    # Avoid adding multiple handlers if logger is already configured
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JSONFormatter(service_name=service_name))
        logger.addHandler(handler)
        logger.propagate = False

    return logger
