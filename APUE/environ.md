## ***environ*** 
1. 获取环境变量

    ```c
    #include<stdio.h>
    extern char** environ; 

    int main(int argv, char* const argc[]) {
        int i;
        for(i =0; environ[i] != NULL; i++){
            printf("environ[%d]=%s\n ",i, environ[i] );

        }
        return 0;
    }
    ``` 