# ynm3k

ynm3k取名自"[要你命3000](http://cn.uncyclopedia.wikia.com/index.php?title=%E8%A6%81%E4%BD%A0%E5%91%BD%E4%B8%89%E5%8D%83)"，目前的功能包括

- 一个通过完全通过json进行配置的mock调试/反向代理服务器
- 一个静态文件服务器

## 安装方法
通过pip安装

```
sudo pip install ynm3k
```

## 基本的使用方法
在8080启动一个mock服务器，根据mock.json的规则进行转发和改写请求

```
y3k --mock mock.json --port 8080
```

mock.json的一些例子如下所示:

- 根据前缀转发请求至不同服务器
```
[
  ["/api/", "http://example.com/api/"],
  ["/static/my_work.html", "http://127.0.0.1/static/my_work.html"],
  ["/", "http://192.168.1.10:8080/"]
]
```

- 为每个请求增加一个特殊的header，比如设置X-Forwarded-For
```
[
 [{"type": "prefix",
   "path": "/",
   "headers": {"X-Forwarded-For": "1.2.3.4"}},
  {"type": "remote",
   "url": "https://ifcfg.cn/"}
 ]
]
```

- 转发某个前缀下的请求到一个本地目录下，并且对于/prefix/dirname/这样的请求自动返回该目录下的index.html的内容
```
[
    ["/prefix/", {"type": "static",
                  "path": "examples/dir",
                  "try_files": "index.html"}
    ]
]
```

- 为每个请求的response，增加一个特殊的header，比如设置Cache-Control

```
[
   [
      "/",
      {
         "type" : "remote",
         "url" : "https://ifcfg.cn/",
         "headers" : {
            "Cache-Control" : "private"
         }
      }
   ]
]
```

- 改写特殊的请求(对于POST /test 这个请求，结果是文件test.json的内容)
```
[
   [
     {
       "type": "exact",
       "path": "/test",
       "method": "POST"
     },
     {
       "type": "file",
       "body": "test.json",
       "headers": {"content-type": "json"}
     }
   ],
   ["/", "http://192.168.1.10:8080/"]
]
```
