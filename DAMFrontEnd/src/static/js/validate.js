$.validator.setDefaults({
    submitHandler: function() {
      alert("提交事件!");
    }
});

$().ready(function() {
	// 提交时验证表单
	var validator = $("#reglog-form").validate({
		errorPlacement: function(error, element) {
			// Append error within linked label
			$( element )
				.closest( "form" )
					.find( "label[for='" + element.attr( "id" ) + "']" )
						.append( error );
		},
        errorElement: "span",
        rules: {
            email: {
                required: true,
                email: true
            },
            username: {
                required: true,
                minlength: 3,
                maxlength: 10
            },
            password: {
                required: true,
                minlength: 3,
                maxlength: 8
            },
            confirm_password: {
                equalTo: "#password"
            }
        },
		messages: {
            email: {
                required: "请输入邮箱",
                email: "邮箱地址无效"
            },
			username: {
				required: "请输入用户名",
                minlength: "不少于3个字符",
                maxlength: "不超过10个字符"
			},
			password: {
				required: "请输入密码",
				minlength: "不少于5个字符",
				maxlength: "不超过16个字符"
            },
            confirm_password: {
                equalTo: "两次输入的密码不一致"
            }
		}
	});
});