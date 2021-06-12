// Set up a websocket at the base endpoint
let LOCATION = window.location;
let WS_PROTOCOL = "";
if (LOCATION.protocol == "https:") {
	WS_PROTOCOL = "wss://";
} else {
	WS_PROTOCOL = "ws://";
}
let WS_ENDPOINT_URL = WS_PROTOCOL + LOCATION.host;
let COMMAND_SOCKET = new WebSocket(WS_ENDPOINT_URL);

// Receivable commands
COMMAND_SOCKET.onmessage = function (response) {
	// Websocket message received, parse for JSON
	console.info(response);
	json_response = JSON.parse(response.data);

	// Check for valid commands
	console.info("Websocket has recieved a message", json_response);
};

// Websocket open event
COMMAND_SOCKET.onopen = function () {
	console.info("Websocket has opened.");
};

// Websocket close event
COMMAND_SOCKET.onclose = function () {
	console.info("Websocket has closed.");
};

// Websocket error event
COMMAND_SOCKET.onerror = function (error) {
	console.error(
		"Websocket encountered a crtical error: ",
		error.message,
		"Closing socket..."
	);
	COMMAND_SOCKET.close();
};
