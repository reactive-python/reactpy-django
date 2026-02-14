import { ReactPyDjangoClient } from "./client";
import { render } from "preact";
import { Layout } from "@reactpy/client";

export function mountComponent(
  mountElement: HTMLElement,
  host: string,
  urlPrefix: string,
  componentPath: string,
  resolvedJsModulesPath: string,
  reconnectInterval: number,
  reconnectMaxInterval: number,
  reconnectMaxRetries: number,
  reconnectBackoffMultiplier: number,
) {
  // WebSocket route for component rendering
  const wsProtocol = `ws${window.location.protocol === "https:" ? "s" : ""}:`;
  const wsOrigin = host
    ? `${wsProtocol}//${host}`
    : `${wsProtocol}//${window.location.host}`;
  const componentUrl = new URL(`${wsOrigin}/${urlPrefix}/${componentPath}`);

  // Embed the initial HTTP path into the WebSocket URL
  componentUrl.searchParams.append("http_path", window.location.pathname);
  if (window.location.search) {
    componentUrl.searchParams.append("http_query_string", window.location.search);
  }

  // HTTP route for JavaScript modules
  const httpProtocol = window.location.protocol;
  let httpOrigin: string;
  let jsModulesPath: string;
  if (host) {
    httpOrigin = `${httpProtocol}//${host}`;
    jsModulesPath = `${urlPrefix}/web_module`;
  } else {
    httpOrigin = `${httpProtocol}//${window.location.host}`;
    if (resolvedJsModulesPath) {
      jsModulesPath = resolvedJsModulesPath;
    } else {
      jsModulesPath = `${urlPrefix}/web_module`;
    }
  }

  // Configure a new ReactPy client
  const client = new ReactPyDjangoClient({
    urls: {
      componentUrl: componentUrl,
      jsModulesPath: `${httpOrigin}/${jsModulesPath}`,
    },
    reconnectOptions: {
      interval: reconnectInterval,
      maxInterval: reconnectMaxInterval,
      maxRetries: reconnectMaxRetries,
      backoffMultiplier: reconnectBackoffMultiplier,
    },
    mountElement: mountElement,
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
    render(<Layout client={client} />, client.mountElement);
  } else {
    console.error(
      "ReactPy mount element is undefined, cannot render the component!",
    );
  }
}
