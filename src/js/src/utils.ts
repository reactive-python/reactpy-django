export function createReconnectingWebSocket(props: {
	url: string;
	readyPromise: Promise<void>;
	onOpen?: () => void;
	onMessage: (message: MessageEvent<any>) => void;
	onClose?: () => void;
	maxInterval?: number;
	maxRetries?: number;
	backoffRate?: number;
	intervalJitter?: number;
}) {
	const {
		maxInterval = 60000,
		maxRetries = 50,
		backoffRate = 1.1,
		intervalJitter = 0.1,
	} = props;

	const startInterval = 750;
	let retries = 0;
	let interval = startInterval;
	const closed = false;
	let everConnected = false;
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
			if (!everConnected) {
				console.info("ReactPy failed to connect!");
				return;
			}

			console.info("ReactPy disconnected!");
			if (props.onClose) {
				props.onClose();
			}

			if (retries >= maxRetries) {
				return;
			}

			const thisInterval = addJitter(interval, intervalJitter);
			console.info(
				`ReactPy reconnecting in ${(thisInterval / 1000).toPrecision(
					4
				)} seconds...`
			);
			setTimeout(connect, thisInterval);
			interval = nextInterval(interval, backoffRate, maxInterval);
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
	backoffRate: number,
	maxInterval: number
): number {
	return Math.min(
		currentInterval *
			// increase interval by backoff rate
			backoffRate,
		// don't exceed max interval
		maxInterval
	);
}

export function addJitter(interval: number, jitter: number): number {
	return (
		interval + (Math.random() * jitter * interval * 2 - jitter * interval)
	);
}

type reconnectOptions = {
	maxInterval?: number;
	maxRetries?: number;
	backoffRate?: number;
	intervalJitter?: number;
};
