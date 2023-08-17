import { mountLayoutWithWebSocket } from "@reactpy/client";

// Set up a websocket at the base endpoint
let HTTP_PROTOCOL = window.location.protocol;
let WS_PROTOCOL = "";
if (HTTP_PROTOCOL == "https:") {
	WS_PROTOCOL = "wss:";
} else {
	WS_PROTOCOL = "ws:";
}

export function mountViewToElement(
	mountElement,
	reactpyHost,
	reactpyUrlPrefix,
	reactpyReconnectMax,
	reactpyComponentPath,
	reactpyResolvedWebModulesPath
) {
	// Determine the Websocket route
	let wsOrigin;
	if (reactpyHost) {
		wsOrigin = `${WS_PROTOCOL}//${reactpyHost}`;
	} else {
		wsOrigin = `${WS_PROTOCOL}//${window.location.host}`;
	}
	const websocketUrl = `${wsOrigin}/${reactpyUrlPrefix}/${reactpyComponentPath}`;

	// Determine the HTTP route
	let httpOrigin;
	let webModulesPath;
	if (reactpyHost) {
		httpOrigin = `${HTTP_PROTOCOL}//${reactpyHost}`;
		webModulesPath = `${reactpyUrlPrefix}/web_module`;
	} else {
		httpOrigin = `${HTTP_PROTOCOL}//${window.location.host}`;
		if (reactpyResolvedWebModulesPath) {
			webModulesPath = reactpyResolvedWebModulesPath;
		} else {
			webModulesPath = `${reactpyUrlPrefix}/web_module`;
		}
	}
	const webModuleUrl = `${httpOrigin}/${webModulesPath}`;

	// Function that loads the JavaScript web module, if needed
	const loadImportSource = (source, sourceType) => {
		return import(
			sourceType == "NAME" ? `${webModuleUrl}/${source}` : source
		);
	};

	// Start rendering the component
	mountLayoutWithWebSocket(
		mountElement,
		websocketUrl,
		loadImportSource,
		reactpyReconnectMax
	);
}
