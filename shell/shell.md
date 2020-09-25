# 学习笔记
## 1 shell特殊字符
```
双引号 用来使Shell无法认出除自负$ ` \ 之外的任何字符或字符串  所见非所得，存在获取变量    
单引号 拥来时Shell无法认出所有特殊字符，强引用   所见即所得  
反引号 用来替换命令 
```

## 2 变量
```text
变量名="变量"
readonly 变量名="变量"  # 只读
set 显示所有变量
unset 变量名   清除变量
readonly 显示当前哪些变量只读 

引用变量包括两种形式："$variable" 与 "${variable}"
```
## 3 数组
```shell script
#!/bin/bash
array_name=(a b c d)
for i in ${array_name[*]} # ${array_name[*]}或${array_name[@]}
do
	  echo $i
done
echo ${#array_name[*]}
```
## 4 控制
### 4.1 if...else...
```shell script
#!/bin/bash
if 条件
then
命令1
else
命令2
fi
```
### 4.2 case判断
```shell script
#!/bin/bash
case 值 in
模式1)
命令1 ;;
模式2)
命令2 ;;
*)
默认命令;;
esac
```
```shell script
#!/bin/bash
echo -n "enter a number form 1 to 3:"
read ANS
case $ANS in
1)
echo "your select 1";;
2)
echo "your select 2";;
3)
echo "your select 3";;
*)
echo "your select 1";;
esac
```
## 5 sed
```shell script
语法
sed [-nefr] [n1,n2] 动作
-n 安静模式
-e 表示直接在命令行模式上进行sed的操作 默认选项
-f 文件
-i 读取文件内容
n1,n2 在行之间处理 10,20 表示10-20行之间处理 
动作支持参数：
a 表示添加，后接字符串，添加到当前行的下一行
p 表示打印输出
c 表示替换
d 表示删除符合模式的行 sed '/regexp/d' regexp正则表达式
i 表示插入，当前行上一行
s 表示搜索 1,20s/old/new/g 替换1-20行的old为new  g表示处理这一行所有匹配的内容
```
```shell script
cat a.sh |sed -n '5,7p'  #打印5-7行  -n p 配合使用
cat a.sh |sed '2,5c I am a good man' # 替换2-5行内容为I am a good man
cat a.sh |sed '2,5s/echo/echo1/g' # 替换2-5行的echo为echo1
cat a.sh |sed 's/echo/echo1/g' # 替换全部echo为echo1
 
ifconfig enp1s0 |grep 'inet ' |awk -F" "  '{print $2}' # -F" " 按照空格切割字符串
```

## 5 awk
awk逐行读入文件,以空格为默认分隔符进行切片
```shell script
格式
awk 'pattern {action}' filename  
pattern 正则表达式，要找的内容
action 执行的命令

awk [-F re] [parameter...] [''prog] [-f progfile] [in_file...]
```