#!/usr/bin/env python
# coding: utf-8
import sys

# メイン関数
def main():
    a, b = set(), set()
    with open(sys.argv[1]) as file:
        for line in file:
            w = line.rstrip('\n')
            a.add(w)
    with open(sys.argv[2]) as file:
        for line in file:
            w = line.rstrip('\n')
            b.add(w)
    c = a & b
    with open(sys.argv[3], 'w') as file:
        for w in sorted(c):
            file.write('%s\n' % w)

# エントリポイント
if __name__ == '__main__':
    main()

