#!/usr/bin/env python3

from flask import Flask, render_template
from datetime import timedelta
import os

app = Flask(__name__)  # 初始化一个Flask对象作为服务器
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(seconds=1)


def getImageList():
    imageList = []
    folder = './static/data/photos/'
    for root, directories, files in os.walk(folder):
        for filename in files:
            filePath = os.path.join(root, filename)
            imageList.append(filePath)
    return imageList


imgList = getImageList()
imgList = [filePath.lstrip('.') for filePath in imgList]  # 去掉文件路径前面的"."


@app.route('/')  # 发现
def discover():
    return render_template('discover_notLog.html', imgList=imgList)


@app.route('/more/')  # 更多
def more():
    return render_template('more_log.html', imgList=imgList)


@app.route('/realtime/')  # 实时
def realtime():
    return render_template('realtime_log.html', imgList=imgList)


@app.route('/login/')  # 登录界面
def login():
    return render_template('login.html')


@app.route('/reg/')  # 注册界面
def reg():
    return render_template('register.html')


@app.route('/upload/')  # 上传界面
def upload():
    return render_template('upload.html')


@app.route('/test/')  # 上传界面
def test():
    return render_template('test.html')


@app.route('/search/')  # 搜索结果界面
def search():
    return render_template('search_notLog.html', imgList=imgList)


if __name__ == '__main__':
    # app.run(host='192.168.137.1', port=8080)  # 运行服务器
    # app.run(host='192.168.43.201', port=8080)
    app.run(host="0.0.0.0", debug="True")
