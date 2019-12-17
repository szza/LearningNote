#include<string>
#include<iostream>
class Foo {
private:
    std::string& str_;
public:
    Foo(std::string& str)
    :str_(str) { 
        std::cout<<"Foo str: "<<&str<<std::endl;
    } 

};
int main(int argc, char const *argv[]) {

    std::string str("szz");
    std::cout<<"main str: "<<&str<<std::endl;
    Foo foo(str);
    return 0;
}