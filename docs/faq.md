# FAQ

- Q: 为什么有时候ynm3k的进程会卡住？
- A: 因为ynm3k默认情况下使用的是的单线程http server，对于并发请求的处理效果并不好，可能会导致进程卡住，可以通过paste等http server来辅助解决这个问题。比如
```
pip install paste
ynm3k --mock mock.json --server paste
```