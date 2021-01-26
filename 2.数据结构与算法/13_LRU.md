# [LRU](https://leetcode-cn.com/problems/lru-cache/)

使用两个哈希表和一个双向链表。
+ 双向链表用来存储数据，为保持数据的优先级，让双向链表的头部是优先级最高，尾部优先级最低。
+ 因为从链表中查找时间复杂度 `O(n)`，两个`hash`表用于快速定位节点位置。

#### 手撸链表实现
```cpp
class LRUCache {
public:
    LRUCache(int capacity)
    :capacity_(capacity) 
    { 
        assert(capacity >=0);
    }

    int get(int key) {
        if(keyNodeMap_.find(key) == keyNodeMap_.end()) 
            return -1;

        // 只有在超过1个节点时才需要移动到头部，再返回值
        nodeLst_.moveToHead(keyNodeMap_[key]);
        return keyNodeMap_[key]->val;
    }
    
    void put(int key, int value) {
        if(keyNodeMap_.find(key) != keyNodeMap_.end()) { 
            Node* node = keyNodeMap_[key];
            node->val  = value;
            nodeLst_.moveToHead(node);
        }
        // 插入一个新的节点
        else { 
            Node* node = new Node(value);
            keyNodeMap_[key]  = node;
            nodeKeyMap_[node] = key;
            nodeLst_.insert(node);
            if(keyNodeMap_.size() > capacity_) 
                removeMostUnusedNode();
        }
    }

private:
    void removeMostUnusedNode() { 
        // 需要先找到节点
        Node* node = nodeLst_.removeTail(); 
        int key = nodeKeyMap_[node];
        keyNodeMap_.erase(key);
        nodeKeyMap_.erase(node);
        
        delete node;
    }

    struct Node { 
        Node* prev;
        Node* succ;
        int val;

        Node(int v, Node* prev=nullptr, Node* succ=nullptr)
        : val(v), prev(prev), succ(succ) 
        { }
    };

    class DoubleList {
    public:
        DoubleList(Node* head=nullptr, Node* tail=nullptr)
        : head(head), tail(tail) 
        { }

        ~DoubleList() {
            // 一次析构掉所有节点
            while(head) { 
                Node* next = head->succ;
                delete head;

                head = next;
            }
        }

        void insert(Node* node) { 
            if(node ==nullptr) return;
            // 若是空链表
            if(head ==nullptr) { 
                head = node; 
                tail = node; 
            }
            else {
                // 插入新的节点，总是放在首部
                node->succ = head;
                head->prev = node;

                head = node;
            }
        }

        void moveToHead(Node* node) { 
            if(node ==nullptr || node == head) return; 
         
            if(node == tail) { 
                tail = node->prev;
                tail->succ = nullptr;
            }
            else { 
                node->prev->succ = node->succ;
                node->succ->prev = node->prev;
            }
            // 加入到首节点
            insert(node);
        }

        Node* removeTail() { 
            if(tail ==nullptr) return tail;

            Node* ret = tail;
            if(head ==tail) { 
                head = nullptr;
                tail = nullptr;
            }
            else { 
                tail = tail->prev;
                tail->succ = nullptr;
            }

            return ret;
        }

    private:
        // 这两个是哨兵，指向链表的头部和尾部节点
        Node* head;
        Node* tail;
    };

private:
    std::unordered_map<int, Node*> keyNodeMap_;
    std::unordered_map<Node*, int> nodeKeyMap_;
    DoubleList nodeLst_;

    size_t capacity_;
};
```
####  使用`STL`库实现
可以更加简练，使用一个链表就能完成LRU设计
```cpp
class LRUCache {
public:
    LRUCache(int capacity)
    : capacity_(capacity) 
    { }
    
    int get(int key) {
      const auto& iter = keyNodeMap_.find(key);

      if(iter == keyNodeMap_.end()) { 
        return -1;
      }
      
      Node node = *(iter->second);
      list_.erase(iter->second);
      list_.push_front(node);
      keyNodeMap_[key] = list_.begin();
      return node.value;
    }
    
    void put(int key, int value) {
      const auto& iter = keyNodeMap_.find(key);

      if(list_.size() == capacity_ && iter == keyNodeMap_.end()) { 
        const Node& tail = list_.back();
        keyNodeMap_.erase(tail.key);
        list_.pop_back();
      }      
    
      if(iter != keyNodeMap_.end()) {  
        list_.erase(iter->second);
        keyNodeMap_.erase(iter);
      }
     
      list_.emplace_front(Node(key, value));
      keyNodeMap_[key] = list_.begin();
    }
private:
    struct Node { 
      int key;
      int value;

      Node(int k, int v) : key(k),value(v) { }
    };

    std::list<Node> list_; // 前端优先级高，即最常使用。从后端删除
    std::unordered_map<int, std::list<Node>::iterator> keyNodeMap_;
    int capacity_;
};

```

## LFU

