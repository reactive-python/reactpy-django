export type ReconnectOptions = {
    maxInterval?: number;
    maxRetries?: number;
    backoffRate?: number;
    intervalJitter?: number;
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
