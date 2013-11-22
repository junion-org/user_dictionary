#!/usr/bin/env python
# coding: utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf_8')
import re
import codecs
import urllib2
import htmlentitydefs

# ストップワード
def stop_word(s):
    if s == u'\u0000':
        return True
    if re.search(r'&#?[0-9a-zA-Z]+;', s):
        return True
    if re.compile(r'\d{4}-\d{2}-\d{2}$').match(s) is not None:
        return True
    if re.compile(r'\d+年$').match(s) is not None:
        return True
    return False

# 実体参照 & 文字参照を通常の文字に戻す
def htmlentity2unicode(text):
    # 正規表現のコンパイル
    reference_regex = re.compile(u'&(#x?[0-9a-f]+|[a-z]+);', re.IGNORECASE)
    num16_regex = re.compile(u'#x\d+', re.IGNORECASE)
    num10_regex = re.compile(u'#\d+', re.IGNORECASE)
    
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

# keywordlist_furigana.csvの読み込み
try:
    fin = open('keywordlist_furigana.csv')
except IOError:
    url = 'http://d.hatena.ne.jp/images/keyword/keywordlist_furigana.csv'
    fin = urllib2.urlopen(url)

# 出力
fout = codecs.open('hatena.csv', 'w', 'utf_8')
for i, line in enumerate(fin):
    try:
        line = unicode(line, 'euc_jp')
    except UnicodeDecodeError:
        continue
    word = line.rstrip().split('\t')[1]
    #word = htmlentity2unicode(word) # HTML特殊文字をデコードする（ただしLRMでエラーがあった）
    if not stop_word(word):
        score = int( max(-32768.0, 6000 - 200 * (len(word)**1.3)) )
        #word = word.replace('"', '""') # ダブルクォートは二重化してエスケープ
        #str = u'"%s",-1,-1,%d,名詞,一般,*,*,*,*,"%s",*,*,hatena\n' % (word, score, word)
        if ',' in word:
            # カンマが存在すれば無視
            continue
        str = u'%s,-1,-1,%d,名詞,一般,*,*,*,*,%s,*,*,hatena\n' % (word, score, word)
        fout.write(str)
fin.close()
fout.close()

