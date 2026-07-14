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
        // Re-mount the component when the WebSocket reconnects
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

  /** Send a mount-component message to the server so it constructs this component. */
  sendMountMessage(): void {
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
