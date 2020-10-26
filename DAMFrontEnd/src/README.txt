直接运行main.py即可（里面就定义了几个路由便于查看网页；另外，我自己随便放了个图片的文件夹进去，便于测试图片）
html文档都在templates里。有的网页有两个版本（log和notLog），因为这些网页在登录和未登录时会呈现不一样的界面。（。。其实只有右上角那块不一样）


下面顺序的我是按需求报告文档顺序来的：
1. 发现界面（每个标签显示8个图）
discover_log.html和discover_notLog.html
http://127.0.0.1:5000/ （这里显示的是未登录界面discover_notLog.html。可以在py文件里改成登录界面discover_log.html。后面的原理相同不再赘述）

2.实时界面（每个标签显示8个图）（其实就是把发现界面的标签名换成时间名了，其他都一样）
realtime_log.html和realtime_notLog.html
http://127.0.0.1:5000/realtime/

3.点击发现界面和实时界面的“更多”按钮可以进入这个更多界面。这里可以显示该标签或时段里的全部图片
more_log.html和more_notLog.html
http://127.0.0.1:5000/more/

4.登录界面
login.html
http://127.0.0.1:5000/login/

5.注册界面
register.html
http://127.0.0.1:5000/reg/

6.搜索结果界面（只做了显示全部结果，暂时没做带筛选功能的）
search_log.html和search_notLog.html
http://127.0.0.1:5000/search/

7.上传界面（这个标签我暂时是用复选框checkbox做的）
upload.html
http://127.0.0.1:5000/upload/


另外做了移动端屏幕大小的适配（直接改变浏览器大小就能看到，或者用浏览器的开发者模式里的手机模式看，或者连个热点在手机上看）
暂时就做了这些，有的功能可能多做了，有的可能少做了，之后再补充吧。