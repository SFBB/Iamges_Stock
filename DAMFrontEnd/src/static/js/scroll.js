$(function () {
    $("#top-button").bind("click", function () {
        $offset = $("#portfolio-wrapper").offset().top - 64;
        $("html,body").animate({ "scrollTop": $offset }, 500);
    });
});

function showTopButton() {
    var scrollTop = document.documentElement.scrollTop || document.body.scrollTop;
    if (scrollTop > 1000) {
        $("#top-button").fadeIn(300);
    }
    else {
        $("#top-button").fadeOut(300);
    }
}
var throttle = function (fn, delay, atleast) {
    var timer = null;
    var previous = null;
    return function () {
        var now = +new Date();
        if (!previous) previous = now;
        if (now - previous > atleast) {
            fn();
            // 重置上一次开始时间为本次结束时间
            previous = now;
            clearTimeout(timer);
        } else {
            clearTimeout(timer);
            timer = setTimeout(function () {
                fn();
                previous = null;
            }, delay);
        }
    }
};
window.onscroll = throttle(showTopButton, 200, 500);