from time import sleep

from reactpy import component, html


@component
def root():
    sleep(1)
    return html.div("Hello, World!")
