var modal;
var span;
var captionText;
var modalImg;
var flag = 0;
window.onload = function () {
    // 获取模态窗口
    modal = document.getElementById('myModal');
    // 获取 <span> 元素，设置关闭模态框按钮
    span = document.getElementsByClassName("close")[0];
    // 点击 <span> 元素上的 (x), 关闭模态框
    span.onclick = function () {
        modal.style.display = "none";
    }
    captionText = document.getElementById("caption");
    modalImg = document.getElementById("img01");
    flag = 1;
}

function displayModal(currentImg) {
    if (flag == 0) { //If the user clicks on the image before the page is fully loaded
        try {
            modal = document.getElementById('myModal');
            span = document.getElementsByClassName("close")[0];
            span.onclick = function () {
                modal.style.display = "none";
            }
            captionText = document.getElementById("caption");
            modalImg = document.getElementById("img01");
        }
        catch (e) {
            console.log(e);
        }
    }
    try {
        modal.style.display = "block";
        modal.style.margin = "auto";
        modalImg.src = currentImg.src;
        modalImg.alt = currentImg.alt;
        captionText.innerHTML = currentImg.alt;
    }
    catch (e) {
        console.log(e);
    }
}