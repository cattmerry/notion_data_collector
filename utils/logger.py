import logging


def logger_setting(level: str) -> logging.Logger:
    """
    본 프로젝트의 로깅을 위한 logger 인스턴스 생성
    :param level: 'DEBUG', 'INFO', 'WARNING'
    :return: logger 인스턴스
    """
    logger = logging.getLogger()

    if len(logger.handlers) > 0:
        return logger

    logger.setLevel(level)

    formatter = logging.Formatter(u'%(asctime)s [%(levelname)8s] %(message)s')

    streaming_handler = logging.StreamHandler()
    streaming_handler.setFormatter(formatter)

    logger.addHandler(streaming_handler)

    return logger
