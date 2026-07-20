import { ReactPyDjangoClient } from "./client";
import { getPageClient } from "./pageClient";
import { Layout, React } from "@reactpy/client";

export type ComponentConfig = {
  dottedPath: string;
  componentUuid: string;
  hasArgs: number;
};

export function mountComponent(
  mountElement: HTMLElement,
  host: string,
  urlPrefix: string,
  componentConfig: ComponentConfig,
  resolvedJsModulesPath: string,
  reconnectInterval: number,
  reconnectMaxInterval: number,
  reconnectMaxRetries: number,
  reconnectBackoffMultiplier: number,
) {
  // Shared WebSocket route per page
  const wsProtocol = `ws${window.location.protocol === "https:" ? "s" : ""}:`;
  const wsOrigin = host
    ? `${wsProtocol}//${host}`
    : `${wsProtocol}//${window.location.host}`;
  const wsUrl = new URL(`${wsOrigin}/${urlPrefix}/`);

  // Embed the initial HTTP path into the WebSocket URL
  wsUrl.searchParams.set("path", window.location.pathname);
  if (window.location.search) {
    wsUrl.searchParams.set("qs", window.location.search);
  }

  // HTTP route for JavaScript modules
  const httpProtocol = window.location.protocol;
  const httpOrigin: string = host
    ? `${httpProtocol}//${host}`
    : `${httpProtocol}//${window.location.host}`;
  const jsModulesPath: string = resolvedJsModulesPath
    ? `${httpOrigin}${resolvedJsModulesPath.startsWith("/") ? "" : "/"}${resolvedJsModulesPath}`
    : `${httpOrigin}/${urlPrefix}/web_module/`;

  // Get or create the shared page client (one per unique WS URL)
  const pageClient = getPageClient(
    wsUrl,
    {
      interval: reconnectInterval,
      maxInterval: reconnectMaxInterval,
      maxRetries: reconnectMaxRetries,
      backoffMultiplier: reconnectBackoffMultiplier,
    },
    jsModulesPath,
  );

  // Create a per-component client that shares the page WebSocket
  const rootId = componentConfig.componentUuid;
  const client = new ReactPyDjangoClient({
    rootId,
    pageClient,
    mountElement,
    jsModulesPath,
    componentConfig,
  });

  // Replace the prerender element with the real element on the first layout update
  if (client.prerenderElement) {
    client.onMessage("layout-update", () => {
      if (client.prerenderElement && client.mountElement) {
        client.prerenderElement.replaceWith(client.mountElement);
        client.prerenderElement = null;
      }
    });
  }

  // Start rendering the component
  if (client.mountElement) {
    React.render(<Layout client={client} />, client.mountElement);

    // The mount-component message is sent by the ReactPyDjangoClient constructor:
    //   - If the shared socket is already OPEN → sent immediately
    //   - If still CONNECTING → queued and sent when the socket opens
    // On reconnect the client's onOpen callback handles re-mounting.
  } else {
    console.error(
      "ReactPy mount element is undefined, cannot render the component!",
    );
  }
}
