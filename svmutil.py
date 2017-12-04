import fileutil
from sklearn import svm

class Cell(object):
  """docstring for Cell"""
  def __init__(self, text):
    super(Cell, self).__init__()
    l = text.split(" ")
    self.label = l[0]
    self.dic = []
    self.maxKey = -1
    for i, t in enumerate(l):
      if i > 0:
        s = t.split(":")
        self.dic.append((int(s[0]), int(s[1])))
        self.maxKey = max(self.maxKey, int(s[0]))
    

def readFile(filename):
  data = fileutil.readFile(filename)
  cellList = []
  maxKey = -1
  for d in data:
    c = Cell(d)
    maxKey = max(maxKey, c.maxKey)
    cellList.append(c)
  print("Read File:" + filename + " Succeed")
  return (maxKey, cellList)

def buildXAndY(maxKey, data):
  Y = []
  X = []
  print("maxKey:" + str(maxKey))
  for d in data:
    Y.append(d.label)
    x = list(0 for i in range(maxKey))
    for i in d.dic:
      x[i[0] - 1] = i[1]
    X.append(x)
  print("Build X and Y Succeed")
  return (X, Y)

def trainModel(X, Y):
  clf = svm.SVC()
  clf.fit(X, Y)
  print("Train Model Succeed")
  return clf

def predict(clf, X, Y):
  resultName = "./data/svm/test_semi_pre.out"
  fileutil.deleteFileIfExist(resultName)
  y = clf.predict(X)
  right = 0
  for i, j in enumerate(y):
    fileutil.writeFile(resultName, str(j) + "\n")
    if j == Y[i]:
      right = right + 1

  acc = (right * 1.0) / len(Y)
  print("ACC:" + str(acc))

def main():
  trainSetName = "./data/svm/trainset_semi_svm.in"
  testSetName = "./data/svm/test_semi_svm.in"
  trK, trD = readFile(trainSetName)
  teK, teD = readFile(testSetName)
  trX, trY = buildXAndY(trK, trD)
  teX, teY = buildXAndY(teK, teD)
  mod = trainModel(trX, trY)
  predict(mod, teX, teY)

if __name__ == '__main__':
  main()
