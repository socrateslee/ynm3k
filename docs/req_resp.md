# request和response的描述方法

通过```y3k --mock config.json```可以让ynm3k加载config.json中的配置，在这个配置中，每一项都是[<request spec>, <response spec>]的二元组，其中request spec是用来匹配当前请求的。ynm3k会在config.json中找到可以匹配当前请求的第一个request spec的，然后根据response spec中的描述生成对当前请求的响应。

请求和响应的描述方法，都可以采用两种方式，一种是字符串的方式的描述，简单、直接，但是不能做比较精细的定制；另外一种是通过dict object来进行表述，就可以定制http method，http headers等属性。字符串方式的请求，都是一种dict object方式的简化写法。

## request spec，请求的描述

### 字符串方式

- __前缀类型__: 直接写成请求的路径前缀。比如'/api/'，那么ynm3k会把路径前缀为'/api/'的请求匹配到这个request spec上。例子中的前缀类型的请求，如果改写为dict object，相当于
```
{
  "type": "prefix",
  "path": "/api/"
}
```
- __完全匹配类型__: 在字符串前面加一个'='。比如'=/api/test'，ynm3k会把路径前缀完全等于'/api/test'的请求匹配到这个request spec上。例子中的完全匹配类型的请求，如果改写成dict object的方式，相当于
```
{
  "type": "exact",
  "path": "/api/test"
}
```

### dict object方式

dict object方式request spec，支持指定如下的属性：

- __type__: request spec本身的类型，必须提供，可以选择的值包括'exact'，'prefix'。
- __path__: 请求的路径，会根据request spec的类型决定这个路径是前缀还是完全匹配。
- __method__: 请求的方法，如'GET', 'POST', 'PUT'等，如果指定了这个属性，那么请求的方法必须和指定的一致才能匹配成功；如果不指定这个属性，那么匹配请求时，任何方法都是可以匹配成功的。

## response spec，响应的描述

### 字符串类型

- __远程方式，remote__: 如果response spec的描述是以'https://'或者'http://'开头的远程地址，那么字符串方式的表述会被解析为remote方式的响应，也就是说请求会被反向代理到这个地址上。远程方式相当于这样的dict object
```
{
  "type": "remote",
  "url": "https://..."
}
```
- __内容类型__: 不满足远程方式条件的会被认为是内容方式，也就是直接把字符串的内容作为响应的body返回。相当于下面的dict object
```
{
  "type": "content",
  "body": "...",
  "headers": {
    "content-type": "text/plain"
  }
}
```

### dict object方式

dict object方式的response spec，全部都可以支持的属性如下：

- __type__: type属性是必须的，决定了response spec的返回响应的方式，也决定了这个dict object中，还需要配置哪些属性。
- __headers__: headers属性可以是一个dict(比如 {"content-type": "application/json"})，或者是一个2-tuple的list(比如 [["content-type", "application/json"]])，用户在返回的响应中设置自定义的headers。
- __status__: status属性是int类型的，可以设置一个http返回码，用于设置或者覆盖当前响应的http return code。

ynm3k可以支持三种基本类型的response spec，即远程(remote)，内容(content)和文件(file)。在ynm3k中提供的其它module，一般既可以通过命令行的方式启动，也可以在response spec中，作为一种特殊的类型来生成响应。

下面对基本类型做一些说明，其他模块的说明将在模块自己的文档中提供：

- __远程，remote__: 远程(type == 'remote')就是通过反向代理的方式，从远程的服务器获取当前的请求。在request spec的类型不同时，响应会有不同的行为，如果request spec的类型是'exact'，会直接返回远程地址的内容；如果request spec的类型是'prefix'，会把请求的后缀映射为远程地址的后缀，比如，如果request spec的path为'/test/'，远程请求的url为'https://www.example.com/product/'，那么会把到'/test/somewhere/inside'映射到远程的'https://www.example.com/product/somewhere/inside'。
    - __url__: 远程模式下，被反向代理到的地址
- __内容，content__: 内容(type == 'content')是直接把响应的body写在了response spec中。
    - __body__: 响应的内容。
- __文件, file__: 文件(type == 'file')，是从文件中读取响应的内容，响应headers中的content-type会根据文件的扩展名来自动设置。
    - __body__: 文件的路径。

其他模块目前可以支持的响应内容包括：

- __static__: 以静态文件的方式，返回一个文件夹下的内容。
- __zip__: 以静态文件的方式，返回一个zip包中的内容。 
