$("#id_username").change(function() {
	// console.log($(this).val());
	var username = $(this).val();

	$.ajax({
		url: '/ajax/validate_username/',
        data: {
          'username': username
        },
        dataType: 'json',
        success: function (data) {
          if(data.is_taken) {
			document.getElementById("alert_username").innerHTML = "用户名已存在";
          } else if(data.is_valid == -1) {
			document.getElementById("alert_username").innerHTML = "用户名长度应在6 - 150个字符范围内";
		  } else if(data.is_valid == -2) {
			document.getElementById("alert_username").innerHTML = "用户名中只能出现字母、数字或 @ . + - _";
		  } else {
			document.getElementById("alert_username").innerHTML = "";
		  }
        }
	});
});

$("#id_email").change(function() {
	console.log($(this).val());
	var email = $(this).val();

	$.ajax({
		url: '/ajax/validate_email/',
        data: {
          'email': email
        },
        dataType: 'json',
        success: function (data) {
          if(data.is_taken) {
			document.getElementById("alert_email").innerHTML = "邮箱已存在";
          } else if(!data.is_valid) {
			document.getElementById("alert_email").innerHTML = "邮箱格式错误";
		  } else {
			document.getElementById("alert_email").innerHTML = "";
		  }
        }
	});
});