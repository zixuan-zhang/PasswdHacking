"""
Created on Oct 5, 2014
@Author: zixuan zhang

This script provide common used method
"""

import os
import bson
import logging
import pymongo
import memcache

SAVE_LOG = "save.log"
FILE_NAME = {
        "renren": "xh-2.txt",
        "gmail": "gmail.txt"
        }
DB_HANDLER = {
        "renren": None,
        "gmail": None
        }
MC = None
_LOGGER = None

def _get_db():
    con = pymongo.Connection("127.0.0.1")
    db = con['password']
    #global DB_HANDLER
    DB_HANDLER["renren"] = db['renren']
    DB_HANDLER["gmail"] = db["gmail"]


def insert_db(data, key="renren"):
    """
    insert data into renren database
    """
    _db = DB_HANDLER[key]
    _db.insert(data)

def save_password(key="renren"):
    """
    save pasword into database
    << key: which file should be saved
    """
    _LOGGER.info("Save Password Started...")
    count = 0
    with open(FILE_NAME[key]) as fp:
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
                insert_db(data, key)
                _LOGGER.info('Count: %d, Account: %s, Password: %s' % (count, account, password))
            except bson.errors.InvalidStringData, err:
                _LOGGER.error("Count: %d, Account: %s, Password: %s\n \
                        InvalidStringError: %s" % (count, account, password, err))
    fp.close()

    # database saved success, record into disk
    with open(SAVE_LOG, "w") as fp:
        fp.write("%s 1" % key)
    fp.close()

def load_password(key):
    """
    load password from database to cache by using memcached
    key-value organized by seq-passwd, like 1-123456, 2-111111
    """

    #clear all data in memcache
    MC.flush_all()
    count = 1
    _LOGGER.info("Caching Password %s Start..." % key)
    _db = DB_HANDLER[key]
    password_pairs = _db.find()
    for password_pair in password_pairs:
        if count % 1000 == 0:
            _LOGGER.info("Caching Password %s Done" % count)
        password = password_pair['password']
        MC.set(str(count), password)
        _LOGGER.info("Caching Count: %d, Password: %s" % (count, password))
        count += 1
    _LOGGER.info("Caching Password Done. Total Count: %d" % (count - 1))

def initialize(key = "renren"):
    """
    Initialize neccessary operations. including:
        1. save password into database (if not done)
        2. cache password into memcache
        3. log handler initialize
    """
    # log format config
    FORMAT = '%(asctime)s %(levelname)s %(name)s %(message)s'
    logging.basicConfig(filename = 'load.log', level = logging.INFO, format = FORMAT)
    global _LOGGER, MC
    _LOGGER = logging.getLogger()

    # database initialize
    _get_db()

    if not os.path.exists(SAVE_LOG):
        save_password(key) # default "renren"
        DB_HANDLER[key].create_index([("password", pymongo.ASCENDING)])

    # memcache initialize
    MC = memcache.Client(['127.0.0.1:11211'])
    load_password(key)

def main():
    initialize("renren")

if __name__ == "__main__":
    main()
