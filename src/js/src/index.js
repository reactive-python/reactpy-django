import { mountLayoutWithWebSocket } from "idom-client-react";

// Set up a websocket at the base endpoint
const LOCATION = window.location;
let WS_PROTOCOL = "";
if (LOCATION.protocol == "https:") {
	WS_PROTOCOL = "wss://";
} else {
	WS_PROTOCOL = "ws://";
}
const WS_ENDPOINT_URL = WS_PROTOCOL + LOCATION.host + "/";

export function mountViewToElement(
	mountElement,
	idomWebsocketUrl,
	idomWebModulesUrl,
	maxReconnectTimeout,
	componentPath
) {
	const WS_URL = WS_ENDPOINT_URL + idomWebsocketUrl + componentPath;
	const WEB_MODULE_URL = LOCATION.origin + "/" + idomWebModulesUrl;
	const loadImportSource = (source, sourceType) => {
		return import(
			sourceType == "NAME" ? `${WEB_MODULE_URL}${source}` : source
		);
	};

	mountLayoutWithWebSocket(
		mountElement,
		WS_URL,
		loadImportSource,
		maxReconnectTimeout
	);
}
