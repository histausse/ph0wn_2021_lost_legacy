#!/usr/bin/env python3

import sys

def proc1(s:str)->list[int]:
    ret_list = []
    for i, c in enumerate(s):
        ret_list.append(proc3(ord(c)+i))
    return ret_list

def proc3(a:int):
    w3 = 1
    w2 = 1
    w4 = a & 255
    while (w2 <= w4):
        w3 *= 3
        while (w3 > 256):
            w3 -= 257
        w2 += 1
    return w3 & 255

def test(s):
    for c in proc1(s):
        print(hex(c))

if __name__ == "__main__":
    test(sys.argv[1])
