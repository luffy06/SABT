#-*-coding:utf-8-*-
import fileutil
import csv
from api import TencentWenZhi, JieBa

twz = TencentWenZhi()
jb = JieBa()

def generateDic(filename):
  result = fileutil.readFileFromCSV(filename)

  themedDicName = "./data/themedic.in"
  sentimentDicName = "./data/sentimentdic.in"

  fileutil.deleteFileIfExist(themedDicName)
  fileutil.deleteFileIfExist(sentimentDicName)

  for r in result:
    sclist= r.sclist
    rowid = r.rowid
    for sc in sclist:
      thtext = sc.theme.text
      swtext = sc.word.text
      anls = sc.anls
      fileutil.writeFile(themedDicName, thtext + "\n")
      fileutil.writeFile(sentimentDicName, swtext + " " + anls + "\n")

  print("Dictionaries generate succeed!")

def getTestData(filename):
  rows = fileutil.readFile(filename)
  rawdata= []
  for r in rows:
    r = r.strip("\n")
    l = r.split(" ")
    rawdata.append(l)
  return rawdata

def getThemeDic():
  filename = "./data/themedic.in"
  rows = fileutil.readFile(filename)
  themes = set([])
  for r in rows:
    r = r.strip("\n")
    themes.add(r)
  return themes

def addExternDic(sentimentDic, filename, anls):
  lines = fileutil.readFile(filename)
  for l in lines:
    l = l.strip("\n")
    if l not in sentimentDic:
      sentimentDic[l] = anls
  return sentimentDic

def getSentimentDic() :
  filename = "./data/sentimentdic.in"
  sentimentDic = {}
  rows = fileutil.readFile(filename)
  for row in rows:
    row = row.strip("\n")
    row = row.split(" ")
    word = row[0]
    sentiment = row[1]
    if word not in sentimentDic:
      sentimentDic[word] = sentiment

  filenameExNe = "./data/ne.in"
  filenameExPo = "./data/po.in"
  # sentimentDic = addExternDic(sentimentDic, filenameExNe, str(-1))
  # sentimentDic = addExternDic(sentimentDic, filenameExPo, str(1))
  return sentimentDic

def getChara(data, themeDic, sentimentDic, preDic):
  result = []
  for d in data:
    if d in preDic:
      result.append("PR")
    elif d in themeDic:
      result.append("TH")
    elif d in sentimentDic:
      result.append("SW")
    else:
      result.append("O")
  return result


def getAnsl(text):
  
  result = twz.getAnsl(text)
  return result

def findAnsl(text, sw, sentimentDic):
  if sw in sentimentDic:
    return sentimentDic[sw]
  else:
    return getAnsl(text)

def preProcess(rawTestSetName):
  testSetName = "./data/test_semi_cutted.out"
  jb.cutWordByCSVFile(rawTestSetName, testSetName)
  # twz.cutWordByCSVFile(rawTestSetName, testSetName)

  rawdata = getTestData(testSetName)
  themeDic = getThemeDic()
  sentimentDic = getSentimentDic()
  return (rawdata, themeDic, sentimentDic)

def process(testSetName):
  punctuation = [',', '，', '.', '。', ':', '：', '!', '！', '?', '？', ';', '；', '、', '…']
  preDic = ['没有', '不是', '别', '不', '不能', '不如', '不想', '没', '不敢', '本来', '不大', '不要',
            '没什么', '无法', '不用', '不然', '非', '不会', '无', '未', '不怎么', '不够', '不算', '减少',
            '从不', '不再', '不让', '不见得', '省了', '不服', '不正', '不可', '没法', '不比']

  rawdata, themeDic, sentimentDic = preProcess(testSetName)

  result = []
  rowid = 0
  for data in rawdata:
    length = len(data)
    found = []
    ThemSwPair = []
    rowid = rowid + 1

    for i in range(length):
      found.append(False)

    chara = getChara(data, themeDic, sentimentDic, preDic)

    for i in range(length-1, -1, -1):
      if chara[i] == 'SW' and found[i] == False:
        found[i] = True
        targetTheme = "NULL"
        targetSentimentWord = data[i]
        text = ""

        # check previous theme
        foundPre = False
        for j in range(i - 1, -1, -1):
          if data[j] in punctuation or chara[j] == "SW":
            break
          elif chara[j] == "TH" and found[j] == False:
            foundPre = True
            found[j] = True
            targetTheme = data[j]
            text = data[j] + text
            break
          text = data[j] + text
        
        if foundPre == False:
          # check back theme
          for j in range(i + 1, length):
            if data[j] in punctuation or chara[j] == "SW":
              break
            elif chara[j] == "TH" and found[j] == False:
              found[j] = True
              targetTheme = data[j]
              text = text + data[j]
              break
            text = text + data[j]

        targetAnsl = findAnsl(text, targetSentimentWord, sentimentDic)

        foundPre = False
        step = 3
        st = i - 1
        ed = max(st - step, -1)
        for j in range(st, ed, -1):
          if data[j] in punctuation or chara[j] == "SW":
            break
          elif chara[j] == "PR" and found[j] == False:
            foundPre = True
            found[j] = True
            targetAnsl = -int(targetAnsl)
            targetSentimentWord = data[j] + targetSentimentWord
            break
        
        if foundPre == False:

          st = i + 1
          ed = min(length, st + step)
          for j in range(st, ed):
            if data[j] in punctuation or chara[j] == "SW":
              break
            elif chara[j] == "PR" and found[j] == False:
              found[j] = True
              targetAnsl = -int(targetAnsl)
              targetSentimentWord = data[j] + targetSentimentWord
              break
        ThemSwPair.append((targetTheme, targetSentimentWord, targetAnsl))
    result.append(ThemSwPair)
  print("Main process run succeed!")
  return result

def showResult(filenamein, thmesw):
  filenameout = "./data/finalresult.csv"

  fileutil.deleteFileIfExist(filenameout)
  origindatas = csv.reader(open(filenamein, encoding='utf-8'))
  writer = csv.writer(open(filenameout, 'w'))
  # writer.writerow(["row_id", "content", "theme", "sentiment_word", "sentiment_anls"])
  for od in origindatas:
    rowdata = []
    rowdata.append(od[0])
    rowdata.append(od[1])
    thlist = ""
    swlist = ""
    alist = ""
    rowthsw = thmesw[int(od[0]) - 1]
    for rts in rowthsw:
      thlist = thlist + rts[0] + ";"
      swlist = swlist + rts[1] + ";"
      alist = alist + str(rts[2]) + ";"
    rowdata.append(thlist)
    rowdata.append(swlist)
    rowdata.append(alist)
    writer.writerow(rowdata)

  print("Result output succeed!")


def main():
  trainingSetName = "./data/trainset_semi_fixed.csv"
  rawTestSetName = "./data/test_semi.csv"
  generateDic(trainingSetName)
  res = process(rawTestSetName)
  showResult(rawTestSetName, res)

if __name__ == '__main__':
  main()
