#!/usr/bin/env python3

# 用于处理用户信息及操作

import os
import sys
import json as JSON
from database_handle import database_handle as dh
from encrypt_and_decrypt import encrypt_and_decrypt_for_users as eadfu


class handle_users():
	def __init__(self):
		self.dh = dh()
		self.eadfu = eadfu()

	def add_user(self, info={"basic": {"name": "", "email": ""}, "password": "", "permission": ""}):
		if "permission" not in info.keys():
			info["permission"] = "Normal"
		self.dh.add_users([{"info": info["basic"], "permission": info["permission"]}])
		with open("static/users/"+info["basic"]["name"]+".json", "w") as file:
			info_json = JSON.dumps(info)
			JSON.dump(info_json, file)
		self.eadfu.encrypt(info["basic"]["name"])
		return

	def remove_user(self, user):
		self.dh.remove_user(user)
		result = os.popen("rm static/users/"+str(user)+"*").read()

	def login(self, info={"name": "", "password": ""}):
		try:
			self.eadfu.decrypt(info["name"])
		except:
			return False, "No Such User!"
		with open("static/users/"+info["name"]+".json") as file:
			data = JSON.load(file)
		self.eadfu.encrypt(info["name"])
		if info["password"] == data["password"]:
			del data["password"]
			return True, data
		else:
			return False, "Wrong Password!"

	def change_password(self, info={"name": "", "password": "", "new_password": ""}):
		try:
			self.eadfu.decrypt(info["name"])
		except:
			return False, "No Such User!"
		with open("static/users/"+info["name"]+".json") as file:
			data = JSON.load(file)
		if info["password"] == data["password"]:
			data["password"] = info["new_password"]
			with open("static/users/"+info["name"]+".json", "w") as file:
				JSON.dump(data, file)
			self.eadfu.encrypt(info["name"])
			del data["password"]
			return True, data
		else:
			self.eadfu.encrypt(info["name"])
			return False, "Wrong Password!"

	def change_email(self, info={"name": "", "email": ""}):
		try:
			self.eadfu.decrypt(info["name"])
		except:
			return False, "No Such User!"
		with open("static/users/"+info["name"]+".json") as file:
			data = JSON.load(file)
		data["email"] = info["email"]
		with open("static/users/"+info["name"]+".json", "w") as file:
			JSON.dump(data, file)
		self.eadfu.encrypt(info["name"])
		del data["password"]
		return True, data

	def get_user_info(self, user):
		try:
			self.eadfu.decrypt(user)
		except:
			return False, "No Such User!"
		with open("static/users/"+user+".json") as file:
			data = JSON.load(file)
		self.eadfu.encrypt(user)
		del data["password"]
		return True, data


if __name__ == "__main__":
	hu = handle_users()
	hu.add_user({"basic": {"name": "a", "email": "a@a.a"}, "password": "aaaaaaaaa"})