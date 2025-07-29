import logging

from parquetdb import ParquetDB

logger = logging.getLogger(__name__)


def main():

    db = ParquetDB("testdb")
    logger.info("Hello, World22222!")


if __name__ == "__main__":
    main()
