from django.shortcuts import render


def renders_per_second(request, count: int = 1):
    return render(
        request,
        "renders_per_second.html",
        {"count": range(max(count, 1))},
    )


def time_to_load(request, count: int = 1):
    return render(
        request,
        "time_to_load.html",
        {"count": range(max(count, 1))},
    )


def net_io_time_to_load(request, count: int = 1):
    return render(
        request,
        "net_io_time_to_load.html",
        {"count": range(max(count, 1))},
    )


def events_per_second(request, count: int = 1):
    return render(
        request,
        "events_per_second.html",
        {"count": range(max(count, 1))},
    )
