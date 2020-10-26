#!/usr/bin/env python3

from flask import Flask, render_template, request, flash, redirect, jsonify, make_response
from datetime import timedelta
import os
import urllib.request
from API import collect_data
from API import create_data
from API import update_data
from bson.objectid import ObjectId
from datetime import datetime, timedelta
from time import sleep
import json as JSON



def get_date(d):
	result = ""
	year = "0000"
	month = "00"
	day = "00"
	hour = "00"
	minute = "00"
	second = "00"
	now = datetime.now() - timedelta(d)
	result += year[:4-len(str(now.year))]+str(now.year)
	result += month[:2-len(str(now.month))]+str(now.month)
	result += day[:2-len(str(now.day))]+str(now.day)
	return result+"000000"



app = Flask(__name__)  # 初始化一个Flask对象作为服务器
app.secret_key = "secret key"
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(seconds=1)

cd = create_data()
cd.remove_corrupted_images() # 这个函数只能在这里使用，后续不要使用。
username = "username"
ud = update_data() # 这个类在这里用于处理不同用户的登录，后面可以用，但是处理登录登出与已登录要用这个。
cdd = collect_data()
user_creating = {}


def getImageList():
	global cdd
	imageList = cdd.get_images()
	print(imageList)
	# imageList = []
	# folder = './static/data/photos/'
	# for root, directories, files in os.walk(folder):
	# 	for filename in files:
	# 		filePath = os.path.join(root, filename)
	# 		imageList.append(filePath)
	return imageList


imgList = getImageList()
# imgList = [filePath.lstrip('.') for filePath in imgList]  # 去掉文件路径前面的"."


@app.route('/', methods=['POST', "GET"])  # 发现
def discover():
	global ud
	# print(request.cookies)
	if "name" in request.cookies:
		info = {"name": request.cookies.get("name"), "password": request.cookies.get("password")}
		if ud.is_login(info):
			print("url is", request.cookies)
			return render_template('discover_log.html', username=info["name"])
	return render_template('discover_notLog.html')


@app.route('/image_list_get/', methods=['GET', 'POST'])  # 发现
def send_back():
	global cdd
	print("send_back() here!")
	# cd = collect_data()
	if request.json["type"] == "kinds":
		# imgList = getImageList()
		kinds = cdd.get_kinds()
		print("kinds here!")
		# print(kinds)
		# images = cd.get_images()
		imgList = {"result": {}}
		for kind in kinds:
			# print(kind)
			# print(cd.search({"kind": [kind["name"]]}))
			print("images searching!")
			images = cdd.search({"kind": [kind["name"]]})["images"]
			imgList["result"][kind["name"]] = images
		# imgList = JSONEncoder().encode(imgList)
		return jsonify(status=200, response=imgList)
	elif request.json["type"] == "labels":
		labels = cdd.get_label_and_tags()["labels"]
		imgList = {"result": {}}
		for label in labels:
			images = cdd.search({"label": [label["name"]]})["images"]
			imgList["result"][label["name"]] = images
		return jsonify(status=200, response=imgList)
	elif request.json["type"] == "time":
		imgList = {"result": {}}
		imgList["result"]["Today"] = cdd.search({"date": [[get_date(0), get_date(-1)]]})["images"]
		imgList["result"]["Yesterday"] = cdd.search({"date": [[get_date(1), get_date(0)]]})["images"]
		imgList["result"]["Before"] = cdd.search({"date": [["00000000000000", get_date(1)]]})["images"]
		return jsonify(status=200, response=imgList)
	elif request.json["type"] == "more":
		imgList = {"result": {}}
		if request.json["content_type"] == "kind":
			imgList["result"][request.json["data_type"]] = cdd.search({"kind": [request.json["data_type"]]})["images"]
		elif request.json["content_type"] == "time":
			if request.json["data_type"] == "Today":
				imgList["result"][request.json["data_type"]] = cdd.search({"date": [[get_date(0), get_date(-1)]]})["images"]
			elif request.json["data_type"] == "Yesterday":
				imgList["result"][request.json["data_type"]] = cdd.search({"date": [[get_date(1), get_date(0)]]})["images"]
			elif request.json["data_type"] == "Before":
				imgList["result"][request.json["data_type"]] = cdd.search({"date": [[get_date(2), get_date(1)]]})["images"]
		print(imgList, request.json)
		return jsonify(status=200, response=imgList)


@app.route('/login_check/', methods=['GET', 'POST'])  # 发现
def login_check():
	global ud
	print(ud.hu.um.user_list)
	print(request.json)
	if ud.is_login(request.json["info"]):
		print("url is", request.json["url"])
		if request.json["url"] == "http://10.112.3.26:5000/":
			return render_template('discover_log.html', username=request.json["info"]["name"])
	else:
		result = {"status": "No Login!"}
		return render_template('notLog.html')


@app.route('/more/')  # 更多
def more():
	imgList = getImageList()
	return render_template('more_log.html', imgList=imgList)


@app.route('/more/kind/<id>')  # 更多
def kind_more(id):
	global ud
	# print(request.cookies)
	if "name" in request.cookies:
		info = {"name": request.cookies.get("name"), "password": request.cookies.get("password")}
		if ud.is_login(info):
			print("url is", request.cookies)
			return render_template('more_log.html', username=info["name"])
	return render_template('more_notLog.html')


@app.route('/more/time/<id>')  # 更多
def time_more(id):
	global ud
	# print(request.cookies)
	if "name" in request.cookies:
		info = {"name": request.cookies.get("name"), "password": request.cookies.get("password")}
		if ud.is_login(info):
			print("url is", request.cookies)
			return render_template('more_log.html', username=info["name"])
	return render_template('more_notLog.html')



@app.route('/realtime/')  # 实时
def realtime():
	global ud
	if "name" in request.cookies:
		info = {"name": request.cookies.get("name"), "password": request.cookies.get("password")}
		if ud.is_login(info):
			print("url is", request.cookies)
			return render_template('realtime_log.html', username=info["name"])
	global cdd
	imgList = getImageList()
	kinds = cdd.get_kinds()
	images = cdd.get_images()
	return render_template('realtime_notLog.html')


@app.route('/login/')  # 登录界面
def login():
	return render_template('login.html')


@app.route('/login/', methods=['POST'])
def do_login():
	global ud
	print("asdaskjdjabfjbaehfbhj")
	# ud = update_data()
	if request.method == 'POST':
		info = {"name": request.form["username"], "password": str(request.form["password"])}
		print(info)
		global user_creating
		if info["name"] in user_creating.keys():
			while True:
				if user_creating[info["name"]].get_progress() == 100:
					break
				sleep(1)
		status, code = ud.login(info)
		print(status)
		username = info["name"]
		if status == True:
			return redirect('/')
		else:
			return render_template("login.html")


@app.route('/check_able_login/', methods=['GET', 'POST'])
def check_able_login():
	global user_creating
	print("asdaskjdjabfjbaehfbhj")
	# ud = update_data()
		# info = {"name": request.form["username"], "password": str(request.form["password"])}
		# print(info)
		# global user_creating
	if request.json["name"] in user_creating.keys():
		if user_creating[request.json["name"]].get_progress() != 100:
			result = {"code": 0}
			return jsonify(status=200, response=result)
		else:
			del user_creating[request.json["name"]]
			result = {"code": 1}
			return jsonify(status=200, response=result)
	result = {"code": 1}
	return jsonify(status=200, response=result)


@app.route('/logout/', methods=['GET', 'POST'])
def do_logout():
	global ud
	resp = make_response(redirect("/"))
	resp.set_cookie("name", "")
	resp.set_cookie("password", "")
	# print("asdaskjdjabfjbaehfbhj")
	# ud = update_data()
	# if request.method == 'POST':
	ud.logout({"name": request.cookies.get("name"), "password": request.cookies.get("password")})
	return redirect("/")


@app.route('/reg/')  # 注册界面
def reg():
	return render_template('register.html')

@app.route('/reg/', methods=['POST'])
def register():
	global cd
	global user_creating
	progress = cd.create_new_user({"basic": {"name": str(request.form["username"]), "email": str(request.form["email"])}, "password": str(request.form["password"]), "permission": "Normal"})[0]["task_progress"]
	user_creating[str(request.form["username"])] = progress
	return redirect('/')

@app.route('/upload/')  # 上传界面
def upload():
	global ud
	info = {"name": request.cookies.get("name"), "password": request.cookies.get("password")}
	if ud.is_login(info):
		return render_template('upload.html', username=info["name"])
	return redirect("/login/")

@app.route('/upload/', methods=['POST'])
def upload_file():
	# print(request.values.getlist("label"))
	# print(request.files["file"].content_type[6:])
	global cd
	# print("asdasdadafasf")
	# return redirect(request.url)
	if request.method == 'POST':
		if 'file' not in request.files:
			flash('No file part')
			return redirect(request.url)
		# file = request.files['file']
		# request.files["file"].save("a.jpeg")
		file = request.files["file"]
		data = {"file": file, "info": {"name": request.form["title"], "by": request.form["by"], "secret": "False", "label": request.values.getlist("label"), "kind": request.values.getlist("kind")}, "data": {"title": request.files["file"].filename, "description": request.form["description"], "comments": []}}
		a = cd.upload_images([data])
		print("Get File!")
		# check if the post request has the file part
		print(request.form["title"])
		# if file.filename == '':
		# 	flash('No file selected for uploading')
		# 	return redirect(request.url)
		# filename = secure_filename(file.filename)
		# print(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		# filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
		# print("Saving ...")
		# file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		# print("Converting ...")
		# result = os.popen("convert "+filepath+" png32:temp.png").read()
		# print("Reading ...")
		# image = Image.open("temp.png")
		# print(image.size)
		# image_hidden = Image.open("watermark_image/b.png")
		# print(image_hidden.size)
		# print("Merging ...")
		# eg = threading.Thread(target=do_merge, args=(image, image_hidden))
		# eg.start()
		# do_merge(image, image_hidden)
		flash('File successfully uploaded')
		return redirect('/')

@app.route('/test/')  # 上传界面
def test():
	return render_template('test.html')


@app.route('/search/')  # 搜索结果界面
def search():
	global ud
	print("asdasd")
	print(request.cookies)
	if "name" in request.cookies:
		info = {"name": request.cookies.get("name"), "password": request.cookies.get("password")}
		if ud.is_login(info):
			print("url is", request.cookies)
			return render_template('search_log.html', username=info["name"])
	return render_template('search_notLog.html')


@app.route('/search_data/', methods=["POST"])  # 搜索结果界面
def search_data():
	global cdd
	# imgList = getImageList()
	data = cdd.search({"name": [request.json["info"]["text"]]})
	imgList = {"result": data}
	return jsonify(status=200, response=imgList)


if __name__ == '__main__':
	# app.run(host='192.168.137.1', port=8080)  # 运行服务器
	# app.run(host='192.168.43.201', port=8080)
	app.run(host="0.0.0.0", debug="True")
