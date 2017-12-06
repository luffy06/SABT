#-*-coding:utf-8-*-
import copy
import re

def isEnglishWord(w):
  w = w.lower()
  if w >= 'a' and w <= 'z':
    return True
  return False

def isNumber(w):
  if w >= '0' and w <= '9':
    return True
  return False

def getNextEnglishWord(text, begin):
  end = len(text)
  for i in range(begin, len(text)):
    if isEnglishWord(text[i]) == False:
      end = i
      break
  return (text[begin:end], end)

def getNextNumber(text, begin):
  nbegin = begin
  if text[begin] == '+' or text[begin] == '-':
    nbegin = begin + 1
  end = len(text)
  foundPoint = False
  for i in range(nbegin, len(text)):
    if isNumber(text[i]) == False:
      if text[i] == '.':
        if foundPoint == False:
          foundPoint = True
        else:
          end = i
          break
      else:
        end = i
        break
  return (text[begin:end], end)

def parseText(text):
  l = len(text)
  res = []
  i = 0
  while i < l:
    if isEnglishWord(text[i]) == True:
      w, i = getNextEnglishWord(text, i)
      res.append(w)
    elif isNumber(text[i]) == True or text[i] == '.':
      w, i = getNextNumber(text, i)
      res.append(w)
    elif i < l - 1 and (text[i] == '-' or text[i] == '+') and (isNumber(text[i + 1]) == True or text[i + 1] == '.'):
      w, i = getNextNumber(text, i)
      res.append(w)
    else:
      res.append(text[i])
      i = i + 1
  res = []
  for j in text:
    res.append(j)
  return res

def getStartPos(begin, textlist):
  if begin == -1:
    return -1
  l = 0
  for i, ti in enumerate(textlist):
    if l >= begin:
      if l == begin:
        return i
      else:
        print("Error")
    l = l + len(ti)
  print("Error 2")
  return -1

class Word(object):
  def __init__(self, text, begin):
    self.text = text
    self.begin = begin
    l = parseText(self.text)
    self.textlen = len(l)

class SentimentCell(object):

  def __init__(self, theme, word, anls):
    self.theme = theme
    self.word = word
    self.anls = anls
    

class Row(object):

  def __init__(self, rowid, text, theme, word, anls):
    self.rowid = rowid
    self.text = text.replace(" ", "，")
    self.textlist = parseText(self.text)
    self.textlen = len(self.text)
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

        # wb = getStartPos(self.text.find(w), self.textlist)
        # tb = getStartPos(self.text.find(t), self.textlist)
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

class SentimentPair(object):
  """docstring for SentimentPair"""
  def __init__(self, rowid, theme, word, vector):
    super(SentimentPair, self).__init__()
    self.rowid = rowid
    self.theme = theme
    self.word = word
    self.vector = vector

  def set_label(self, label):
    self.label = label

  def set_anls(self, anls):
    self.anls = anls
    
if __name__ == '__main__':
  text = "你好啊Ok，我就克一把0.+fds2131-.12312"
  print(parseText(text))

