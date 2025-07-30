import logging
from pydantic import BaseModel
from typing import Optional

from .Enums import ParseMode


class Config(BaseModel):
    # polling
    polling_delay: float = 1 / 30
    wait_polling_delay: float = 1 / 20
    polling_time: float = 10
    
    # connection
    timeout: float = 5
    update_limit: int = 100
    retry_count: int = 5
    
    # name
    name_max_length: int = 18
    
    # log
    log_format: str = '[%(levelname)s] - %(name)s - %(message)s'
    log_file: Optional[str] = None
    stream_handler_level: int = logging.INFO
    file_handler_level: int = logging.WARNING
    
    # parse
    parse_mode: Optional[ParseMode] = None
    
    # actions
    auto_actions: bool = True

    
        