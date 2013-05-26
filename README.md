SNS客户端平台  
Python3 + PyQt  

特性：

1. 多账户同时登录，多条时间线统一显示。
2. 一键状态更新。
3. 便捷的账户切换，可随时显示单个账户时间线、评论、AT等。
4. 评论、转发任意账户状态。
5. 关键字过滤（基于用户自定义关键词）。
6. 划词搜索（开发中）
7. 划词翻译（开发中）

安装：  
Ubuntu:  
> sudo apt-get install python3 python3-pyqt4 python3-six  
> git clone https://github.com/hbprotoss/weii.git  
> cd weibo  
> ./weibo

使用注意事项：

1. 请删除`qt-at-spi`这个包，它会导致Qt打开文件对话框崩溃。
   >sudo apt-get remove qt-at-spi
2. 使用过旧版本的朋友请清空~/.weibo目录。
3. 关键词配置功能还未提供图形接口，请在~/.weibo/keywords.txt中指定要过滤的关键词（通配符、正则表达式匹配 功能正在开发中）

*****************************

正处于开发阶段，不稳定期，添加功能中。(注：这个repo会在基本功能完成后废弃，用于发布的repo待定)  


