import reflex as rx

from app.states.global_state import GlobalState

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
                # Wallet Section
                rx.el.div(
                    rx.el.p(
                        "WALLET",
                        class_name="text-xs font-bold text-slate-500 px-4 mb-4 tracking-widest",
                    ),
                    
                    # Wallet selector
                    rx.el.div(
                        rx.el.label(
                            "Select Wallet",
                            class_name="text-xs text-slate-500 px-4 mb-2 block",
                        ),
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
                                rx.el.option("Alice (Client)", value="Alice"),
                                rx.el.option("Bob (Worker)", value="Bob"),
                                on_change=GlobalState.set_current_user,
                                class_name="w-full bg-slate-900/50 border border-slate-700 text-slate-300 text-sm rounded-lg focus:ring-cyan-500 focus:border-cyan-500 block pl-10 p-2.5 appearance-none cursor-pointer hover:border-cyan-500/50 transition-colors",
                            ),
                            rx.icon(
                                "chevron-down",
                                class_name="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500 pointer-events-none",
                            ),
                            class_name="relative px-4",
                        ),
                    ),
                    
                    # Wallet info card
                    rx.cond(
                        GlobalState.current_user,
                        rx.el.div(
                            rx.el.div(
                                rx.icon("circle_user_round", class_name="h-8 w-8 text-cyan-400 mb-3"),
                                rx.el.p(
                                    GlobalState.current_user,
                                    class_name="text-sm font-medium text-slate-300 mb-1",
                                ),
                                rx.el.div(
                                    rx.el.span("Balance: ", class_name="text-xs text-slate-500"),
                                    rx.el.span(
                                        f"{GlobalState.wallet_balance} GAS",
                                        class_name="text-lg font-bold text-cyan-400",
                                    ),
                                ),
                                class_name="text-center",
                            ),
                            class_name="mx-4 mt-4 p-4 rounded-xl bg-gradient-to-br from-slate-800/60 to-slate-900/60 border border-slate-700",
                        ),
                        rx.el.div(
                            rx.el.p(
                                "No wallet connected",
                                class_name="text-sm text-slate-500 text-center",
                            ),
                            class_name="mx-4 mt-4 p-4 rounded-xl bg-slate-900/30 border border-slate-800",
                        ),
                    ),
                    
                    class_name="mb-6",
                ),

                rx.el.div(class_name="my-4 border-t border-slate-800/50 mx-4"),

                # Status section
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

