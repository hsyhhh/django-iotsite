from django.shortcuts import render, redirect
from django.http import Http404, HttpResponse, JsonResponse, HttpResponseRedirect
from django.template import loader
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.auth.models import AnonymousUser, User
from django.contrib.auth import authenticate, logout
from django.contrib.auth import login as auth_login
from django.contrib import messages

from .models import *

from django_ajax.decorators import ajax
from django.urls import reverse
import json


# Create your views here.
def index(request):
	client_list = Client.objects.all().order_by('client_id')
	online_client_list = []
	total_client_num = len(client_list)
	online_client_num = 0
	now = timezone.now() - timedelta(hours=1)
	for client in client_list:
		if client.time >= now:
			online_client_num += 1
			online_client_list.append(client)

	now = timezone.now()
	now_time = now.strftime("%Y/%m/%d, %H:%M:%S")

	msg_list = Message.objects.order_by('time')
	oldest_msg_time = msg_list[0].time
	oldest_msg_time = oldest_msg_time.strftime("%Y/%m/%d, %H:%M:%S")

	# 获取msgChart的label列表
	if now.minute == 0 and now.second == 0:
		now_ceiling = datetime(year=now.year, month=now.month, day=now.day, hour=now.hour)
	else:
		now_ceiling = datetime(year=now.year, month=now.month, day=now.day, hour=now.hour+1)
	msgChart_labels = []
	for i in range(25):
		tmp_time = now_ceiling - timedelta(hours = i)
		if i == 0:
			msgChart_labels.append(tmp_time.strftime("%m/%d %H:%M"))
		elif tmp_time.hour == 0:
			msgChart_labels.append(tmp_time.strftime("%m/%d %H:%M"))
		else:
			msgChart_labels.append(tmp_time.strftime("%H:%M"))
	msgChart_labels = msgChart_labels[::-1]
	print(msgChart_labels)
	json_msgChart_labels = json.dumps(msgChart_labels)

	# 从数据库读取当前用户所拥有的设备并返回
	if request.user.is_authenticated: 
		device_list = Device.objects.filter(user=request.user).order_by('device_id')
	else:
		device_list = None

	# 从数据库读取过去24小时内每小时接收到的数据量,共24个数据
	msgChart_data = []
	pre_tmp_time = now_ceiling
	for i in range(1, 25):
		tmp_time = now_ceiling - timedelta(hours = i)
		tmp_set = msg_list.filter(time__gte=tmp_time).filter(time__lte=pre_tmp_time)
		msgChart_data.append(len(tmp_set))
		pre_tmp_time = tmp_time
	msgChart_data = msgChart_data[::-1]
	print(msgChart_data)
	json_msgChart_data = json.dumps(msgChart_data)

	context = {
		'device_list': device_list,
		'client_list': client_list,
		'online_client_list': online_client_list,
		'total_client_num': total_client_num,
		'online_client_num': online_client_num,
		'oldest_msg_time': oldest_msg_time,
		'msg_num': len(msg_list),
		'now_time': now_time,
		'msgChart_labels': json_msgChart_labels,
		'msgChart_data': json_msgChart_data,
	}
	template = loader.get_template('index.html')
	return HttpResponse(template.render(context, request))

def login(request):
	username = request.POST['username']
	password = request.POST['password']
	user = authenticate(request, username=username, password=password)
	if user is not None:
		auth_login(request, user)
		return render(request, 'index.html')
	else:
		return render(request, 'login.html')

def logout(request):
	logout(request)
	return render(request, 'index.html')

def signup(request):
	# return render(request, 'signup.html')
	if request.method == "POST":
		username = request.POST['username']
		email = request.POST['email']
		password1 = request.POST['password1']
		password2 = request.POST['password2']

		# 用户名在系统中不存在,且用户名符合格式要求
		is_username_valid = (not User.objects.filter(username__iexact=username).exists()) and _is_username_valid(username) == 0
		# 邮箱在系统中不存在,且邮箱符合格式要求
		is_email_valid = (not User.objects.filter(email__iexact=email).exists()) and _is_email_valid(email)
		# 密码是否有效,返回值:0,-1,-2
		is_password_valid = (_is_password_valid(password1, password2) == 0)

		context = {
			'is_password_valid': _is_password_valid(password1, password2),
			'username': username,
			'email': email,
			'password1': password1,
			'password2': password2,
		}
		# print(is_username_valid and is_email_valid and is_password_valid)
		if is_username_valid and is_email_valid and is_password_valid:
			user = User.objects.create_user(username, email, password1)
			if user is not None:
				auth_login(request, user)
				user.save()
			# return render(request, 'index.html')
			return HttpResponseRedirect("/")
		else:
			# print(is_password_valid)
			template = loader.get_template('signup.html')
			return HttpResponse(template.render(context, request))
	else:
		return render(request, 'signup.html')

def validate_username(request):
	username = request.GET.get('username', None)
	data = {
		'is_taken': User.objects.filter(username__iexact=username).exists(),
		'is_valid': _is_username_valid(username)
	}
	return JsonResponse(data)

def validate_email(request):
	email = request.GET.get('email', None)
	if len(email) == 0:
		data = {
			'is_taken': False,
			'is_valid':True
		}
	else:
		data = {
		'is_taken': User.objects.filter(email__iexact=email).exists(),
		'is_valid': _is_email_valid(email)
		}
	return JsonResponse(data)

def profile(request):
	if request.user.is_authenticated: 
		device_list = Device.objects.filter(user=request.user).order_by('device_id')
	else:
		device_list = None
	info_or_pwd = 0
	error_msg = ''
	error_type = 0
	has_error = False
	# 修改信息: info_or_pwd = 0
	if request.method == "POST" and 'email' in request.POST:
		info_or_pwd = 0

		email = request.POST['email']
		if User.objects.filter(email__iexact=email).exists() and email != request.user.email:
			has_error = True
			error_msg = "邮箱已存在"
		elif not _is_email_valid(email):
			has_error = True
			error_msg = "邮箱格式错误"
		else:
			user = request.user
			user.email = request.POST['email']
			user.first_name = request.POST['realname']
			user.save()
		context = {
			'info_or_pwd': info_or_pwd,
			'has_error': has_error,
			'error_msg': error_msg,
			'device_list': device_list,
		}
		template = loader.get_template('profile.html')
		return HttpResponse(template.render(context, request))
		return render(request, 'profile.html')
	# 修改密码: info_or_pwd = 1
	elif request.method == "POST" and 'oripwd' in request.POST:
		info_or_pwd = 1
		# 验证原密码
		oripwd = request.POST['oripwd']
		user = authenticate(request, username=request.user.username, password=oripwd)
		# 原密码错误: 0
		if user is None:
			has_error = True
			error_type = 0
			error_msg = "原密码验证错误，请重新输入"
		# 原密码验证成功
		else:
			pwd1 = request.POST['pwd1']
			pwd2 = request.POST['pwd2']
			tmp = _is_password_valid(pwd1, pwd2)
			# 两次输入的密码不一致: 1
			if tmp == -1:
				has_error = True
				error_type = 1
				error_msg = "两次输入的密码不一致，请重新输入"
			# 密码格式无效: 2
			elif tmp == -2:
				has_error = True
				error_type = 2
				error_msg = "密码长度要求6个字符及以上"
			# 成功,可以修改密码
			elif tmp == 0:
				user = request.user
				user.set_password(pwd1)
				user.save()
				auth_login(request, user)
		context = {
			'info_or_pwd': info_or_pwd,
			'has_error': has_error,
			'error_type': error_type,
			'error_msg': error_msg,
			'device_list': device_list,
		}
		template = loader.get_template('profile.html')
		return HttpResponse(template.render(context, request))
	context = {
			'device_list': device_list,
	}
	return render(request, 'profile.html', context)

def mydevice(request):
	has_error = False
	is_saved = False
	error_msg = ''
	# 从数据库读取当前用户所拥有的设备并返回
	if request.user.is_authenticated: 
		device_list = Device.objects.filter(user=request.user).order_by('device_id')
		client_list = Client.objects.all().order_by('client_id')
	else:
		device_list = None
		client_list = None
	# 得到当前用户拥有所有设备的id
	user_client_id_list = []
	if device_list is not None:
		for device in device_list:
			user_client_id_list.append(device.client_id)
	# 处理添加设备的请求
	if request.method == "POST" and 'client_id' in request.POST and 'device_id' in request.POST and 'device_name' in request.POST:
		client_id = request.POST['client_id']
		device_id = request.POST['device_id']
		device_name = request.POST['device_name']
		# 当前用户已经拥有该设备
		if client_id in user_client_id_list:
			has_error = True
			error_msg = '您已经拥有该设备，请选择未拥有的设备'
			context = {
				'device_list': device_list,
				'client_list': client_list,
				'has_error': has_error,
				'error_msg': error_msg,
			}
			template = loader.get_template('mydevice.html')
			return HttpResponse(template.render(context, request))
		else:
			device = Device(
				device_id = device_id,
				device_name = device_name,
				user = request.user,
				client = Client.objects.get(client_id=client_id)
			)
			device.save()
			is_saved = True
		# 重新读取当前用户所拥有的设备
		if request.user.is_authenticated: 
			device_list = Device.objects.filter(user=request.user).order_by('device_id')
		else:
			device_list = None
	# 处理修改设备信息的请求
	elif request.method == "POST" and 'client_id_to_edit' in request.POST and 'device_id' in request.POST and 'device_name' in request.POST:
		client_id_to_edit = request.POST['client_id_to_edit']
		device_id = request.POST['device_id']
		device_name = request.POST['device_name']
		Device.objects.filter(client_id=client_id_to_edit,user=request.user).update(device_id=device_id,device_name=device_name)
		# 重新读取当前用户所拥有的设备
		if request.user.is_authenticated: 
			device_list = Device.objects.filter(user=request.user).order_by('device_id')
		else:
			device_list = None
	context = {
		'device_list': device_list,
		'client_list': client_list,
		'has_error': has_error,
		'is_saved': is_saved,
	}
	template = loader.get_template('mydevice.html')
	return HttpResponse(template.render(context, request))

def delete_client(request, client_id):
	user = request.user
	Device.objects.get(user=user, client=client_id).delete()
	# 从数据库读取当前用户所拥有的设备并返回
	if request.user.is_authenticated: 
		device_list = Device.objects.filter(user=request.user).order_by('device_id')
		client_list = Client.objects.all().order_by('client_id')
	else:
		device_list = None
		client_list = None
	context = {
		'device_list': device_list,
		'client_list': client_list,
	}
	return redirect(reverse('mydevice'), context)

def client(request, client_id):
	# print(client_id)
	# 从数据库读取当前用户所拥有的设备并返回
	device_list = Device.objects.filter(user=request.user)
	# 查看该client_id是否存在
	try:
		client = Client.objects.get(client_id=client_id)
	except Client.DoesNotExist:
		raise Http404("Client dose not exist")
	for device in device_list:
		if device.client.client_id == client_id:
			this_device = device
	# 得到当前时间
	now = timezone.now()
	now_time = now.strftime("%Y/%m/%d, %H:%M:%S")
	# 得到该设备最近30条的数据,index为0的是最新数据
	msg_list = Message.objects.filter(client_id=client_id).order_by('time')[::-1][:30]
	for i in range(len(msg_list)):
		msg_list[i].lng = round(msg_list[i].lng, 3)
		msg_list[i].lat = round(msg_list[i].lat, 3)

	# 得到该设备最近16条的数据,用来绘制数值变化曲线,index为0是最老的数据
	msg_value_list = msg_list[:16][::-1]
	# 得到该设备近16条数据的时间和值
	valueChart_labels = []
	valueChart_data = []
	for msg in msg_value_list:
		valueChart_labels.append(msg.time.strftime("%H:%M:%S"))
		valueChart_data.append(msg.value)
	
	# 得到该设备近5条数据,用来在地图显示历史轨迹,index为0是最老的数据
	msg_pos_list = msg_list[:5][::-1]
	# 得到该设备近5条数据的时间和经纬度
	pos_time_data = []
	pos_lng_data = []
	pos_lat_data = []
	for msg in msg_pos_list:
		pos_time_data.append(msg.time.strftime("%H:%M:%S"))
		pos_lng_data.append(msg.lng)
		pos_lat_data.append(msg.lat)
	
	for i in range(len(msg_list)):
		msg_list[i].time = str(msg_list[i].time)

	context = {
		'device_list': device_list,
		'client': client, 
		'device': this_device,
		'now_time': now_time,
		'valueChart_labels': valueChart_labels,
		'valueChart_data': valueChart_data,
		'pos_time_data': pos_time_data,
		'pos_lng_data': pos_lng_data,
		'pos_lat_data': pos_lat_data,
		'msg_list': msg_list,
	}
	return render(request, 'client.html', context)

def client_ajax(request):
	client_id = request.GET.get('client_id', None)
	print(client_id)
	data = {
		'hello': 1
	}
	return JsonResponse(data)

def _is_username_valid(username):
	# 用户名要求
	# 6 - 150 characters (-1)
	# letters, digits and @/./+/-/_ only (-2)
	if len(username) < 6 or len(username) > 150:
		return -1
	allowed_ch_set = {'@', '.', '+', '-', '_'}
	for c in username:
		if not c.isdigit() and not c.isalpha() and c not in allowed_ch_set:
			return -2
	return 0
		
def _is_email_valid(email):
	import re
	regex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'
	if re.search(regex, email):
		return True
	else:
		return False

# 0: 密码有效
# -1: 两次输入的密码不一致
# -2: 密码格式无效,要求6字节及以上
def _is_password_valid(password1, password2):
	if password1 != password2:
		return -1
	elif len(password1) < 6:
		return -2
	else:
		return 0