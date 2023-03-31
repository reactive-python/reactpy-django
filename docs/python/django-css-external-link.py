from reactpy import component, html


@component
def my_component():
    return html.div(
        html.link(
            {"rel": "stylesheet", "href": "https://example.com/external-styles.css"}
        ),
        html.button("My Button!"),
    )
