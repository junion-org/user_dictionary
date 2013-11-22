#!/usr/bin/env python
# coding: utf-8
import sys
import codecs

# メイン関数
def main():
    rfp = open(sys.argv[1])
    wfp = codecs.open(sys.argv[2], 'w', 'utf8')
    for line in rfp:
        try:
            line = unicode(line, 'euc_jp')
        except UnicodeDecodeError:
            continue
        word = line.rstrip().split('\t')[1]
        wfp.write('%s\n' % word)

# エントリポイント
if __name__ == '__main__':
    main()

