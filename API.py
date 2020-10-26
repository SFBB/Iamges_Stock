#!/usr/bin/env python3

# 用于提供基础的收集数据库信息的功能

import json as JSON
from database_handle import database_handle as dh
from handle_image import handle_images as hi
from handle_image import detect_corrupted_images
from handle_user import handle_users as hu
from encrypt_and_decrypt import encrypt_and_decrypt as ead
from bson.objectid import ObjectId
# import copy
from task_manager import task_manager



def object_to_string(list):
	for i in list:
		i["_id"] = str(i["_id"])
	return list

def string_to_object(list):
	for i in list:
		i["_id"] = ObjectId(i["_id"])
	return list



# 收集数据
class collect_data():
	def __init__(self, mode="normal"):
		self.mode = mode
		self.dh = dh()
		self.hu = hu()

	# 负责搜寻，获取较细致的数据相见"search info example"与"result example"
	def search(self, info):
		print("Searching ...")
		if "secret" in info.keys():
			secret = info["secret"]
			del info["secret"]
		else:
			secret = "False"
		methods = {"name": {self.dh.get_images_by_name: "images", self.dh.get_albums_by_name: "albums"},
				   "label": {self.dh.get_images_by_label: "images"}, "tag": {self.dh.get_albums_by_tag: "albums"},
				   "kind": {self.dh.get_images_by_kind: "images"}, "album": {self.dh.get_images_by_album: "images"},
				   "user": {self.dh.get_images_by_user: "images", self.dh.get_albums_by_user: "albums"}, "date": {self.dh.get_images_by_date: "images", self.dh.get_albums_by_date: "albums"},
				   "last_edit_time": {self.dh.get_images_by_last_edit_time: "images", self.dh.get_albums_by_last_edit_time: "albums"}}
		handled = {"images": False, "albums": False}
		result = {"images": [], "albums": []}
		for i in info:
			if info[i] == []:
				continue
			else:
				for method in methods[i]:
					handle_type = methods[i][method]
					if not handled[handle_type]:
						for ii in info[i]:
							list_temp = method(ii)
							for iii in list_temp:
								if iii not in result[handle_type]:
									result[handle_type].append(iii)
						handled[handle_type] = True
					else:
						result_temp = []
						for ii in info[i]:
							list_temp = method(ii)
							for iii in list_temp:
								if iii in result[handle_type]:
									result_temp.append(iii)
						result[handle_type] = result_temp
		result = self.handle_secret(secret, result)
		print(result)
		return result

	# 这个基本不需要用，类内使用
	def handle_secret(self, secret, list):
		if secret == "True":
			return list
		else:
			result = {"images": [], "albums": []}
			for i in list:
				for ii in list[i]:
					if ii["secret"] != "True":
						result[i].append(ii)
			return result

	# 获取kind列表，每一个kind有name和image_list，image_list含有图像的ObjectId
	def get_kinds(self):
		print("get_kinds here in API.py")
		result = self.dh.get_kinds()
		print(result)
		return result

	# 获取label与tag列表，每一个label与tag里含有name和image_list，image_list含有图像的ObjectId
	def get_label_and_tags(self):
		result = {"labels": [], "tags": []}
		result["labels"] = self.dh.get_labels()
		result["tags"] = self.dh.get_tags()
		return result

	# 获取album列表，每一个album含有name与image_list
	def get_albums(self):
		result = self.dh.get_image_list()
		return result

	# 获取用户列表，含有用户名、email，但是没有密码
	def get_users(self):
		result = self.dh.get_user_list()
		return result

	# 获取单个的用户信息
	def get_user(self, user):
		return self.hu.get_user_info(user)

	# 获取全部的image列表，每一个image含有name,label,kind,by,data,last_edit_data,ObjectId,location,secret
	def get_images(self):
		result = self.dh.get_image_list()
		return result



# 创建数据
class create_data():
	def __init__(self, mode="normal"):
		self.mode = mode
		self.dh = dh()
		self.hi = hi()
		self.hu = hu()
		self.task_manager = task_manager()

	# 上传图片，详见"upload_images info example"与"upload_images result example"
	def upload_images(self, images=[{"file": "", "info": {"name": "", "by": "", "secret": "", "label": [], "kind": []}, "data": {"title": "", "description": "", "comments": [{"by": "", "content": ""}]}}]):
		image_info_list = []
		task_progresses = []
		for image in images:
			temp_progresses = []
			image["info"]["location"] = self.hi.get_image_location()
			image_info_list.append(image["info"])
			task_progress = self.task_manager.add_task(image["info"]["location"], self.hi.add_image, (image,))
			temp_progresses.append(task_progress)
			if image["info"]["secret"] == "True":
				EAD = ead(image["info"]["by)"])
				task_progress = self.task_manager.add_task(image["info"]["location"], EAD.encrypt, (image["info"]["location"],))
				temp_progresses.append(task_progress)
			task_progress = self.task_manager.add_task(image["info"]["location"], self.dh.add_images, ([image["info"]],))
			task_progresses.append({"info": image["info"], "task_progress": temp_progresses})
		print("Completed!")
		return task_progresses

	# 创建album，详见函数
	def create_album(self, album={"name": "", "by": "", "tag": "", "image_list": "", "secret": ""}):
		self.dh.add_albums([album])
		return

	# 不要用
	def new_kind(self, kinds, image_id):
		self.dh.add_kinds(kinds, image_id)
		return

	# 创建新的用户，用于注册，详见函数
	def create_new_user(self, info={"basic": {"name": "", "email": ""}, "password": "", "permission": ""}):
		task_progresses = []
		task_progress = self.task_manager.add_task(info["basic"]["name"], self.hu.add_user, (info,))
		task_progresses.append({"info": info, "task_progress": task_progress})
		return task_progresses

	# 删除破损的images，详见main.py的说明，慎用
	def remove_corrupted_images(self):
		ids = detect_corrupted_images()
		targets = []
		targets_another = []
		for id in ids:
			targets.append("static/images/"+str(id))
			target_another = self.dh.get_image_by_location("static/images/"+str(id))["_id"]
			targets_another += target_another
		self.hi.remove_images(targets)
		self.dh.remove_images(targets_another)



# 更新数据
class update_data():
	def __init__(self):
		self.dh = dh()
		self.hi = hi()
		self.hu = hu()

	# 登录，详见函数
	def login(self, info={"name": "", "password": ""}):
		status, code = self.hu.login(info)
		return status, code

	# 检查是否已登录，详见函数
	def is_login(self, info={"name": "", "password": ""}):
		return self.hu.logined(info)

	# 登出，详见函数
	def logout(self, info={"name": "", "password": ""}):
		self.hu.logout(info)

	# 更新image信息，用于处理添加label、kind，移除label、kind，详见函数
	def update_image_info(self, info={"image_id": "", "info": {"lable": [], "kind": []}}):
		self.dh.update_infos_on_image(info["info"], info["image_id"])

	# 标记image为secret，详见函数
	def mark_image_secret(self, info={"by": "", "image_id": ""}):
		EAD = ead(info["by"])
		self.dh.mark_image_as_secret([info["image_id"]], "True")
		EAD.encrypt(self.dh.get_image_by_id(info["image_id"])["location"])

	# 标记image为unsecret，详见函数
	def mark_image_unsecret(self, info={"by": "", "image_id": ""}):
		EAD = ead(info["by"])
		EAD.decrypt(self.dh.get_image_by_id(info["image_id"])["location"])
		self.dh.mark_image_as_secret([info["image_id"]], "False")

	# 标记album为secret，详见函数
	def mark_album_secret(self, info={"album_id": ""}):
		self.dh.mark_album_as_secret([info["album_id"]], "True")

	# 标记album为secret，详见函数
	def mark_album_unsecret(self, info={"album_id": ""}):
		self.dh.mark_album_as_secret([info["album_id"]], "False")

	# 更新album信息，用于处理添加tag，移除tag，详见函数
	def update_album_info(self, info={"album_id": "", "info": {"tag": []}}):
		self.dh.update_infos_on_album(info["info"], info["album_id"])

	# 添加新的comment到image，详见函数
	def new_comment(self, comment={"image_id": "", "info": {"by": "", "content": ""}}):
		info = self.hi.get_image_info(comment["image_id"])
		info["comments"].append(comment["info"])
		self.hi.update_image_info(comment["image_id"], info)

	# 添加image到album，详见函数
	def add_images_to_album(self, info={"image_ids": [], "album_id": ""}):
		for image_id in info["image_ids"]:
			self.dh.add_image_to_album(image_id, info["album_id"])



# 移除数据
class remove_data():
	def __init__(self):
		self.dh = dh()
		self.hi = hi()
		self.hu = hu()

	# 移除image，image要有"_id"，即ObjectId
	def remove_image(self, image={"_id": ""}):
		location = self.dh.get_image_by_id(image["_id"])["location"]
		self.dh.remove_images([image["_id"]])
		self.hi.remove_image(location)

	# 移除album，详见函数
	def remove_album(self, album={"_id"}):
		self.dh.remove_albums([album["_id"]])

	# 移除用户，user为用户名
	def remove_user(self, user):
		self.hu.remove_user(user)

	# 移除images从album，详见函数
	def remove_images_from_album(self, info={"image_ids": [], "album_id": ""}):
		for image_id in info["image_ids"]:
			self.dh.remove_image_from_album(image_id, info["album_id"])



if __name__ == "__main__":
	cd = collect_data()
	# cd.search({"name": ["first image", "first album"], "label": ["first"], "tag": ["first"], "secret": "False", "kind": [], "album": [], "user": [], "date": [], "last_edit_date": []})
	# cd.search({"name": [], "label": [], "tag": [], "secret": "False", "kind": [], "album": [ObjectId("5db1a110a57efe14687f4296")], "user": [], "date": [], "last_edit_date": []})
	# cd.search({"name": [], "label": [], "tag": [], "kind": [], "album": [], "user": ["anzhe"], "date": [], "last_edit_date": []})
	# print()
	# print()
	# print()
	# cd.search({"user": ["anzhe"], "secret": "True"})
	# cd.get_kinds()
	# cd.get_users()
	# cd.get_label_and_tags()
	# cd.get_albums()
	# cd.get_albums()