#!/usr/bin/env python
# coding: utf-8
import re
import os
import codecs
import urllib2
import unicodedata
import htmlentitydefs
from optparse import OptionParser

# 設定
urls = {
        'wikipedia' : 'http://dumps.wikimedia.org/jawiki/latest/jawiki-latest-all-titles-in-ns0.gz',
        'hatena'    : 'http://d.hatena.ne.jp/images/keyword/keywordlist_furigana.csv',
        'niconico'  : 'http://tkido.com/data/nicoime.zip',
}
names = {
        'wikipedia' : urls['wikipedia'].split('/')[-1],
        'hatena'    : urls['hatena'].split('/')[-1],
        'niconico'  : urls['niconico'].split('/')[-1],
}
reference_regex = re.compile(u'&(#x?[0-9a-f]+|[a-z]+);', re.IGNORECASE)
num16_regex     = re.compile(u'#x\d+', re.IGNORECASE)
num10_regex     = re.compile(u'#\d+', re.IGNORECASE)

def exists(source):
    """
    同じディレクトリに対象ソースが存在するかチェックする
    """
    return os.path.exists(names[source])

def download(source, chunk_size=8192, show_progress=True):
    """
    対象ソースを同じディレクトリにダウンロードする
    """
    file       = open(names[source], 'wb')
    response   = urllib2.urlopen(urls[source])
    total_size = response.info().getheader('Content-Length').strip()
    total_size = int(total_size)
    bytes_read = 0
    while True:
        chunk = response.read(chunk_size)
        file.write(chunk)
        bytes_read += len(chunk)
        if not chunk:
            break
        if show_progress:
            progress(names[source], bytes_read, chunk_size, total_size)
    file.close()

def progress(filename, bytes_read, chunk_size, total_size):
    """
    ダウンロード状況を出力する
    """
    percent = float(bytes_read) / total_size
    percent = round(percent * 100, 2)
    bars = int(0.5 * percent)
    print '%5.2f%% [%s%s] %s\r' % (percent, '=' * bars, ' ' * (50 - bars), filename),
    if bytes_read >= total_size:
        print

def wikipedia_keywords():
    """
    wikipediaキーワードを返す
    """
    name  = 'wikipedia'
    words = set()
    # ダウンロード，解凍
    if not exists(name):
        download(name)
        filename = names[name]
        os.system('gunzip -c %s > %s' % (filename, filename.split('.')[0]))
    # キーワード抽出
    with open(names[name].split('.')[0]) as file:
        for i, line in enumerate(file):
            print 'wikipedia:\t%8d lines.\r' % (i+1),
            try:
                line = line.rstrip()
                line = unicode(line, 'utf8')
                line = unicodedata.normalize('NFKC', line)
                line = line.strip()
            except UnicodeDecodeError:
                continue
            if not filter(line):
                words.add(line)
        print
    return words

def hatena_keywords():
    """
    hatenaキーワードを返す
    """
    name  = 'hatena'
    words = set()
    # ダウンロード，解凍
    if not exists(name):
        download(name)
    # キーワード抽出
    with open(names[name]) as file:
        for i, line in enumerate(file):
            print 'hatena:\t\t%8d lines.\r' % (i+1),
            try:
                line = line.rstrip()
                line = unicode(line, 'euc-jp')
                line = htmlentity2unicode(line)
                line = unicodedata.normalize('NFKC', line)
                line = line.split('\t')[1].strip()
            except UnicodeDecodeError:
                continue
            if not filter(line):
                words.add(line)
        print
    return words

def niconico_keywords():
    """
    niconicoキーワードを返す
    """
    name  = 'niconico'
    words = set()
    # ダウンロード，解凍
    if not exists(name):
        download(name)
        filename = names[name]
        os.system('unzip -q %s' % filename)
    # キーワード抽出
    with codecs.open('%s_msime.txt' % names[name].split('.')[0], 'r', 'utf-16-le') as file:
        # 8行読み飛ばし
        for i in range(8):
            file.readline()
        for i, line in enumerate(file):
            print 'niconico:\t%8d lines.\r' % (i+1),
            try:
                line = line.rstrip()
                line = htmlentity2unicode(line)
                line = unicodedata.normalize('NFKC', line)
                if '\t' not in line:
                    continue
                line = line.split('\t')[1].strip()
            except UnicodeDecodeError:
                continue
            if not filter(line):
                words.add(line)
        print
    return words

def htmlentity2unicode(text):
    """
    実体参照 & 文字参照を通常の文字に戻す
    """
    result = u''
    i = 0
    while True:
        # 実体参照 or 文字参照を見つける
        match = reference_regex.search(text, i)
        if match is None:
            result += text[i:]
            break
        result += text[i:match.start()]
        i = match.end()
        name = match.group(1)
        # 実体参照
        if name in htmlentitydefs.name2codepoint.keys():
            result += unichr(htmlentitydefs.name2codepoint[name])
        # 文字参照
        elif num16_regex.match(name):
            # 16進数
            result += unichr(int(u'0'+name[1:], 16))
        elif num10_regex.match(name):
            # 10進数
            result += unichr(int(name[1:]))
    return result

def filter(word):
    """
    キーワードのフィルタリング
    """
    # 空白文字や非文字を除外
    if not word or word == u'\u0000' or word == u'\ufeff':
        return True
    # コンマやダブルクオートを除外
    if re.search(r'[,"]', word):
        return True
    # 先頭文字の記号を除外
    #if re.search(r"^[!#/%&-*'\$\(\)\+\.]", word[0]):
    #    return True
    #if re.search(r'&#?[0-9a-zA-Z]+;', s):
    #    return True
    #if re.compile(r'\d{4}-\d{2}-\d{2}$').match(s) is not None:
    #    return True
    #if re.compile(r'\d+年$').match(s) is not None:
    #    return True
    return False

# メイン関数
def main():
    parser = OptionParser(usage='usage: %prog [wikipedia, hatena, niconico, intersection, meet]')
    options, args = parser.parse_args()
    # 引数チェック
    if len(args) != 1:
        parser.error('incorrect number of arguments.')
        return
    # sourceのチェック
    source = args[0]
    if source not in ('wikipedia', 'hatena', 'niconico', 'intersection', 'meet'):
        parser.error('source should be wikipedia, hatena, niconico, intersection and meet')
        return
    # ダウンロード，解凍，キーワード抽出
    wikipedia = wikipedia_keywords() if source in ('wikipedia', 'intersection', 'meet') else set()
    hatena    = hatena_keywords()    if source in ('hatena',    'intersection', 'meet') else set()
    niconico  = niconico_keywords()  if source in ('niconico',  'intersection', 'meet') else set()
    # キーワードの集計
    if source == 'intersection':
        words = wikipedia & hatena & niconico
    else:
        words = wikipedia | hatena | niconico
    # 辞書の作成
    with codecs.open('%s.csv' % source, 'w', 'utf8') as file:
        for i, word in enumerate(sorted(words)):
            print 'output:\t\t%8d lines.\r' % (i+1),
            score = int( max(-32768.0, 6000 - 200 * (len(word)**1.3)) )
            file.write(
                    u'%s,-1,-1,%d,名詞,固有名詞,一般,*,*,*,%s,*,*,%s\n' %
                    (word, score, word, source)
            )
        print

# エントリポイント
if __name__ == '__main__':
    main()

