#!/usr/bin/env python3
"""
Personal data
"""

import re
import logging
from typing import List
import mysql.connector
from os import environ


PII_FIELDS = ("ssn", "password", "phone", "name", "email")


def filter_datum(fields: List[str], redaction: str,
                 message: str, separator: str) -> str:
    """ Returns log message """
    for f in fields:
        message = re.sub(f'{f}=.*?{separator}',
                         f'{f}={redaction}{separator}', message)
    return message


def get_logger() -> logging.Logger:
    """ Returns logger """
    logger = logging.getLogger("user_data")
    logger.propagate = False
    logger.setLevel(logging.INFO)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(RedactingFormatter(list(PII_FIELDS)))
    logger.addHandler(stream_handler)

    return logger


def get_db() -> mysql.connector.connection.MySQLConnection:
    """ Returns a DB connection """
    username = environ.get("PERSONAL_DATA_DB_USERNAME", "root")
    password = environ.get("PERSONAL_DATA_DB_PASSWORD", "")
    host = environ.get("PERSONAL_DATA_DB_HOST", "localhost")
    db_name = environ.get("PERSONAL_DATA_DB_NAME")

    cnx = mysql.connector.connection.MySQLConnection(user=username,
                                                     password=password,
                                                     host=host,
                                                     database=db_name)
    return cnx


def main():
    """
    Main method
    """
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users;")

    fields = [i[0] for i in cursor.description]
    logger = get_logger()

    for row in cursor:
        str_row = ''.join(f'{f}={str(r)}; ' for r, f in zip(row, fields))
        logger.info(str_row.strip())

    cursor.close()
    db.close()


class RedactingFormatter(logging.Formatter):
    """ Redacting Formatter class
        """

    REDACTION = "***"
    FORMAT = "[HOLBERTON] %(name)s %(levelname)s %(asctime)-15s: %(message)s"
    SEPARATOR = ";"

    def __init__(self, fields: List[str]):
        super(RedactingFormatter, self).__init__(self.FORMAT)
        self.fields = fields

    def format(self, record: logging.LogRecord) -> str:
        """ Filters values """
        record.msg = filter_datum(self.fields, self.REDACTION,
                                  record.getMessage(), self.SEPARATOR)
        return super(RedactingFormatter, self).format(record)


if __name__ == '__main__':
    main()
