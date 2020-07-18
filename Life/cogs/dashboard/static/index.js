function parseTime(milliseconds) {
    let seconds = milliseconds / 1000;
    const hours = parseInt(seconds / 3600);
    seconds = seconds % 3600;
    const minutes = parseInt(seconds / 60);
    seconds = Math.round(seconds % 60)

    if (hours > 0)
        return hours+'h '+minutes+'m '+seconds+'s '
    else if (minutes > 0)
        return minutes+'m '+seconds+'s '
    else if (seconds > 0)
        return seconds+'s '
}

function getWebsocketUrl() {
    const ws_protocol = `${window.location.protocol.replace('http', 'ws').replace('https', 'wss')}`
    return `${ws_protocol}${window.location.host}/websocket`
}

function getCookie(cname) {
    const name = cname + "=";
    const decodedCookie = decodeURIComponent(document.cookie);
    const ca = decodedCookie.split(';');
    for(let i = 0; i <ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) === ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) === 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
}
