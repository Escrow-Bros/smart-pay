import reflex as rx
from app.states.global_state import GlobalState

def my_jobs_view() -> rx.Component:
    """View for client's job history."""
    return rx.el.div(
        # Header
        rx.el.div(
            rx.el.h2("My Jobs", class_name="text-3xl font-bold text-white mb-2"),
            rx.el.p(
                "Track and manage your posted gigs.",
                class_name="text-slate-400",
            ),
            class_name="mb-8",
        ),
        
        # Job list
        rx.cond(
            GlobalState.is_loading_jobs,
            rx.el.div(
                rx.el.span("Loading...", class_name="text-slate-400"),
                class_name="text-center py-8",
            ),
            rx.cond(
                GlobalState.client_jobs.length() > 0,
                rx.foreach(
                    GlobalState.client_jobs,
                    lambda job: rx.el.div(
                        rx.el.div(
                            rx.el.div(
                                rx.el.span(f"Job #{job['job_id']}", class_name="text-cyan-400 font-semibold"),
                                rx.el.span(
                                    job['status'],
                                    class_name=rx.cond(
                                        job['status'] == "OPEN",
                                        "bg-green-500/20 text-green-400 px-3 py-1 rounded-full text-xs",
                                        rx.cond(
                                            job['status'] == "LOCKED",
                                            "bg-yellow-500/20 text-yellow-400 px-3 py-1 rounded-full text-xs",
                                            "bg-blue-500/20 text-blue-400 px-3 py-1 rounded-full text-xs",
                                        ),
                                    ),
                                ),
                                class_name="flex justify-between items-center mb-2",
                            ),
                            rx.el.p(job['description'], class_name="text-slate-300 text-sm mb-2"),
                            rx.el.div(
                                rx.el.span(f"{job['amount']} GAS", class_name="text-cyan-400 font-semibold"),
                                rx.el.span(f" • {job['created_at']}", class_name="text-slate-500 text-xs"),
                                class_name="flex items-center gap-2",
                            ),
                        ),
                        class_name="bg-slate-900/50 border border-slate-800 rounded-xl p-4 mb-4 hover:border-slate-700 transition-colors",
                    ),
                ),
                rx.el.div(
                    rx.el.p("No jobs yet. Create your first job!", class_name="text-slate-400"),
                    class_name="text-center py-8 bg-slate-900/30 border border-slate-800 rounded-xl",
                ),
            ),
        ),
        
        class_name="animate-in fade-in duration-500",
    )

def wallet_view() -> rx.Component:
    """Wallet details view."""
    return rx.el.div(
        # Header
        rx.el.div(
            rx.el.h2("Wallet", class_name="text-3xl font-bold text-white mb-2"),
            rx.el.p(
                "View your wallet details and balance.",
                class_name="text-slate-400",
            ),
            class_name="mb-8",
        ),
        
        # Wallet card
        rx.el.div(
            rx.el.div(
                rx.icon("wallet", class_name="h-16 w-16 text-cyan-400 mb-6"),
                
                # User name
                rx.el.div(
                    rx.el.p("Connected as", class_name="text-xs text-slate-500 mb-1"),
                    rx.el.p(
                        GlobalState.current_user,
                        class_name="text-xl font-semibold text-white mb-6",
                    ),
                ),
                
                # Address
                rx.el.div(
                    rx.el.p("Wallet Address", class_name="text-xs text-slate-500 mb-2"),
                    rx.el.div(
                        rx.el.code(
                            GlobalState.wallet_address,
                            class_name="text-sm text-cyan-400 bg-slate-900/50 px-4 py-2 rounded-lg font-mono",
                        ),
                        rx.el.button(
                            rx.icon("copy", class_name="h-4 w-4"),
                            on_click=GlobalState.copy_address,
                            class_name="ml-2 p-2 bg-slate-800 hover:bg-slate-700 rounded-lg transition-colors",
                        ),
                        class_name="flex items-center justify-center mb-8",
                    ),
                ),
                
                # Balance
                rx.el.div(
                    rx.el.p("Balance", class_name="text-xs text-slate-500 mb-2"),
                    rx.el.div(
                        rx.el.span(
                            f"{GlobalState.wallet_balance}",
                            class_name="text-5xl font-bold text-cyan-400",
                        ),
                        rx.el.span(
                            " GAS",
                            class_name="text-2xl text-slate-400 ml-2",
                        ),
                        class_name="flex items-baseline justify-center",
                    ),
                ),
                
                class_name="text-center p-12",
            ),
            class_name="bg-gradient-to-br from-slate-900/80 to-slate-950/80 border border-slate-700 rounded-3xl max-w-2xl mx-auto",
        ),
        
        class_name="animate-in fade-in duration-500",
    )
