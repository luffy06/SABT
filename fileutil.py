#-*-coding:utf-8-*-
import os
import sys
import xdrlib
import xlrd
import csv

from data import Row

def readFile(filename):
  file = open(filename, "r")
  result = file.readlines()
  file.close()
  return result

def readFileFromExcel(filename):
  data = xlrd.open_workbook(filename)
  table = data.sheets()[0]
  rows = table.nrows
  result = []
  for i in range(rows):
    if i == 0:
      continue
    rowid = table.cell(i, 0).value
    text = str(table.cell(i, 1).value).lower()
    theme = table.cell(i, 2).value.lower().replace(" ", "")
    word = table.cell(i, 3).value.lower().replace(" ", "")
    anls = table.cell(i, 4).value
    if theme != "" and word != "":
      row = Row(rowid, text, theme, word, anls)
      result.append(row)
  return result

def readFileFromCSV(filename):
  origindata = csv.reader(open(filename, encoding='utf-8'))
  result = []
  for od in origindata:
    l = len(od)
    rowid = od[0]
    text = od[1].lower()
    theme = ""
    word = ""
    anls = ""
    if l > 2:
      theme = od[2].lower().replace(" ", "")
      word = od[3].lower().replace(" ", "")
      anls = od[4]
    if text != "" and rowid != "":
      row = Row(rowid, text, theme, word, anls)
      result.append(row)
  return result

def writeFile(filename, data):
  f = open(filename, "a")
  f.write(data)
  f.close()

def writeCSV(filename, data):
  writer = csv.writer(open(filename, "a", encoding='utf-8'))
  for d in data:
    writer.wirterow(d)

def checkFileIfExist(filename):
  return os.path.exists(filename)
  
def deleteFileIfExist(filename):
  if checkFileIfExist(filename):
    os.remove(filename)

if __name__ == '__main__':
  writeFile("text", "sss")