### I/O操作

1. *`errno`*  
    *`errno`* 是一个全局的错误变量。  

2. *`open`*  
    open函数有两种设计：
    ```c
    int open(const char* filename, int flags); // 打开已经存在的文件
    int open(const char* filename, int flags, mode_t mode); //可以用于创建文件
    /**
      flags: O_RDWR   // 读写
             O_RDONLY // 只读
             O_WRONLY // 只写
             配合
             "|O_CREAT"  // 文件不存在时创建
             "|O_TRUNC"  // 将打开的文件原来的内容清空
      mode: 文件的权限。文件的权限此处需要将实际文件权限(比如777)和本地掩码(umask得到0022)取反后进行按位与。
    */
    ```
3. *`read`*  
    *`read`* 设计
    ```c
    #include<unistd.h>
    sszie_t read(int fd, void* buff,  size_t count);
    /*
    size_t  表示无符号
    sszit_t 表示有符号
    返回值：
        -1: 读取失败
        0 : 读取完成
        >0: 读取的字节数
    */
    ``` 
4. *`write`* 和 *`read`* 类似。
5. 系统的I/O函数和C库函数的区别
    + 标准的C库函数，内部有一个系统维护的缓冲区。
    + 上面都的 *`write`* 和 *`read`*的缓冲区是由用户自己进行维护。

6. *`lseek`*   
    + 获取文件大小
    + 移动文件指针
    + 文件拓展

7. *`stat`* 
    + 命令：*`stat`*：*`stat + 文件名`*
    + 函数：  