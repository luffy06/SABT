import os
import numpy as np
import random

import fileutil as fu
from data import Row, Word, SentimentCell

TRAIN_RATE = 0.8
VALID_RATE = 0.3

crf_model_file = 'crfmodel/model_file'
window = 20

def mkdir(dirname):
  if os.path.exists(dirname):
    fu.rmdir(dirname)
  os.mkdir(dirname)

def load_data(filename):
  datas = fu.read_file_from_csv(filename)
  return datas

def apart(datas):
  # random.shuffle(datas)
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
  print('TRAIN:%d\tVALID:%d\tTEST:%d' %(len(train), len(valid), len(test)))
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
  line = ''
  for row in datas:
    for i, t in enumerate(row.text):
      if types == 'train':
        line = line + t + '\t' + row.position[i] + '-' + row.order[i] + '\n'
      else:
        line = line + t + '\n'
    line = line + '\n'
    if len(line) > 100000:
      fu.write_file(crf_in, line)
      line = ''
  if line != '':
      fu.write_file(crf_in, line)    

def train_crf(train_file):
  crf_learn = 'D:/crf++/CRF++-0.58_zip/crf_learn.exe'
  template_file = 'D:/crf++/CRF++-0.58_zip/template_file'
  f = 3.0
  c = 1.5
  cmd = crf_learn + ' -f %f -c %f ' + template_file + ' ' + train_file + ' ' + crf_model_file
  os.system(cmd)

def predict_crf(test_file, result_file):
  print('Predict CRF ' + test_file)
  crf_test = 'D:/crf++/CRF++-0.58_zip/crf_test.exe'
  cmd = crf_test + ' -m ' + crf_model_file + ' ' + test_file + ' > ' + result_file
  os.system(cmd)

def parse_crf_line(line):
  ls = line.split('\t')
  sp = ls[1].split('-')
  return (ls[0], sp[0], sp[1])

def get_ts(begin, lines):
  ts = ''
  length = len(lines)
  end = length
  for i in range(begin, length):
    char, ptag, wtag = parse_crf_line(lines[i])
    ts = ts + char
    if ptag == 'E' or ptag == 'S':
      return (i + 1, ts)
  return (length, ts)

def row_process(lines):
  th_list = []
  sw_list = []
  i = 0
  begin = 0
  while i < len(lines):
    char, ptag, wtag = parse_crf_line(lines[i])
    if wtag == 'T':
      begin = i
      i, th = get_ts(i, lines)
      th_list.append(Word(th, begin))
    elif wtag == 'S':
      begin = i
      i, sw = get_ts(i, lines)
      sw_list.append(Word(sw, begin))     
    else:    
      i = i + 1
  return (th_list, sw_list)

def parse_crf(filename):
  lines = fu.read_file(filename)
  row_list = []
  last_line = 0
  for i, l in enumerate(lines):
    if l == '' or i == len(lines) - 1:
      row_list.append(row_process(lines[last_line:i]))
      last_line = i + 1
  return row_list

def generate_dic(data):
  word_dic = {}
  ct = 0
  for d in data:
    for t in d.text:
      if t not in word_dic:
        ct = ct + 1
        word_dic[t] = ct
        
  print('DIC SIZE: %d' % (ct))
  return word_dic

def get_window(textlist, position, direction, length):
  vec = []
  for i in range(window):
    r_pos = position + direction * i
    if r_pos >= 0 and r_pos < length:
      vec.append(textlist[r_pos])
    else:
      vec.append('DEFAULF')
  return vec

def generate_vector(th, sw, textlist, length, dic):
  sw_front_vec = get_window(textlist, sw.begin + sw.textlen - 1, -1, length)
  sw_back_vec = get_window(textlist, sw.begin, 1, length)
  if th.begin != -1:
    th_front_vec = get_window(textlist, th.begin + th.textlen - 1, -1, length)
    th_back_vec = get_window(textlist, th.begin, 1, length)
  else:
    th_front_vec = []
    th_back_vec = []    
  
  vec = []
  front_vec = []
  back_vec = []
  if th.begin != -1:
    if sw.begin < th.begin:
      front_vec = sw_back_vec
      back_vec = th_front_vec
    else:
      front_vec = th_back_vec
      back_vec = sw_front_vec
  else:
    front_vec = sw_front_vec
    back_vec = sw_back_vec

  for i in front_vec:
    value = dic[i] if i in dic else 0
    vec.append(str(value))
  for i in back_vec:
    value = dic[i] if i in dic else 0
    vec.append(str(value))
  return vec

def get_model_train_input(data, types, dic):
  model_in = 'nn/model_' + types + '.npy'
  model_label_in = 'nn/model_label_' + types + '.npy'
  model_anls_in = 'nn/model_anls_' + types + '.npy'
  model_anls_label_in = 'nn/model_anls_label_' + types + '.npy'
  positive = 0
  negative = 0
  train_data = []
  train_anls = []
  for d in data:
    for sc in d.sclist:
      positive = positive + 1
      vec = generate_vector(sc.theme, sc.word, d.textlist, d.textlen, dic)
      train_data.append([vec, 1])
      train_anls.append([vec, sc.anls + 1])

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
              vec = generate_vector(th, sw, d.textlist, d.textlen, dic)
              train_data.append([vec, 0])

  random.shuffle(train_data)
  train_data = np.array(train_data)
  train_anls = np.array(train_anls)
  np.save(model_in, train_data[:, 0])
  np.save(model_label_in, train_data[:, 1])
  np.save(model_anls_in, train_anls[:, 0])
  np.save(model_anls_label_in, train_anls[:, 1])

  print('Postive Sample: %d Negative Sample: %d' % (positive, negative))
  print('Generate ' + types + ' DataSet of Model Succeed')    

def get_model_test_label_input(datas, word_list, types, dic):
  model_in = 'nn/model_label_' + types + '.npy'
  assert(len(datas) == len(word_list))
  vec_list = []
  vec_word_list = []
  for i, l in enumerate(word_list):
    row = datas[i]
    th_list = l[0]
    sw_list = l[1]
    size = 1

    for j, sw in enumerate(sw_list):
      vec = generate_vector(Word('', -1), sw, row.textlist, row.textlen, dic)
      vec_list.append([vec, i])
      vec_word_list.append((SentimentCell(Word('', -1), sw, -100), i))
      for k, th in enumerate(th_list):
        length = 0
        if th.begin > sw.begin:
          length = th.begin - sw.begin + th.textlen
        else:
          length = sw.begin - th.begin + sw.textlen
        if length <= window:
          vec = generate_vector(th, sw, row.textlist, row.textlen, dic)
          vec_list.append([vec, i])
          vec_word_list.append((SentimentCell(th, sw, -100), i))
          size = size + 1
  vec_list = np.array(vec_list)
  np.save(model_in, vec_list[:, 0])
  return vec_list, vec_word_list

def train_label():
  cmd = 'python3 train_label.py'
  os.system(cmd)

def predict_label():
  cmd = 'python3 predict_label.py'
  os.system(cmd)

# filter datas where label equals 1
def parse_label(datas, word_datas, filename):
  lines = np.load(filename)
  idx = np.where(lines == 1)[0]
  ndatas = datas[idx]
  nwdatas = []
  for i in idx:
    nwdatas.append(word_datas[i])
  model_in = 'nn/model_anls_test.npy'
  np.save(model_in, ndatas[:, 0])
  return ndatas, nwdatas

def train_anls():
  cmd = 'python3 train_anls.py'
  os.system(cmd)

def predict_anls():
  cmd = 'python3 predict_anls.py'
  os.system(cmd)

def parse_anls(datas, word_list, filename):
  lines = np.load(filename)
  print('%d %d' %(len(lines), len(word_list)))
  assert(len(lines) == len(word_list))
  ndatas = datas
  for i, nd in enumerate(ndatas):
    ndatas[i].sclist = []
  for i, wl in enumerate(word_list):
    w = wl[0]
    index = wl[1]
    w.anls = lines[i] - 1
    assert(index >= 0 and index < len(datas))
    ndatas[index].sclist.append(w)
  return ndatas

def main():
  trainfile = 'data/trainset_semi_fixed.csv'
  origindatas = load_data(trainfile)
  
  train_data, valid_data, test_data = apart(origindatas)
  train_data = encapsulate(train_data)
  valid_data = encapsulate(valid_data)
  test_data = encapsulate(test_data)
  word_dic = generate_dic(train_data)

  mkdir('crf')
  get_crf_input(train_data, 'train')
  get_crf_input(valid_data, 'valid')
  get_crf_input(test_data, 'test')

  if os.path.exists(crf_model_file) == False:
    train_crf('crf/crf_train.in')
  predict_crf('crf/crf_test.in', 'crf/crf_test_result.in')

  test_list = parse_crf('crf/crf_test_result.in')

  mkdir('nn')
  get_model_train_input(train_data, 'train', word_dic)
  get_model_train_input(valid_data, 'valid', word_dic)
  vec_list, vec_word_list = get_model_test_label_input(test_data, test_list, 'test', word_dic)
  
  mkdir('model')
  train_label()
  predict_label()
  vec_list, vec_word_list = parse_label(vec_list, vec_word_list, 'nn/label_result.npy')
  print('VEC SIZE: %d %d' % (len(vec_list), len(vec_word_list)))

  train_anls()
  predict_anls()
  pre_test_data = parse_anls(test_data, vec_word_list, 'nn/anls_result.npy')
  # print(pre_test_data)

if __name__ == '__main__':
  main()