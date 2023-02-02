from idom import component, html

from django_idom.hooks import use_scope


@component
def my_component():
    my_scope = use_scope()
    return html.div(str(my_scope))
