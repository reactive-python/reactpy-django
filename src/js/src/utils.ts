export function createReconnectingWebSocket(props: {
  url: URL;
  readyPromise: Promise<void>;
  onOpen?: () => void;
  onMessage: (message: MessageEvent<any>) => void;
  onClose?: () => void;
  startInterval: number;
  maxInterval: number;
  maxRetries: number;
  backoffMultiplier: number;
}) {
  const { startInterval, maxInterval, maxRetries, backoffMultiplier } = props;
  let retries = 0;
  let interval = startInterval;
  let everConnected = false;
  const closed = false;
  const socket: { current?: WebSocket } = {};

  const connect = () => {
    if (closed) {
      return;
    }
    socket.current = new WebSocket(props.url);
    socket.current.onopen = () => {
      everConnected = true;
      console.info("ReactPy connected!");
      interval = startInterval;
      retries = 0;
      if (props.onOpen) {
        props.onOpen();
      }
    };
    socket.current.onmessage = props.onMessage;
    socket.current.onclose = () => {
      if (props.onClose) {
        props.onClose();
      }
      if (!everConnected) {
        console.info("ReactPy failed to connect!");
        return;
      }
      console.info("ReactPy disconnected!");
      if (retries >= maxRetries) {
        console.info("ReactPy connection max retries exhausted!");
        return;
      }
      console.info(
        `ReactPy reconnecting in ${(interval / 1000).toPrecision(4)} seconds...`,
      );
      setTimeout(connect, interval);
      interval = nextInterval(interval, backoffMultiplier, maxInterval);
      retries++;
    };
  };

  props.readyPromise
    .then(() => console.info("Starting ReactPy client..."))
    .then(connect);

  return socket;
}

export function nextInterval(
  currentInterval: number,
  backoffMultiplier: number,
  maxInterval: number,
): number {
  return Math.min(
    // increase interval by backoff multiplier
    currentInterval * backoffMultiplier,
    // don't exceed max interval
    maxInterval,
  );
}
