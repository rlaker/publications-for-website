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
        } else if (pre.classList.contains("bibvisible")) {
            pre.classList.add("bibhidden")
            pre.classList.remove("bibvisible")
        }
    }
}

function expandAuthors(expandLink) {
    var element = expandLink;
    // finds the <tr> tag
    while (element.nodeName.toUpperCase() != 'TR') {
        element = element.parentNode;
    }

    // then gets the span elements inside the <tr>
    var authors = element.getElementsByTagName('span');
    console.log(authors);
    // cycles through the span elements and checks if it contains a
    for (var i = 0; i < authors.length; i++) {
        var span = authors[i];
        // if hidden then show it
        console.log(span);
        if (span.classList.contains("longAuthors")) {
            span.classList.remove("longAuthors")
            span.classList.add("shortAuthors")
        } else if (span.classList.contains("shortAuthors")) {
            // if shown then hide it
            span.classList.add("longAuthors")
            span.classList.remove("shortAuthors")
        }
    }
}