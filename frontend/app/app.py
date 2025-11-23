import reflex as rx

from app.components.layout import layout
from app.components.landing import landing_page
from app.components.client_view import client_view
from app.components.worker_view import worker_view
from app.states.global_state import GlobalState

def index() -> rx.Component:
    """Landing page with role selection."""
    return landing_page()

def app_page() -> rx.Component:
    """Main application page based on selected role."""
    return layout(rx.cond(GlobalState.user_mode, client_view(), worker_view()))

app = rx.App(
    theme=rx.theme(appearance="light"),
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
    ],
)

# Landing page
app.add_page(index, route="/")

# Main app page with polling
app.add_page(app_page, route="/app", on_load=GlobalState.start_polling)

