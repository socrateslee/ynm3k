# Use cases

## 设置http header来强制浏览器不缓存资源

```
[
  "/",
  {
    "type": "remote",
    "url": "https://www.amazonaws.cn/",
    "headers": {
      "Cache-Control": "no-cache, no-store, must-revalidate",
      "Pragma": "no-cache",
      "Expires": "0"
    }
  }
]
```