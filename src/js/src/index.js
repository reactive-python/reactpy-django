import { mountLayoutWithWebSocket } from "idom-client-react";

// Set up a websocket at the base endpoint
let LOCATION = window.location;
let WS_PROTOCOL = "";
if (LOCATION.protocol == "https:") {
  WS_PROTOCOL = "wss://";
} else {
  WS_PROTOCOL = "ws://";
}
let WS_ENDPOINT_URL = WS_PROTOCOL + LOCATION.host + "/";

export function mountViewToElement(
  mountPoint,
  idomWebsocketUrl,
  idomWebModulesUrl,
  viewId,
  queryParams
) {
  const fullWebsocketUrl =
    WS_ENDPOINT_URL + idomWebsocketUrl + viewId + "/?" + queryParams;

  const fullWebModulesUrl = LOCATION.origin + "/" + idomWebModulesUrl
  const loadImportSource = (source, sourceType) => {
    return import(
      sourceType == "NAME" ? `${fullWebModulesUrl}${source}` : source
    );
  };

  mountLayoutWithWebSocket(mountPoint, fullWebsocketUrl, loadImportSource);
}
