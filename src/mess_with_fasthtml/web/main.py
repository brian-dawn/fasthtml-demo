import os

from fasthtml.common import *


hdrs = (
    MarkdownJS(),
    HighlightJS(langs=["python", "javascript", "html", "css"]),
    Link(
        rel="stylesheet",
        href="https://cdn.jsdelivr.net/npm/sakura.css/css/sakura.css",
        type="text/css",
    ),
)

# Turn off live in production.
not_live = os.environ.get("NO_LIVE", False)

app, rt = fast_app(live=not not_live, hdrs=hdrs, key_fname="/tmp/sesskey")


count = 0


def counter_component():
    return (
        Button(
            f"{count}",
            hx_post="/increment",
            hx_target="#count",
            hx_swap="innerHTML",
            id="count",
        ),
    )


def markdown_component():
    return Div(
        """
# Hello World
* This is a list
* This is a list
""",
        cls="marked",
    )


@rt("/")
def get():
    return Div(
        "hello world",
        counter_component(),
        markdown_component(),
    )


@app.post("/increment")
def increment():
    global count
    count += 1
    return count


serve()
