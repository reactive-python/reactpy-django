import {
	BaseReactPyClient,
	ReactPyClient,
	ReactPyModule,
} from "@reactpy/client";
import { createReconnectingWebSocket } from "./utils";
import { ReactPyDjangoClientProps, ReactPyUrls } from "./types";

export class ReactPyDjangoClient
	extends BaseReactPyClient
	implements ReactPyClient
{
	urls: ReactPyUrls;
	socket: { current?: WebSocket };
	mountElement: HTMLElement | null = null;
	prerenderElement: HTMLElement | null = null;
	offlineElement: HTMLElement | null = null;

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
		this.mountElement = props.mountElement;
		this.prerenderElement = props.prerenderElement;
		this.offlineElement = props.offlineElement;
	}

	sendMessage(message: any): void {
		this.socket.current?.send(JSON.stringify(message));
	}

	loadModule(moduleName: string): Promise<ReactPyModule> {
		return import(`${this.urls.jsModules}/${moduleName}`);
	}
}
