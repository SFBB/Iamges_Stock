#!/usr/bin/env python3

# 用于提供基础的收集数据库信息的功能

import json as JSON
from database_handle import database_handle as dh
from handle_image import handle_images as hi
from handle_user import handle_users as hu
from encrypt_and_decrypt import encrypt_and_decrypt as ead
from bson.objectid import ObjectId
# import copy
from threading import Thread as Process
from threading import Lock



class progress():
	def __init__(self):
		self.value = 0

	def set_progress(self, value):
		if value > 100:
			value = 100
		elif value < 0:
			value = 0
		self.value = value

	def get_progress(self):
		return self.value



class task_manager():
	def __init__(self):
		self.tasks = {}
		self.lock = Lock()

	def check(self):
		self.lock.acquire()
		delete_locations = []
		delete_tasks = []
		for location in self.tasks:
			for task_index in range(len(self.tasks[location]["tasks"])):
				if self.tasks[location]["progress"][task_index].get_progress() == 100:
					delete_tasks.append(task_index)
			for index in delete_tasks:
				del self.tasks[location]["tasks"][index]
				del self.tasks[location]["progress"][index]
			if len(self.tasks[location]["tasks"]) == 0:
				delete_locations.append(location)
		for location in delete_locations:
			del self.tasks[location]
		self.lock.release()
		print(self.tasks)

	def add_task(self, location, func, args):
		self.lock.acquire()
		task_progress = progress()
		if location not in self.tasks.keys():
			lock = Lock()
			self.tasks[location] = {"tasks": [Process(target=self.do_task, args=(lock, func, args, task_progress))], "progress": [task_progress], "lock": lock}
		else:
			self.tasks[location]["tasks"].append(Process(target=self.do_task, args=(self.tasks[location]["lock"], func, args, task_progress)))
			self.tasks[location]["progress"].append(task_progress)
		self.do_tasks(location)
		self.lock.release()
		return task_progress

	def do_tasks(self, location):
		print("location:", location)
		for task_index in range(len(self.tasks[location]["tasks"])):
			if self.tasks[location]["progress"][task_index].get_progress() == 100 or self.tasks[location]["tasks"][task_index].is_alive():
				continue
			else:
				self.tasks[location]["tasks"][task_index].start()

	def do_task(self, lock, func, args, task_progress):
		lock.acquire()
		try:
			func(*args)
			self.check()
			task_progress.set_progress(100)
		finally:
			lock.release()



class collect_data():
	def __init__(self, mode="normal"):
		self.mode = mode
		self.dh = dh()
		self.hu = hu()

	def search(self, info):
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
		return result

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

	def get_kinds(self):
		result = self.dh.get_kinds()
		return result

	def get_label_and_tags(self):
		result = {"labels": [], "tags": []}
		result["labels"] = self.dh.get_labels()
		result["tags"] = self.dh.get_tags()
		return result

	def get_albums(self):
		result = self.dh.get_image_list()
		return result

	def get_users(self):
		result = self.dh.get_user_list()
		return result

	def get_user(self, user):
		return self.hu.get_user_info(user)

	def get_images(self, info):
		result = self.dh.get_album_list()
		return result



class create_data():
	def __init__(self, mode="normal"):
		self.mode = mode
		self.dh = dh()
		self.hi = hi()
		self.hu = hu()
		self.task_manager = task_manager()

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
			task_progresses.append({"info": image["info"], "task_progress": temp_progresses})
		self.dh.add_images(image_info_list)
		return task_progresses

	def create_album(self, album={"name": "", "by": "", "tag": "", "image_list": "", "secret": ""}):
		self.dh.add_albums([album])
		return

	def new_kind(self, kinds, image_id):
		self.dh.add_kinds(kinds, image_id)
		return

	def creat_new_user(self, info={"basic": {"name": "", "email": ""}, "password": "", "permission": ""}):
		self.hu.add_user(info)
		return



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