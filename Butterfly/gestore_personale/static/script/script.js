function makeListeners(request){
    var submits = document.querySelectorAll('input[type="button"]');
    for(var i=0;i<submits.length;i++){
        submits[i].onclick = function(element){
            click(request, element.target.id);
        }
    }
}

function isrequestReady(request){
    return (request.readyState == 4 &&
            request.status == 200 &&
            request.responseText
            );
}


function getIo(id){
    if(id.indexOf("topics")!=-1) return "topics";
    if(id.indexOf("projects")!=-1) return "projects";
    if(id.indexOf("availability")!=-1) return "availability";
    if(id.indexOf("platform")!=-1) return "platform";
    return "data";
}


function makeRequest(request, url, method, id){
    var io = getIo(id);
    var form = document.getElementById(io);
    var formData = new FormData(form);
    if(id.indexOf("panel")!=-1) formData.append("panel", "panel");
    if(id) formData.append(id, id);
    if(io=="data") io = "html";
    else if(io=="projects") io = "topics";
    request.open(method, url);
    request.send(formData);
    request.onreadystatechange = function(){
        if(isrequestReady(request)){
            document.getElementById(io).innerHTML = request.responseText;
            makeListeners(request);
        }
    }
}

function getRequestType(id){
    if(id.indexOf("post")!=-1) return "POST";
    if(id.indexOf("put")!=-1) return "PUT";
    if(id.indexOf("delete")!=-1) return "DELETE";
    return "GET";
}

function getRequestUrl(id){
    if(id.indexOf("preference")!=-1) return "web_preference";
    else if(id.indexOf("project")!=-1) return "web_project";
    return "web_user";
}

function click(request, id){
    var requestType = getRequestType(id);
    var requestUrl = getRequestUrl(id);
    makeRequest(request, requestUrl, requestType, id)
}

window.onload = function () {
    var request = new XMLHttpRequest();
    makeListeners(request);
}
