$(document).ready(function () {

});
function hideElement(toDelete) {
    var confirmDelete = confirm("确定删除这张照片吗？");
    if (confirmDelete == true) {
        $(toDelete).parents(".column").fadeOut(300);
        return true;
    }
    else {
        return false;
    }
}