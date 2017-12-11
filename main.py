#-*-coding:utf-8-*-
#!/usr/bin/python3
import fileutil
from data import Word, SentimentPair
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

def sortDic(dic):
  dic = dict(sorted(dic.items(), key=lambda d: d[0]))
  return dic

def getWordVector(sentence, dic):
  X = {}
  count = len(dic) + 1
  for i in sentence:
    if i not in dic:
      dic[i] = count
      count = count + 1
    index = dic[i]
    X[index] = 1
  X = sortDic(X)
  return (X, dic)

def getTestVector(sentence, dic):
  X = {}
  for i in sentence:
    if i not in dic:
      dic[i] = 0
    index = dic[i]
    X[index] = 1
  X = sortDic(X)
  return (X, dic)

def generateVector(method, th, sw, textlist, length, window):
  if method == 1:
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
    j = 1
    if res == False:
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
    middleP = min(sw.begin + sw.textlen, th.begin + th.textlen)
    middleE = max(sw.begin, th.begin)
    end = max(sw.begin + sw.textlen, th.begin + th.textlen)
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
      begin = i
      i, theme = getTS(i, lines)
      themelist.append((theme, begin))
    elif crfTag == 'S':
      begin = i
      i, sw = getTS(i, lines)
      swlist.append((sw, begin))
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

def preProcess(trainingSetName, method, window):
  trainingSetNameSVM = "./data/svm/trainset_semi_svm.in"
  trainingSetLabelNameSVM = "./data/svm/trainset_semi_label_svm.in"
  fileutil.deleteFileIfExist(trainingSetNameSVM)
  fileutil.deleteFileIfExist(trainingSetLabelNameSVM)

  result = fileutil.readFileFromCSV(trainingSetName)
  getCRF(result)
  print("Generate Trainset of CRF Succeed")

  positive = 0
  negative = 0
  wordDic = {}
  for r in result:
    for sc in r.sclist:
      vec = generateVector(method, sc.theme, sc.word, r.textlist, r.textlen, window)
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
            vec = generateVector(method, th, sw, r.textlist, r.textlen, window)
            x, wordDic = getWordVector(vec, wordDic)
            y = 0
            line = str(y)
            for xi in x:
              line = line + " "  + str(xi) + ":" + str(x[xi])
            fileutil.writeFile(trainingSetNameSVM, line + "\n")
  print("Postive Sample: " + str(positive) + " Negative Sample: " + str(negative))
  print("Generate Trainset of SVM Succeed")
  return wordDic

def getCRFInput():
  trainingSetName = "./data/trainset_semi_fixed.csv"
  rawTestSetName = "./data/test_semi.csv"
  trainsetOutputName = "./data/crf/trainset_fixed.out"
  testOutputName = "./data/crf/testset_onewordline_text.out"
  testFixedOutputName = "./data/crf/test_fixed.out"
  trainset = fileutil.readFileFromCSV(trainingSetName)
  getCRF(trainset)

  fileutil.deleteFileIfExist(trainsetOutputName)
  for r in trainset:
    fileutil.writeFile(trainsetOutputName, r.text + "\n")


  test = fileutil.readFileFromCSV(rawTestSetName)
  fileutil.deleteFileIfExist(testOutputName)
  for r in test:
    for w in r.text:
      fileutil.writeFile(testOutputName, w + "\n")
    fileutil.writeFile(testOutputName, "\n")

  fileutil.deleteFileIfExist(testFixedOutputName)
  for r in test:
    fileutil.writeFile(testFixedOutputName, r.text + "\n")

def checkPair(begin, end, textlist):
  punc = [',', '，', '.', '。', ':', '：', '!', '！', '?', '？', ';', '；', '、', '…']
  for i in range(begin, end + 1):
    if textlist[i] in punc:
      return False
  return True

def getSVMPairsInput(window):
  trainingSetName = "./data/trainset_semi_fixed.csv"
  rawTestSetName = "./data/test_semi.csv"
  testSetNameSVM = "./data/svm/test_semi_svm.in"
  method = 2
  wordDic = preProcess(trainingSetName, method, window)
  maxDim = -1
  for i in wordDic:
    maxDim = max(maxDim, wordDic[i])
  print("MAX Dimensionality: " + str(maxDim))
  testList = fileutil.readFileFromCSV(rawTestSetName)
  rowList = crfToRaw()
  fileutil.deleteFileIfExist(testSetNameSVM)
  assert len(rowList) == len(testList)
  sp = []
  for r in rowList:
    tmp = []
    for th in r[1]:
      tmp.append((th[0], th[1], "TH"))
    for sw in r[2]:
      tmp.append((sw[0], sw[1], "SW"))
    tmp.sort(key=lambda x: x[1])
    l = []
    t = 1
    s = 1
    for i in tmp:
      if i[2] == 'TH':
        l.append((i[0], i[1], i[2], t))
        t = t + 1
      else:
        l.append((i[0], i[1], i[2], s))
        s = s + 1        
    
    length = len(l)
    rowid = r[0] - 1
    for i, d in enumerate(l):
      vecList = []
      if d[2] == "SW":
        if i - 1 >= 0 and l[i - 1][2] == "TH" and checkPair(l[i - 1][1], d[1], testList[rowid].textlist) == True:
          v = generateVector(method, Word(l[i - 1][0], l[i - 1][1]), Word(d[0], d[1]), testList[rowid].textlist, testList[rowid].textlen, window)
          x, wordDic = getTestVector(v, wordDic)
          s = SentimentPair(r[0], l[i - 1][0], d[0], x, d[3], l[i - 1][3])
          sp.append(s)
          line = str(1)
          for j in x:
            line = line + " " + str(j) + ":" + str(x[j])
          fileutil.writeFile(testSetNameSVM, line + "\n")
        if i + 1 < length and l[i + 1][2] == "TH" and checkPair(d[1], l[i + 1][1], testList[rowid].textlist) == True:
          v = generateVector(method, Word(l[i + 1][0], l[i + 1][1]), Word(d[0], d[1]), testList[rowid].textlist, testList[rowid].textlen, window)
          x, wordDic = getTestVector(v, wordDic)
          s = SentimentPair(r[0], l[i + 1][0], d[0], x, d[3], l[i + 1][3])
          sp.append(s)
          line = str(1)
          for j in x:
            line = line + " " + str(j) + ":" + str(x[j])
          fileutil.writeFile(testSetNameSVM, line + "\n")
        v = generateVector(method, Word('NULL', -1), Word(d[0], d[1]), testList[rowid].textlist, testList[rowid].textlen, window)
        x, wordDic = getTestVector(v, wordDic)
        s = SentimentPair(r[0], 'NULL', d[0], x, d[3], -1)
        sp.append(s)
        line = str(1)
        for j in x:
          line = line + " " + str(j) + ":" + str(x[j])
        fileutil.writeFile(testSetNameSVM, line + "\n")
  print("Generate Testset of SVM Succeed")
  return sp

def getSVMLabelInput(sp):
  testPairsResult = "./data/svm/test_semi_pairresult.in"
  testSetLabelNameSVM = "./data/svm/test_semi_label_svm.in"
  if fileutil.checkFileIfExist(testPairsResult) == False:
    return []
  lines = fileutil.readFile(testPairsResult)
  fileutil.deleteFileIfExist(testSetLabelNameSVM)
  assert len(lines) == len(sp)
  nsp = []
  visSw = {}
  visTh = {}
  ct = 0
  nonct = 0
  nullct = 0
  lps = (-1, -1)
  ind = -1
  for i, l in enumerate(lines):
    l = l.strip('\n')
    sp[i].set_label(int(l))
    ps = (sp[i].rowid, sp[i].swnum)
    pt = (sp[i].rowid, sp[i].thnum)
    if int(l) == 1 and ps not in visSw:
      if pt not in visTh:
        # print("Using" + " " + str(sp[i].rowid) + " " + str(sp[i].thnum) + " " + str(sp[i].theme) + " " + str(sp[i].word))
        if pt[1] != -1:
          visTh[pt] = True
        visSw[ps] = True
        nonct = nonct + 1
        nsp.append(sp[i])
        line = l
        for j in sp[i].vector:
          line = line + " " + str(j) + ":" + str(sp[i].vector[j])
        fileutil.writeFile(testSetLabelNameSVM, line + "\n")
      else:
        ct = ct + 1
        # print("Exist" + " " + str(sp[i].rowid) + " " + str(sp[i].thnum) + " " + str(sp[i].theme) + " " + str(sp[i].word))
    # add NULL Theme
    if ps != lps:
      if lps[0] > 0 and lps not in visSw:
        ind = -1
        for k in range(i):
          if sp[i - k].rowid == lps[0] and sp[i - k].swnum == lps[1] and sp[i - k].thnum == -1:
            ind = i - k
            break
        if ind == -1:
          print("Not Found " + str(lps[0]) + " " + str(lps[1]))
        else:
          nullct = nullct + 1
          nsp.append(sp[ind])
          line = l
          for j in sp[ind].vector:
            line = line + " " + str(j) + ":" + str(sp[ind].vector[j])
          fileutil.writeFile(testSetLabelNameSVM, line + "\n")
      lps = ps
  print("Repeat Theme " + str(ct))
  print("Pair Theme is Not NULL: " + str(nonct) + " NULL:" + str(nullct))
  print("Generate Testset of Label Succeed")
  return nsp

def getFinalResult(sp, dic):
  rawTestSetName = "./data/test_semi.csv"
  finalResult = "./data/finalresult.csv"
  result = fileutil.readFileFromCSV(rawTestSetName)
  if dic == False:
    testAnlsResult = "./data/svm/test_semi_anlsresult.in"
    if fileutil.checkFileIfExist(testAnlsResult) == False:
      sp = []
    lines = fileutil.readFile(testAnlsResult)
    fileutil.deleteFileIfExist(finalResult)
    assert len(lines) == len(sp)
    for i, l in enumerate(lines):
      l = l.strip('\n')
      sp[i].set_anls(int(l))
  else:
    filename = "./data/sentimentdic.out"
    lines = fileutil.readFile(filename)
    swdic = {}
    error = 0
    notfound = 0
    for l in lines:
      s = l.strip('\n').split(' ')
      if s[0] not in swdic:
        swdic[s[0]] = s[1]
      elif swdic[s[0]] != s[1]:
        error = error + 1
    print("Error Dic:" + str(error))
    for i, s in enumerate(sp):
      anls = 0
      if s.word in swdic:
        anls = swdic[s.word]
      else:
        notfound = notfound + 1
      sp[i].set_anls(anls)
    
    rate = notfound
    if len(sp) > 0:
      rate = rate * 1.0 / len(sp)
    else:
      rate = 0
    print("Not Found in Dic:" + str(notfound) + " Rate: %.6f" % rate)
  sp.sort(key=lambda x: x.rowid)

  data = []
  j = 0
  splen = len(sp)
  for i, r in enumerate(result):
    d = [r.rowid, r.text]
    if j < splen:
      th = ''
      sw = ''
      an = ''
      while j < splen and int(sp[j].rowid) == int(r.rowid):
        th = th + str(sp[j].theme) + ';'
        sw = sw + str(sp[j].word) + ';'
        an = an + str(sp[j].anls) + ';'
        j = j + 1
      d.append(th)
      d.append(sw)
      d.append(an)
    data.append(d)
  fileutil.writeCSV(finalResult, data)

if __name__ == '__main__':
  window = 20
  getCRFInput()
  sp = getSVMPairsInput(window)
  sp = getSVMLabelInput(sp)
  getFinalResult(sp, True)