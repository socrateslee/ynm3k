# 静态文件服务，static模块

static模块可以以静态文件的方式，针对文件系统中的目录提供服务。

在--mock的config.json中，需要设置以下的参数:

- __type__: type == 'static'时，表示采用static方式提供响应。
- __path__: 要提供静态文件的路径，需要以'/'结尾。
- __serve\_dir__: boolean, 是否要在访问目录时，显示目录列表。
- __try\_files__: 一个默认文件的列表，比如可以提供["index.html", "index.htm"]。提供了这个参数是，如果访问的路径是一个目录，那么会在这个目录下寻找列表中的文件，如果存在，会返回这个文件的内容作为响应的内容。

举例：

```
[
  ["/img/",
   {"type": "static",
    "path": "/abc/img/"}
  ],
  ["/html/",
   {"type": "static",
    "path": "/cde/html/",
    "try_files": ["index.html"]}
  ],
  ["/download/",
   {"type": "static",
    "path": "/fgh/download/",
    "serve_dir": true}
  ]
]
```

通过y3k在命令行，可以以如下启动:

```
y3k --static <PATH> [--static-prefix <PREFIX>] [--static-serve-dir]
```

其中

- __--static <PATH>__: 把<PATH>路径下的内容，作为一个静态文件服务提供出来。
- __--static-prefix <PREFIX>__: 启动--static参数后，指定这个模块的路径前缀。
- __--static-serve-dir__: 启动--static参数后，如果提供这个参数，将允许把目录列表作为请求返回。
