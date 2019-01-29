# 命令行参数

ynm3k的在安装成功后，可以通过y3k命令启动的，y3k命令支持以下的基本参数：

- __--help__: 显示帮助信息。
- __--version__: 显示当前版本。
- __--host__: 设置y3k绑定的地址，默认为0.0.0.0 。
- __--port__: 设置y3k启动之后的端口号，默认为8080 。
- __\-\-mock <CONFIG>__: 接受一个.json文件作为配置文件，具体的配置文件的格式详见配置文件一节中的内容。
- __\-\-mock-prefix <PREFIX>__: 指定--mock的参数所启动的服务的路径前缀。
- __\-\-reload <GLOB PATTERN>__: 让ynm3k进程监视<GLOB PATTERN>所对应的文件或者路径，如果发生变化，则重新加载ynm3k服务器。比如，可以监控mock的配置文件，在配置发生变化时自动重新加载。
- __\-\-server <SERVER>__: 因为ynm3k是通过bottle.py启动的，默认的服务器为python自带的wsgiref中的simple-server，通过这个参数可以指定用来启动服务的web server，具体见 https://bottlepy.org/docs/dev/deployment.html#switching-the-server-backend 。

下面的参数主要用于单独启动各个功能模块(这些功能模块往往也可以作为--mock参数所引入的配置文件的一部分来加载):

## static静态文件模块
- __--static <PATH>__: 把<PATH>路径下的内容，作为一个静态文件服务提供出来。
- __--static-prefix <PREFIX>__: 启动--static参数后，指定这个模块的路径前缀。
- __--static-serve-dir__: 启动--static参数后，如果提供这个参数，将允许把目录列表作为请求返回。

## zip模块
- __--zip <FILE>__: 指定一个zip文件，把zip文件的内容作为一个静态文件服务提供出来。
- __--zip-prefix__: 启动--zip参数后，指定这个模块的路径前缀。

