from reactpy import component, html


def thumbnail(video):
    return None


def like_button(video):
    return None


@component
def video(video):
    return html.div(
        thumbnail(video),
        html.a(
            {"href": video.url},
            html.h3(video.title),
            html.p(video.description),
        ),
        like_button(video),
    )
