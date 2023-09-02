from reactpy import component, html, use_state


def filter_videos(videos, search_text):
    return None


def search_input(dictionary, value):
    return None


def video_list(videos, empty_heading):
    return None


@component
def searchable_video_list(videos):
    search_text, set_search_text = use_state("")
    found_videos = filter_videos(videos, search_text)

    return html._(
        search_input(
            {"on_change": lambda new_text: set_search_text(new_text)},
            value=search_text,
        ),
        video_list(
            videos=found_videos,
            empty_heading=f"No matches for “{search_text}”",
        ),
    )
