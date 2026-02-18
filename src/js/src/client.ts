import {
  BaseReactPyClient,
  createReconnectingWebSocket,
  type GenericReactPyClientProps,
  type ReactPyClientInterface,
  type ReactPyModule,
  type ReactPyUrls,
} from "@reactpy/client";

export class ReactPyDjangoClient
  extends BaseReactPyClient
  implements ReactPyClientInterface
{
  urls: ReactPyUrls;
  socket: { current?: WebSocket };
  mountElement: HTMLElement;
  prerenderElement: HTMLElement | null = null;
  offlineElement: HTMLElement | null = null;
  private readonly messageQueue: any[] = [];

  constructor(props: GenericReactPyClientProps) {
    super();

    this.urls = props.urls;
    this.mountElement = props.mountElement;
    this.prerenderElement = document.getElementById(
      props.mountElement.id + "-prerender",
    );
    this.offlineElement = document.getElementById(
      props.mountElement.id + "-offline",
    );

    this.socket = createReconnectingWebSocket({
      url: this.urls.componentUrl,
      readyPromise: this.ready,
      ...props.reconnectOptions,
      // onMessage: Use standard ReactPy message routing
      onMessage: async ({ data }) => this.handleIncoming(JSON.parse(data)),
      // onClose: If offlineElement exists, show it and hide the mountElement/prerenderElement
      onClose: () => {
        if (this.prerenderElement) {
          this.prerenderElement.remove();
          this.prerenderElement = null;
        }
        if (this.offlineElement && this.mountElement) {
          this.mountElement.hidden = true;
          this.offlineElement.hidden = false;
        }
      },
      // onOpen: If offlineElement exists, hide it and show the mountElement
      onOpen: () => {
        if (this.offlineElement && this.mountElement) {
          this.offlineElement.hidden = true;
          this.mountElement.hidden = false;
        }
      },
    });
  }

  sendMessage(message: any): void {
    if (
      this.socket.current &&
      this.socket.current.readyState === WebSocket.OPEN
    ) {
      this.socket.current.send(JSON.stringify(message));
    } else {
      this.messageQueue.push(message);
    }
  }

  loadModule(moduleName: string): Promise<ReactPyModule> {
    return import(`${this.urls.jsModulesPath}${moduleName}`);
  }
}
