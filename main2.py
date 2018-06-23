import os
import numpy as np
import random

import fileutil as fu
from data import Row

TRAIN_RATE = 0.8
VALID_RATE = 0.3

def load_data(filename):
  datas = fu.read_file_from_csv(filename)
  return datas

def apart(datas):
  random.shuffle(datas)
  train = []
  valid = []
  test = []
  valid_size = int(len(datas) * TRAIN_RATE)
  train_size = int(valid_size * (1 - VALID_RATE))
  for i, d in enumerate(datas):
    if i < train_size:
      train.append(d)
    elif i < valid_size:
      valid.append(d)
    else:
      test.append(d)
  return train, valid, test

def encapsulate(datas):
  obdatas = []
  for dline in datas:
    rowid = dline[0]
    text = dline[1].lower()
    theme = ''
    word = ''
    anls = ''
    if len(dline) > 2:
      theme = dline[2].lower().replace(' ', '')
      word = dline[3].lower().replace(' ', '')
      anls = dline[4]
    if text != '' and rowid != '':
      row = Row(rowid, text, theme, word, anls)
      obdatas.append(row)
  return obdatas

def get_crf_input(datas, types):
  dirname = 'crf'
  crf_in = os.path.join(dirname, 'crf_' + types + '.in')
  for row in datas:
    for i, t in enumerate(row.text):
      if types == 'train':
        fu.write_file(crf_in, t + '\t' + row.position[i] + '-' + row.order[i] + '\n')
      else:
        fu.write_file(crf_in, t + '\n')
    fu.write_file(crf_in, '\n')

def generate_dic(data):
  word_dic = {}
  ct = 1
  for d in data:
    for t in d.text:
      if t not in word_dic:
        word_dic[t] = ct
        ct = ct + 1
  return word_dic

def get_window(begin, end, length, window):
  if end - begin + 1 == window:
    return (begin, end, True)
  elif end + 1 >= window:
    return (end - window + 1, end, True)
  elif length >= window:
    return (0, window - 1, True)
  return (0, length - 1, False)

def generate_vector(method, th, sw, textlist, length, window):
  if method == 1:
    tlen = th.textlen
    slen = sw.textlen
    st = 0
    ed = 0
    enough = False
    vec = []
    if th.begin == -1:
      # Theme word is null
      st, ed, enough = get_window(sw.begin, sw.begin + slen - 1, length, window)
    else:
      begin = min(sw.begin, th.begin)
      end = max(sw.begin, th.begin)
      if sw.begin > th.begin:
        end = end + slen - 1
      else:
        end = end + tlen - 1
      st, ed, enough = get_window(begin, end, length, window)
    j = 1
    if enough == False:
      for i in range(window - (ed - st + 1)):
        vec.append(("DEFAULF", j))
        j = j + 1
    for i in range(st, ed + 1):
      vec.append((textlist[i], j))
      j = j + 1
    return vec
  elif method == 2:
    vec = []
    begin = min(sw.begin, th.begin)
    end = max(sw.begin + sw.textlen, th.begin + th.textlen)
    middleP = min(sw.begin + sw.textlen, th.begin + th.textlen)
    middleE = max(sw.begin, th.begin)
    if th.begin == -1:
      begin = sw.begin
      middleP = sw.begin + sw.textlen
      middleE = sw.begin
      end = sw.begin + sw.textlen

    stepSide = int(window * 0.4)
    stepMiddle = window - 2 * stepSide
    for i in range(stepSide):
      pos = begin - (stepSide - i)
      if pos >= 0:
        vec.append((textlist[pos], -1))
      else:
        vec.append(("DEFAULF", -1))
    
    for i in range(stepMiddle):
      pos = middleE - (stepMiddle - i)
      if pos > middleP:
        vec.append((textlist[pos], 0))
      else:
        vec.append(("DEFAULF", 0))      

    for i in range(stepSide):
      pos = end + (i + 1)
      if pos < len(textlist):
        vec.append((textlist[pos], 1))
      else:
        vec.append(("DEFAULF", 1))
    return vec
  else:
    print("Wrong Method for Generate Vector")
    return []


def get_model_input(data, types, dic):
  
  positive = 0
  negative = 0
  window = 20
  for d in data:
    for sc in d.sclist:
      vec = generate_vector(method, sc.theme, sc.word, d.textlist, d.textlen, window)
      x, wordDic = getWordVector(vec, wordDic)
      positive = positive + 1
      y = 1
      line = str(y)
      for i in x:
        line = line + " "  + str(i) + ":" + str(x[i])
      fileutil.writeFile(trainingSetNameSVM, line + "\n")
      line = str(sc.anls)
      for i in x:
        line = line + " "  + str(i) + ":" + str(x[i])
      fileutil.writeFile(trainingSetLabelNameSVM, line + "\n")

  for r in result:
    for i, sci in enumerate(r.sclist):
      for j, scj in enumerate(r.sclist):
        if i == j:
          continue
        # TODO
        th = sci.theme
        sw = scj.word
        if th.begin != -1:
          length = 0
          if th.begin > sw.begin:
            length = th.begin - sw.begin + th.textlen
          else:
            length = sw.begin - th.begin + sw.textlen
          if length <= window:
            negative = negative + 1
            vec = generate_vector(method, th, sw, r.textlist, r.textlen, window)
            x, wordDic = getWordVector(vec, wordDic)
            y = 0
            line = str(y)
            for xi in x:
              line = line + " "  + str(xi) + ":" + str(x[xi])
            fileutil.writeFile(trainingSetNameSVM, line + "\n")
  print("Postive Sample: " + str(positive) + " Negative Sample: " + str(negative))
  print("Generate Trainset of SVM Succeed")
  return wordDic    
    

def main():
  trainfile = 'data/trainset_semi_fixed.csv'
  origindatas = load_data(trainfile)
  
  train_data, valid_data, test_data = apart(origindatas)
  train_data = encapsulate(train_data)
  valid_data = encapsulate(valid_data)
  test_data = encapsulate(test_data)
  
  dirname = 'crf'
  if os.path.exists(dirname):
    fu.rmdir(dirname)
  os.mkdir(dirname)

  word_dic = generate_dic(train_data)

  get_crf_input(train_data, 'train')
  get_crf_input(train_data, 'valid')
  get_crf_input(train_data, 'test')

  get_model_input()


if __name__ == '__main__':
  main()