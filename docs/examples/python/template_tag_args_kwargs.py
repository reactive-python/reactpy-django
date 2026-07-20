from reactpy import component


@component
def frog_greeter(number, name, species=""):
    return f"Hello #{number}, {name} the {species}!"
