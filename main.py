#-*-coding:utf-8-*-
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

def writeWordVector(label, sentence, dic):
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
    for i in  range(window - (end - begin + 1)):
      vec.append("DEFAULF")
  for i in range(begin, end + 1):
    vec.append(textlist[i])
  return vec


def preProcess(trainingSetName):
  result = fileutil.readFileFromCSV(trainingSetName)
  getCRF(result)

  window = 10
  X = []
  Y = []
  wordDic = {}
  for r in result:
    for sc in r.sclist:
      vec = generateVector(sc.theme, sc.word, r.textlist, r.textlen, window)
      x, y, wordDic = getWordVector(1, vec, wordDic)
      X.append(x)
      Y.append(y)

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
          if length <= 10:
            vec = generateVector(th, sw, r.textlist, r.textlen, window)
            x, y, wordDic = getWordVector(0, vec, wordDic)
            X.append(x)
            Y.append(y)



def main():
  trainingSetName = "./data/trainset_semi_fixed.csv"
  rawTestSetName = "./data/test_semi.csv"
  preProcess(trainingSetName)

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
  test()
  # main()
