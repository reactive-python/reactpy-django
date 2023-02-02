from idom import component, html


@component
def my_component():
    return html.div(
        html.script({"src": "https://example.com/external-scripts.js"}),
        html.button("My Button!"),
    )
