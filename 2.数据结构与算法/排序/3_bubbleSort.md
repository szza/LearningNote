# 冒泡法 BubbleSort

冒泡法排序是排序算法中的基本方法，其时间复杂度是`O(n^2)`。

## 逆序对

冒泡法，每一趟遍历都会消除一些逆序对，让最大值元素归位。比如第一趟遍历让最大值元素归位，第二趟让第二大元素归位，一直到第n趟让第n大，也就是最小的元素归位。
```cpp

void bubbleSort(std::vector<int>& arr){
    if(arr.empty()) return;

    size_t hi = arr.size()-1;
    for(size_t lo=0; lo < hi--; ++lo) { 
        // 这其实就相当于在每趟遍历中，都当前未归位的最大值元素归位
        // hi-- 表示从最后一个归位的元素不考虑
        for(size_t lo=0; lo < hi; ++lo) { 
            if(arr[lo] > arr[lo+1]) 
                std::swap(arr[lo], arr[lo+1]);
        }
    }
}
```
这其实也是一种贪心的思想体现：因为只要将遇到的所有“逆序对”消除，那么就是一个有序的序列，而冒泡排序就是每遇到一个逆序对就修正这个逆序对，消除他，通过n趟的迭代，那么就能消除所有的逆序对，就会变得有序。

### 时间复杂度
毫无疑问是O(n^2)。即使是一个有序的序列，用冒泡法时间复杂度依然是O(n^2)。因为在每一轮迭代中，只是考虑逆序对，将最大未归位元素归位。可是如果前面的部分元素已经归位，那么是否可以直接跳过而不再迭代？？？
```cpp
void bubbleSort(std::vector<int>& arr){
    if(arr.empty()) return;

    size_t last = 0;
    size_t hi = arr.size()-1;
    for(size_t lo=0; lo < hi; ++lo) { 
        for(size_t lo=0; lo < hi; ++lo) { 
            if(arr[lo] > arr[lo+1]) {
                std::swap(arr[lo], arr[lo+1]);
                last = lo; // 记录下最后一次交换元素的位置
            }
        }
        hi = last; // 下次就从最后一次更新元素位置开始
    }
}
```
如此不仅在序列本身有序时时间复杂度仅为O(n),也为普通情况下进行了改善，不再是每次都遍历，而是直接跳到最后一次交换元素的位置。

