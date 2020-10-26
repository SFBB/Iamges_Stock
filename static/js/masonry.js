var box;
var items;
var gap = 16;

window.onload = function () {
    box = document.getElementById('masonry');
    items = box.children;
    waterFall();
    function waterFall() {
        var pageWidth = getClient().width;
        var itemWidth = items[0].offsetWidth;
        var columns = parseInt(pageWidth / (itemWidth + gap));
        var margin = (pageWidth + gap - columns * (itemWidth + gap)) / 2;
        var arr = [];
        for (var i = 0; i < items.length; i++) {
            items[i].style.position = "absolute";
            items[i].style.margin = 0;
            if (i < columns) {
                //确定第一行
                items[i].style.top = 0;
                items[i].style.left = (itemWidth + gap) * i + margin + 'px';
                arr.push(items[i].offsetHeight);

            }
            else {
                // 其他行
                var minHeight = arr[0];
                var index = 0;
                for (var j = 0; j < arr.length; j++) {
                    if (minHeight > arr[j]) {
                        minHeight = arr[j];
                        index = j;
                    }
                }
                items[i].style.top = arr[index] + gap + 'px';
                // left值就是最小列距离左边的距离
                items[i].style.left = items[index].offsetLeft + 'px';
                // 最小列的高度 = 当前自己的高度 + 拼接过来的高度 + 间隙的高度
                arr[index] = arr[index] + items[i].offsetHeight + gap;
            }
        }
        var maxHeight = arr[0];
        var indexMax = 0;
        for (var j = 0; j < arr.length; j++) {
            if (maxHeight < arr[j]) {
                maxHeight = arr[j];
                indexMax = j;
            }
        }
        box.style.height = (arr[indexMax] + gap) + 'px';
    }
    // 页面尺寸改变时实时触发
    window.onresize = function () {
        waterFall();
    };
    // 当加载到第30张的时候
    // window.onscroll = function () {
    // if (getClient().height + getScrollTop() >= items[items.length - 1].offsetTop) {
    //     // 模拟 ajax 获取数据    
    //     var datas = [
    //         "../image/瀑布流/001.jpg",
    //         ...
    //         "../image/瀑布流/030.jpg"
    //     ];
    //     for (var i = 0; i < datas.length; i++) {
    //         var div = document.createElement("div");
    //         div.className = "item";
    //         div.innerHTML = '<img src="' + datas[i] + '" alt="">';
    //         box.appendChild(div);
    //     }
    //     waterFall();
    // }

    // };
};

// clientWidth 处理兼容性
function getClient() {
    return {
        width: document.body.clientWidth || window.innerWidth || document.documentElement.clientWidth,
        height: document.body.clientHeight || window.innerHeight || document.documentElement.clientHeight
    }
}
// scrollTop兼容性处理
function getScrollTop() {
    return window.pageYOffset || document.documentElement.scrollTop;
}