import reflex as rx

from app.states.global_state import GlobalState

def sidebar_item(icon: str, label: str, is_active: bool = False) -> rx.Component:

    """A reusable sidebar navigation item."""

    return rx.el.div(

        rx.icon(

            icon,

            class_name=rx.cond(

                is_active, "text-cyan-400 h-5 w-5", "text-slate-400 h-5 w-5"

            ),

        ),

        rx.el.span(

            label,

            class_name=rx.cond(

                is_active,

                "text-cyan-100 font-medium tracking-wide",

                "text-slate-400 font-medium group-hover:text-slate-200 transition-colors",

            ),

        ),

        class_name=rx.cond(

            is_active,

            "flex items-center gap-3 px-4 py-3 rounded-xl bg-cyan-500/10 border border-cyan-500/20 cursor-pointer shadow-[0_0_10px_rgba(34,211,238,0.1)]",

            "flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-slate-800/50 border border-transparent cursor-pointer group transition-all duration-200",

        ),

    )

def sidebar() -> rx.Component:

    """The persistent left sidebar component."""

    return rx.el.aside(

        rx.el.div(

            rx.el.div(

                rx.icon("hexagon", class_name="text-cyan-400 h-8 w-8 animate-pulse"),

                rx.el.h1(

                    "SmartPay",

                    class_name="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-purple-500 tracking-tighter",

                ),

                class_name="flex items-center gap-3",

            ),

            class_name="h-20 flex items-center px-6 border-b border-slate-800",

        ),

        rx.el.nav(

            rx.el.div(

                rx.el.p(

                    "MENU",

                    class_name="text-xs font-bold text-slate-500 px-4 mb-4 tracking-widest",

                ),

                rx.el.div(

                    sidebar_item("layout-dashboard", "Dashboard", is_active=True),

                    sidebar_item("briefcase", "My Jobs"),

                    sidebar_item("wallet", "Wallet"),

                    sidebar_item("history", "Transaction History"),

                    sidebar_item("settings", "Settings"),

                    class_name="flex flex-col gap-2 px-3",

                ),

                rx.el.div(class_name="my-4 border-t border-slate-800/50 mx-4"),

                rx.el.div(

                    rx.el.p(

                        "SETTINGS",

                        class_name="text-xs font-bold text-slate-500 px-4 mb-4 tracking-widest",

                    ),

                    rx.el.div(

                        rx.el.label(

                            rx.el.span(

                                "Worker Mode",

                                class_name="text-sm font-medium text-slate-300",

                            ),

                            rx.el.div(

                                rx.el.input(

                                    type="checkbox",

                                    default_checked=~GlobalState.user_mode,

                                    on_change=GlobalState.set_worker_mode,

                                    class_name="sr-only peer",

                                ),

                                rx.el.div(

                                    class_name="w-11 h-6 bg-slate-800 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-slate-300 after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-cyan-600 border border-slate-600"

                                ),

                                class_name="relative inline-flex items-center cursor-pointer",

                            ),

                            class_name="flex items-center justify-between px-4 py-2 hover:bg-slate-800/30 transition-colors cursor-pointer rounded-lg mx-2",

                        ),

                        class_name="mb-6",

                    ),

                    rx.el.div(

                        rx.el.p(

                            "WALLET CONNECT",

                            class_name="text-xs font-bold text-slate-500 px-4 mb-2 tracking-widest",

                        ),

                        rx.el.div(

                            rx.el.div(

                                rx.icon(

                                    "wallet",

                                    class_name="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-cyan-500",

                                ),

                                rx.el.select(

                                    rx.el.option(

                                        "Select Wallet",

                                        value="",

                                        disabled=True,

                                        selected=True,

                                    ),

                                    rx.el.option("Alice", value="Alice"),

                                    rx.el.option("Bob", value="Bob"),

                                    on_change=GlobalState.set_current_user,

                                    class_name="w-full bg-slate-900/50 border border-slate-700 text-slate-300 text-sm rounded-lg focus:ring-cyan-500 focus:border-cyan-500 block w-full pl-10 p-2.5 appearance-none cursor-pointer hover:border-cyan-500/50 transition-colors",

                                ),

                                rx.icon(

                                    "chevron-down",

                                    class_name="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500 pointer-events-none",

                                ),

                                class_name="relative",

                            ),

                            class_name="px-4",

                        ),

                    ),

                    class_name="pb-4",

                ),

                class_name="py-6",

            ),

            rx.el.div(

                rx.el.div(

                    rx.el.div(

                        rx.icon("user_pen", class_name="h-10 w-10 text-purple-400"),

                        rx.el.div(

                            rx.el.p(

                                "Status",

                                class_name="text-xs text-slate-400 uppercase font-bold",

                            ),

                            rx.el.p(

                                GlobalState.mode_label,

                                class_name="text-sm font-medium text-slate-200",

                            ),

                        ),

                        class_name="flex items-center gap-3",

                    ),

                    class_name="p-4 rounded-xl bg-slate-800/50 border border-slate-700 backdrop-blur-sm",

                ),

                class_name="mt-auto p-4 border-t border-slate-800",

            ),

            class_name="flex-1 flex flex-col overflow-y-auto",

        ),

        class_name="w-72 h-screen fixed left-0 top-0 flex flex-col bg-slate-950 border-r border-slate-800 shadow-2xl z-50",

    )

