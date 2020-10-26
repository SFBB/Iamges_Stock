#!/usr/bin/env python3

# 用于提供数据库的基本的操作，如"mark as secret"等

from pymongo import MongoClient
from bson.objectid import ObjectId
# pprint library is used to make the output look more pretty
from pprint import pprint
# connect to MongoDB, change the << MONGODB URL >> to reflect your own connection string
from datetime import datetime
import json as JSON
from handle_image import handle_images as hi



class JSONEncoder(JSON.JSONEncoder):
	def default(self, o):
		if isinstance(o, ObjectId):
			return str(o)
		return JSON.JSONEncoder.default(o)



def between(date, date_target):
	date_start = int(date[0])
	date_end = int(date[1])
	date_target = int(date_target)
	if date_target >= date_start and date_target <= date_end:
		return True
	else:
		return False

def get_date():
	result = ""
	year = "0000"
	month = "00"
	day = "00"
	hour = "00"
	minute = "00"
	second = "00"
	now = datetime.now()
	result += year[:4-len(str(now.year))]+str(now.year)
	result += month[:2-len(str(now.month))]+str(now.month)
	result += day[:2-len(str(now.day))]+str(now.day)
	result += hour[:2-len(str(now.hour))]+str(now.hour)
	result += minute[:2-len(str(now.minute))]+str(now.minute)
	result += second[:2-len(str(now.second))]+str(now.second)
	return result

class database_handle():
	def __init__(self):
		self.client = MongoClient(port=27017)
		self.db = self.client.dam_database
		self.hi = hi()

	def add_users(self, user_info_list):
		for user_info in user_info_list:
			user_info["info"]["date"] = get_date()
			result = self.db.users.find({"name": user_info["info"]["name"]})
			if result.count() != 0:
				continue
			# user_info["location"] = "static/users/"+user_info["name"]
			self.db.users.insert_one(user_info["info"])
			self.db.permissions.update_one({"name": user_info["permission"]}, {"$push": {"user_list": user_info["info"]["name"]}})

	def add_images(self, image_info_list):
		result = []
		for image_info in image_info_list:
			if "secret" not in image_info:
				image_info["secret"] = "False"
			image_info["date"] = get_date()
			image_info["last_edit_time"] = get_date()
			self.db.images.insert_one(image_info)
			result.append(image_info)
			self.add_labels(image_info["label"], image_info["_id"])
			self.add_kinds(image_info["kind"], image_info["_id"])
		return JSON.loads(JSONEncoder().encode(result))

	def add_kinds(self, kinds, image_id):
		for kind in kinds:
			result = self.db.kinds.find({"name": kind})
			if result.count() == 0:
				self.db.kinds.insert_one({"name": kind, "image_list": []})
			self.db.kinds.update_one({"name": kind}, {"$push": {"image_list": ObjectId(image_id)}})
		self.db.images.update_one({"_id": ObjectId(image_id)}, {"$set": {"last_edit_time": get_date()}})

	def add_albums(self, album_info_list):
		result = []
		for album_info in album_info_list:
			if "secret" not in album_info:
				album_info["secret"] = "False"
			album_info["date"] = get_date()
			album_info["last_edit_time"] = get_date()
			self.db.albums.insert_one(album_info)
			result.append(album_info)
			self.add_tags(album_info["tag"], album_info["_id"])
		return JSON.loads(JSONEncoder().encode(result))

	def add_labels(self, labels, image_id):
		for label in labels:
			result = self.db.labels.find({"name": label})
			if result.count() == 0:
				self.db.labels.insert_one({"name": label, "image_list": []})
			self.db.labels.update_one({"name": label}, {"$push": {"image_list": ObjectId(image_id)}})
		self.db.images.update_one({"_id": ObjectId(image_id)}, {"$set": {"last_edit_time": get_date()}})

	def add_tags(self, tags, album_id):
		for tag in tags:
			result = self.db.tags.find({"name": tag})
			if result.count() == 0:
				self.db.tags.insert_one({"name": tag, "album_list": []})
			self.db.tags.update_one({"name": tag}, {"$push": {"album_list": ObjectId(album_id)}})
		self.db.albums.update_one({"_id": ObjectId(album_id)}, {"$set": {"last_edit_time": get_date()}})

	def add_image_to_album(self, image_id, album_id):
		self.db.albums.update_one({"_id": ObjectId(album_id)}, {"$push": {"image_list": ObjectId(image_id)}})
		self.db.albums.update_one({"_id": ObjectId(album_id)}, {"$set": {"last_edit_time": get_date()}})

	def mark_image_as_secret(self, image_ids, status):
		for image_id in image_ids:
			self.db.images.update_one({"_id": ObjectId(image_id)}, {"$set": {"secret": status}})
			self.db.images.update_one({"_id": ObjectId(image_id)}, {"$set": {"last_edit_time": get_date()}})

	def mark_album_as_secret(self, album_ids, status):
		for album_id in album_ids:
			self.db.albums.update_one({"_id": ObjectId(album_id)}, {"$set": {"secret": status}})
			self.db.albums.update_one({"_id": ObjectId(album_id)}, {"$set": {"last_edit_time": get_date()}})

	def update_infos_on_image(self, info, image_id):
		for i in info:
			if i == "label":
				origin = self.db.images.find({"_id": ObjectId(image_id)})[0]["label"]
				for ii in info["label"]:
					if ii not in origin:
						self.add_image_to_label(image_id, ii)
				for ii in origin:
					if ii not in info["label"]:
						self.remove_image_from_label(image_id, ii)
			if i == "kind":
				origin = self.db.images.find({"_id": ObjectId(image_id)})[0]["kind"]
				for ii in info["kind"]:
					if ii not in origin:
						self.add_image_to_kind(image_id, ii)
				for ii in origin:
					if ii not in info["kind"]:
						self.remove_image_from_kind(image_id, ii)
			self.db.images.update_one({"_id": ObjectId(image_id)}, {"$set": {i: info[i]}})
		self.db.images.update_one({"_id": ObjectId(image_id)}, {"$set": {"last_edit_time": get_date()}})

	def update_infos_on_album(self, info, album_id):
		for i in info:
			if i == "tag":
				origin = self.db.images.find({"_id": ObjectId(album_id)})[0]["tag"]
				for ii in info["tag"]:
					if ii not in origin:
						self.add_album_to_tag(album_id, ii)
				for ii in origin:
					if ii not in info["tag"]:
						self.remove_album_from_tag(album_id, ii)
			self.db.images.update_one({"_id": ObjectId(album_id)}, {"$set": {i: info[i]}})
		self.db.images.update_one({"_id": ObjectId(album_id)}, {"$set": {"last_edit_time": get_date()}})

	def add_image_to_label(self, image_id, label):
		image_list = self.db.labels.find({"name": label})[0]["image_list"]
		if image_id in image_list:
			return
		else:
			self.db.labels.update_one({"name": label}, {"$push": {"image_list": ObjectId(image_id)}})

	def add_image_to_kind(self, image_id, kind):
		image_list = self.db.kinds.find({"name": kind})[0]["image_list"]
		if image_id in image_list:
			return
		else:
			self.db.kinds.update_one({"name": kind}, {"$push": {"image_list": ObjectId(image_id)}})

	def add_album_to_tag(self, album_id, tag):
		album_list = self.db.tags.find({"name": tag})[0]["album_list"]
		if album_id in album_list:
			return
		else:
			self.db.tags.update_one({"name": tag}, {"$push": {"album_list": ObjectId(album_id)}})

	def remove_image_from_label(self, image_id, label):
		image_list = self.db.labels.find({"name": label})[0]["image_list"]
		if image_id in image_list:
			self.db.labels.update_one({"name": label}, {"$pull": {"image_list": ObjectId(image_id)}})
		else:
			return

	def remove_image_from_kind(self, image_id, kind):
		image_list = self.db.kinds.find({"name": kind})[0]["image_list"]
		if image_id in image_list:
			self.db.kinds.update_one({"name": kind}, {"$pull": {"image_list": ObjectId(image_id)}})
		else:
			return

	def remove_album_from_tag(self, album_id, tag):
		album_list = self.db.tags.find({"name": tag})[0]["album_list"]
		if album_id in album_list:
			self.db.tags.update_one({"name": tag}, {"$pull": {"album_list": ObjectId(album_id)}})
		else:
			return

	def remove_image_from_album(self, image_id, album_id):
		image_list = self.db.albums.find({"_id": ObjectId(album_id)})[0]["image_list"]
		if image_id in image_list:
			self.db.albums.update_one({"_id": ObjectId(album_id)}, {"$pull": {"image_list": ObjectId(image_id)}})
		else:
			return

	def remove_images(self, image_ids):
		for image_id in image_ids:
			image_info = self.db.images.find({"_id": ObjectId(image_id)})[0]
			for label in image_info["label"]:
				self.remove_image_from_label(image_id, label)
			for kind in image_info["kind"]:
				self.remove_album_from_tag(image_id, kind)
			albums = self.db.albums.find({})
			for album in albums:
				self.remove_image_from_album(image_id, album["_id"])
			self.hi.remove_image(image_info["location"])
			self.db.images.remove({"_id": ObjectId(image_id)})

	def remove_albums(self, album_ids):
		for album_id in album_ids:
			album_info = self.db.albums.find({"_id": ObjectId(album_id)})[0]
			for tag in album_info["tag"]:
				self.remove_album_from_tag(album_id, tag)
			self.db.albums.remove({"_id": ObjectId(album_id)})

	def remove_user(self, user):
		self.db.users.remove({"name": user})
		image_list = self.get_images_by_user(user)
		for image in image_list:
			self.hi.remove_image(image["location"])
			self.db.remove({"_id": ObjectId(image["_id"])})
		album_list = self.get_albums_by_user(user)
		for album in album_list:
			self.db.remove({"_id": ObjectId(album["_id"])})

	def get_image_by_id(self, id):
		result = self.db.images.find({"_id": ObjectId(id)})[0]
		try:
			with open(result["location"]+".json") as file:
				data = JSON.load(file)
		except:
			data = {"title": "encrypted", "description": "encrypted", "comments": "encrypted"}
		result["data"] = data
		return JSON.loads(JSONEncoder().encode(result))

	def get_images_by_name(self, name):
		result = []
		result_temp = self.db.images.find({"name": name})
		for image in result_temp:
			try:
				with open(image["location"]+".json") as file:
					data = JSON.load(file)
			except:
				data = {"title": "encrypted", "description": "encrypted", "comments": "encrypted"}
			image["data"] = data
			result.append(image)
		return JSON.loads(JSONEncoder().encode(result))

	def get_images_by_label(self, label):
		result = []
		result_temp = self.db.images.find({"label": label})
		for image in result_temp:
			try:
				with open(image["location"]+".json") as file:
					data = JSON.load(file)
			except:
				data = {"title": "encrypted", "description": "encrypted", "comments": "encrypted"}
			image["data"] = data
			result.append(image)
		return JSON.loads(JSONEncoder().encode(result))

	def get_images_by_kind(self, kind):
		result = []
		result_temp = self.db.images.find({"kind": kind})
		for image in result_temp:
			try:
				with open(image["location"]+".json") as file:
					data = JSON.load(file)
			except:
				data = {"title": "encrypted", "description": "encrypted", "comments": "encrypted"}
			image["data"] = data
			result.append(image)
		return JSON.loads(JSONEncoder().encode(result))

	def get_images_by_user(self, user):
		result = []
		result_temp = self.db.images.find({"by": user})
		for image in result_temp:
			try:
				with open(image["location"]+".json") as file:
					data = JSON.load(file)
			except:
				data = {"title": "encrypted", "description": "encrypted", "comments": "encrypted"}
			image["data"] = data
			result.append(image)
		return JSON.loads(JSONEncoder().encode(result))

	def get_images_by_album(self, album):
		result = []
		result_temp = self.db.albums.find({"_id": ObjectId(album)}, {"_id": 0, "image_list": 1})[0]
		for image in result_temp["image_list"]:
			image = self.get_image_by_id(image)
			try:
				with open(image["location"]+".json") as file:
					data = JSON.load(file)
			except:
				data = {"title": "encrypted", "description": "encrypted", "comments": "encrypted"}
			image["data"] = data
			result.append(image)
		return JSON.loads(JSONEncoder().encode(result))

	def get_images_by_date(self, date):
		result = []
		result_temp = self.db.images.find()
		for image in result_temp:
			if between(date, image["date"]):
				try:
					with open(image["location"]+".json") as file:
						data = JSON.load(file)
				except:
					data = {"title": "encrypted", "description": "encrypted", "comments": "encrypted"}
				image["data"] = data
				result.append(image)
		return JSON.loads(JSONEncoder().encode(result))

	def get_image_by_location(self, location):
		result = []
		result_temp = self.db.images.find({"location": location}, {"_id": 1})
		for i in result_temp:
			result.append(i["_id"])
		return JSON.loads(JSONEncoder().encode(result))

	def get_images_by_last_edit_time(self, last_edit_time):
		result = []
		result_temp = self.db.images.find()
		for image in result_temp:
			if between(last_edit_time, image["last_edit_time"]):
				try:
					with open(image["location"]+".json") as file:
						data = JSON.load(file)
				except:
					data = {"title": "encrypted", "description": "encrypted", "comments": "encrypted"}
				image["data"] = data
				result.append(image)
		return JSON.loads(JSONEncoder().encode(result))

	def get_album_by_id(self, id):
		result = self.db.albums.find({"_id": ObjectId(id)})[0]
		return JSON.loads(JSONEncoder().encode(result))

	def get_albums_by_name(self, name):
		result = []
		result_temp = self.db.albums.find({"name": name})
		for album in result_temp:
			result.append(album)
		return JSON.loads(JSONEncoder().encode(result))

	def get_albums_by_tag(self, tag):
		result = []
		result_temp = self.db.albums.find({"tag": tag})
		for album in result_temp:
			result.append(album)
		return JSON.loads(JSONEncoder().encode(result))

	def get_albums_by_user(self, user):
		result = []
		result_temp = self.db.albums.find({"by": user})
		for album in result_temp:
			result.append(album)
		return JSON.loads(JSONEncoder().encode(result))

	def get_albums_by_date(self, date):
		result = []
		result_temp = self.db.albums.find()
		for album in result_temp:
			if between(date, album["date"]):
				result.append(album)
		return JSON.loads(JSONEncoder().encode(result))

	def get_albums_by_last_edit_time(self, last_edit_time):
		result = []
		result_temp = self.db.albums.find()
		for album in result_temp:
			if between(last_edit_time, album["last_edit_time"]):
				result.append(album)
		return JSON.loads(JSONEncoder().encode(result))

	def get_user_list(self):
		result = []
		result_temp = self.db.users.find({})
		for user in result_temp:
			result.append(user)
		return JSON.loads(JSONEncoder().encode(result))

	def get_image_list(self):
		result = []
		result_temp = self.db.images.find({})
		for image in result_temp:
			result.append(image)
		return JSON.loads(JSONEncoder().encode(result))

	def get_album_list(self):
		result = []
		result_temp = self.db.albums.find({})
		for album in result_temp:
			result.append(album)
		return JSON.loads(JSONEncoder().encode(result))

	def get_kinds(self):
		print("get_kinds() here in database_handle.py!")
		result = []
		result_temp = self.db.kinds.find({})
		for kind in result_temp:
			result.append(kind)
		return JSON.loads(JSONEncoder().encode(result))

	def get_labels(self):
		result = []
		result_temp = self.db.labels.find({})
		for label in result_temp:
			result.append(label)
		return JSON.loads(JSONEncoder().encode(result))

	def get_tags(self):
		result = []
		result_temp = self.db.tags.find({})
		for tag in result_temp:
			result.append(tag)
		return JSON.loads(JSONEncoder().encode(result))


if __name__ == "__main__":
	dh = database_handle()
	# dh.add_users([{"info": {"name": "anzhe", "email": "3170101219@zju.edu.cn", "location": "here"}, "permission": "Normal"}, {"info": {"name": "an", "email": "3170101219@zju.edu.cn"}, "permission": "Normal"}])
	# result_images = dh.add_images([{"name": "first image", "secret": "False", "label": ["first", "image", "done"], "kind": ["nature", "flower"], "by": "anzhe", "location": "../static/images/0"}])
	# print(result_images)
	# result_albums = dh.add_albums([{"name": "first album", "secret": "False", "tag": ["first", "album", "done"], "by": "anzhe", "image_list": []}])
	# for i in result_images:
	# 	dh.add_image_to_album(i["_id"], result_albums[0]["_id"])
	# dh.remove_images([ObjectId('5da94c4ba57efe4a42b3bb3a'), ObjectId('5da958a3a57efe4dd7094e54'), ObjectId('5da958c2a57efe4de5004909'), ObjectId('5da958e5a57efe4e0101529c'), ObjectId('5da97224a57efe53ee6810c2'), ObjectId('5da97241a57efe53fddd9eb8'), ObjectId('5da97255a57efe54137f42b0'), ObjectId('5da97262a57efe54208aaabe'), ObjectId('5da97264a57efe542774d5ea'), ObjectId('5da97266a57efe542e67c6ea'), ObjectId('5da97dc0a57efe576305aac2'), ObjectId('5db19c2ba57efe1170bae5e7'), ObjectId('5db19c30a57efe117c8fb2bc'), ObjectId('5db19c32a57efe118318640a'), ObjectId('5db19c72a57efe119c383129'), ObjectId('5db1a110a57efe14687f4295')])
	dh.add_kinds(["test", "test another"], ObjectId("5db29ebca57efe594a7b6ed2"))