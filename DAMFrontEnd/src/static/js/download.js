function openDownloadDialog(url, saveName) {
    
    // for ie 10 and later
    if (window.navigator.msSaveBlob) {
        let blob = new Blob([url],{type:'image/png'});
        try {
            console.log(url);
            console.log(saveName);
            window.navigator.msSaveBlob(blob, saveName+'.png');
            console.log("ok");
        }
        catch (e) {
            console.log(e);
        }
    }
    // 谷歌浏览器 创建a标签 添加download属性下载
    else {
        if (typeof url == 'object' && url instanceof Blob) {
            url = URL.createObjectURL(url); // 创建blob地址
        }
        var aLink = document.createElement('a');
        aLink.href = url;
        aLink.download = saveName || ''; // HTML5新增的属性，指定保存文件名，可以不要后缀，注意，file:///模式下不会生效
        var event;
        if (window.MouseEvent) {
            event = new MouseEvent('click');
        }
        else {
            event = document.createEvent('MouseEvents');
            event.initMouseEvent('click', true, false, window, 0, 0, 0, 0, 0, false, false, false, false, 0, null);
        }
        aLink.dispatchEvent(event);
    }
}