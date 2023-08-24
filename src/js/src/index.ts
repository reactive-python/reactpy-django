import { mount, BaseReactPyClient, ReactPyClient } from "@reactpy/client";
import { createReconnectingWebSocket } from "./utils";
import { ReactPyDjangoClientProps, ReactPyUrls } from "./types";

export class ReactPyDjangoClient
	extends BaseReactPyClient
	implements ReactPyClient
{
	urls: ReactPyUrls;
	socket: { current?: WebSocket };

	constructor(props: ReactPyDjangoClientProps) {
		super();
		this.urls = props.urls;
		this.socket = createReconnectingWebSocket({
			readyPromise: this.ready,
			url: this.urls.componentUrl,
			onMessage: async ({ data }) =>
				this.handleIncoming(JSON.parse(data)),
			...props.reconnectOptions,
		});
	}

	sendMessage(message: any): void {
		this.socket.current?.send(JSON.stringify(message));
	}

	loadModule(moduleName: string) {
		return import(`${this.urls.jsModules}/${moduleName}`);
	}
}

export function mountComponent(
	mountElement: HTMLElement,
	host: string,
	urlPrefix: string,
	componentPath: string,
	resolvedJsModulesPath: string,
	reconnectMaxInterval: number,
	reconnectJitterMultiplier: number,
	reconnectBackoffMultiplier: number,
	reconnectMaxRetries: number
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

	// Set up the client
	const client = new ReactPyDjangoClient({
		urls: {
			componentUrl: `${wsOrigin}/${urlPrefix}/${componentPath}`,
			query: document.location.search,
			jsModules: `${httpOrigin}/${jsModulesPath}`,
		},
		reconnectOptions: {
			maxInterval: reconnectMaxInterval,
			intervalJitter: reconnectJitterMultiplier,
			backoffRate: reconnectBackoffMultiplier,
			maxRetries: reconnectMaxRetries,
		},
	});

	// Start rendering the component
	mount(mountElement, client);
}
