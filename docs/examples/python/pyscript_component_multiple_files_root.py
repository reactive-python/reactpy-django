from reactpy import component, html, pyscript_component


@component
def server_side_component():
    return html.div(
        pyscript_component(
            "./example_project/my_app/components/root.py",
            "./example_project/my_app/components/child.py",
        ),
    )
