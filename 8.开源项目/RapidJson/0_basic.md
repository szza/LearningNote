# basic　

```cpp
template <typename Encoding, typename Allocator = MemoryPoolAllocator<> > 
class GenericValue {

private:
    template <typename, typename> 
    friend class GenericValue;
    
    template <typename, typename, typename> 
    friend class GenericDocument;
}

```