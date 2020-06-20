# stream 2
+ `FileReadStream` ：文件流 只读
+ `FileWriteStream` ：文件流 只写
+ `MemoryStream` : 内存流 只读
+ `StringStream`

## introduce
这里的只读属性的类，即其数据来源于外，内存分配也在类外，这个类只是提供操作，不传入类的资源的生命周期进行管理。而只写类`FileWriteStream`是在重复使用缓冲区。下面几个类都是字节流。
### `MemoryStream`  
```cpp
  struct MemoryStream {
      typedef char Ch; // byte

      MemoryStream(const Ch *src, size_t size) 
      : src_(src), 
        begin_(src), 
        end_(src + size), 
        size_(size) 
      { }
      ...

      const Ch* src_;     //!< Current read position.
      const Ch* begin_;   //!< Original head of the string.
      const Ch* end_;     //!< End of stream.
      size_t size_;       //!< Size of the stream.
  };
```
在构造`MemoryStream`对象时，此对象的读取的数据流从外部传入`src`，由于其类型是`const Ch*`，因此不可以被修改，只能修改指针的位置以读取数据。

这个类与`StringStream`的不同之处：
+ `StringStream`的全名是`GenericStringStream<UTF8<>>`，是有固定的编码方式`UTF8`，而`MemoryStream`是一个字节流，并没有指定的编码方式。
+ 在构造`MemoryStream`时传入的`buffer`需要提供其长度，不需要是`\0`结尾。而`StringStream`是假定输入的`buffer`字符流是以`null`结尾的，因此不需要提供长度。
+ 由于`MemoryStream`没有指定编码方式，因此需要一个方法实现自动检测其编码：`peek4()`，而后者因为指定了编码格式所以不需要。

这个类一般被 `EncodedInputStream` or `AutoUTFInputStream`包裹(wrapper)


### `FileReadStream`
```cpp
class FileReadStream {
public:
    typedef char Ch;    //!< Character type (byte).

    FileReadStream(std::FILE* fp, char* buffer, size_t bufferSize) 
    : fp_(fp), 
      buffer_(buffer), 
      bufferLast_(0), 
      current_(buffer_), 
      bufferSize_(bufferSize), 
      readCount_(0), 
      count_(0), 
      eof_(false) 
    { 
        RAPIDJSON_ASSERT(fp_ != 0);
        RAPIDJSON_ASSERT(bufferSize >= 4);
        Read();
    }
    ...
private:
    void Read() { ...}

    std::FILE* fp_;     //　文件指针
    Ch* buffer_;        //　第一个字节
    Ch* bufferLast_;    //　最后一个字节
    Ch* current_;       //　当前读取字节处
    size_t bufferSize_;　
    size_t readCount_;　//一次读取的字节数
    size_t count_;  //!< Number of characters read
    bool eof_;         
    // 填充7个字节
};
```
从`fp`指向的文件中最大读取`bufferSize`个字节到`buffer`中，然后对其进行`buffer`进行操作。这里有个核心函数`read()`：
  ```cpp
    void Read() {
        if (current_ < bufferLast_)
            ++current_;
        else if (!eof_) {
            count_ += readCount_;
            // 将内容读取到 buffer 中
            readCount_ = std::fread(buffer_, 1, bufferSize_, fp_);
            bufferLast_ = buffer_ + readCount_ - 1; // 指向最后一个字节的位置
            current_ = buffer_;
            // 待读取的内容长度不足 bufferSize_，即使读完也不足
            if (readCount_ < bufferSize_) {
                buffer_[readCount_] = '\0';
                ++bufferLast_;
                eof_ = true;
            }
        }   
    }
  ```
  这个函数在首次调用时，一次性的将数据读取到`buffer`中，最多读取`bufferＳize_`，如果没有这个数，说明文件读完了。在以后调用`read`时，都将是移动`current`指针。　　

  这个类和`MemoryStream`很类似，只是此类从文件中读取，后者从内存中读取。此外，这个类读取到`buffer`中的字节流最后是以`\0`结尾的。其他操作接口一致，因此也需要`peek4()`来检测文件内容的编码方式。

### `FileWriteStream`
```cpp
class FileWriteStream {
public:
    typedef char Ch;    

    FileWriteStream(std::FILE* fp, char* buffer, size_t bufferSize) 
    : fp_(fp), 
      buffer_(buffer), 
      bufferEnd_(buffer + bufferSize), 
      current_(buffer_) 
    {  RAPIDJSON_ASSERT(fp_ != 0); }
    ...

private:
    // Prohibit copy constructor & assignment operator.
    FileWriteStream(const FileWriteStream&);
    FileWriteStream& operator=(const FileWriteStream&);

    std::FILE* fp_;
    char* buffer_;
    char* bufferEnd_;
    char* current_;
};
```
这个类是将数据写入到`buffer`中，待数据量最大到`bufferSize`就将数据更新到`fp`指向的文件中，然后这个`buffer`就又可以循环利用。因此这个`buffer`提供的内存需要由外部提供。将数据写入文件的函数是`flush`：
```cpp
    void Flush() {
        if (current_ != buffer_) {
            size_t result = std::fwrite(buffer_, 1, static_cast<size_t>(current_ - buffer_), fp_);
            if (result < static_cast<size_t>(current_ - buffer_)) {
                // failure deliberately ignored at this time
                // added to avoid warn_unused_result build errors
            }
            // (void)result; 
            current_ = buffer_;
        }
    }
```

## c++ streaｍ
使用`BasicIStreamWrapper`和`BasicOStreamWrapper`对`c++`库的流进行封装了。