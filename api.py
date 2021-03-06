from QcloudApi.qcloudapi import QcloudApi
from aip import AipNlp
import jieba
import thulac
import fileutil
import json

class BaseAPI(object):
  """docstring for BaseAPI"""
  def __init__(self):
    super(BaseAPI, self).__init__()

  def showProcess(self, nowProcess, totalProcess):
    percent = nowProcess * 100.0 / totalProcess
    eachProcess = totalProcess / 10
    if nowProcess % eachProcess == 0:
      print(str(nowProcess) + "/" + str(totalProcess) + " " + str(percent) + "%")

class TencentWenZhi(BaseAPI):
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

  def cutWord(self, text, times, errormessage):
    if times > 5:
      print("error:" + text + " in LexicalAnalysis\nMessage: " + errormessage)
      jb = JieBa()
      return jb.cutWord(text)

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
      return self.cutWord(text, times + 1, res['message'])


  def cutWordByCSVFile(self, filenamein, filenameout):
    rawdata = fileutil.readFileFromCSV(filenamein)
    fileutil.deleteFileIfExist(filenameout)
    result = ""
    totalProcess = len(rawdata)
    process = 0
    for rd in rawdata:
      text = rd.text
      res = self.cutWord(text, 0, "")
      process = process + 1
      self.showProcess(process, totalProcess)
      for r in res:
        result = result + r + " "
      result = result + "\n"
    fileutil.writeFile(filenameout, result)

class JieBa(BaseAPI):
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
    totalProcess = len(rawdata)
    process = 0
    for rd in rawdata:
      text = rd.text
      res = self.cutWord(text)
      process = process + 1
      self.showProcess(process, totalProcess)
      for r in res:
        result = result + r + " "
      result = result + "\n"
    fileutil.writeFile(filenameout, result)

class BaiDuNlp(BaseAPI):
  """docstring for BaiDuNlp"""
  def __init__(self):
    super(BaiDuNlp, self).__init__()
    self.APP_ID = '10323015'
    self.API_KEY = 'zYbYSDZxIFvH4I53ye2jp8qf'
    self.SECRET_KEY = '3os02bOi9hxZC9775MbKVcYo4BP7GTSm'
    self.client = AipNlp(self.APP_ID, self.API_KEY, self.SECRET_KEY)

  def cutWord(self, text, times, errormessage):
    if times > 5:
      print("error:" + text + " in BaiDuNlp\nMessage: " + errormessage)
      jb = JieBa()
      return jb.cutWord(text)

    result = []
    res = self.client.dnnlm(text)
    if 'error_code' not in res:
      for r in res['items']:
        result.append(r['word'])
      return result
    else:
      return self.cutWord(text, times + 1, res['error_msg'])

  def cutWordByCSVFile(self, filenamein, filenameout):
    rawdata = fileutil.readFileFromCSV(filenamein)
    fileutil.deleteFileIfExist(filenameout)
    result = ""
    totalProcess = len(rawdata)
    process = 0
    for rd in rawdata:
      text = rd.text
      res = self.cutWord(text, 0, "")
      process = process + 1
      self.showProcess(process, totalProcess)
      for r in res:
        result = result + r + " "
      result = result + "\n"
    fileutil.writeFile(filenameout, result)

class ThuLac(BaseAPI):
  """docstring for ThuLac"""
  def __init__(self):
    super(ThuLac, self).__init__()
    self.thu = thulac.thulac()
    
  def cutWord(self, text):
    result = self.thu.cut(text)
    return result

  def cutWordByCSVFile(self, filenamein, filenameout):
    rawdata = fileutil.readFileFromCSV(filenamein)
    fileutil.deleteFileIfExist(filenameout)
    result = ""
    totalProcess = len(rawdata)
    process = 0
    for rd in rawdata:
      text = rd.text
      res = self.cutWord(text)
      process = process + 1
      self.showProcess(process, totalProcess)
      for r in res:
        result = result + r[0] + " "
      result = result + "\n"
    fileutil.writeFile(filenameout, result)

    

def test(method, filenamein, filenameout):
  if method == 1:
    jb = JieBa()
    jb.cutWordByCSVFile(filenamein, filenameout)
  elif method == 2:
    twz = TencentWenZhi()
    twz.cutWordByCSVFile(filenamein, filenameout)
  elif method == 3:
    an = BaiDuNlp()
    an.cutWordByCSVFile(filenamein, filenameout)
  elif method == 4:
    th = ThuLac()
    th.cutWordByCSVFile(filenamein, filenameout)

if __name__ == '__main__':
  filenamein = "./data/test_semi_fixed.csv"
  filenameout = "./data/test_cutted.out"
  test(3, filenamein, filenameout)

