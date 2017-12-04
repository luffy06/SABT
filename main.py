#-*-coding:utf-8-*-
#!/usr/bin/python3
import fileutil
from data import Word
# CRF

def getCRF(data):
  crfFileName = "./data/crf/crf.out"
  fileutil.deleteFileIfExist(crfFileName)
  for r in data:
    j = 0
    for i in r.text:
      fileutil.writeFile(crfFileName, i + "\t" + r.position[j] + "-" + r.order[j] + "\n")
      j = j + 1
    fileutil.writeFile(crfFileName, "\n")

def getWindow(begin, end, length, window):
  if end - begin + 1 == window:
    return (begin, end, True)
  elif end + 1 >= window:
    return (end - window + 1, end, True)
  elif length >= window:
    return (0, window - 1, True)
  return (0, length - 1, False)

def getWordVector(label, sentence, dic):
  X = {}
  count = len(dic) + 1
  length = len(sentence)
  for i in range(length):
    wordLoc = (sentence[i], i+1)
    if wordLoc not in dic:
      dic[wordLoc] = count
      count = count + 1
    index = dic[wordLoc]
    X[index] = 1  
  return (X, label, dic)

def generateVector(th, sw, textlist, length, window):
  tlen = th.textlen
  slen = sw.textlen
  st = 0
  ed = 0
  res = False
  vec = []
  if th.begin == -1:
    st, ed, res = getWindow(sw.begin, sw.begin + slen - 1, length, window)
  else:
    begin = min(sw.begin, th.begin)
    end = max(sw.begin, th.begin)
    if sw.begin > th.begin:
      end = end + slen - 1
    else:
      end = end + tlen - 1
    st, ed, res = getWindow(begin, end, length, window)
  if res == False:
    for i in range(window - (ed - st + 1)):
      vec.append("DEFAULF")
  for i in range(st, ed + 1):
    vec.append(textlist[i])
  return vec

def parseCRF(line):
  line = line.strip('\n')
  ls = line.split('\t')
  sp = ls[1].split('-')
  return (ls[0], sp[0], sp[1])

def getTS(begin, lines):
  TS = ''
  length = len(lines)
  end = length
  for i in range(begin, length):
    l = parseCRF(lines[i])
    TS = TS + l[0]
    if l[1] == 'E' or l[1] == 'S':
      return (i + 1, TS)
  return (length, TS)

def rowProcess(rowid, lines):
  themelist = []
  swlist = []
  length = len(lines)
  i = 0
  while i < length:
    l = parseCRF(lines[i])
    charact, crfTag = (l[0], l[2])
    if crfTag == 'T':
      i, theme = getTS(i, lines)
      themelist.append((theme, i))
    elif crfTag == 'S':
      i, sw = getTS(i, lines)
      swlist.append((sw, i))
    else:
      i = i + 1
  return (rowid, themelist, swlist)

def crfToRaw():
  filename = './data/crf_test.in'
  rowList = []
  rowid = 1
  begin = 0
  result = fileutil.readFile(filename)
  for i, r in enumerate(result):
    if r == '\n' or i == len(result) - 1:
      rowList.append(rowProcess(rowid, result[begin:i]))
      begin = i + 1
      rowid = rowid + 1  
  return rowList

def preProcess(trainingSetName):
  trainingSetNameSVM = "./data/trainset_semi_svm.in"
  fileutil.deleteFileIfExist(trainingSetNameSVM)

  result = fileutil.readFileFromCSV(trainingSetName)
  getCRF(result)
  print("Generate Trainset of CRF Succeed")

  window = 10
  wordDic = {}
  for r in result:
    for sc in r.sclist:
      vec = generateVector(sc.theme, sc.word, r.textlist, r.textlen, window)
      x, y, wordDic = getWordVector(1, vec, wordDic)
      line = str(y)
      for i in x:
        line = line + " "  + str(i) + ":" + str(x[i])
      fileutil.writeFile(trainingSetNameSVM, line + "\n")

  for r in result:
    for i, sci in enumerate(r.sclist):
      for j, scj in enumerate(r.sclist):
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
            vec = generateVector(th, sw, r.textlist, r.textlen, window)
            x, y, wordDic = getWordVector(0, vec, wordDic)
            line = str(y)
            for xi in x:
              line = line + " "  + str(xi) + ":" + str(x[xi])
            fileutil.writeFile(trainingSetNameSVM, line + "\n")

  print("Generate Trainset of SVM Succeed")
  return wordDic

def main():
  trainingSetName = "./data/trainset_semi_fixed.csv"
  rawTestSetName = "./data/test_semi.csv"
  # wordDic = preProcess(trainingSetName)
  testList = fileutil.readFileFromCSV(rawTestSetName)
  rowList = crfToRaw()
  print(len(rowList))
  assert len(rowList) == len(textlist)
  window = 10
  for r in rowList:
    l = []
    for th in r[1]:
      l.append((th[0], th[1], "TH"))
    for sw in r[2]:
      l.append((sw[0], sw[1], "SW"))
    l.sort(key=lambda x: x[1])
    length = len(l)
    for i, d in enumerate(l):
      if i > 0 and i < length - 1:
        if d[2] == "TH":
          if l[i - 1][2] == "SW":
            vec = generateVector(Word(d[0], d[1]), Word(line[i - 1][0], line[i - 1][1]), testList[r.rowid].textlist, testList[r.rowid].textlen, window)

          if l[i + 1][2] == "SW":
            vec = generateVector(Word(d[0], d[1]), Word(line[i + 1][0], line[i + 1][1]), testList[r.rowid].textlist, testList[r.rowid].textlen, window)
        elif d[2] == "SW":
          pass
        else:
          print("Error Label")
      elif i == 0:
        pass
      else:
        pass


def test():
  trainingSetName = "./data/trainset_semi_fixed.csv"
  rawTestSetName = "./data/test_semi.csv"
  trainsetOutputName = "./data/crf/trainset_fixed.out"
  testOutputName = "./data/crf/testset_onewordline_text.out"
  testFixedOutputName = "./data/crf/test_fixed.out"
  trainset = fileutil.readFileFromCSV(trainingSetName)
  getCRF(trainset)

  fileutil.deleteFileIfExist(trainsetOutputName)
  for r in trainset:
    fileutil.writeFile(trainsetOutputName, r.rowid + "," + r.text + ",")
    for sc in r.sclist:
      fileutil.writeFile(trainsetOutputName, sc.theme.text + ";")
    fileutil.writeFile(trainsetOutputName, ",")
    for sc in r.sclist:
      fileutil.writeFile(trainsetOutputName, sc.word.text + ";")
    fileutil.writeFile(trainsetOutputName, ",")
    for sc in r.sclist:
      fileutil.writeFile(trainsetOutputName, str(sc.anls) + ";")
    fileutil.writeFile(trainsetOutputName, "\n")


  test = fileutil.readFileFromCSV(rawTestSetName)
  fileutil.deleteFileIfExist(testOutputName)
  for r in test:
    for w in r.text:
      fileutil.writeFile(testOutputName, w + "\n")
    fileutil.writeFile(testOutputName, "\n")

  fileutil.deleteFileIfExist(testFixedOutputName)
  for r in test:
    fileutil.writeFile(testFixedOutputName, r.rowid + "," + r.text + "\n")

if __name__ == '__main__':
  test()
  # main()
