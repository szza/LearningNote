### *makefile*

```makefile
# obj=main.o ./src/add.c ./src/sub.c ./src/mul.c ./src/div.c
# makefile中提供的函数，都有返回值,使用函数来取代obj的首写输入方式
src = $(wildcard ./*.c, ./src/*.c)  # 表示取出指定目录下所有的.c文件
obj = $(patsubst ./%.c, ./%.o, $(src))
target = main
CC = gcc
CPPFLAGS = -I
$(target):$(obj)
	$(CC) $(obj) -o $(target)

%.o:%.c
	$(CC) -c $< -o $@
# 自动变量
# $<: 表示规则中的第一个依赖，比如main.o 
# $@: 表示规则中的目标，比如main
# $^: 表示规则中的所有依赖，比如main.o ./src/add.c ./src/sub.c ./src/mul.c ./src/div.c,
# 	  只能在规则中的命令中使用
# 系统变量 一般是大写。
# CC=gcc

# .PHONY:clean 表示生成伪目标，以防止和同目录结构下存在clean文件时无法编译
.PHONY:clean
clean:
#-rm 表示如果这条命令执行失败，就忽略
#-f  表示强制执行，以防止在没有*.o和main文件时，make clean失败。
	-rm -f  $(target) $(obj)

```
