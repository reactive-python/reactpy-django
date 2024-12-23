export type ReconnectOptions = {
  startInterval: number;
  maxInterval: number;
  maxRetries: number;
  backoffMultiplier: number;
};

export type ReactPyUrls = {
  componentUrl: URL;
  query: string;
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
  onSubmitCallback: (data: Object) => void;
  formId: string;
}

export interface SetCookieProps {
  cookie: string;
  completeCallback: (success: boolean) => void;
}
