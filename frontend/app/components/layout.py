import reflex as rx

from app.components.sidebar import sidebar

def layout(content: rx.Component) -> rx.Component:

    """The main application layout wrapper."""

    return rx.el.div(

        sidebar(),

        rx.el.main(

            rx.el.div(content, class_name="max-w-7xl mx-auto"),

            class_name="ml-72 min-h-screen flex-1 bg-slate-900 p-8 text-slate-200",

        ),

        class_name="flex min-h-screen bg-slate-900 font-['Inter']",

    )

