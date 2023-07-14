from datetime import datetime

from reactpy import component, hooks, html


@component
def renders_per_second():
    start_time, _set_start_time = hooks.use_state(datetime.now())
    count, set_count = hooks.use_state(0)
    seconds_elapsed = (datetime.now() - start_time).total_seconds()

    @hooks.use_effect
    def run_tests():
        set_count(count + 1)

    rps = count / (seconds_elapsed or 0.01)

    return html.div(
        html.div(f"Total renders: {count}"),
        html.div(
            {"class_name": "rps", "data-rps": rps},
            f"Renders Per Second: {rps}",
        ),
    )


@component
def time_to_load():
    return html.div({"class_name": "ttl"}, "Loaded!")


NET_IO_GIANT_STR = "@" * 10000000


@component
def net_io_time_to_load():
    return html.div(
        {"class_name": "ttl"},
        html.div({"style": {"display": "none"}}, NET_IO_GIANT_STR),
        html.div("Loaded!"),
    )


@component
def events_per_second():
    count, set_count = hooks.use_state(0)
    start_time, _set_start_time = hooks.use_state(datetime.now())
    seconds_elapsed = (datetime.now() - start_time).total_seconds()
    eps = count / (seconds_elapsed or 0.01)

    async def event_handler(event):
        if event["target"]["value"] != str(count):
            set_count(count + 1)

    return html.div(
        html.div(f"Total events: {count}"),
        html.div(
            {"class_name": "eps", "data-eps": eps},
            f"Event Driven Renders Per Second: {eps}",
        ),
        html.input(
            {
                "type": "text",
                "default_value": "0",
                "data-count": str(count),
                "on_click": event_handler,
            }
        ),
    )
