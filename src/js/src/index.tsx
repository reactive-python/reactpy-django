import { ReactPyDjangoClient } from "./client";
import React from "react";
import ReactDOM from "react-dom";
import { Layout } from "@reactpy/client/src/components";
import { DjangoFormProps } from "./types";

/**
 * Interface used to bind a ReactPy node to React.
 */
export function bind(node) {
  return {
    create: (type, props, children) =>
      React.createElement(type, props, ...children),
    render: (element) => {
      ReactDOM.render(element, node);
    },
    unmount: () => ReactDOM.unmountComponentAtNode(node),
  };
}

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
  let httpProtocol = window.location.protocol;
  let wsProtocol = `ws${httpProtocol === "https:" ? "s" : ""}:`;

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
  let componentUrl = new URL(`${wsOrigin}/${urlPrefix}/${componentPath}`);
  componentUrl.searchParams.append("http_pathname", window.location.pathname);
  if (window.location.search) {
    componentUrl.searchParams.append("http_search", window.location.search);
  }

  // Configure a new ReactPy client
  const client = new ReactPyDjangoClient({
    urls: {
      componentUrl: componentUrl,
      query: document.location.search,
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
    client.onMessage("layout-update", ({ path, model }) => {
      if (client.prerenderElement) {
        client.prerenderElement.replaceWith(client.mountElement);
        client.prerenderElement = null;
      }
    });
  }

  // Start rendering the component
  ReactDOM.render(<Layout client={client} />, client.mountElement);
}

export function DjangoForm({
  onSubmitCallback,
  formId,
}: DjangoFormProps): null {
  React.useEffect(() => {
    const form = document.getElementById(formId) as HTMLFormElement;

    // Submission event function
    const onSubmitEvent = (event) => {
      event.preventDefault();
      const formData = new FormData(form);
      console.log(Object.fromEntries(formData));
      onSubmitCallback(Object.fromEntries(formData));
    };

    // Bind the event listener
    if (form) {
      form.addEventListener("submit", onSubmitEvent);
    }

    // Unbind the event listener when the component dismounts
    return () => {
      if (form) {
        form.removeEventListener("submit", onSubmitEvent);
      }
    };
  }, []);

  return null;
}
