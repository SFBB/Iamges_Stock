from threading import Thread as Process
from threading import Lock



# 记录任务的完成度，主要用于upload_images，用于监测上传(添加水印、更新数据库)是否完成
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



# 不要用，文件内使用
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

	def has_task(self, location):
		if location in self.tasks.keys():
			return True
		else:
			return False