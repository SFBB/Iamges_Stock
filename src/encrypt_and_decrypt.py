#!/usr/bin/env python3

# 用于提供根据用户id来进行对单个文件的加密于解密功能

import Crypto
from Crypto.PublicKey import RSA
from Crypto import Random
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
import ast
import base64
import os
import sys


class encrypt_and_decrypt():
	def __init__(self, user_id):
		self.user_id = user_id
		if self.has_key():
			self.key = self.get_key()
		else:
			self.key = self.gen_new_key()

	def encrypt(self, location):
		with open(location+".png", "rb") as file:
			content = file.read()
		with open(location+".thumbnail.png", "rb") as file:
			content_thumbnail = file.read()
		with open(location+".json", "rb") as file:
			content_json = file.read()
		session_key = get_random_bytes(32)

		cipher_rsa = PKCS1_OAEP.new(self.key)
		enc_session_key = cipher_rsa.encrypt(session_key)

		cipher_aes = AES.new(session_key, AES.MODE_EAX)
		ciphertext, tag = cipher_aes.encrypt_and_digest(content)
		cipher_aes_thumbnail = AES.new(session_key, AES.MODE_EAX)
		ciphertext_thumbnail, tag_thumbnail = cipher_aes_thumbnail.encrypt_and_digest(content_thumbnail)
		cipher_aes_json = AES.new(session_key, AES.MODE_EAX)
		ciphertext_json, tag_json = cipher_aes_json.encrypt_and_digest(content_json)

		result = [enc_session_key, cipher_aes.nonce, tag, ciphertext]
		result_thumbnail = [enc_session_key, cipher_aes_thumbnail.nonce, tag_thumbnail, ciphertext_thumbnail]
		result_json = [enc_session_key, cipher_aes_json.nonce, tag_json, ciphertext_json]
		all = bytes(0)
		for i in result:
			all += i
		all = base64.b64encode(all)
		result = [all]
		all = bytes(0)
		for i in result_thumbnail:
			all += i
		all = base64.b64encode(all)
		result_thumbnail = [all]
		all = bytes(0)
		for i in result_json:
			all += i
		all = base64.b64encode(all)
		result_json = [all]
		with open(location+".png.encrypt", "wb") as file:
			for i in result:
				file.write(i)
		result = os.popen(location+".png")
		with open("rm "+location+".thumbnail.png.encrypt", "wb") as file:
			for i in result_thumbnail:
				file.write(i)
		result = os.popen("rm "+location+".thumbnail.png")
		with open(location+".json.encrypt", "wb") as file:
			for i in result_json:
				file.write(i)
		result = os.popen("rm "+location+".json")

	def decrypt(self, location):
		with open(location+".png.encrypt", "rb") as file:
			content = file.read()
		with open(location+".thumbnail.png.encrypt", "rb") as file:
			content_thumbnail = file.read()
		with open(location+".json.encrypt", "rb") as file:
			content_json = file.read()
		content = base64.b64decode(content)
		content_thumbnail = base64.b64decode(content_thumbnail)
		content_json = base64.b64decode(content_json)

		key_size = self.key.size_in_bytes()
		enc_session_key = content[:key_size]
		content = content[key_size:]
		nonce = content[:16]
		content = content[16:]
		tag = content[:16]
		content = content[16:]
		ciphertext = content

		key_size_thumbnail = self.key.size_in_bytes()
		enc_session_key_thumbnail = content_thumbnail[:key_size_thumbnail]
		content_thumbnail = content_thumbnail[key_size_thumbnail:]
		nonce_thumbnail = content_thumbnail[:16]
		content_thumbnail = content_thumbnail[16:]
		tag_thumbnail = content_thumbnail[:16]
		content_thumbnail = content_thumbnail[16:]
		ciphertext_thumbnail = content_thumbnail

		key_size_json = self.key.size_in_bytes()
		enc_session_key_json = content_json[:key_size_json]
		content_json = content_json[key_size_json:]
		nonce_json = content_json[:16]
		content_json = content_json[16:]
		tag_json = content_json[:16]
		content_json = content_json[16:]
		ciphertext_json = content_json

		cipher_rsa = PKCS1_OAEP.new(self.key)
		session_key = cipher_rsa.decrypt(enc_session_key)
		session_key_thumbnail = cipher_rsa.decrypt(enc_session_key_thumbnail)
		session_key_json = cipher_rsa.decrypt(enc_session_key_json)

		cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
		result = cipher_aes.decrypt_and_verify(content, tag)
		cipher_aes_thumbnail = AES.new(session_key_thumbnail, AES.MODE_EAX, nonce_thumbnail)
		result_thumbnail = cipher_aes_thumbnail.decrypt_and_verify(content_thumbnail, tag_thumbnail)
		cipher_aes_json = AES.new(session_key_json, AES.MODE_EAX, nonce_json)
		result_json = cipher_aes_json.decrypt_and_verify(content_json, tag_json)
		with open(location+".png", "wb") as file:
			file.write(result)
		result = os.popen("rm "+location+".png.encrypt")
		with open(location+".thumbnail.png", "wb") as file:
			file.write(result_thumbnail)
		result = os.popen("rm "+location+".thumbnail.png.encrypt")
		with open(location+".json", "wb") as file:
			file.write(result_json)
		result = os.popen("rm "+location+".json.encrypt")

	def has_key(self):
		result = os.popen("ls static/users/"+str(self.user_id)+".key > /dev/null 2>&1; echo $?").read().split("\n")[0]
		if result == "0":
			return True
		else:
			return False

	def get_key(self):
		try:
			key_file = open("static/users/"+str(self.user_id)+".key", "rb")
		except:
			print("No Key!")
			return None
		key_info = key_file.read()
		key_file.close()
		key = RSA.importKey(key_info)
		return key

	def gen_new_key(self):
		random_generator = Random.new().read
		key = RSA.generate(4096, random_generator) #generate pub and priv key

		key_file = open("static/users/"+str(self.user_id)+".key", "wb")
		key_file.write(key.exportKey())
		key_file.close()

		key_file = open("static/users/"+str(self.user_id)+".publickey", "wb")
		key_file.write(key.publickey().exportKey())
		key_file.close()
		return key.exportKey()

	def update_key(self):
		return

class encrypt_and_decrypt_for_users():
	def __init__(self):
		if self.has_key():
			self.key = self.get_key()
		else:
			self.key = self.gen_new_key()

	def encrypt(self, user):
		with open("static/users/"+str(user)+".json", "rb") as file:
			content = file.read()
		with open("static/users/"+str(user)+".key", "rb") as file:
			content_thumbnail = file.read()
		with open("static/users/"+str(user)+".publickey", "rb") as file:
			content_json = file.read()
		session_key = get_random_bytes(32)

		cipher_rsa = PKCS1_OAEP.new(self.key)
		enc_session_key = cipher_rsa.encrypt(session_key)

		cipher_aes = AES.new(session_key, AES.MODE_EAX)
		ciphertext, tag = cipher_aes.encrypt_and_digest(content)
		cipher_aes_thumbnail = AES.new(session_key, AES.MODE_EAX)
		ciphertext_thumbnail, tag_thumbnail = cipher_aes_thumbnail.encrypt_and_digest(content_thumbnail)
		cipher_aes_json = AES.new(session_key, AES.MODE_EAX)
		ciphertext_json, tag_json = cipher_aes_json.encrypt_and_digest(content_json)

		result = [enc_session_key, cipher_aes.nonce, tag, ciphertext]
		result_thumbnail = [enc_session_key, cipher_aes_thumbnail.nonce, tag_thumbnail, ciphertext_thumbnail]
		result_json = [enc_session_key, cipher_aes_json.nonce, tag_json, ciphertext_json]
		all = bytes(0)
		for i in result:
			all += i
		all = base64.b64encode(all)
		result = [all]
		all = bytes(0)
		for i in result_thumbnail:
			all += i
		all = base64.b64encode(all)
		result_thumbnail = [all]
		all = bytes(0)
		for i in result_json:
			all += i
		all = base64.b64encode(all)
		result_json = [all]
		with open("static/users/"+str(user)+".json.encrypt", "wb") as file:
			for i in result:
				file.write(i)
		result = os.popen("rm static/users/"+str(user)+".json")
		with open("static/users/"+str(user)+".key.encrypt", "wb") as file:
			for i in result_thumbnail:
				file.write(i)
		result = os.popen("rm static/users/"+str(user)+".key")
		with open("static/users/"+str(user)+".publickey.encrypt", "wb") as file:
			for i in result_json:
				file.write(i)
		result = os.popen("rm static/users/"+str(user)+".publickey")

	def decrypt(self, user):
		with open("static/users/"+str(user)+".json.encrypt", "rb") as file:
			content = file.read()
		with open("static/users/"+str(user)+".key.encrypt", "rb") as file:
			content_thumbnail = file.read()
		with open("static/users/"+str(user)+".publickey.encrypt", "rb") as file:
			content_json = file.read()
		content = base64.b64decode(content)
		content_thumbnail = base64.b64decode(content_thumbnail)
		content_json = base64.b64decode(content_json)

		key_size = self.key.size_in_bytes()
		enc_session_key = content[:key_size]
		content = content[key_size:]
		nonce = content[:16]
		content = content[16:]
		tag = content[:16]
		content = content[16:]
		ciphertext = content

		key_size_thumbnail = self.key.size_in_bytes()
		enc_session_key_thumbnail = content_thumbnail[:key_size_thumbnail]
		content_thumbnail = content_thumbnail[key_size_thumbnail:]
		nonce_thumbnail = content_thumbnail[:16]
		content_thumbnail = content_thumbnail[16:]
		tag_thumbnail = content_thumbnail[:16]
		content_thumbnail = content_thumbnail[16:]
		ciphertext_thumbnail = content_thumbnail

		key_size_json = self.key.size_in_bytes()
		enc_session_key_json = content_json[:key_size_json]
		content_json = content_json[key_size_json:]
		nonce_json = content_json[:16]
		content_json = content_json[16:]
		tag_json = content_json[:16]
		content_json = content_json[16:]
		ciphertext_json = content_json

		cipher_rsa = PKCS1_OAEP.new(self.key)
		session_key = cipher_rsa.decrypt(enc_session_key)
		session_key_thumbnail = cipher_rsa.decrypt(enc_session_key_thumbnail)
		session_key_json = cipher_rsa.decrypt(enc_session_key_json)

		cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
		result = cipher_aes.decrypt_and_verify(content, tag)
		cipher_aes_thumbnail = AES.new(session_key_thumbnail, AES.MODE_EAX, nonce_thumbnail)
		result_thumbnail = cipher_aes_thumbnail.decrypt_and_verify(content_thumbnail, tag_thumbnail)
		cipher_aes_json = AES.new(session_key_json, AES.MODE_EAX, nonce_json)
		result_json = cipher_aes_json.decrypt_and_verify(content_json, tag_json)
		with open("static/users/"+str(user)+".json", "wb") as file:
			file.write(result)
		result = os.popen("rm static/users/"+str(user)+".json.encrypt")
		with open("static/users/"+str(user)+".key", "wb") as file:
			file.write(result_thumbnail)
		result = os.popen("rm static/users/"+str(user)+".key.encrypt")
		with open("static/users/"+str(user)+".publickey", "wb") as file:
			file.write(result_json)
		result = os.popen("rm static/users/"+str(user)+".publickey.encrypt")

	def has_key(self):
		result = os.popen("ls static/keys/users.key > /dev/null 2>&1; echo $?").read().split("\n")[0]
		if result == "0":
			return True
		else:
			return False

	def gen_new_key(self):
		random_generator = Random.new().read
		key = RSA.generate(4096, random_generator) #generate pub and priv key

		key_file = open("static/keys/users.key", "wb")
		key_file.write(key.exportKey())
		key_file.close()

		key_file = open("static/keys/users.publickey", "wb")
		key_file.write(key.publickey().exportKey())
		key_file.close()
		return key.exportKey()

	def get_key(self):
		try:
			key_file = open("static/keys/users.key", "rb")
		except:
			print("No Key!")
			return None
		key_info = key_file.read()
		key_file.close()
		key = RSA.importKey(key_info)
		return key


if __name__ == "__main__":
	ed = encrypt_and_decrypt("a")
	ed.encrypt("a")
	# ed.encrypt(2)
	# ed.encrypt(4)
	# ed.encrypt(7)
	# ed.encrypt(8)
	# ed.encrypt(9)
	ed.decrypt("a")
	# ed.decrypt(2)
	# ed.decrypt(4)
	# ed.decrypt(7)
	# ed.decrypt(8)
	# ed.decrypt(9)