from reactpy import component, html, pyscript_component


@component
def server_side_component():
    return html.div(
        "This text is from my server-side component",
        pyscript_component(
            "./example_project/my_app/components/root.py",
        ),
    )
