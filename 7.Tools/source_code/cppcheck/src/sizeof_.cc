#include<iostream>
#include<vector>

int main(int argc, char const *argv[]) {

    char buff[12];
    // std::cout<<sizeof(name)<<std::endl;
    int n = snprintf(buff, sizeof(buff), "%5d", 5);
    printf("%d.\n", n);
    return 0;
}
