from reactpy import component, html


@component
def root():
    from pyscript.js_modules import moment

    time: str = moment.default().format("YYYY-MM-DD HH:mm:ss")

    return html.div(
        {"id": "moment", "data-success": bool(time)},
        "Using the JavaScript package 'moment' to calculate time: ",
        time,
    )
