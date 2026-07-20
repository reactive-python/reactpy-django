from reactpy import component, html


@component
def root():
    return html.div("This text is from my client-side component")
