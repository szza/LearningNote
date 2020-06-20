# encodedStream
这些都是`wrapper`，因此其对流的接受方式都是引用方式。
+ `EncodedInputStream`：只读，对输入的字节流编码为指定格式返回，字节流:`MemoryStream`,`FileReadStream`
+ `EncodedOutputStream`:只写，以指定的编码格式写入输出流
+ `AutoUTFInputStream`：自动检测
+ `AutoUTFOutputStream`