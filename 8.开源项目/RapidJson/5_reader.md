# reader 

Json解析器，是SAX风格的解析器，解析方式分为:递归方式和迭代方式(iterative)。每种解析方式又可以分为`non-destructive`和`destructive`，即采用副本和就地解析。

## `StreamLocalCopy`
```cpp
template<typename Stream>
class StreamLocalCopy<Stream, 1> {
public:
    StreamLocalCopy(Stream& original) 
    : s(original),  // 这里会调用构造函数
      original_(original)  
    { }
    
    ~StreamLocalCopy() 
    { original_ = s; }  // 将对于副本s的改变同步到original中

    Stream s;  
private:
    StreamLocalCopy& operator=(const StreamLocalCopy&) /* = delete */;

    Stream& original_;// 原来的流
};

```
在这个类的特化版本`StreamLocalCopy<Stream, 1>`中，会调用一次构造函数对输入流进行一次构造，产生一个副本，然后后面对这个副本进行修改，就是`no-destructive`，如果是`StreamLocalCopy<Stream, 0>`，就是直接对输入流本身进行修改。
```cpp
template<typename Stream, int = StreamTraits<Stream>::copyOptimization>
class StreamLocalCopy;
```
而这个取决于是否这个输入流的`copyOptimization`，根据前面分析可知，这个参数为１的类只有`template <typename Encoding> struct GenericInsituStringStream;` 和 `template <typename Encoding> struct GenericStringStream;`，其余的输入流都是0。

## `GenericReader`
+ ` non-destructive parsing`：需要分为一个栈内存，来存放从输入流中decoded的内容
+ `in-situ parsing`：直接将decoded的结果写入到原文本字符串，没有中间buffer。

```cpp
    template <typename SourceEncoding, typename TargetEncoding, typename StackAllocator = CrtAllocator>
    class GenericReader {
    public:
        typedef typename SourceEncoding::Ch Ch; //!< SourceEncoding character type
        // ...
        template <unsigned parseFlags, typename InputStream, typename Handler>
        ParseResult Parse(InputStream& is, Handler& handler) { /**/  }
        // ...
    private:
        static const size_t kDefaultStackCapacity = 256;   
        internal::Stack<StackAllocator> stack_;  //!< A stack for storing decoded string temporarily during non-destructive parsing.
        ParseResult parseResult_;
        IterativeParsingState state_;
    }
```
在`parse`函数中，接受一个待解析的输入流`is`，对其解析，解析结果？？？

### `void ParseNumber(InputStream& is, Handler& handler)`
解析数字是整个解析类型中最复杂的。
#### `class NumberStream;`
`ParseNumber`中用到了这个类，来实现是否`insuit parsing`:
```cpp
    template<typename InputStream, bool backup, bool pushOnTake> 
    class NumberStream　{ 
        NumberStream(GenericReader& reader, InputStream& s) 
        : is(s) 
        {  (void)reader;  }
    // ...
    protected:
        InputStream& is;
  };
```
+ `backup`：即是否备份，即是否'insitu parsing`
+ `pushOnTake`：`take()`的时候是否也将这个值`push`到stack中
只有第一个参数为`true`的时候才有第二个参数为`true`，因为只有第一个参数`true`了，才会使用栈。在`ParseNumber`中使用如下：
```cpp
    internal::StreamLocalCopy<InputStream> copy(is);
     
    NumberStream<InputStream,
        ((parseFlags & kParseNumbersAsStringsFlag) != 0) ?
            ((parseFlags & kParseInsituFlag) == 0) :            // true，即不使用栈将数字解析为字符串，false，使用栈存储解析的字符
            ((parseFlags & kParseFullPrecisionFlag) != 0),      // true，即使用栈全精度解析，false 不是全精度也不需要用栈
        // true && true -->  true -->　就地将数字解析为字符串 --> 是通过take实现
        (parseFlags & kParseNumbersAsStringsFlag) != 0 &&
            (parseFlags & kParseInsituFlag) == 0>  s(*this, copy.s);  // *this 是reader, copy.s是流
```
其一个特化版本的构造函数
```cpp
    template<typename InputStream>
    class NumberStream<InputStream, true, false> : public NumberStream<InputStream, false, false> {
        typedef NumberStream<InputStream, false, false> Base;
    public:
        // 从输入流中读取，存到reader的栈中
        NumberStream(GenericReader& reader, InputStream& is) 
        : Base(reader, is), stackStream(reader.stack_) 
        { }
    // ...  
    private:
        StackStream<char> stackStream;
    };
```
这个类也是个`wrapper`，其成员变量`InputStream& is`也是引用，即直接对`copy.s`进行修改。而`stack_`就是`reader.stack_`用来存储decoded的值:
```cpp
      Ch TakePush() {
          stackStream.Put(static_cast<char>(Base::is.Peek()));
          return Base::is.Take();
      }

      void Push(char c) {
          stackStream.Put(c);
      }
```
`TakePush`是将待解析流`is`的当前字节入栈，而`Push`则是压入一些转义字符。当模板参数`pushOnTake`也是`true`时，`take()`内部就是`TakePush()`实现。
#### 解析结果
解析结果分为三个层次，充分为了效率考虑。如果待解析的数字是负数，且类型范围:[2^31, 2^21-1]，超出范围用int64，再超出范围用double。
```cpp
        double d = 0.0;
        unsigned i = 0;
        uint64_t i64 = 0;
        bool use64bit  = false;
        bool useDouble = false;
        int significandDigit = 0; // 有效位数
```

###　发送事件
对于五种数据类型的解析，开始结束都会发送相应的时间，比如解析一个数组，开始的时候会触发事件：　，结束的时候会触发：，要是想完整的实现一个Json文本解析，需要完整的实现下面类里的函数。自定义一个`class Handler`，如果不定义，传入默认的`BaseReadHandler`即什么也不做。
```cpp
template<typename Encoding = UTF8<>, typename Derived = void>
struct BaseReaderHandler {
    typedef typename Encoding::Ch Ch;
    // 即： 如果 Derived 指定了，那么就使用这个类，否则使用默认基类 BaseReaderHandler
    typedef typename internal::SelectIf<internal::IsSame<Derived, void>, BaseReaderHandler, Derived>::Type Override;

    bool Default() { return true; }
    bool Null() { /** 传入的参数即解析完成的值　*/ }
    bool Bool(bool) { /**传入的参数即解析完成的值*/ }
    bool Int(int) { /** ...*/ }
    bool Uint(unsigned) { /** ...*/ }
    bool Int64(int64_t) { /** ...*/ }
    bool Uint64(uint64_t) { /** ...*/ }
    bool Double(double) { /** ...*/ }
    /// enabled via kParseNumbersAsStringsFlag, string is not null-terminated (use length)
    bool String(const Ch*, SizeType, bool) { /** ...*/ }
    bool StartObject() { /** ...*/ }
    bool EndObject(SizeType) { /** ...*/ }
    bool StartArray() { /** ...*/ }
    bool EndArray(SizeType) { /** ...*/ }
    bool RawNumber(const Ch* str, SizeType len, bool copy) { return static_cast<Override&>(*this).String(str, len, copy); }
    bool Key(const Ch* str, SizeType len, bool copy) { return static_cast<Override&>(*this).String(str, len, copy); }
```

