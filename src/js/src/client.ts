import {
  BaseReactPyClient,
  type ReactPyClientInterface,
  type ReactPyModule,
} from "@reactpy/client";
import { PageClient } from "./pageClient";
import type { ComponentConfig } from "./mount";

export type ReactPyDjangoClientProps = {
  rootId: string;
  pageClient: PageClient;
  mountElement: HTMLElement;
  jsModulesPath: string;
  componentConfig: ComponentConfig;
};

export class ReactPyDjangoClient
  extends BaseReactPyClient
  implements ReactPyClientInterface
{
  readonly rootId: string;
  readonly pageClient: PageClient;
  readonly mountElement: HTMLElement;
  readonly prerenderElement: HTMLElement | null = null;
  readonly offlineElement: HTMLElement | null = null;
  readonly jsModulesPath: string;
  private readonly componentConfig: ComponentConfig;
  private mountSent = false;

  constructor(props: ReactPyDjangoClientProps) {
    super();

    this.rootId = props.rootId;
    this.pageClient = props.pageClient;
    this.mountElement = props.mountElement;
    this.jsModulesPath = props.jsModulesPath;
    this.componentConfig = props.componentConfig;

    this.prerenderElement = document.getElementById(
      props.mountElement.id + "-prerender",
    );
    this.offlineElement = document.getElementById(
      props.mountElement.id + "-offline",
    );

    // Register with the shared page client for message routing
    this.pageClient.registerComponent(this.rootId, {
      handleIncoming: (message: any) => this.handleIncoming(message),
      onOpen: () => {
        // Reset mount guard on (re)connect — the server drops all component
        // state and we must send mount-component again.
        this.mountSent = false;
        this.sendMountMessage();
        if (this.offlineElement && this.mountElement) {
          this.offlineElement.hidden = true;
          this.mountElement.hidden = false;
        }
      },
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
    });
  }

  /**
   * Override onMessage to trigger the shared WebSocket connection on the
   * first handler subscription. This prevents a race where the initial
   * layout-update from the server arrives before Layout's useEffect has
   * registered the "layout-update" handler.
   *
   * For components created after the shared socket is already open (e.g.
   * after SPA navigation or lazy-loading), the mount-component message
   * is sent here — onOpen won't fire again.
   */
  onMessage(type: string, handler: (message: any) => void): () => void {
    const unsubscribe = super.onMessage(type, handler);
    this.pageClient.connect();
    if (
      !this.mountSent &&
      this.pageClient.socket.current?.readyState === WebSocket.OPEN
    ) {
      this.sendMountMessage();
    }
    return unsubscribe;
  }

  /** Send a mount-component message to the server so it constructs this component. */
  private sendMountMessage(): void {
    if (this.mountSent) return;
    this.mountSent = true;
    this.pageClient.sendMessage(this.rootId, {
      type: "mount-component",
      rootId: this.rootId,
      dottedPath: this.componentConfig.dottedPath,
      componentUuid: this.componentConfig.componentUuid,
      hasArgs: Boolean(this.componentConfig.hasArgs),
    });
  }

  sendMessage(message: any): void {
    this.pageClient.sendMessage(this.rootId, message);
  }

  loadModule(moduleName: string): Promise<ReactPyModule> {
    return import(`${this.jsModulesPath}${moduleName}`);
  }

  destroy(): void {
    this.pageClient.unregisterComponent(this.rootId);
  }
}
