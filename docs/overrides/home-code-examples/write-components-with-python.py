from reactpy import component, html


@component
def video_list(videos, empty_heading):
    count = len(videos)
    heading = empty_heading
    if count > 0:
        noun = "Videos" if count > 1 else "Video"
        heading = f"{count} {noun}"

    return html.section(
        html.h2(heading),
        [video(video) for video in videos],
    )
