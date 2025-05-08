import logging

def setup_logger(name, log_file, level=logging.INFO):
    """
    設置日誌記錄器
    :param name: 日誌記錄器名稱
    :param log_file: 日誌檔案路徑
    :param level: 日誌等級
    :return: 設置好的日誌記錄器
    """
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # 檔案日誌
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)

    # 控制台日誌
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger