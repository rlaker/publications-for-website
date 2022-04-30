function showBibHere(biblink) {
    var element = biblink;
    while (element.nodeName.toUpperCase() != 'TR') {
        element = element.parentNode;
    }
    var bibsources = element.getElementsByTagName('pre');
    for (var i = 0; i < bibsources.length; i++) {
        var pre = bibsources[i];
        if (pre.classList.contains("bibhidden")) {
            pre.classList.remove("bibhidden")
            pre.classList.add("bibvisible")
        } else {
            pre.classList.add("bibhidden")
            pre.classList.remove("bibvisible")
        }
    }
}