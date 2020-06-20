cmake_minimum_required(VERSION 3.10)
project(smuduo)

set(CXX_FLAGS
 -g
 -D_FILE_OFFSET_BITS=64
 -Wall
 )
string(REPLACE ";" " " CMAKE_CXX_FLAGS "${CXX_FLAGS}")
set(CMAKE_BUILD_TYPE "DEBUG")
set(CMAKE_CXX_FLAGS_DEBUG "-O0")
set(CMAKE_<CXX>_COMPILER "g++")     # g++ 编译器
set(CMAKE_CXX_STANDARD 11)          # C11
set(CMAKE_CXX_STANDARD_REQUIRED True) 
set(EXECUTABLE_OUTPUT_PATH  ${PROJECT_BINARY_DIR}/bin)
set(LIBRARY_OUTPUT_PATH ${PROJECT_BINARY_DIR}/lib)

include_directories(${PROJECT_SOURCE_DIR})  

add_subdirectory(src)    
