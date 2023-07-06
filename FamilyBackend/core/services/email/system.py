from decouple import config
from django.template.loader import render_to_string


def render_email(file: str, context: dict):
    context["base_url"] = config(
        "FRONTEND_URL",
        config("FRONTEND_URL"),
    )
    return render_to_string(file, context)
