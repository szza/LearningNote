cmake_minimum_required(VERSION 3.10)
project(smuduo)

set(CXX_FLAGS 
-g 
-D_FILE_OFFSET_BITS=64
-Wall
)
set(CMAKE_<CXX>_COMPILER "g++")
set(EXECUTABLE_OUTPUT_PATH  ${PROJECT_BINARY_DIR}/bin)
set(LIBRARY_OUTPUT_PATH ${PROJECT_BINARY_DIR}/lib)

include_directories(${PROJECT_SOURCE_DIR})  

add_subdirectory(muduo/base)    
add_subdirectory(muduo/unitest)