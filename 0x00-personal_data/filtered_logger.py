#!/usr/bin/env python3
"""Filtered logger module"""
from typing import List
import re
import logging
import os
import mysql.connector


PII_FIELDS = ('name', 'email', 'phone', 'ssn', 'password')


def filter_datum(fields: List[str], redaction: str,
                 message: str, separator: str) -> str:
    """Returns an obfuscated log message"""
    for fd in fields:
        message = re.sub(fd+'=.*?'+separator,
                         fd+'='+redaction+separator, message)
    return message


class RedactingFormatter(logging.Formatter):
    """ Redacting Formatter class"""

    REDACTION = "***"
    FORMAT = "[HOLBERTON] %(name)s %(levelname)s %(asctime)-15s: %(message)s"
    SEPARATOR = ";"

    def __init__(self, fields: List[str]):
        super(RedactingFormatter, self).__init__(self.FORMAT)
        self.fields = fields

    def format(self, record: logging.LogRecord) -> str:
        """
        Redact the message of LogRecord
        """
        return filter_datum(self.fields, self.REDACTION,
                            super().format(record), self.SEPARATOR)


def get_logger() -> logging.Logger:
    """
    Return a logging.Logger object
    """
    ret_log = logging.getLogger("user_data")
    ret_log.setLevel(logging.INFO)
    ret_log.propagate = False

    steam_hdler = logging.StreamHandler()

    formatter = RedactingFormatter(PII_FIELDS)

    steam_hdler.setFormatter(formatter)
    ret_log.addHandler(steam_hdler)
    return ret_log


def get_db() -> mysql.connector.connection.MySQLConnection:
    """
    Implement db
    """
    host = os.getenv('PERSONAL_DATA_DB_HOST') or "localhost"
    db = os.getenv('PERSONAL_DATA_DB_NAME')
    user = os.getenv('PERSONAL_DATA_DB_USERNAME') or "root"
    pswrd = os.getenv('PERSONAL_DATA_DB_PASSWORD') or ""
    cntn = mysql.connector.connect(user=user,
                                   password=pswrd,
                                   host=host,
                                   database=db)
    return cntn


def main():
    """
    Logs the information about user records.
    """
    db = get_db()
    logger = get_logger()
    cusr = db.cursor()
    cusr.execute("SELECT * FROM users;")
    cols = cusr.column_names
    for row in cusr:
        msg = "".join("{}={}; ".format(k, v) for k, v in zip(cols, row))
        logger.info(msg.strip())
    cusr.close()
    db.close()


if __name__ == "__main__":
    main()
