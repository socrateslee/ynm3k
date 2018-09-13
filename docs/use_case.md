# 使用范例

## 设置http header来强制浏览器不缓存资源

在下面的配置中，通过设置浏览器缓存相关的header，可以强制的要求浏览器不做任何缓存，每次请求都要刷新数据

```
[
   [
      "/",
      {
         "url" : "https://www.amazonaws.cn/",
         "type" : "remote",
         "headers" : {
            "Pragma" : "no-cache",
            "Expires" : "0",
            "Cache-Control" : "no-cache, no-store, must-revalidate"
         }
      }
   ]
]
```


## 通过设置http response status code为302，跳转至某一url

```
[
  [
    "/",
    {
      "type": "content",
      "status": 302,
      "headers": {
        "Location": "https://valarmorghulis.io"
      }
    }
  ]
]
```
