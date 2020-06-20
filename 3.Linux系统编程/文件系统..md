# 文件系统

## 获取文件状态函数
```c
    #include <sys/types.h>
    #include <sys/stat.h>
    #include <unistd.h>

    int stat(const char *pathname, struct stat *statbuf);
    int fstat(int fd, struct stat *statbuf);
    int lstat(const char *pathname, struct stat *statbuf);

    #include <fcntl.h>           /* Definition of AT_* constants */
    #include <sys/stat.h>

    int fstatat(int dirfd, const char *pathname, struct stat *statbuf,
                int flags);

```
这些函数对于文件不需要读写权限，只需要最基本的可执行权限：`---x--x--x`。
### 区别
+ `lstat`：和`stat`不同之处在于如果`pathname`指向的一个符号连接，那么`lstat`返回的就是符号连接本身，而不是其引用的文件。
+ `fstat`：和`stat`不同之处在于获取文件描述符`fd`的状态信息。
