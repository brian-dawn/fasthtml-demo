import os

from fasthtml.common import *
from mangum import Mangum


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
        render_all_the_rows(),
    )


def markdown_component():
    return Div(
        """
# Hello World
* This is a list
""",
        cls="marked",
    )


def render_all_the_rows():
    return Div(*[Div(f"Row {i}") for i in range(count)])


@rt("/")
def get():
    return Div("Click the button!", counter_component(), render_all_the_rows())


@app.post("/increment")
def increment():
    global count
    count += 1
    return count


# This is used so we can run the app in AWS.
handler = Mangum(app, lifespan="off")

# Otherwise we are running locally.
if __name__ == "__main__":
    serve()
