# SLR(1)文法分析器

基于Python3的SLR(1)文法分析器。目前的功能：

- 分析文法各非终结符号的FOLLOW(A)集合
- 分析文法所有的有效项目集族
- 计算文法的SLR(1)分析矩阵
- 判断输入串是否为文法的合法语句

## 依赖库

- Pandas

## 使用方法

    python main.py

进阶的使用方法：修改`grammar.txt`文件中的文法规则以自定义文法。