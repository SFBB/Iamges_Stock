function showImg(fileInput) {
    var imgFile = fileInput.files[0];
    if (imgFile.type != "image/png" && imgFile.type != "image/jpg" && imgFile.type != "image/jpeg") {
        $("#tips-msg").html("请上传正确格式的图片文件");
        $("#widget-tips").fadeIn(300);
        setTimeout(function () { $("#widget-tips").fadeOut(300); }, 2000);
        fileInput.value = "";
        $("#upload-box").css("background-color", "rgb(235, 235, 235)");
        $("#upload-tip").css("display", "block");
        $("#image-show").hide();
        return false;
    }
    if (imgFile.size > 50 * 1024 * 1024) {
        $("#tips-msg").html("文件大小不能超过50M");
        $("#widget-tips").fadeIn(300);
        setTimeout(function () { $("#widget-tips").fadeOut(300); }, 2000);
        fileInput.value = "";
        $("#upload-box").css("background-color", "rgb(235, 235, 235)");
        $("#upload-tip").css("display", "block");
        $("#image-show").hide();
        return false;
    }
    var fr = new FileReader();
    fr.onload = function () {
        document.getElementById('image-show').src = fr.result;
        $("#image-show").show();
    };
    fr.readAsDataURL(imgFile);
    $("#upload-tip").css("display", "none");
    $("#upload-box").css("background-color", "rgb(255, 255, 255)");
}

$.validator.setDefaults({
    submitHandler: function (form) {
        var imgFile = document.getElementById('file-input').value;
        if (imgFile == "" || imgFile == null) {
            $("#tips-msg").html("请上传图片");
            $("#widget-tips").fadeIn(300);
            setTimeout(function () { $("#widget-tips").fadeOut(300); }, 2000);
            return false;
        }
        else {
            form.submit();
        }
    }
});

$().ready(function () {
    // 提交时验证表单
    var validator = $("#upload-form").validate({
        errorPlacement: function (error, element) {
            // Append error within linked label
            $(element)
                .closest("form")
                .find("label[for='" + element.attr("id") + "']")
                .append(error);
        },
        errorElement: "span",
        rules: {
            title: {
                required: true,
                maxlength: 20
            },
            description: {
                maxlength: 50
            }
        },
        messages: {
            title: {
                required: "请为您的照片取一个名字",
                maxlength: "不能超过20个字符"
            },
            description: {
                maxlength: "不能超过50个字符"
            }
        }
    });
});