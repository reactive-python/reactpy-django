export type ReconnectOptions = {
  startInterval: number;
  maxInterval: number;
  maxRetries: number;
  backoffMultiplier: number;
};

export type ReactPyUrls = {
  componentUrl: URL;
  jsModules: string;
};

export type ReactPyDjangoClientProps = {
  urls: ReactPyUrls;
  reconnectOptions: ReconnectOptions;
  mountElement: HTMLElement | null;
  prerenderElement: HTMLElement | null;
  offlineElement: HTMLElement | null;
};

export interface DjangoFormProps {
  onSubmitCallback: (data: object) => void;
  formId: string;
}

export interface HttpRequestProps {
  method: string;
  url: string;
  body: string;
  callback: (status: number, response: string) => void;
}
