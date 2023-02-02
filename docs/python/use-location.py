from idom import component, html

from django_idom.hooks import use_location


@component
def my_component():
    my_location = use_location()
    return html.div(str(my_location))
