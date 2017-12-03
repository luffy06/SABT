#-*-coding:utf-8-*-
import copy
import re

def getNextNumber(text, begin):
  isEnglish = False
  for i in range(begin, len(text)):
    if (text[i] >= 'A' and text[i] <= 'Z') or (text[i] >= 'a' and text[i] <= 'z'):
      isEnglish = True
    else:
      if isEnglish == True:
        return i
  return 0


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
    self.textlist = []
    self.parse(theme, word, anls)
    self.crf()

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
        tb = self.text.find(t)

        if wb != -1 and t != "" and w != "" and a != "":
          sc = SentimentCell(Word(t, tb), Word(w, wb), a)
          self.sclist.append(sc)
    else:
      print("Length is not matched!!!!!" + str(self.rowid) + " theme:" + theme + " word:" + word + " anls:" + anls)

  def crf(self):
    self.order = []
    self.position = []
    for i in self.text:
      self.order.append("O")
      self.position.append("S")

    length = len(self.text)
    for sc in self.sclist:
      pos = 0
      wlen = len(sc.word.text)
      while pos < length:
        sb = self.text.find(sc.word.text, pos)
        if sb == -1:
          break
        for i in range(sb, sb + wlen):
          self.order[i] = "S"
          self.position[i] = "M"
        if wlen == 1:
          self.position[sb] = "S"
        else:
          self.position[sb] = "B"
          self.position[sb + wlen - 1] = "E"
        pos = sb + wlen

    for sc in self.sclist:
      pos = 0
      tlen = len(sc.theme.text)
      while pos < length:
        tb = self.text.find(sc.theme.text, pos)
        if tb == -1:
          break
        for i in range(tb, tb + tlen):
          self.order[i] = "T"
          self.position[i] = "M"
        if tlen == 1:
          self.position[tb] = "S"
        else:
          self.position[tb] = "B"
          self.position[tb + tlen - 1] = "E"
        pos = tb + tlen

