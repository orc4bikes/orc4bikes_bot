import logging
import logging.handlers

from src.Orc4bikesBot import Orc4bikesBot

class ErrorDrivenHandler(logging.handlers.MemoryHandler):
    """Event driven handler, buffers INFO logs and emit only when ERROR logs occurs."""
    def shouldFlush(self, record: logging.LogRecord) -> bool:
        if record.levelno >= logging.ERROR:
            self.buffer.insert(0, logging.LogRecord(
                name=record.name,
                level=record.levelno,
                pathname=record.pathname,
                lineno=record.lineno,
                msg="---------- Error occurred, flushing logs... ----------",
                args=None,
                exc_info=None))
            self.buffer.pop()
            return True
        if len(self.buffer) > self.capacity:
            self.buffer.pop(0)
        return False

def prep_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        fmt='%(asctime)s.%(msecs)03d %(filename)s: [%(levelname)s] %(message)s',
        datefmt="%Y-%m-%d %H:%M:%S")

    target_stream_handler = logging.StreamHandler()
    target_stream_handler.setFormatter(formatter)
    memory_handler = ErrorDrivenHandler(20, target=target_stream_handler)
    memory_handler.setFormatter(formatter)
    logger.addHandler(memory_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.WARNING)
    logger.addHandler(stream_handler)

    return logger


if __name__ == '__main__':
    logger = prep_logging()
    
    newbot = Orc4bikesBot()
    logger.info("Running Orc4bikesBot now")
    print("Running Orc4bikesBot now...")

    newbot.main()
