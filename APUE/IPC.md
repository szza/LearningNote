# IPC

1. 简介  
进程间通信的三种主要方式有:
    + 管道: 使用最简单
    + 信号：开销最小
    + 共享映射区：无血缘关系
    + 本地套接字：最稳定

### 1. mmp
+ 简介
    + `mmp`函数
    + 借组共享内存放磁盘文件，借组指针访问磁盘文件
    + 父子进程、血缘关系进程 通信
    + 匿名映射区
+ 函数
    ```c
    #include <sys/mman.h>

    void *mmap(void *addr, size_t length, int prot, int flags, int fd, off_t offset);
    ```
    函数返回的是：创建映射区的首地址，失败返回`MAP_FAILED`。
    + 参数
        + `addr`：直接传入 <font color=blue>`NULL`</font>
        + `length`：欲创建映射区的大小
        + `prot`：**映射区权限**：`PORT_READ、PORT_WRITE、PORT_READ|PORT_WRITE`。
        + `flags`：标志参数。是否会将映射区所作的修改反映到物理设备（磁盘）上。
            + `MAP_SHARED`：会   
            + `MAP_PRIVATE`：不会
        + `fd`：用来创建映射区的文件描述符
        + `offset`：映射文件的偏移。(4k的整倍数)
    + 注意事项  
        + 不能创建0字节大小的映射区，因此新创建出来的文件不能用于创建映射区
        + 权限
            + 创建映射区的权限，要小于等于打开文件权限
            + 创建映射区的过程中，隐含着一次对打开文件的读操作。
        + `offset`: 必须是4k的整数倍,`mmu`创建的最小大小就是4k
        + 关闭fd，对`mmap`无影响。
+ 父子进程通信  
    父子进程之间的也可以通过`mmap`建立的映射区来完成数据通信。但是`mmap`函数的`flags`标志位应该设置`flags=MAP_SHARED`。
    + 父子进程共享：
        + 打开的文件描述符
        + `mmap`建立的映射区。
    + 匿名映射  
        由于`mmap`需要在进程之间通信时，需要借组一个文件描述符，但是对应的文件仅仅在通信期间存在，为了省略这一临时文件，产生匿名映射。  
        + Linux独有的方法：宏`MAP_ANONYMOUS/MAP_ANON`。  
        此时不需要使用`open`函数创建文件，只需要如下使用，不需要文件描述符：       
        &emsp;&emsp;*`char* pmem = mmap(NULL, len, PROT_READ|PROT_WRITE, MAP_SHARED|MAP_ANON, -1, 0);`*
        + 通用的方法：  
            ```c
            int fd = open("/dev/zero", O_RDWR);
            char* pmem = mmap(NULL, len, PROT_READ|PROT_WRITE, MAP_SHARED, fd, 0);  
            ```
        使用的是一个文件`/dev/zero`完成。
+ `mmap`实现无血缘关系进程间通信  
实际上`mmp`是内核**借助文件**帮我们创建了一个映射区。多个进程利用该映射区完成书的传递。由于内核是多进程共享，因此无血缘关系的进程间也可以使用`mmap`完成数据通信。