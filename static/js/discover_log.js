alert("asdasd");
document.onloadeddata = $.ajax({
	type: "POST",
	url: "/image_list_get/",
	dataType: "json",
	// headers: {"Content-Type": "application/json"},
	contentType: "application/json; charset=utf-8",
	data: JSON.stringify({"type": "kinds"}),
	success: function(response){
		// response = $.parseJSON(response)
		// locolStorage.setItem("result", response)
		console.log(response);
		result = response.response["result"];
		place = document.getElementsByClassName("label-div")[0]
		for(var kind in result){
			var paragraph = document.createElement("p");
			console.log(paragraph);
			paragraph.className = "label";
			label = document.createTextNode(kind);
			paragraph.append(label);
			place.append(paragraph);
			href = document.createElement("a");
			href.href = "/more/";
			href.className = "icon icon-arrow-right button";
			href.innerHTML = "更多";
			place.append(href);
			images = document.createElement("div");
			images.id = "portfolio";
			images.className = "container";
			place.append(images);
			for(var image of result[kind]){
				column = document.createElement("div");
				column.className = "column";
				images.append(column);
				thumbnail = document.createElement("div");
				thumbnail.className = "thumbnail";
				column.append(thumbnail);
				image_item = document.createElement("img");
				image_item.src = "/"+image["location"]+".thumbnail.png";
				image_item.alt = image["name"];
				image_item.className = "image image-full";
				image_item.onclick = function(){displayModal(this)};
				thumbnail.append(image_item);
				download_button = document.createElement("div");
				thumbnail.append(download_button);
				link = document.createElement("a");
				link.href = "/"+image["location"]+".thumbnail.png";
				link.download = image["name"];
				download_button.append(link);
				icon = document.createElement("img");
				icon.className = "download-icon";
				icon.src = "/static/data/images/download.png";
				link.append(icon);
				info = document.createElement("div");
				info.className = "info";
				thumbnail.append(info);
				title = document.createElement("span");
				title.className = "name-info";
				title.innerHTML = image["name"];
				info.append(title);
				user = document.createElement("span");
				user.className = "user-info";
				user.innerHTML = image["by"];
				info.append(user);
			}
		}
	}
});
function logout(){
	$.ajax({
		type: "POST",
		url: "/logout/",
		dataType: "html",
		// headers: {"Content-Type": "application/json"},
		contentType: "application/json; charset=utf-8",
		data: JSON.stringify({"info": {"name": localStorage.getItem("name"), "password": localStorage.getItem("password")}, "url": window.location.href}),
		success: function(response){
			window.location.reload()
			return true;
		}
	});
}
function search(){
	search_text = document.getElementById("search").value;
	$.ajax({
		alert(search_text)
		type: "POST",
		url: "/search/",
		dataType: "html",
		// headers: {"Content-Type": "application/json"},
		contentType: "application/json; charset=utf-8",
		data: JSON.stringify({"info": {"text": search_text, "url": window.location.href}),
		success: function(response){
			window.location.reload()
			return true;
		}
	});
}
