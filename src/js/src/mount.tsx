import { ReactPyDjangoClient } from "./client";
import { render } from "preact";
import { Layout } from "@reactpy/client/src/components";

export function mountComponent(
  mountElement: HTMLElement,
  host: string,
  urlPrefix: string,
  componentPath: string,
  resolvedJsModulesPath: string,
  reconnectStartInterval: number,
  reconnectMaxInterval: number,
  reconnectMaxRetries: number,
  reconnectBackoffMultiplier: number,
) {
  // Protocols
  const httpProtocol = window.location.protocol;
  const wsProtocol = `ws${httpProtocol === "https:" ? "s" : ""}:`;

  // WebSocket route (for Python components)
  let wsOrigin: string;
  if (host) {
    wsOrigin = `${wsProtocol}//${host}`;
  } else {
    wsOrigin = `${wsProtocol}//${window.location.host}`;
  }

  // HTTP route (for JavaScript modules)
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

  // Embed the initial HTTP path into the WebSocket URL
  const componentUrl = new URL(`${wsOrigin}/${urlPrefix}/${componentPath}`);
  componentUrl.searchParams.append("http_pathname", window.location.pathname);
  if (window.location.search) {
    componentUrl.searchParams.append("http_search", window.location.search);
  }

  // Configure a new ReactPy client
  const client = new ReactPyDjangoClient({
    urls: {
      componentUrl: componentUrl,
      jsModules: `${httpOrigin}/${jsModulesPath}`,
    },
    reconnectOptions: {
      startInterval: reconnectStartInterval,
      maxInterval: reconnectMaxInterval,
      backoffMultiplier: reconnectBackoffMultiplier,
      maxRetries: reconnectMaxRetries,
    },
    mountElement: mountElement,
    prerenderElement: document.getElementById(mountElement.id + "-prerender"),
    offlineElement: document.getElementById(mountElement.id + "-offline"),
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
