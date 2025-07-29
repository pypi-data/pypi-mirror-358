import logging
import sys
from typing import Optional

SUCCESS = 25
logging.addLevelName(SUCCESS, 'SUCCESS')

class ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': '\033[36m',
        'INFO': '\033[90m',     
        'SUCCESS': '\033[92m',
        'WARNING': '\033[33m',
        'ERROR': '\033[31m',    
        'CRITICAL': '\033[35m',
        'RESET': '\033[0m',     
        'NAME': '\033[94m',     
    }
    
    def format(self, record):
        log_message = super().format(record)
        
        level_color = self.COLORS.get(record.levelname, '')
        name_color = self.COLORS['NAME']
        reset = self.COLORS['RESET']
        
        parts = log_message.split(' - ')
        if len(parts) >= 4:
            timestamp, name, level, message = parts[0], parts[1], parts[2], ' - '.join(parts[3:])
            level_padded = level.ljust(9)
            name_width = 30
            name_parts = name.split('.')
            if len(name_parts) > 2:
                first = name_parts[0]
                last = name_parts[-1]
                display = f"{first}...{last}"
                if len(display) > name_width:
                    max_last_len = name_width - len(first) - 6
                    if max_last_len > 0:
                        last_trunc = last[:max_last_len] + '...'
                        display = f"{first}...{last_trunc}"
                    else:
                        display = (first + '...')[:name_width]
                name_display = display.ljust(name_width)
            else:
                joined = '.'.join(name_parts)
                if len(joined) > name_width:
                    name_display = joined[:name_width-3] + '...'
                else:
                    name_display = joined.ljust(name_width)
            formatted = f"{level_color}{level_padded}{reset} {name_color}{name_display}{reset} | {message}"
        else:
            formatted = f"{level_color}{log_message}{reset}"
        
        return formatted

class SuccessLogger(logging.Logger):
    def success(self, msg, *args, **kwargs):
        if self.isEnabledFor(SUCCESS):
            self._log(SUCCESS, msg, args, **kwargs)

logging.setLoggerClass(SuccessLogger)

def setup_logger(name: Optional[str] = None, level: Optional[int] = None) -> SuccessLogger:
    if name is None:
        import inspect
        frame = inspect.currentframe().f_back
        name = frame.f_globals.get('__name__', 'test-api')
    
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = ColoredFormatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.propagate = False
        
    if level is not None:
        logger.setLevel(level)
    
    return logger