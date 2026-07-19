import { type ReactPyModule } from "@reactpy/client";
import { createReconnectingWebSocket } from "./websocket";

type ComponentRecord = {
  handleIncoming: (message: any) => void;
  onOpen?: () => void;
  onClose?: () => void;
};

const pageClients = new Map<string, PageClient>();

function pageClientKey(wsUrl: URL): string {
  return `${wsUrl.origin}${wsUrl.pathname}`;
}

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
  const key = pageClientKey(wsUrl);
  if (!pageClients.has(key)) {
    pageClients.set(
      key,
      new PageClient(key, wsUrl, reconnectOptions, jsModulesPath),
    );
  }
  return pageClients.get(key)!;
}

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
  private connected = false;

  constructor(
    private readonly key: string,
    private wsUrl: URL,
    private reconnectOptions: {
      interval: number;
      maxInterval: number;
      maxRetries: number;
      backoffMultiplier: number;
    },
    jsModulesPath: string,
  ) {
    this.jsModulesPath = jsModulesPath;
  }

  /**
   * Start the shared WebSocket connection. Safe to call multiple times —
   * only the first call triggers the connection. Call this after at least
   * one component has subscribed its layout-update handler, so there is no
   * race between the server's initial render and the handler registration.
   */
  connect(): void {
    if (this.connected) return;
    this.connected = true;

    this.socket = createReconnectingWebSocket({
      url: this.wsUrl,
      readyPromise: Promise.resolve(),
      ...this.reconnectOptions,
      onMessage: async ({ data }) => this.handleIncoming(JSON.parse(data)),
      onOpen: () => {
        for (const [, record] of this.components) {
          if (record.onOpen) record.onOpen();
        }
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
    const rootId = message.rootId;
    if (rootId && this.components.has(rootId)) {
      const componentMessage = { ...message };
      delete componentMessage.rootId;
      this.components.get(rootId)!.handleIncoming(componentMessage);
    }
  }

  close(): void {
    if (this.socket.current) {
      this.socket.current.close();
      this.socket.current = undefined;
    }
    this.components.clear();
  }

  dispose(): void {
    this.close();
    disposePageClient(this.key);
  }

  loadModule(moduleName: string): Promise<ReactPyModule> {
    return import(`${this.jsModulesPath}${moduleName}`);
  }
}
