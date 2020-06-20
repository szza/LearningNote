# stream


## outline
+ `GenericStreamWrapper` 
+ `GenericStringStream`：只可读
+ `GenericInsituStringStream`：一个就地可读可写。  
+ `StreamTraits`：特征提取

## 简介
+ `GenericStreamWrapper`：为使用流提供了一个`wraper`。
    ```cpp
    template <typename InputStream, typename Encoding = UTF8<> >
    class GenericStreamWrapper {
    public:
        GenericStreamWrapper(InputStream& is)
        : is_(is)
        { }
        ...
    protected:
        InputStream& is_;   // 只是引用，此类不负责其生命周期，对 is_的改变即对输入流的改变
    };
  ```
    在这个类中，成员变量是`is_`是输入流对象的引用，因此这个类并不会产生复制开销，符合`wrapper`性质。`wrapper`模板类本质上类似于一个借口，为不同的编码方式的输入流提供统一的使用借口。方便将输入流作为其他函数的借口时，更加方便的使用。

+ `GenericStringStream`：当输入流就是 `const Ch* `字符串类型，因为是`const`类型，因此这个特化类是只读属性
    ```cpp
    //只读
    template <typename Encoding>
    struct GenericStringStream {
        typedef typename Encoding::Ch Ch;

        GenericStringStream(const Ch *src) 
        : src_(src), 
        head_(src) 
        { }
        ...

        const Ch* src_;     // sr 指向的类型是 const ch，因此是src_每次指向的值不能改变，即src可以概念，但是 *src可以不改变
        const Ch* head_;    //!< Original head of the string.
    };

    typedef GenericStringStream<UTF8<> > StringStream;
    ```
+ `GenericInsituStringStream` ：就地(inplace/insitu)读写。其输入流是类型是 `CH* src`，因此可以读写。由于输入的类是`Ch*`，因此无法直接接受`const char*`类型的字符串，比如`"Hello World"`，传入的是一个内存数据的指针，
    ```cpp
    //读写
    template <typename Encoding>
    struct GenericInsituStringStream {
       typedef typename Encoding::Ch Ch;

      GenericInsituStringStream(Ch *src) 
      : src_(src), 
        dst_(0), 
        head_(src)  
      { }

        ...

        Ch* src_;  // 用于读取
        Ch* dst_;  // 用于写
        Ch* head_; // 记录字符串的首地址
    };

    typedef GenericInsituStringStream<UTF8<> > InsituStringStream;
    ```
+ `StreamTraits`：　上述两个类其属性都是`char*`类型，因此在复制的时候可以加速优化，比如使用加速指令集，因此使用了一个萃取机制：
    ```cpp
        template<typename Stream>
        struct StreamTraits {
            enum { copyOptimization = 0 };
        };
        // 特化本版
        template <typename Encoding>
        struct StreamTraits<GenericStringStream<Encoding> > {
            enum { copyOptimization = 1 };
        };
        // 注意这里也是 copyOptimization = 1
        template <typename Encoding>
        struct StreamTraits<GenericInsituStringStream<Encoding> > {
        enum { copyOptimization = 1 };
        };
    ```
    这个就是`trait`实现的机制，定义一个模板，再定义一些特化版本，只有这些版本才能识别`copyOptimization = 1`，这两个类在之后的`class Reader`中作为输入流时也是要调用栈的，因此这个参数是`copyOptimization = 1`。
    
    ```cpp
    template<typename Stream, int = StreamTraits<Stream>::copyOptimization>
    class StreamLocalCopy;

    //! Do copy optimization.
    // 特化本版进行优化
    // 能满足这个特化版本的只有上面的　GenericStringStream　和　GenericInsituStringStream　两个类
    template<typename Stream>
    class StreamLocalCopy<Stream, 1> {
    public:
        // 不是直接对流操作，而是对其副本进行操作
        // 操作完毕将改变后的流给原来的流
        StreamLocalCopy(Stream& original) 
        : s(original),  // 这里会调用构造函数，默认的复制构造函数，只是复制了指针
        original_(original)  
        { }
        
        ~StreamLocalCopy() 
        { original_ = s; }  // 将对于副本s的改变同步到original中

        Stream s;  // 用来跳过空白
    private:
        StreamLocalCopy& operator=(const StreamLocalCopy&) /* = delete */;

        Stream& original_;// 原来的流
    };

    //! Keep reference.
    // 相比较上面的复制版本，没有调用构造函数
    template<typename Stream>
    class StreamLocalCopy<Stream, 0> {
    public:
        StreamLocalCopy(Stream& original) 
        : s(original) 
        { }

        Stream& s;

    private:
        StreamLocalCopy& operator=(const StreamLocalCopy&) /* = delete */;
    };

    //　后面的使用
    internal::StreamLocalCopy<InputStream> copy(is);
    ```

    