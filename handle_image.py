#!/usr/bin/env python3

# 用于处理用户上传的图片

import os
import sys
import json as JSON
from PIL import Image
import threading
from time import sleep



next_id = 0

def near_value(i):
	if i < 64:
		return 0
	elif i < 64*2:
		return 1
	elif i < 64*3:
		return 2
	else:
		return 3

def restore_value(i):
	return i*85

def decimal_to_binary(i):
    return '{0:08b}'.format(i)

def binary_to_decimal(i):
    return int(i, 2)

def get_value(i):
    return binary_to_decimal("00000000"[:8-len(i)]+i)

def merge(image_1, image_2):
	image_2 = image_2.resize(image_1.size)
	data_1 = image_1.load()
	data_2 = image_2.load()
	result = Image.new(image_1.mode, image_1.size)
	result_data = result.load()
	for i in range(image_1.size[0]):
		# sleep(0.001)
		for j in range(image_1.size[1]):
			r1, g1, b1, a1 = data_1[i, j]
			r2, g2, b2, a2 = data_2[i, j]
			result_data[i, j] = (binary_to_decimal(decimal_to_binary(r1)[:6]+decimal_to_binary(near_value(r2))[6:]),
								 binary_to_decimal(decimal_to_binary(g1)[:6]+decimal_to_binary(near_value(g2))[6:]),
								 binary_to_decimal(decimal_to_binary(b1)[:6]+decimal_to_binary(near_value(b2))[6:]),
								 binary_to_decimal(decimal_to_binary(a1)[:6]+decimal_to_binary(near_value(a2))[6:]))
	# print(data_1.size)
	return result

def unmerge(image, size=[1920, 1080]):
	data = image.load()
	result = Image.new(image.mode, image.size)
	result_data = result.load()
	for i in range(image.size[0]):
		for j in range(image.size[1]):
			r, g, b, a = data[i, j]
			result_data[i, j] = (restore_value(get_value(decimal_to_binary(r)[6:])),
								 restore_value(get_value(decimal_to_binary(g)[6:])),
								 restore_value(get_value(decimal_to_binary(b)[6:])),
								 restore_value(get_value(decimal_to_binary(a)[6:])))
	result = result.resize(size)
	return result

def do_merge(image_1, image_2, output_name):
	global next_id
	temp_id = next_id
	next_id += 1
	print("next id is "+str(temp_id))
	result = merge(image_1, image_2)
	print("Saving result ...")
	result.save(output_name)
	print("Successful!")


def detect_images():
	path = "static/images/"
	result = os.popen("ls "+path).read().split("\n")
	result = result[:len(result)-1]
	result_temp = result.copy()
	result = []
	for i in result_temp:
		if ".json" in i:
			result.append(int(i[:i.index(".json")]))
	if result == []:
		return [0]
	result.sort()
	index = 0
	ids = []
	while True:
		if index not in result:
			ids.append(index)
		index += 1
		if index >= result[len(result)-1]:
			ids.append(index+1)
			break
	return ids

def detect_corrupted_images():
	path = "static/images/"
	result = os.popen("ls "+path).read().split("\n")
	result = result[:len(result)-1]
	result_temp = result.copy()
	result = []
	for i in result_temp:
		if ".json" in i:
			result.append(int(i[:i.index(".json")]))
	result.sort()
	ids = []
	for i in result:
		a = os.popen("ls "+path+str(i)+".thumbnail.png> /dev/null 2>&1; echo $?").read().split("\n")[0]
		if a != "0":
			ids.append(i)
	return ids

class handle_images():
	def __init__(self):
		self.ids = detect_images()
		self.update_next_id()

	def update_next_id(self):
		if len(self.ids) > 1:
			self.next_id = self.ids[0]
			self.ids = self.ids[1:]
		elif len(self.ids) == 1:
			self.next_id = self.ids.pop()
		else:
			self.next_id += 1

	def add_image(self, image):
		filename = image["info"]["location"]+"."+image["file"].content_type[6:]
		with open(filename, "wb") as file:
			file.write(image["file"].stream.read())
		# image["file"].save(filename, len(image["file"].stream.read()))
		result = os.popen("convert "+filename+" png32:"+image["info"]["location"]+".temp.png").read()
		image_source = Image.open(image["info"]["location"]+".temp.png")
		image_hidden = Image.open("static/watermark_image/b.png")
		do_merge(image_source, image_hidden, image["info"]["location"]+".thumbnail.png")
		# eg = threading.Thread(target=do_merge, args=(image_source, image_hidden, image["info"]["location"]+".thumbnail.png"))
		# eg.start()
		with open(image["info"]["location"]+".json", "w") as file:
			JSON.dump(image["data"], file)

	def remove_images(self, image_ids):
		for image_id in image_ids:
			result = os.popen("rm "+image_id+"*").read()

	def remove_image(self, location):
		result = os.popen("rm "+location+"*").read()

	def update_image_info(self, image_id, info):
		data = self.get_image_info(image_id)
		for i in info:
			if info[i] != data[i]:
				data[i] = info[i]
		with open(image_id+".json", "w") as file:
			JSON.dump(data, file)
		return data

	def get_image_info(self, image_id):
		with open(image_id+".json", "r") as file:
			data = JSON.load(file)
		return data

	def get_image_location(self):
		result = "static/images/"+str(self.next_id)
		self.update_next_id()
		return result


if __name__ == "__main__":
	ids = detect_images()
	print(ids)
	hi = handle_images()
	hi.update_next_id()
	hi.update_next_id()
	hi.update_next_id()
	hi.update_next_id()
	hi.update_next_id()
	hi.update_next_id()