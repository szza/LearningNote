# Protocol Buffer 

特点：

+ 原始内存中的数据结构可以二进制形式发送/保存，那么接收端要和发送端的内存模型、字节序等待保持一致。且扩展性不好。

+ XML：XML占用大量空间，对它进行编码/解码会给应用程序带来巨大的性能损失。 *Also, navigating an XML DOM tree is considerably more complicated than navigating simple fields in a class normally would be*

+ 容易扩展，使得兼容之前的版本。但是在修改`.proto`文件时需要满足几个条件

  + **不能**修改现存字段的 `field_num`
  + **不能**添加或者删除任何 **`required`**字段
  + 能删除  **` optional`** 和 **`repeated`** 字段
  + 能新增  **` optional`** 和 **`repeated`** 字段，但是这些新的字段的 `field_num` 必须是新的。（不仅不能是当前使用的`field_num`，而且还不能是已经删除的字段的 `field_num`）。

  如果满足这些条件，那么就能轻松的实现版本之间的兼容性。对于旧版本的代码，旧的版本会忽略掉新增的字段，而被删除的  **`optional`** 字段就会直接使用其默认值，被删除的 **`repeated`**  字段就为空，一个元素也没有。

  因为新增的  **`optional`** 字段并不会出现在旧版本中，因此要么用  `has_xxx`函数显示地检测这些增加的  **`optional`** 字段是否设置了，或者为这些字段在 `field_num` 之后提供一个合理的默认值 `[default = value]`。当然，没有人为设置一个默认值，那么就会使用系统的默认值.

  |  类型   | 系统默认值 |
  | :-----: | :--------: |
  | string  |     ""     |
  |  bool   |   false    |
  | numeric |     0      |

  

## *Synax*





## *Style Guide*  
为了方便阅读`.proto`，书写 `.proto` 时应遵守的习惯。下面是一些常用的习惯。
#### *Standard file formatting*  
+ 每行的字符个数最多80个
+ 缩进为2个字符
#### *File structure*  
`.proto`文件名应该保持为  `lower_snake_case.proto` 格式。而 `.proto`文件里应该按照以下格式有序排列：

1. License header (if applicable)
2. File overview
3. Syntax
4. Package
5. Imports (sorted)
6. File options
7. Everything else
#### *Message and field names*  
使用驼峰的命名方式来命名 `message` 名，比如 `SongServerRequest`。对于`message`的每个字段命名方式使用 下划线`_` 分割，比如 `song_name `。
```protobuf
message SongServerRequest {
	required String song_name = 1;
}
```
在C++下，最后的使用如下：
```cpp
  const string& song_name() { ... }
  void set_song_name(const string& x) { ... }
```
如果在字段的命名中出现数字，格式为：`song_name1`，而不是`song_name_1`
#### *Repeated fields*  
对于有 `Repeated` 修饰的字段，应该使得每个字段的复数形式来命名。
```protobuf
  repeated string keys = 1;			 // key --> keys
  ...
  repeated MyMessage accounts = 17;	 // account --> accounts
```
#### *Enums*   
枚举名使用驼峰的方式，每个枚举值使用的是 `ENUMNAME_VALUE`格式：
```protobuf
enum Foo {
  FOO_UNSPECIFIED = 0;
  FOO_FIRST_VALUE = 1;
  FOO_SECOND_VALUE = 2;
}
```
#### *Services*  
如果 `.proto` 提供的是一个 **RPC** 服务， 使用驼峰命名方式来命名服务名和方法名。 
```protobuf
service FooService {
  rpc GetSomething(FooRequest) returns (FooResponse);
}
```
## *Encoding*

这个文档，描述的是 *protocol buffer* 的二进制生成格式。了解这个能让我们更好书写*`.proto` ，使得生产的代码更小。

每个字段

#### *Message Structure*

`message` 就是一些键值对的组合，`message` 的二进制流中使用的每个字段的 `number`来作为键。而每个字段的“name”和声明的“类型”只有在解码端通过引用消息类型的定义来确定。（？？？ 函数）

| *Type* |    *Meaning*     |                        *Used For*                        |
| :----: | :--------------: | :------------------------------------------------------: |
|   0    |      Varint      | int32, int64, uint32, uint64, sint32, sint64, bool, enum |
|   1    |      64-int      |                fixed64, sfixed64, double                 |
|   2    | Length-delimited | string, bytes, embedded messages, packed repeated fields |
|   3    |   Start group    |                   groups (deprecated)                    |
|   4    |    End group     |                   groups (deprecated)                    |
|   5    |      32-bit      |                 ixed32, sfixed32, float                  |

Message 的每个键值对的值都是由：**`filed_num <<3 | wire_type`**  得到的，也因此 `field_num` 不能重复。

####  *Signed Integers*

在 *Protocol buffer* 中 *wire type* 是0的都是被编码为 *varints* ，但是在 *protobuff* 中的有符号类型 （**`sint` and `sint64`**） 和 标准的 `int` 类型（**`int32` and `int64`**）在负数的编码方式上有很大的差异。
+ 如果负数类型是 **`int32` or `int64`** ，结果是 `varint` 就将总是 10个字节长度。而实际上，这个负数是被当一个极大的无符号数来处理的。
+ 如果负数类型是 **`sint` or  `sint64`** ，得到的 `varint` 就将会使用  **`ZigZag`**的编码方式，更加有效。
> ***ZigZag*** 编码方式是将有符号数映射到无符号数， 这样就能使绝对值较小的数字（例如-1）也有一个较小的`varint`编码值。
> $$
> [-2^{31}, 2^{31}-1] --> [0, 2^{32}-1]
> $$
> 一个有符号数的正负数个数是等于无符号的个数，因此可以完成映射。而映射的方式如下：
>
> | Signed Original | Encoded As |
> | :-------------: | :--------: |
> |        0        |     0      |
> |       -1        |     1      |
> |        1        |     2      |
> |       -2        |     3      |
> |        2        |     4      |
> |   2147483647    | 4294967294 |
> |   -2147483648   | 4294967295 |
>
> 编码方式如下：
>
> **sint32**：
>
> ```c
> (n <<1) ^ (n >>31); // n 是正数，n >> 31 得到的是0；否则得到的全是 1
> ```
>
> **sint64**
>
> ```cpp
> (n <<1) ^ (n >>63)
> ```

#### *Non-varint Number*

*Non-varint* 类型的数字比较简单，它可以肯定的告诉解析器需要32/64位的内存大小，此时是用小端序存储的。

+ 32位：对应的 `wire type: 5`
+ 64位：对应的 `wire type: 1`

#### *Strings*

`wire type: 2`。这个类型 前面是 varint 编码的长度，后跟指定数量的数据字节。

```protobuf
message Test2 {
	optional string b = 2;
}
```

比如，如果`b`的值是“ testing”，将会得到如下的二进制格式：

```c
12 07 74 65 73 74 69 6e 67
```

+ `key`: `12`。`12` 是如下解码的：前面的五位是 ***field_num***=2，最后三位是 *** wire_type***=2
  
    ```c
    0001 0010 --> 000010 010 
    ```
    
+ `testing` 的长度: `07`

+ `testing`的表示：`74 65 73 74 69 6e 67`

#### *Service*





##  Protocol Buffer C++

#### 编译

编译格式如下，最后生成的是 `.proto`文件名的`.pb.h`和`.pb.cc`

```
protoc --proto_path=src --cpp_out=build/gen src/foo.proto src/bar/baz.proto
```







### 参考链接

1. [Protocol Buffer语法指南译]([https://colobu.com/2015/01/07/Protobuf-language-guide/#%E5%AE%9A%E4%B9%89%E4%B8%80%E4%B8%AA%E6%B6%88%E6%81%AF%E7%B1%BB%E5%9E%8B](https://colobu.com/2015/01/07/Protobuf-language-guide/#定义一个消息类型))
2. [Protocol Buffer](https://developers.google.com/protocol-buffers/docs/proto3)
3. [required、repeated、option区别](https://blog.csdn.net/code_style/article/details/82751720?utm_medium=distribute.pc_relevant.none-task-blog-BlogCommendFromMachineLearnPai2-3.compare&depth_1-utm_source=distribute.pc_relevant.none-task-blog-BlogCommendFromMachineLearnPai2-3.compare)





























