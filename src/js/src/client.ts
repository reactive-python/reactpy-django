import {
  ReactPyClient,
  createReconnectingWebSocket,
  type GenericReactPyClientProps,
} from "@reactpy/client";

export class ReactPyDjangoClient extends ReactPyClient {
  prerenderElement: HTMLElement | null = null;
  offlineElement: HTMLElement | null = null;

  constructor(props: GenericReactPyClientProps) {
    super(props);
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
}
