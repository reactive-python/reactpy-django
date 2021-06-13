import { mountLayoutWithWebSocket } from "idom-client-react";

// Set up a websocket at the base endpoint
let LOCATION = window.location;
let WS_PROTOCOL = "";
if (LOCATION.protocol == "https:") {
  WS_PROTOCOL = "wss://";
} else {
  WS_PROTOCOL = "ws://";
}
let WS_ENDPOINT_URL = WS_PROTOCOL + LOCATION.host;

mountLayoutWithWebSocket(document.getElementById("mount"), WS_ENDPOINT_URL);
