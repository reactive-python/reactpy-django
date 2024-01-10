import { mount } from "./mount";
import { ReactPyDjangoClient } from "./client";

export function mountComponent(
	mountElement: HTMLElement,
	host: string,
	urlPrefix: string,
	componentPath: string,
	resolvedJsModulesPath: string,
	reconnectStartInterval: number,
	reconnectMaxInterval: number,
	reconnectMaxRetries: number,
	reconnectBackoffMultiplier: number
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
	});

	// Start rendering the component
	mount(mountElement, client);
}
