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

## 文件说明

#### grammar.py/class Grammar

表示文法的类，使用init_grammar函数的返回值进行初始化，在初始化时对文法的FIRST和FOLLOW集进行分析。

#### project.py/class Project

表示'项目'的类。含有文法的一条产生式，以及表示圆点位置的整形变量。

#### project.py/class ProjectSet

表示项目集的类。含有Project示例的集合。

#### SLRMap.py/class SLRMap

表示SLR(1)分析表的类。在初始化时计算分析表。

#### SLRAn.py/class SLRAn

表示SLR(1)分析器的类。调用analysis函数进行输入串分析。