// Support TLS-specific URLs, when appropriate.
if (window.location.protocol == "https:") {
  var ws_scheme = "wss://";
} else {
  var ws_scheme = "ws://"
};


var statusSocket = new ReconnectingWebSocket(ws_scheme + location.host + "/status");

statusSocket.onmessage = function (message) {
    /* var reader = new FileReader();
    reader.addEventListener("loadend", function () {
       // reader.result contains the contents of blob as a binary string
       document.getElementById('steppy').innerHTML = '<h1 class="status">' + reader.result + '</h1>';
    });
    reader.readAsBinaryString(message.data);*/
    document.getElementById('steppy').innerHTML = '<h1 class="status">' + message.data + '</h1>';
};
// statusSocket.send('toto');
