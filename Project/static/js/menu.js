function setPara(key,value){
    let url = window.location.href;
    var list = url.split(/\?|&/);
    index = url.indexOf(key);
    if (index == -1){
        if (url.indexOf("?") > -1)
            url += `&${key}=${value}`;
        else
            url += `?${key}=${value}`;
        }
    else{
        url = `${list[0]}\?`;
        for(i = 1; i<list.length; i++){
            if (list[i].indexOf(key) > -1)
                list[i] = `${key}=${value}`;
            url += i<2 ? list[i] : `&${list[i]}`;
        }
    }
    window.location.href = url;
}