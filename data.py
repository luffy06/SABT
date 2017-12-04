#-*-coding:utf-8-*-
import copy
import re
# from api import TencentWenZhi

class Word(object):
  def __init__(self, text, begin):
    self.text = text
    self.begin = begin

class SentimentCell(object):

  def __init__(self, theme, word, anls):
    self.theme = theme
    self.word = word
    self.anls = anls
    

class Row(object):

  def __init__(self, rowid, text, theme, word, anls):
    self.rowid = rowid
    self.text = text
    self.parse(theme, word, anls)

  def parse(self, theme, word, anls):
    self.sclist = []
    thlist = theme.split(';')
    wlist = word.split(';')
    alist = anls.split(';')
    if len(thlist) == len(wlist) and len(thlist) == len(alist):
      length = len(thlist)
      for i in range(length):
        t = thlist[i]
        w = wlist[i]
        a = alist[i]

        wb = self.text.find(w)      

        if wb != -1 and t != "" and w != "" and a != "":
          # t = TencentWenZhi.fixWrongWord(t)
          # w = TencentWenZhi.fixWrongWord(w)
          sc = SentimentCell(Word(t, -1), Word(w, -1), a)
          self.sclist.append(sc)
    else:
      print("Length is not matched!!!!!" + str(self.rowid) + " theme:" + theme + " word:" + word + " anls:" + anls)