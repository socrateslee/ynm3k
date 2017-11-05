# 对于response的个性化后处理

在response spec中，operations指定了一个或者多个对response进行的后处理操作，可以通过这些操作，对response进行个性化的加工，从而给一些特殊的调试场景提供支持。

operations参数可以是一个操作的列表(list)，每个操作通过一个dict object进行定义；operations也可以是一个dict object，这时相当于只有一个个性化操作需要处理。每个操作的dict object格式为

```
{
  "type": "<操作类型>",
  ...  # 针对于不同操作类型的特殊参数
}
```

下面我们会根据不同的操作类型做详细的说明。

## insert\_adjacent\_html，向dom中插入标签

insert\_adjacent\_html可以向响应body中的html dom中插入个性化标签代码，使用方法和js中insertAdjacentHTML比较相似，这种操作只有在响应的content type为text/html时才会生效。另外，如果要启用这个操作，必须要安装beautiful soup 4，安装方法为

```
# 在虚拟环境中
pip install bs4
# 需要root权限时
sudo pip install bs4
```

具体支持的参数包括

- __selector__: 一个css选择器，比如"title", "body a"等，插入标签操作讲作用于被选择到的所有dom元素上。
- __position__: html代码插入的位置，支持"beforebegin", "afterbegin", "beforeend", "afterend"这四个位置，具体位置对应的方式可以参考 https://developer.mozilla.org/en-US/docs/Web/API/Element/insertAdjacentHTML 中的说明。
- __html__: 要插入的html代码。

比如，我们可以通过下面的配置，为转发的网页都加上[vConsole](https://github.com/Tencent/vConsole)，可以在不需要修改源代码的情况下直接调试移动端的页面，便于对生产和线上环境的通过手机对移动端页面进行调试和故障排查。

```
[
 ["/",
  {"type": "remote",
   "url": "https://m.baidu.com/",
   "operations": {"type": "insert_adjacent_html",
                  "selector": "title",
                  "position": "afterend",
                  "html": "<script src='https://res.wx.qq.com/mmbizwap/zh_CN/htmledition/js/vconsole/3.0.0/vconsole.min.js'></script><script>var vConsole = new VConsole();</script>"}
  }]
]
```