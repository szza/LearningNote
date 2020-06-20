### ***exit、wait、waitpid、exec***

1. *exit*  
    8种方式使进程终止，其中五种是正常终止:
    + 正常终止:  
        + 从 *main* 返回：return 0 == exit(0)
        + 调用 *exit*   
            在退出时，会调用一系列的终止处理程序(可以调用函数 *atexit* 进行注册)，关闭所有标准 *I/O*流等。
        + 调用 *_exit/_Exit*   
            Linux的 *_exit/_Exit* 与 *exit* 不同，前者是直接退出，不 *flush* 缓冲区，而后者会。*exit* 内部调用 *_exit*，且 *flush* 缓冲区。  
        + 最后一个线程从启动例程返回
        + 从最后一个线程调用 *pthread_exit*
    + 异常终止：
        + 调用 *abort* ：产生 *SIGABRT* 信号。
        + 接到一个信号
        + 最后一个线程对取消请求做出响应
    
    无论如何进程如何终止，最后都会执行内核中的同一段代码，关闭所有的描述符，释放所用的存储器。

2. 终止状态   
    当一个进行终止，内核向其父进程发生 ***SIGCHLD*** 信号。进程终止，其父进程通过调用 *wiat、waitpid* 来获取**正常终止**进程的的退出状态。  
    + 孤儿进程  
    父进程通过 *fork* 产生子进程，但是父进程在子进程之前终止，那么该子进程的父进程都会变成 ***init*** 进程，*init* 进程ID是1。这些父进程先终止的子进程被叫做 **孤儿进程**。
    + 僵死进程  
    如果子进程在父进程之前终止，父进程只能通过 *wiat、waitpid* 来获取终止的子进程的状态信息。这样一个已经终止、但是其父进程尚未对其进程善后处理的（获取子进程的相关信息、释放它占用的资源）进程叫做 **僵死进程**。 如果父进程没有 *wiat、waitpid* 来获取终止的子进程的状态状态，这些进程终止后都会变成 **僵死进程**。
    
    ` init进程的子进程不存在僵死进程：只要有一个进程终止，就会调用一个wait函数取得其终止状态。`
 
    + 查看僵死进程： `ps -e -o stat,ppid,pid,cmd|egrep '^[Zz]'`
    + 杀死僵死进程： `kill -9 ID`  
    [参考地址](https://blog.csdn.net/qq_37837134/article/details/82683107)
    ```bash
     s：ps命令用于获取当前系统的进程信息.
    
    -e：参数用于列出所有的进程
    
    -o：参数用于设定输出格式。这里只输出进程的stat(状态信息)、ppid(父进程pid)、pid(当前进程的pid)，cmd(即进程的可执行文件)。

    egrep：是linux下的正则表达式工具

    '^[Zz]'：这是正则表达式，^表示第一个字符的位置，[Zz]，表示z或者大写的Z字母，即表示第一个字符为Z或者z开头的进程数据，只所以这样是因为僵尸进程的状态信息以Z或者z字母开头。
    ```

3. ***wiat、waitpid***  
    ```c
    #include<sys/wait.h>
    pid_t wait(int* statloc);  
    pid_t waitpid(pid_t pid, int* statloc, int options); // 
    /*
    // 返回时返回值是终止进程的id，子进程终止状态存储在statloc
    // 如果不关心终止状态，就令statloc为null，statloc详见P191
    */
    ```
    + 异同点
        + *wiat* 是阻塞的，*waitpid* 有个选项可以不阻塞。
        + *wiat* 等待其调用后的第一个子线程终止， *waitpid* 可以控制它等待的子线程。
        + *wait* 出错是：调用该函数的进程没有子线程，*waitpid* 出错还可能是指定的进程或者进程组不存在。
        + 都可以回收子进程资源
        + 都获取子进程退出状态（退出原因）。

4. *exec*  
    ```c
    #include <unistd.h>
    extern char **environ;

    int execl  (const char *path, const char *arg, ... /* (char  *) NULL */);
    int execv  (const char *path, char *const argv[]);
    int execve (const char *path, char *const argv[], char const* envp[]);
    int execle (const char *path, const char *arg, ... /*, (char *) NULL, char * const envp[] */);
    int execlp (const char *file, const char *arg, ... /* (char  *) NULL */);
    int execvp (const char *file, char *const argv[]);
    int execvpe(const char *file, char *const argv[], char *const envp[]);
    ```
    只有失败时候才返回-1，成功时直接执行被执行的函数，不会返回，即 *exec* 同一作用域的后面的部分不会运行：
    ```c
        exec(...);
        perroe("exec call error.\n");
        exit(1);
    ```
    
    
