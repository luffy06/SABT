#-*-coding:utf-8-*-
#!/usr/bin/python3
import fileutil
# CRF

def getCRF(data):
  crfFileName = "./data/crf.out"
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

def getTS(begin, lines):
  TS = ''
  print(lines)
  for i in range(begin, len(lines)):
    lines[i] = lines[i].strip('\n')
    lines[i] = lines[i].split(' ')
    charact = lines[0]
    crfTag = lines[1]
    crfTag =  crfTag.split('-')
    loc = crfTag[0]
    if loc != 'E':
      TS += charact
    else:
      return (i, TS)

def rowProcess(rowid, lines):
  copyLines = lines
  begin = 0
  themelist = []
  swlist = []
  # print(len(lines))
  for i in range(begin, len(lines)):
    lines[i] = lines[i].strip('\n')
    lines[i] = lines[i].split(' ')
    charact,crfTag = (lines[i][0],lines[i][1])
    print(charact + " " + crfTag)
    print(i)
    crfTag =  crfTag.split('-')
    tag = crfTag[1]
    if tag == 'T':
      begin, theme = getTS(i, copyLines)
      themelist.append((theme, i))
    if tag == 'S':
      begin, sw = getTS(i, copyLines)
      swlist.append((sw, i))

  return (rowid, themelist, swlist)


def crfToRaw():
  filename = '/Users/apple/Desktop/test.data'
  rowList = []
  rowid = 1
  begin = 0
  result = fileutil.readFile(filename)
  for i in range(begin, len(result)):
    if result[i] == '\n':
      rowList.append(rowProcess(rowid, result[begin:i]))
      begin = i + 1
      rowid += 1

  for row in rowList:
    print(row)

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
  wordDic = preProcess(trainingSetName)
  

def test():
  trainingSetName = "./data/trainset_semi_fixed.csv"
  rawTestSetName = "./data/test_semi.csv"
  outputName = "./testset_onewordline_text.out"
  result = fileutil.readFileFromCSV(rawTestSetName)
  fileutil.deleteFileIfExist(outputName)
  for r in result:
    for w in r.text:
      fileutil.writeFile(outputName, w + "\n")
    fileutil.writeFile(outputName, "\n")

if __name__ == '__main__':
  # test()
  crfToRaw()
  main()
