# topK
`topK`没有第0大，都是第一大或者第一小开始。 第一小/大就是对应有序数组的`arr[0]/arr[N-1]`。

## [最小的k个数](https://leetcode-cn.com/problems/zui-xiao-de-kge-shu-lcof/)
#### 基于快排的方法
参考[quicksort](./排序/1_quickSort_.md)，先将数组排序，再取出前k个数。这个方法是就地执行，会改变数组本身。

注意：选择第K小的元素，使用快排的选择算法，而这道题是求取最小的k个数，需要先对他们进行排序。
```cpp
class Solution {
public:
    vector<int> getLeastNumbers(vector<int>& arr, int k) {
        if(arr.empty() || k<=0 || arr.size() < k) 
            return resultSet_;
         
        for(int lo=0, hi=arr.size()-1;lo < hi;) {  
            int L=lo, R=hi;
            int pivot = arr[lo];

            while(L < R) { 
                while(L < R && pivot <= arr[R]) --R; arr[L] = arr[R]; //将大于轴点数子换到左侧
                while(L < R && arr[L]<= pivot)  ++L; arr[R] = arr[L];
            } //L == R
            // 每次经过一轮循环，pivot左侧的元素都不大于它，右侧的元素都不小于它
            arr[L] = pivot;
            
            if(L <= k) lo = L+1; // 进入右侧
            if(L >= k) hi = L-1; // 进入左侧
        } // lo == hi 时 lo <=k<=hi，因此 lo == hi==k

        while(k) 
        { 
            --k;
            resultSet_.push_back(arr[k]);
        }

        return resultSet_;
    }

private:
    std::vector<int> resultSet_;
};
```
#### 基于最大堆的方法 
维持一个大小为`k`的大顶堆，使得堆顶元素最大。元素个数不足`k`就直接放入堆中，超过k个元素，和堆顶元素进行比较，小于堆顶就弹堆顶，放入当前元素。 

时间复杂度是`O(n*logk)`，空间复杂度是`O(k)`。

这个优点在于：不用一次性的将全部数据加载进入内存，适合海量数据。
```cpp
class Solution {
public:
    vector<int> getLeastNumbers(vector<int>& arr, int k) {
        if(arr.empty() || k<=0 || arr.size() < k) return std::vector<int>{ };
        std::vector<int> resultSet_(k);
        std::priority_queue<int> big_;  // 优先级队列
        
        for(int& num : arr) { 
            if(big_.size() < k) { 
                big_.push(num);
            }
            else { 
            // 满了 
            // 将大的元素取出来，将小的元素压入
                if(big_.top() > num) { 
                    big_.pop();
                    big_.push(num);
                }
            }
        }
        
        while(k) { 
            resultSet_[k-1] =big_.top();
            big_.pop();
            
            --k;
        }
            
        return resultSet_;
    }
};

```
上面这两种解法各有优缺点， 各自适用于不同的场合， 因此应聘者仵动手做题之前要先问消楚题目的要求， 包括输入的数据揽有多大、能否－次性载入内存、是否允许交换输入数据中数字的顺序等

## [两个有序数组的中位数](https://leetcode-cn.com/problems/median-of-two-sorted-arrays/)
```题目
给定两个大小为 m 和 n 的有序数组 nums1 和 nums2。请你找出这两个有序数组的中位数，并且要求算法的时间复杂度为 O(log(m + n))。

你可以假设 nums1 和 nums2 不会同时为空。 
```
### `topK`
利用求`topK`问题的思路。假设有数据：
```
A: 1, 3, 4, 9
B: 1, 2, 3, 4, 5, 6, 7, 8
k = 7 
```
`A`的中位数是`k/2=3`。表示的是第3个，即下标为`2 = k/2-1`。`A[2] > B[2]`，因此`B[2]`前面面的元素不可能是中位数，比如`B[1]`最多也只是第4大。
而`A`中都是有可能的。比如`A[0]`只要比`B[5]`大，那么就是第7大，`A[0]`只要比`B[2]`大，那么`A[3]`就是第7大。下一次比较：
```
A: 1, 3, 4, 9
B: 4, 5, 6, 7, 8
```
> 引理
>
>一般地， 两个有序数组 **`A[0], A[1], A[2] ... A[k/2-1], A[k/2] ... A[n]`** 和 **`B[0], B[1], B[2] ... B[k/2-1], B[k/2]...B[m]`** 。如果 *`A[k/2-1] < B[k/2-1]`* ，那么  *`A[0], A[1], A[2] ... A[k/2-1]`* 都不可能是第 *`k`* 小的数字。  
>
>`A` 数组中比 `A[k/2-1]` 小的数有 `k/2-1`个。B数组中，`B[k/2-1]`前面有`k/2-1`。在最好的情况下`B[k/2-1]`前面最大的一个元素`B[k/2-2] < A[0]`，那么此时`A[k/2-1]`也只是第`k/2-1 + k/2`小，即最好的情况下，`A[k/2-1]`也是只是第`k-1`小。因此 `A[k/2-1]` 前面的元素都不可能满足条件。

因此，根据这个结论，可以在每次从两个有序数组中选出中位数，且比较出大小后，**较小的中位数及其所在数组前面的部分都可以抛弃**（减而治之）。比如，上面`A[0] ~ A[k/2-1]`都可以抛弃。直接从`A[k/2]`再次寻找。此时`k`将会减少`k/2`，即从剩余的数组中查找 ***`k = k - k/2`*** 小的元素。

+ `A[k/2-1] = B[k/2-1]`时，就可以直接返回了，此时两个数就是原问题的第K小的数。
+ 某个数组到头了。比如`A`序列到达`A[n]`，而`B`还没到达`B[n]`。

  如果`A[n] < B[k/2-1]`，那么根据上面的结论，`A[n]`及其前面可以全部抛弃，`A`剩余长度就是0。然后 ***`k = k - k/2`*** 那么最终的结果肯定就是在`B`中，此时可以直接访问得到`B`得到。 
  如果`A[n] > B[k/2-1]`，自然抛弃`B[k/2]`前面的所有元素。下次对比时:
  ```
    A: A[n]
    B: B[k/2], ..., B[m]
  ```
  注意：每次`k`在抛弃一段之后都是会减少一半的。
#### 根据topK求中位数
有了求 *`topK`* 的算法。可以利用 *`topk`* 来求解中位数，第`k`小的元素对应的下标是`k-1`：
+ 当两个数组长度和是奇数时， `k = length /2 + 1 =(2 * n + 1) /2 + 1 = n + 1`。
+ 当两个数组长度和是偶数时， k 是上中位数和下中位数和的平均数:   
    上中位数：`left  = length /2    = n`  
    下中位数：`right = length /2 +1 = n +1;` 

  为统一这两个写法:  
    + `left  = (length +1) / 2`  
    + `right = (length +2) / 2`
#### 代码实现 
```cpp 
class Solution {
public:
    double findMedianSortedArrays(vector<int>& nums1, vector<int>& nums2) {

        int n = nums1.size(); 
        int m = nums2.size(); 

        int length = n + m;
        int left  = (length +1) /2;
        int right = (length +2) /2;   

      return  static_cast<double>(__getTopK(nums1, 0, n, nums2, 0, m, left) + 
                                  __getTopK(nums1, 0, n, nums2, 0, m, right)) /2;
    }

    int __getTopK(std::vector<int>& nums1, int s1, int e1, 
                  std::vector<int>& nums2, int s2, int e2, 
                  int k) 
    { 
      int len1 = e1 - s1, len2 = e2- s2;

      if(len1 ==0) { return nums2[s2 +k-1]; }
      if(len2 ==0) { return nums1[s1 +k-1]; }

      if(k==1) return std::min(nums1[s1], nums2[s2]);

      // 求取此时的中点索引
      // 有可能 s1 + k/2直接越界了，因此要么到达 nums1 的中点，要么到达 nums1 的终点
      int i = s1 + std::min(len1, k/2)-1; 
      int j = s2 + std::min(len2, k/2)-1;
      
      int result = 0;
      
      if(nums1[i] < nums2[j]) 
      { 
        // 要抛弃的长度就是 [s1, i]， 因此 k - (i+1 -s1)
        result =__getTopK(nums1, i+1, e1, nums2, s2, e2, k - (i+1 - s1)); 
      }
      else 
      {
        result = __getTopK(nums1, s1, e1, nums2, j+1, e2, k-(j+1 - s2));
      }

      return result;
    }
};
```

## [无序数据流的中位数](https://leetcode-cn.com/problems/shu-ju-liu-zhong-de-zhong-wei-shu-lcof/)
```
题目描述：

如何得到一个数据流中的中位数？如果从数据流中读出奇数个数值，那么中位数就是所有数值排序之后位于中间的数值。如果从数据流中读出偶数个数值，那么中位数就是所有数值排序之后中间两个数的平均值。
```
#### 分析

整个数据可以看作被中位数分为两部分：左边的不大于中位数，右边的不小于中位数。用一个数据结构保存中位数两边的数据，**使得左边的数据都小于右边的数据**。

大顶堆和小顶堆：因为大顶堆头部最大，尾部最小，因为可以让小于中位数的存在大顶堆，反之大于中位数的位于小顶堆。使得数据流中的数据均匀分布在两个堆中。

问题是怎么分布均匀，两队数据个数之差不超过1？ 让数据流中的数，先进入大顶堆，然后将大顶堆首部的元素移到小顶堆，就能使得左边的永远不大于右边的。如果导致小顶堆元素个数多于大顶堆，就从小顶堆顶取出一个给大顶堆，仍保持总体的有序性。
+ 如果总数个数是奇数，大顶堆个数是m，那么小顶堆个数是m-1。大顶堆顶即中位数。
+ 如果总数个数是偶数，大顶堆个数是m，那么小顶堆个数是m。两堆顶和的平均数就是中位数。

#### 代码实现 
```cpp
class MedianFinder {
public:    
    void addNum(int num) {
        //每次都先加入大顶堆
        big.push(num);

        small.push(big.top());
        big.pop();

        if(big.size() < small.size()) {  
            big.push(small.top());
            small.pop();
        }
    }
    
    double findMedian() {
        return big.size() > small.size() ? 
                    static_cast<double>(big.top()) :
                    static_cast<double>(big.top() + small.top()) /2 ;
    }
private:
    std::priority_queue<int> big;
    std::priority_queue<int, std::vector<int>, std::greater<int>> small;
};
```


## [前k个高频数](https://leetcode-cn.com/problems/top-k-frequent-words/submissions/)
还是利用堆实现：达到 `O(n*log(k))` 的时间复杂度，并在空间复杂度为`O(n)`，因为还有个map使用了空间。

比较无语的是比较器：先比较频率，频率相同时，字符小的优先级别高。
```cpp
class Solution {
public:
    typedef std::vector<std::string> vectorStr;

    vectorStr topKFrequent(vectorStr& words, int k) {
        if(words.empty() || k<=0) return resultSet_; 
       
        for(const auto& word : words) ++map_[word];

        for(const auto& entry: map_) { 
            if(heap_.size() < k) 
            { 
              heap_.push({entry.second, entry.first});
            }
            else 
            {   
              if(entry.second < heap_.top().first || 
                (entry.second == heap_.top().first && entry.first > heap_.top().second)) 
                continue;

              heap_.pop();
              heap_.push({entry.second, entry.first});
            }
        }

        resultSet_.resize(k);
        while(k--) 
        { 
            resultSet_[k] = heap_.top().second;
            heap_.pop();
        }
        return resultSet_;
    }
private:
    struct Comparator { 
      bool operator()(const std::pair<int, std::string>& lhs, 
                      const std::pair<int, std::string>& rhs) const
      { 
        return lhs.first == rhs.first ? 
               lhs.second < rhs.second:   // 频率一致，字母顺序小的 优先级更高
               lhs.first  > rhs.first;    // 先按照频率比较
      }  
   };

    std::priority_queue<std::pair<int, std::string>,
                        std::vector<std::pair<int, std::string>>,
                        Comparator> heap_;
    std::unordered_map<std::string, int> map_;
    vectorStr resultSet_;
};
```