# 信号2
#### 1. `pause`
```c
    #include <unistd.h>

    int pause(void);
```
调用`pause`函数的进程将一直堵塞到(即放弃cpu)有信号递达将其唤醒。
+ 返回值：
    + 如果信号的默认动作是终止进程，则进程终止。
    + 如果信号的默认动作是忽略，继承基于处于挂起状态，`pause`不返回。
    + 如果信号处理动作是捕捉，则信号处理函数调用结束，**`pause`返回-1, `errno`设置为`EINTR`**。
    + `pause`接受到的信号被屏蔽，`puase`就将会永远不被唤醒。
+ 实现`sleep`函数功能：`alarm() + pause() `
#### 2.`sigsuspend`
```c
    #include <signal.h>

    int sigsuspend(const sigset_t *mask); // mask是临时的，在函数执行时有效
```
+ 特点。这是一个原子操作，将**设置mask指的屏蔽字** + **使得进程休眠（pause）** 变成原子操作。可用来替代`pause`具有的时许竞争隐患。比如用`alarm() + pause() `实现的`sleep`函数功能。
+ 返回。和`pause`一样，无成功返回值。如果返回调用进程，返回-1，并且`errno=EINTR`。
```c
    alarm(secs);
    pause();
```
+ 原因：  
  
    如果在调用`alarm`之后，调用进程失去了cpu控制权，但是在cpu控制权回到这个进程之前`alarm`的计时时候到达，当cpu控制权回归调用进程时先处理`SIGALRM`信号，再调用`pause`函数，这就导致`pause`再也接受不到信号，因此这个进程就永远堵塞。
+ 解决方案：  
  
    使得`sigsuspend(sus_mask) = alarm() + pause() `成为一个原子操作。
    + 先使用`sigprocmask`设置信号屏蔽集合，使得cpu在`sigsuspend`之前不处理。
    + 比如同样发生上述调用进程失去cpu控制权的情况，cpu控制权返回时，并不会先处理`SIGALRM`信号
    + 因此到`sigsuspend`函数时，在这个函数的`sus_mask`中解除对`SIGALRM`的屏蔽，使得 **信号处理函数的执行后直接返回，唤醒cpu（这是因为pause的堵塞导致）**。

+ 关键点: **调用进程的堵塞原因**
    + 调用进程失去cpu的控制权
    + 调用`pause`导致的cpu挂起

#### 3.全局变量异步I/O
 尽量避免使用全局变量。类似于多线程中的多个线程对同一个变量进行操作，很容易造成异常。

#### 4.不可/可重入函数
 + 定义可重入函数，函数内部不能含有全局变量或者`static`变量，以及`malloc`和`free`。
 + 信号捕捉函数应该设计为可重入函数。
 + 信号处理函数可以调用的可重入函数，参考 man 7 signal
 + 其他大多是不可重入的，因为：
    + 使用静态数据结构
    + 调用`malloc/free`
    + 是标准I/O函数
#### 5.`SIGCHLD`
这是子进程向父进程发送的信号，那么可否利用这个信号来回收子进程？
+ 要求
    + 在父进程中注册对信号`SIGCHLD`的捕捉函数。
    + 循环产生十个子进程
    + 十个子进程在父进程前终止
    + 能顺利回收十个子进程

+ 信号处理函数
```c
    void exe_sigchld(int singo) {
        pid_t pid;
        int statloc;
        // 这里的while很关键
        while(pid = waitpid(0, &statloc, WNOHANG) > 0) {
            if(WIFEXITED(statloc))  
                printf("child process pid=%d, exited  status:%d.\n", pid, WEXITSTATUS(statloc));
            else if(WIFSIGNALED(statloc))
                printf("child process pid=%d, signaled stauts:%d.\n", pid, WTERMSIG(statloc)); 
        }
    }
```
上面都`while`处理很关键，不是`if`而是`while`，是因为：
+ 对于多个子进程同时发送终止信号`SINCHLD`，父进程只调用一次信号处理函数。
+ 如果是`if`那么进入一次信号处理函数，只能处理一个终止的子进程，那么对于同时终止的其他进程就无法处理，剩下的就只能成为僵死进程。
+ 选用`while`就可以一次进入信号处理函数，但是可以处理多个终止的子进程。
#### 6.信号传参
信号不能携带大量参数，实在有特殊需求时也可以。有相关的函数：
+ 发送信号传参
```c
    #include <signal.h>

    int sigqueue(pid_t pid, int sig, const union sigval value);
        
    union sigval {
        int   sival_int;
        void *sival_ptr;
    };
```
类似于`kill`,但是多了一个发送参数，可以作为数据发送。联合体`sigval`在跨进程传递数据时候不要使用指针，因此各个进程之间的虚拟地址不同，指针传参是为同一个进程准备的，跨进程传参使用的是int类型。

+ 捕捉函数传参
```c
    #include <signal.h>

    int sigaction(int signum, const struct sigaction *act, struct sigaction *oldact);

    struct sigaction {
        void     (*sa_handler)(int);        
        void     (*sa_sigaction)(int, siginfo_t *, void *);
        sigset_t   sa_mask;
        int        sa_flags;
        void     (*sa_restorer)(void);
    };
```
使用的结构体`sigaction`的第二项:`sa_sigaction`，此时`sa_flags = SA_SIGINFO`。

#### 7.中断系统调用
系统调用分为二类：慢速系统调用和其他系统调用
+ 慢速系统调用：可能会使进程永远堵塞的一类。如果在堵塞期间收到一个信号，该系统调用就会被中断，那么就不再被执行。也可以设定系统调用是否重启。这类函数诸如:`read、write、pause、wait`。
+ 其他系统调用：`getpid(), getppid(),fork()...`

慢速系统调用**被信号中断**时的行为，和`pause`类似：
+ 想中断`pause`，信号不能屏蔽
+ 信号的处理方式必须是捕捉（默认和忽略都不可）
+ 中断后返回-1，设置`errno`为`EINTR`

可修改`sa_flags`参数来设置被信号中断后系统调用是否重启。 
+ `SA_RESTART`:重启这个慢速调用函数  
    比如：
    + `read`被一个信号中断，处理完信号，`read`应该继续工作，所以需要重启。
    + `pause`被信号中断就不需要重启，因为不影响。
+ `SA_NODEFER`:不屏蔽待捕捉信号