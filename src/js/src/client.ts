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
    this.mountElement = props.mountElement;
    this.prerenderElement = props.prerenderElement;
    this.offlineElement = props.offlineElement;
    this.socket = createReconnectingWebSocket({
      url: this.urls.componentUrl,
      readyPromise: this.ready,
      ...props.reconnectOptions,
      onMessage: async ({ data }) => this.handleIncoming(JSON.parse(data)),
      onClose: () => {
        // If offlineElement exists, show it and hide the mountElement/prerenderElement
        if (this.prerenderElement) {
          this.prerenderElement.remove();
          this.prerenderElement = null;
        }
        if (this.offlineElement && this.mountElement) {
          this.mountElement.hidden = true;
          this.offlineElement.hidden = false;
        }
      },
      onOpen: () => {
        // If offlineElement exists, hide it and show the mountElement
        if (this.offlineElement && this.mountElement) {
          this.offlineElement.hidden = true;
          this.mountElement.hidden = false;
        }
      },
    });
  }

  sendMessage(message: any): void {
    this.socket.current?.send(JSON.stringify(message));
  }

  loadModule(moduleName: string): Promise<ReactPyModule> {
    return import(`${this.urls.jsModules}/${moduleName}`);
  }
}
