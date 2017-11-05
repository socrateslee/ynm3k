# zip模块

zip模块可以把一个zip文件作为一个静态的目录来服务。

在通过--mock参数指定的config.json中，需要设置以下的参数:

- __type__: type == 'zip'时，表示采用zip模块来提供相应。
- __path__: zip文件的路径。
- __encoding__: 可选，zip文件的编码，默认值为utf-8，对于一些文件名编码为gbk文件，可以指定这个参数为'gbk'.

下面一个config.json的例子:

```
[
   ['/book/', '/home/ubuntu/book.zip']
]
```

如果采用y3k在命令行方式直接serve一个zip文件，可以以如下的方式启动:

```
y3k --zip <ZIP_FILE_NAME> [--zip-prefix <PATH_PREFIX>]
```

其中

- __--zip <FILE>__: 指定一个zip文件，把zip文件的内容作为一个静态文件服务提供出来。
- __--zip-prefix__: 启动--zip参数后，指定这个模块的路径前缀，如果这个参数指定了'/audio/'，那么/audio/会对应这个zip文件的根路径。

