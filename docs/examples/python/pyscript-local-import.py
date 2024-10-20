from reactpy import component, html


@component
def root():
    from pyscript.js_modules import moment

    return html.div(
        {"id": "moment"},
        "Using the JavaScript package 'moment' to calculate time: ",
        moment.default().format("YYYY-MM-DD HH:mm:ss"),
    )
