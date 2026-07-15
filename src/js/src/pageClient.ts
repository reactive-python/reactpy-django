import { type ReactPyModule } from "@reactpy/client";
import { createReconnectingWebSocket } from "./websocket";

type ComponentRecord = {
  handleIncoming: (message: any) => void;
  onOpen?: () => void;
  onClose?: () => void;
};

const pageClients = new Map<string, PageClient>();

export function getPageClient(
  wsUrl: URL,
  reconnectOptions: {
    interval: number;
    maxInterval: number;
    maxRetries: number;
    backoffMultiplier: number;
  },
  jsModulesPath: string,
): PageClient {
  const key = `${wsUrl.origin}${wsUrl.pathname}`;
  if (!pageClients.has(key)) {
    pageClients.set(
      key,
      new PageClient(key, wsUrl, reconnectOptions, jsModulesPath),
    );
  }
  return pageClients.get(key)!;
}

/**
 * Dispose a cached PageClient, close its WebSocket, and remove it from the
 * global map. Useful during SPA page transitions where the old page's WS
 * should no longer be reused.
 */
export function disposePageClient(key: string): void {
  const client = pageClients.get(key);
  if (client) {
    client.close();
    pageClients.delete(key);
  }
}

export class PageClient {
  private components: Map<string, ComponentRecord> = new Map();
  socket: { current?: WebSocket } = {};
  private readonly messageQueue: any[] = [];
  private readonly jsModulesPath: string;

  constructor(
    private readonly key: string,
    private wsUrl: URL,
    reconnectOptions: {
      interval: number;
      maxInterval: number;
      maxRetries: number;
      backoffMultiplier: number;
    },
    jsModulesPath: string,
  ) {
    this.jsModulesPath = jsModulesPath;

    // Immediately-resolved promise — the shared socket connects right away
    const immediatePromise = Promise.resolve();

    this.socket = createReconnectingWebSocket({
      url: wsUrl,
      readyPromise: immediatePromise,
      ...reconnectOptions,
      onMessage: async ({ data }) => this.handleIncoming(JSON.parse(data)),
      onOpen: () => {
        // Notify all registered components that the connection is back
        for (const [, record] of this.components) {
          if (record.onOpen) record.onOpen();
        }
        // Drain queued messages
        while (this.messageQueue.length > 0) {
          this.sendRaw(this.messageQueue.shift());
        }
      },
      onClose: () => {
        for (const [, record] of this.components) {
          if (record.onClose) record.onClose();
        }
      },
    });
  }

  registerComponent(rootId: string, record: ComponentRecord): void {
    this.components.set(rootId, record);
  }

  unregisterComponent(rootId: string): void {
    this.components.delete(rootId);
  }

  /** Tag an outgoing message with rootId and send it through the shared socket. */
  sendMessage(rootId: string, message: any): void {
    message.rootId = rootId;
    this.sendRaw(message);
  }

  private sendRaw(message: any): void {
    if (
      this.socket.current &&
      this.socket.current.readyState === WebSocket.OPEN
    ) {
      this.socket.current.send(JSON.stringify(message));
    } else {
      this.messageQueue.push(message);
    }
  }

  /** Route an incoming message to the correct component by rootId. */
  private handleIncoming(message: any): void {
    const { rootId } = message;
    if (rootId && this.components.has(rootId)) {
      // Strip rootId before forwarding to the component's handler
      const componentMessage = { ...message };
      delete componentMessage.rootId;
      this.components.get(rootId)!.handleIncoming(componentMessage);
    }
  }

  /** Close the underlying WebSocket and clear all registered components. */
  close(): void {
    if (this.socket.current) {
      this.socket.current.close();
      this.socket.current = undefined;
    }
    this.components.clear();
  }

  /**
   * Dispose this PageClient — closes the WebSocket, clears components, and
   * removes the entry from the global cache. Call during SPA page transitions
   * or when the page is fully torn down.
   */
  dispose(): void {
    this.close();
    disposePageClient(this.key);
  }

  loadModule(moduleName: string): Promise<ReactPyModule> {
    return import(`${this.jsModulesPath}${moduleName}`);
  }
}
