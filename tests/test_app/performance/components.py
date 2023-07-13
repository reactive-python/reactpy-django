from datetime import datetime

from reactpy import component, hooks, html


@component
def renders_per_second():
    start_time, _ = hooks.use_state(datetime.now())
    count, set_count = hooks.use_state(0)
    seconds_elapsed = (datetime.now() - start_time).total_seconds()

    @hooks.use_effect
    def run_tests():
        set_count(count + 1)

    return html.div(
        {"id": "test-runner"},
        html.div(f"Total renders: {count}"),
        html.div(
            {"class_name": "rps"},
            f"Renders Per Second: {count / (seconds_elapsed or 0.01)}",
        ),
    )
