"""
Create on Oct 6, 2014
@Author: zixuan zhang

This script is to analyze pinyin pattern in password
"""

import time

import pymongo

from common import DB_HANDLER, _LOGGER

class Node(object):
    """
    pinyin tree node class
    """
    def __init__(self, character="$", isValue=False):
        character = character.lower()
        self.char = character
        self.isValue = isValue
        self.childs = {}
        """
        for i in range(26):
            childs[chr(i+ord('a'))] = None
        """

class PinyinTree(object):
    """
    pinyin tree
    """
    def __init__(self):
        self.root = Node(character="$", isValue=False)
        self.pinyin_count = 0

    def insert_pinyin(self, pinyin):
        current = self.root
        self.pinyin_count += 1
        count = 0
        for char in pinyin:
            if char not in current.childs:
                if count == (len(pinyin) - 1):
                    child = Node(char, isValue=True)
                else:
                    child = Node(char, isValue=False)
                current.childs[char] = child
            elif count == (len(pinyin) - 1) and not current.childs[char].isValue:
                current.childs[char].isValue = True
            count += 1
            current = current.childs[char]

    def _load_chars(self, node, pinyin):
        pinyin.append(node.char)
        if node.isValue:
            p = ""
            for c in pinyin:
                p += c
            #_LOGGER.info(p)
        for child in node.childs:
            self._load_chars(node.childs[child], pinyin)
            pinyin.pop(len(pinyin) - 1)
        
    def print_pinyins(self):
        print "Pinyin Total Count: %d" % self.pinyin_count
        #_LOGGER.info("Pinyin Total Count: %d" % self.pinyin_count)
        pinyin = []
        node = self.root
        self._load_chars(node, pinyin)

    def exists(self, pinyin):
        current = self.root
        count = 0
        for char in pinyin:
            if char not in current.childs:
                return False
            if count == (len(pinyin) - 1):
                if not current.childs[char].isValue:
                    return False
                else:
                    return True
            current = current.childs[char]
            count += 1

def build_pinyin_tree(pinyinTree):
    con = pymongo.Connection("127.0.0.1")
    db = con['password']
    pinyins = db.pinyin.find()

    for pinyin in pinyins:
        pinyinTree.insert_pinyin(pinyin['pinyin'])
    pinyinTree.print_pinyins()

def is_pinyin(pinyinTree, pinyin):
    if not pinyin:
        return True
    #print "Judge %s" % pinyin
    for i in range(1, len(pinyin) + 1):
        substr = pinyin[0:i]
        if pinyinTree.exists(substr):
            substr2 = pinyin[i:]
            #print "%s match, next substring %s" % (substr, substr2)
            result = is_pinyin(pinyinTree, substr2)
            #print "%s judge result: " % substr2, result
            if result:
                return True
    return False

def driver():
    pinyinTree = PinyinTree()
    build_pinyin_tree(pinyinTree)
    #print pinyinTree.exists("zhang")
    #print pinyinTree.exists("zi")
    #print pinyinTree.exists("xuan")
    now = time.time()
    for i in range(100000):
        is_pinyin(pinyinTree, "zhangzixuan")
        is_pinyin(pinyinTree, "zhuzhu")
    cost = time.time() - now
    print cost

def main():
    driver()

if __name__ == "__main__":
    main()
