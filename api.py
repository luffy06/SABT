from QcloudApi.qcloudapi import QcloudApi
import jieba
import fileutil
import json

class TencentWenZhi(object):
  """docstring for TencentWenZhi"""
  def __init__(self):
    super(TencentWenZhi, self).__init__()
    self.module = "wenzhi"
    self.config = {
      'Region': 'ap-guangzhou',
      'secretId': 'AKIDDKGOQWmRErJaga9sFRcdVDj4ED1e2Qdg',
      'secretKey': '85xeCev3zmOpEboqhNrAIF4jMo8HIH5i',
      'method': 'POST',
      'SignatureMethod': 'HmacSHA1'
    }
    self.service = QcloudApi(self.module, self.config)

  def getAnsl(self, text):
    action = "TextSentiment"
    params = {
      'content': text,
      'type': 1
    }
    res = self.service.call(action, params)
    res = json.loads(res.decode("utf-8"))
    if res['code'] == 0:
      if res['positive'] > res['negative']:
        return "1"
      elif res['positive'] < res['negative']:
        return "-1"
      else:
        return "0"
    else:
      print("error:" + text + " in TextSentiment\nMessage:" + res['message'])
      return "0"

  def fixWrongWord(text):
    action = "LexicalCheck"
    params = {
      'text': text
    }
    res = self.service.call(action, params)
    res = json.loads(res.decode("utf-8"))
    if res['code'] == 0:
      return res['text']
    else:
      print("error:" + text + " in LexicalCheck\nMessage:" + res['message'])
      return text

  def cutWord(self, text):
    action = "LexicalAnalysis"
    params = {
      'text': text,
      'code': 0x00200000
    }
    res = self.service.call(action, params)
    res = json.loads(res.decode("utf-8"))
    if res['code'] == 0:
      result = []
      for r in res['tokens']:
        result.append(r['word'])
      return result
    else:
      print("error:" + text + "in LexicalAnalysis\nMessage:" + res['message'])
      return []


  def cutWordByCSVFile(self, filenamein, filenameout):
    rawdata = fileutil.readFileFromCSV(filenamein)
    fileutil.deleteFileIfExist(filenameout)
    result = ""
    for rd in rawdata:
      text = rd.text
      res = self.cutWord(text)
      for r in res:
        result = result + r + " "
      result = result + "\n"
    fileutil.writeFile(filenameout, result)

class JieBa(object):
  """docstring for JieBa"""
  def __init__(self):
    super(JieBa, self).__init__()
  
  def cutWord(self, text):
    result = jieba.cut(text)
    return result

  def cutWordByCSVFile(self, filenamein, filenameout):
    rawdata = fileutil.readFileFromCSV(filenamein)
    fileutil.deleteFileIfExist(filenameout)
    result = ""
    for rd in rawdata:
      text = rd.text
      res = self.cutWord(text)
      for r in res:
        result = result + r + " "
      result = result + "\n"
    fileutil.writeFile(filenameout, result)

def test():
  # jb = JieBa()
  # JieBa.cutWordByCSVFile("./data/test_semi.csv", "./data/test_cutted.out")
  twz = TencentWenZhi()
  twz.cutWordByCSVFile("./data/test_semi.csv", "./data/test_cutted.out")

if __name__ == '__main__':
  test()

