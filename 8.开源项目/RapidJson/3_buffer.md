# buffer

+ `GenericMemoryBuffer`
+ `GenericStringBuffer`

二者的区别类似于`MemoryStream`和`StringStream`。

## introduce
### `GenericMemoryBuffer`
```cpp
template <typename Allocator = CrtAllocator>
struct GenericMemoryBuffer {
    typedef char Ch; // byte

    GenericMemoryBuffer(Allocator* allocator = 0, size_t capacity = kDefaultCapacity) 
    : stack_(allocator, capacity)
    { }

    void Put(Ch c) { *stack_.template Push<Ch>() = c; }     // Push单个字节
    void Flush() {}

    void Clear() { stack_.Clear(); }
    void ShrinkToFit() { stack_.ShrinkToFit(); }
    Ch* Push(size_t count) { return stack_.template Push<Ch>(count); }  // push多个字节
    void Pop(size_t count) { stack_.template Pop<Ch>(count); }
    
    const Ch* GetBuffer() const {
        return stack_.template Bottom<Ch>();
    }

    size_t GetSize() const { return stack_.GetSize(); }

    static const size_t kDefaultCapacity = 256;
    mutable internal::Stack<Allocator> stack_;
};

typedef GenericMemoryBuffer<> MemoryBuffer;
```
`GenericMemoryBuffer`实际上就是一个栈`stack_`，对`Internal::Stack`进行了二次封装，以字节为单位。

### 
```cpp
template <typename Encoding, typename Allocator = CrtAllocator>
class GenericStringBuffer {
public:
    typedef typename Encoding::Ch Ch;

    GenericStringBuffer(Allocator* allocator = 0, size_t capacity = kDefaultCapacity) 
    : stack_(allocator, capacity) 
    { }

    ...
    static const size_t kDefaultCapacity = 256;
    mutable internal::Stack<Allocator> stack_;
    ...
};
typedef GenericStringBuffer<UTF8<> > StringBuffer;
```
本质上也是对`stack`进行了二次封装，支持不同的编码格式。