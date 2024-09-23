# pylint: disable=assignment-from-no-return, unnecessary-lambda
from reactpy import component, html, use_state


def filter_videos(*_, **__): ...


def search_input(*_, **__): ...


def video_list(*_, **__): ...


@component
def searchable_video_list(videos):
    search_text, set_search_text = use_state("")
    found_videos = filter_videos(videos, search_text)

    return html._(
        search_input(
            {"onChange": lambda new_text: set_search_text(new_text)},
            value=search_text,
        ),
        video_list(
            videos=found_videos,
            empty_heading=f"No matches for “{search_text}”",
        ),
    )
