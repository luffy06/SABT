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

def get_model_input(data, types):
  

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

  get_crf_input(train_data, 'train')
  get_crf_input(train_data, 'valid')
  get_crf_input(train_data, 'test')




if __name__ == '__main__':
  main()