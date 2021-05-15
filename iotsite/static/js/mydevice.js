function add_dev_form_submit() {
	if(document.getElementById('id_device_id').value.length != 0 && document.getElementById('id_device_name').value.length != 0) {
		document.getElementById("add-dev-form").submit();
	}
	if(document.getElementById('id_device_id').value.length == 0) {
		document.getElementById("alert_add_dev_id").innerHTML = "以上字段不可为空";
	} else {
		document.getElementById("alert_add_dev_id").innerHTML = "";
	}
	if(document.getElementById('id_device_name').value.length == 0) {
		document.getElementById("alert_add_dev_name").innerHTML = "以上字段不可为空";
	} else {
		document.getElementById("alert_add_dev_name").innerHTML = "";
	}
}

function add_dev_form_close() {
	document.getElementById("alert_add_dev").innerHTML = "";
	document.getElementById("alert_add_dev_id").innerHTML = "";
	document.getElementById("alert_add_dev_name").innerHTML = "";
}

$(function () {
	$('.tooltip-test').tooltip({container: 'body'})
})