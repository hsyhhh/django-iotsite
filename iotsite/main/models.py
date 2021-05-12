from django.db import models
from django.contrib.auth.models import User

# Create your models here.

# class User(models.Model):
# 	user_name = models.CharField(max_length=20, primary_key=True)
# 	email = models.EmailField()
# 	password = models.CharField(max_length=20) # md5

# 	def __str__(self):
# 	 return self.user_name

class Client(models.Model):
	client_id = models.CharField(max_length=20, primary_key=True)
	info = models.CharField(max_length=100)
	value = models.IntegerField()
	alert = models.BooleanField(default=False)
	lng = models.FloatField()
	lat = models.FloatField()
	time = models.DateTimeField()

	def __str__(self):
		return self.client_id

class Device(models.Model):
	device_id = models.CharField(max_length=20)
	device_name = models.CharField(max_length=20)
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	client = models.ForeignKey(Client, on_delete=models.CASCADE)

	def __str__(self):
		return self.user.username + "-" + self.client.client_id

class Message(models.Model):
	client_id = models.CharField(max_length=20) # 非primary key
	info = models.CharField(max_length=100)
	value = models.IntegerField()
	alert = models.BooleanField(default=False)
	lng = models.FloatField()
	lat = models.FloatField()
	time = models.DateTimeField()

	def __str__(self):
		return self.client_id + "-" + str(self.time)

