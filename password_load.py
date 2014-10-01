"""
Created on Sep 30, 2014
@Author: zixuan zhang

This script is to load account-password pair into MongoDB
"""

import os
import bson
import logging
import pymongo

FILE_NAME = 'xh-2.txt'

#log format config
FORMAT = '%(asctime)s %(levelname)s %(name)s %(message)s'
logging.basicConfig(filename = 'load.log', level = logging.INFO, format = FORMAT)
_LOGGER = logging.getLogger()

def _get_db():
    con = pymongo.Connection("127.0.0.1")
    db = con['passwd']
    return db

_db = _get_db()
def pair_insert(data):
    _db.renren.insert(data)
    
def load():
    count = 0
    with open(FILE_NAME) as fp:
        for line in fp:
            items = line.split()
            count += 1
            if len(items) < 2:
                _LOGGER.warning("Count: %d,\
                        InfoIncompleteError: No password exits")
                continue
            account = items[0]
            password = items[1]
            try:
                length = len(password)
            except Exception, err:
                _LOGGER.error("Count: %d, Account: %s, Password: %s\n \
                        LengthGetError: %s" % (count, account, password, err))
                continue
            try:
                data = {"_id": account, "password": password, "length": length}
                pair_insert(data)
                _LOGGER.info('Count: %d, Account: %s, Password: %s' % (count, account, password))
            except bson.errors.InvalidStringData, err:
                _LOGGER.error("Count: %d, Account: %s, Password: %s\n \
                        InvalidStringError: %s" % (count, account, password, err))
    fp.close()

def main():
    load()

if __name__ == "__main__":
    main()
