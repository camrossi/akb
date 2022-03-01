var getUrlParameter = function getUrlParameter(sParam) {
    var sPageURL = window.location.search.substring(1),
        sURLVariables = sPageURL.split('&'),
        sParameterName,
        i;

    for (i = 0; i < sURLVariables.length; i++) {
        sParameterName = sURLVariables[i].split('=');

        if (sParameterName[0] === sParam) {
            return sParameterName[1] === undefined ? true : decodeURIComponent(sParameterName[1]);
        }
    }
    return false;
};

var next_ip = function next_ip(ipv4_with_mask) {
    var octect = ipv4_with_mask.split("/")[0].split(".");
    var mask = ipv4_with_mask.split("/")[1];
    octect[3] = ""  + ((octect[3] * 1 + 1));
    var next_ip = octect.join(".")
    return next_ip + "/" + mask
}
