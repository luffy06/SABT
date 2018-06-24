import os
import sys
import csv

from data import Row

def read_file(filename):
  file = open(filename, 'r', encoding='utf8')
  result = list(map(lambda x : x.strip(), file.readlines()))
  file.close()
  return result

def write_file(filename, data):
  f = open(filename, 'a', encoding='utf8')
  f.write(data)
  f.close()

def read_file_from_csv(filename):
  origindata = csv.reader(open(filename, encoding='utf8'))
  result = []
  for od in origindata:
    line = []
    for o in od:
      line.append(o.strip())
    result.append(line)
  return result

def write_csv(filename, data):
  writer = csv.writer(open(filename, 'w', encoding='utf8'))
  for d in data:
    writer.writerow(d)

def rmdir(dirname):
  if os.path.isfile(dirname):
    os.remove(dirname)
    return 
  for f in os.listdir(dirname):
    filename = os.path.join(dirname, f)
    rmdir(filename)
  os.rmdir(dirname)

if __name__ == '__main__':
  writeFile("text", "sss")