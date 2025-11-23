import reflex as rx
from app.states.global_state import GlobalState

def nav_item(icon: str, label: str, view_name: str) -> rx.Component:
    """Navigation item with active state."""
    is_active = GlobalState.current_view == view_name
    
    return rx.el.div(
        rx.icon(
            icon,
            class_name=rx.cond(
                is_active,
                "text-cyan-400 h-5 w-5",
                "text-slate-400 h-5 w-5"
            ),
        ),
        rx.el.span(
            label,
            class_name=rx.cond(
                is_active,
                "text-cyan-100 font-medium",
                "text-slate-400 font-medium"
            ),
        ),
        on_click=GlobalState.navigate_to(view_name),
        class_name=rx.cond(
            is_active,
            "flex items-center gap-3 px-4 py-3 rounded-xl bg-cyan-500/10 border border-cyan-500/20 cursor-pointer",
            "flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-slate-800/50 border border-transparent cursor-pointer transition-all"
        ),
    )

def sidebar() -> rx.Component:
    """The persistent left sidebar component."""

    return rx.el.aside(
        # Header
        rx.el.div(
            rx.el.div(
                rx.icon("shield_check", class_name="text-cyan-400 h-8 w-8"),
                rx.el.h1(
                    "GigShield",
                    class_name="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-purple-500 tracking-tighter",
                ),
                class_name="flex items-center gap-3",
            ),
            class_name="h-20 flex items-center px-6 border-b border-slate-800",
        ),

        rx.el.nav(
            rx.el.div(
                # Navigation
                rx.el.div(
                    rx.el.p(
                        "MENU",
                        class_name="text-xs font-bold text-slate-500 px-4 mb-4 tracking-widest",
                    ),
                    rx.cond(
                        GlobalState.user_mode,
                        # Client navigation
                        rx.el.div(
                            nav_item("circle_plus", "Create New Job", "create"),
                            nav_item("briefcase", "My Jobs", "jobs"),
                            nav_item("wallet", "Wallet", "wallet"),
                            class_name="flex flex-col gap-2 px-3",
                        ),
                        # Worker navigation
                        rx.el.div(
                            nav_item("briefcase", "Available Jobs", "create"),
                            nav_item("check_check", "My Work", "jobs"),
                            nav_item("wallet", "Wallet", "wallet"),
                            class_name="flex flex-col gap-2 px-3",
                        ),
                    ),
                    class_name="mb-6",
                ),

                rx.el.div(class_name="my-4 border-t border-slate-800/50 mx-4"),

                # Status
                rx.el.div(
                    rx.el.p(
                        "STATUS",
                        class_name="text-xs font-bold text-slate-500 px-4 mb-4 tracking-widest",
                    ),
                    rx.el.div(
                        rx.icon("user_pen", class_name="h-8 w-8 text-purple-400"),
                        rx.el.div(
                            rx.el.p(
                                "Current Mode",
                                class_name="text-xs text-slate-400 uppercase font-bold",
                            ),
                            rx.el.p(
                                GlobalState.mode_label,
                                class_name="text-sm font-medium text-slate-200",
                            ),
                        ),
                        class_name="flex items-center gap-3 mx-4 p-4 rounded-xl bg-slate-800/50 border border-slate-700",
                    ),
                ),

                class_name="py-6",
            ),

            # Bottom section
            rx.el.div(
                # Switch Role button
                rx.link(
                    rx.el.div(
                        rx.icon("arrow_left", class_name="h-4 w-4"),
                        rx.el.span(
                            "Switch Role",
                            class_name="text-sm font-medium",
                        ),
                        class_name="flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-gradient-to-r from-cyan-500/10 to-purple-500/10 border border-cyan-500/30 hover:border-cyan-500/50 text-cyan-300 hover:text-cyan-200 transition-all duration-200 cursor-pointer",
                    ),
                    href="/",
                ),
                class_name="mt-auto p-4 border-t border-slate-800",
            ),

            class_name="flex-1 flex flex-col overflow-y-auto",
        ),

        class_name="w-72 h-screen fixed left-0 top-0 flex flex-col bg-slate-950 border-r border-slate-800 shadow-2xl z-50",
    )
