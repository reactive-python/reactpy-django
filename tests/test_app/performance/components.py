from django.utils import timezone
from reactpy import component, hooks, html


@component
def renders_per_second():
    start_time, _set_start_time = hooks.use_state(timezone.now())
    count, set_count = hooks.use_state(0)
    seconds_elapsed = (timezone.now() - start_time).total_seconds()

    @hooks.use_effect
    def run_tests():
        set_count(count + 1)

    rps = count / (seconds_elapsed or 0.01)

    return html.div(
        html.div(f"Total renders: {count}"),
        html.div(
            {"className": "rps", "data-rps": rps},
            f"Renders Per Second: {rps}",
        ),
    )


@component
def time_to_load():
    return html.div({"className": "ttl"}, "Loaded!")


GIANT_STR_10MB = "@" * 10000000


@component
def net_io_time_to_load():
    return html.div(
        {"className": "ttl"},
        html.div({"style": {"display": "none"}}, GIANT_STR_10MB),
        html.div("Loaded!"),
    )


GIANT_STR_1MB = "@" * 1000000


@component
def mixed_time_to_load():
    start_time, _set_start_time = hooks.use_state(timezone.now())
    count, set_count = hooks.use_state(0)
    seconds_elapsed = (timezone.now() - start_time).total_seconds()

    @hooks.use_effect
    def run_tests():
        set_count(count + 1)

    rps = count / (seconds_elapsed or 0.01)

    return html.div(
        html.div({"style": {"display": "none"}}, GIANT_STR_1MB),
        html.div(f"Total renders: {count}"),
        html.div(
            {"className": "rps", "data-rps": rps},
            f"Renders Per Second: {rps}",
        ),
    )


@component
def event_renders_per_second():
    count, set_count = hooks.use_state(0)
    start_time, _set_start_time = hooks.use_state(timezone.now())
    seconds_elapsed = (timezone.now() - start_time).total_seconds()
    erps = count / (seconds_elapsed or 0.01)

    async def event_handler(event):
        if event["target"]["value"] != str(count):
            set_count(count + 1)

    return html.div(
        html.div(f"Total events: {count}"),
        html.div(
            {"className": "erps", "data-erps": erps},
            f"Event Renders Per Second: {erps}",
        ),
        html.input({
            "type": "text",
            "defaultValue": "0",
            "data-count": str(count),
            "onClick": event_handler,
        }),
    )


@component
def event_timing(worker_num: int):
    clicked, set_clicked = hooks.use_state(False)

    async def event_handler(_event):
        set_clicked(True)

    return html.div(
        html.input(
            {
                "className": "et",
                "data-clicked": clicked,
                "data-worker-num": worker_num,
                "value": f"Clicked: {clicked}",
                "type": "button",
                "onClick": event_handler,
            },
        ),
    )
