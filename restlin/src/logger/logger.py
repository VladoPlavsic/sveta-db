import logging

class Logger:
    def __init__(self, filename):
        logging.basicConfig(
            filename="src/logger/log", level=logging.INFO)

    def log_info(self, message):
        logging.info(message)

    def log_warning(self, message):
        logging.warning(message)

    def log_error(self, message):
        logging.error(message)

def main():
    logger = Logger("test")
    logger.log_info("INFO")
    logger.log_warning("WARNING")
    logger.log_error("ERROR")

if __name__ == "__main__":
    main()
