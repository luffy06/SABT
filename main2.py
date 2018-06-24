import os
import numpy as np
import random

import fileutil as fu
from data import Row

TRAIN_RATE = 0.8
VALID_RATE = 0.3

def mkdir(dirname):
  if os.path.exists(dirname):
    fu.rmdir(dirname)
  os.mkdir(dirname)

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

def get_window(textlist, position, direction, length, window):
  vec = []
  for i in range(window):
    r_pos = position + direction * i
    if r_pos >= 0 and r_pos < length:
      vec.append(textlist[r_pos])
    else:
      vec.append('DEFAULF')
  return vec

def generate_vector(th, sw, textlist, length, window, dic):
  sw_front_vec = get_window(textlist, sw.begin + sw.textlen - 1, -1, length, window)
  sw_back_vec = get_window(textlist, sw.begin, 1, length, window)
  th_front_vec = get_window(textlist, th.begin + th.textlen - 1, -1, length, window)
  th_back_vec = get_window(textlist, th.begin, 1, length, window)
  vec = []
  front_vec = []
  back_vec = []
  if sw.begin < th.begin:
    front_vec = sw_back_vec
    back_vec = th_front_vec
  else:
    front_vec = th_back_vec
    back_vec = sw_front_vec

  for i in front_vec:
    value = dic[i] if i in dic else 0
    vec.append(str(value))
  for i in back_vec:
    value = dic[i] if i in dic else 0
    vec.append(str(value))
  return vec

def get_model_input(data, types, dic):
  model_in = 'model/model_' + types + '.npy'
  model_label_in = 'model/model_label_' + types + '.npy'
  positive = 0
  negative = 0
  window = 20
  train_data = []
  for d in data:
    for sc in d.sclist:
      positive = positive + 1
      vec = generate_vector(sc.theme, sc.word, d.textlist, d.textlen, window, dic)
      train_data.append([vec, 1])

  if types == 'train':
    for d in data:
      for i, sci in enumerate(d.sclist):
        for j, scj in enumerate(d.sclist):
          if i == j:
            continue

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
              vec = generate_vector(th, sw, d.textlist, d.textlen, window, dic)
              train_data.append([vec, 0])

  random.shuffle(train_data)
  train_data = np.array(train_data)
  np.save(model_in, train_data[:, 0])
  np.save(model_label_in, train_data[:, 1])
  a = np.load(model_in)
  # for td in train_data:
  #   fu.write_file(model_label_in, str(td[1]) + '\n')
  #   vec = td[0]
  #   line = ''
  #   for v in vec:
  #     line = line + v + '\t'
  #   fu.write_file(model_in, line + '\n')
  print('Postive Sample: %d Negative Sample: %d' % (positive, negative))
  print('Generate ' + types + ' DataSet of Model Succeed')    

def evaluate(data, result):
  tp = 0
  fp = 0
  fn1 = 0
  fn2 = 0
  
  return f1  

def main():
  trainfile = 'data/trainset_semi_fixed.csv'
  origindatas = load_data(trainfile)
  
  train_data, valid_data, test_data = apart(origindatas)
  train_data = encapsulate(train_data)
  valid_data = encapsulate(valid_data)
  test_data = encapsulate(test_data)
  
  mkdir('crf')
  word_dic = generate_dic(train_data)

  # get_crf_input(train_data, 'train')
  # get_crf_input(valid_data, 'valid')
  # get_crf_input(test_data, 'test')

  mkdir('model')
  get_model_input(train_data, 'train', word_dic)
  get_model_input(valid_data, 'valid', word_dic)
  get_model_input(test_data, 'test', word_dic)


if __name__ == '__main__':
  main()