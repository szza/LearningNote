### gcc 

1. 编译过程
    +  预处理:头文件展开，宏替换，注释去掉  
        *`gcc -E hello.c -o hello.i`*
    +  编译器:C文件变成汇编文件  
        *`gcc -S hello.i -o hello.s`*
    + 汇编器:把汇编文件变成二进制文件  
        *`gcc -c hello.s -o hello.o`*
    + 链接器:把函数库中的相应代码组合到目标文件中  
        *`gcc hello.o -o hello`*  

    编译过程：![编译过程](./Image/complie.png)

2. gcc 参数

    + *`-I`* + 路径： 提供编译时所需头文件路径
