### **fork, vfork**

1.  *fork*  
    + 用于创建子进程。
    + 在调用时，返回两次：子进程的返回值是0，父进程的返回值的新建子进程的ID。
    + 子进程是父进程的副本。子进程和父进程继续执行 *fork* 之后的指令。
        + 子进程获得父进程的 **数据空间、堆、栈的副本**
        + 共享的是：**文件描述符、mmap建立的映射区** 
        + 子进程和父进程共享的是 **代码段**，*fork* 之后各自执行。
        + 父进程和子进程的执行顺序谁先谁后是未知的，是竞争的关系。
    + *COW*  
        *COW* 即写时复制(*Copy-On-Write*)， **数据空间、堆、栈的副本**在创建子进程时并不创建副本。而是在父进程或者子进程修改这片区域时，内核为修改区域的那块内存制作一个副本，以提高效率。  
    + *fork*   
        *fork* 失败的原因：  
        + 系统中已经有太多的进程  
        + 该实际用户Id的进程数超过了系统限制
    + 案例  
        ```c
        #include<stdio.h>
        #include<stdlib.h>
        #include<unistd.h>

        int globvar = 10;
        char buf[] = "a writte to stdout.\n";

        int main(int argv, char* argc[]){

            int var;
            pid_t pid;

            var = 88;
            if(write(STDOUT_FILENO, buf, sizeof(buf)-1) != sizeof(buf)-1){
                printf("write error");
                exit(1);
            }
            printf("before fork.\n");
            // 创建子进程后，后面的代码，父进程和子进程独立运行。
            if((pid=fork()) < 0){
                printf("fork() error.\n");
                exit(1);
            }
            else if(pid == 0){
                globvar++; //子进程运行不改变父进程的值
                var++;
            }
            else
                sleep(2);
            printf("pid=%ld, globvar=%d, var=%d.\n",(long)getpid() , globvar, var);
            retdurn 0;
        }
        ```
        
2. *vfork*   
    + 与 *fork* 一样都创建新的进程，他的是目的是执行一个程序。  
    + 与 *fork* 的区别在于：
        + **它并不将父进程的地址空间复制到子进程中** 。在子进程 *exec/exit* 之前，和父进程共享地址空间，提高了工作效率。但是在在子进程 *exec/exit* 之前，子进程如果修改了数据、进行函数调用、返回都会带来未知的结果。  
        + *vfork* 保证子进程比父进程先运行，在子进程 *exec/exit* 之后父进程才会运行。
    + 案例
        ```c
        // 将上面的修改如下：
        if((pid=vfork()) < 0){
            printf("fork() error.\n");
            exit(1);
        }
        else if(pid == 0){
            globvar++; // 会改变父进程的变量值
            var++;
            _exit(0);
        }
        // 去掉sleep(2)是因为vfork能保证子进程先运行
        ```
        
    + 结果对比：

        ```bash 
        # fork 
        szz@ubuntu:~/Study/SystemProgram/IO$ ./f
        a writte to stdout.
        before fork.
        pid=4304, globvar=11, var=89. # 子进程
        pid=4303, globvar=10, var=88. # 父进程

        # vfork
        szz@ubuntu:./vf
        a writte to stdout.
        before fork.
        pid=4301, globvar=11, var=89.# 父进程
        ```
        
+ 补充：  
    *fork* 的两次返回:
    ![fork](https://github.com/szza/LearningNote/blob/master/APUE/Image/fork.jpg)
+ *gdb* 调试  
    *`set follow-fork-mode child`*  : 跟踪子进程  
    *`set follow-fork-mode parent`* : 跟踪父进程
+ 进程和程序的区别   
    程序占用磁盘空间，进程占用系统资源。