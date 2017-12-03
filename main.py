#-*-coding:utf-8-*-
import fileutil

# CRF

def getCRF(trainingSetName):
  crfFileName = "./data/crf.out"
  result = fileutil.readFileFromCSV(trainingSetName)
  fileutil.deleteFileIfExist(crfFileName)
  for r in result:
    j = 0
    for i in r.text:
      fileutil.writeFile(crfFileName, i + "\t" + r.position[j] + "-" + r.order[j] + "\n")
      j = j + 1
    fileutil.writeFile(crfFileName, "\n")


def crf():
  trainingSetName = "./data/trainset_semi_fixed.csv"
  rawTestSetName = "./data/test_semi.csv"
  getCRF(trainingSetName)

if __name__ == '__main__':
  crf()
