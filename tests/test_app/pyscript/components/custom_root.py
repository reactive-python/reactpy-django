from reactpy import component, html


@component
def main():
    return html.div({"id": "custom-root"}, "Component with a custom root name.")
