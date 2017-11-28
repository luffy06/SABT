# 问题

## 分词效果

现在使用jieba分词。

解决方案：
1. 使用thulac分词。

## 词典问题

**主要问题：训练数据2w，测试数据2w --> 词典数量过低**

解决方案：
1. 加入外部词典：现在效果是加入外部词典后，效果**更差**

## <情感、主题>查找、前缀词查找

现在不限步长查找。

解决方案：
1. 可限定步长。

前缀词词典不完善。

解决方案：
1. 重新处理前缀词词典。