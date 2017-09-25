# 配置文件

ynm3k可以通过--mock参数指定一个json格式的配置文件：

```
y3k --mock config.json
```

这个json文件的内容是一个list，list中每一项都是一个二元组，二元组的第一项为是http请求的描述(request spec)，第二项为http响应的描述(response spec)。

ynm3k的在处理请求的时候，会按照配置文件的这个list的顺序，匹配当前请求是否满足每一个request spec的条件，如果找到了一个满足条件的request spec，那么会根据对应的response spec生成一个响应来返回。request spec和response spec的都既可以是一个dict object，也可以是一个字符串(仅仅应用于处理简单的反向代理的模式)。

配置文件的结构如下：

```
[
    [<Request Spec>, <Response Spec>],
    ...
]
```

## 配置文件的范例

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

