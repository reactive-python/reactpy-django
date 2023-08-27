export type ReconnectOptions = {
    startInterval: number;
    maxInterval: number;
    maxRetries: number;
    backoffMultiplier: number;
}

export type ReactPyUrls = {
    componentUrl: string;
    query: string;
    jsModules: string;
}

export type ReactPyDjangoClientProps = {
    urls: ReactPyUrls;
    reconnectOptions: ReconnectOptions;
}
