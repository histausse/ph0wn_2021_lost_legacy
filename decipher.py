#!/usr/bin/env python3

import sys
from cipher import proc1
TEST_ID = "Niklaus Wirth"
TEST_PWD = "Oberon is as simple as possible"

def decipher(l:list[int])->str:
    values = []
    for i, c in enumerate(l):
        w3 = 1
        w2 = 0 # There is a small off by one :)
        while (w3 & 255) != c:
            w3 *= 3
            while (w3 > 256):
                w3 -= 257
            w2 += 1
        values.append(chr(w2-i))
    return "".join(values)

def read_database():
    with open("database.bin", "br") as db:
        for i in range(40):
            db.seek(i*16)
            chunk = db.read(32)
            try:
                print(decipher(chunk))
            except Exception as e:
                print(e)


def test():
    print(decipher(proc1(TEST_ID)))
    print(decipher(proc1(TEST_PWD)))

if __name__ == "__main__":
    read_database()
