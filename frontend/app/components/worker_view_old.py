import reflex as rx

from app.states.global_state import GlobalState

def worker_view() -> rx.Component:
    """The dashboard view for Worker mode (Job Execution & Stats)."""

    return rx.el.div(
        
        # Header
        rx.el.div(
            rx.el.h2("Worker Dashboard", class_name="text-3xl font-bold text-white mb-2"),
            rx.el.p(
                "Find gigs, complete tasks, and earn securely.",
                class_name="text-slate-400",
            ),
            class_name="mb-8",
        ),

        # Stats cards
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.icon("briefcase", class_name="h-6 w-6 text-cyan-400 mb-4"),
                    rx.el.h3(
                        "Available Jobs",
                        class_name="text-lg font-semibold text-white mb-1",
                    ),
                    rx.el.p(
                        str(GlobalState.available_jobs.length()),
                        class_name="text-2xl text-slate-300 font-bold",
                    ),
                    class_name="p-6 rounded-2xl bg-slate-800/40 border border-slate-700 hover:border-cyan-500/50 transition-colors cursor-default",
                )
            ),
            rx.el.div(
                rx.el.div(
                    rx.icon("check_check", class_name="h-6 w-6 text-purple-400 mb-4"),
                    rx.el.h3(
                        "Completed Jobs",
                        class_name="text-lg font-semibold text-white mb-1",
                    ),
                    rx.el.p(
                        str(GlobalState.worker_stats.get("total_jobs", 0)),
                        class_name="text-2xl text-slate-300 font-bold",
                    ),
                    class_name="p-6 rounded-2xl bg-slate-800/40 border border-slate-700 hover:border-purple-500/50 transition-colors cursor-default",
                )
            ),
            rx.el.div(
                rx.el.div(
                    rx.icon("coins", class_name="h-6 w-6 text-pink-400 mb-4"),
                    rx.el.h3(
                        "Total Earnings",
                        class_name="text-lg font-semibold text-white mb-1",
                    ),
                    rx.el.p(
                        f"{GlobalState.worker_stats.get('total_earnings', 0)} GAS",
                        class_name="text-2xl text-slate-300 font-bold",
                    ),
                    class_name="p-6 rounded-2xl bg-slate-800/40 border border-slate-700 hover:border-pink-500/50 transition-colors cursor-default",
                )
            ),
            class_name="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10",
        ),

        # Current job section
        rx.cond(
            GlobalState.current_job,
            rx.el.div(
                rx.el.h3(
                    "Current Assignment", class_name="text-xl font-bold text-white mb-6"
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            rx.el.div(
                                rx.el.h4(
                                    f"Job #{GlobalState.current_job['job_id']}",
                                    class_name="text-xs font-mono text-cyan-400 mb-1",
                                ),
                                rx.el.h3(
                                    GlobalState.current_job['description'],
                                    class_name="text-lg font-semibold text-white",
                                ),
                            ),
                            rx.el.span(
                                "In Progress",
                                class_name="px-3 py-1 rounded-full bg-yellow-500/10 text-yellow-500 text-xs font-medium border border-yellow-500/20",
                            ),
                            class_name="flex justify-between items-start mb-4",
                        ),
                        rx.el.div(
                            rx.el.div(
                                rx.icon("coins", class_name="h-4 w-4 text-purple-400 mr-2"),
                                rx.el.span(
                                    f"Reward: {GlobalState.current_job['amount']} GAS",
                                    class_name="text-slate-300 font-mono"
                                ),
                                class_name="flex items-center",
                            ),
                            class_name="text-sm",
                        ),
                        class_name="bg-slate-900/80 p-6 rounded-xl border border-slate-700 mb-8",
                    ),
                    rx.el.div(
                        rx.el.label(
                            "Submit Proof of Work",
                            class_name="block text-sm font-medium text-slate-300 mb-3",
                        ),
                        rx.upload.root(
                            rx.el.div(
                                rx.icon(
                                    "camera", class_name="h-10 w-10 text-slate-500 mb-3"
                                ),
                                rx.el.p(
                                    "Drop proof photo here or click to select",
                                    class_name="text-slate-400 text-sm",
                                ),
                                rx.el.p(
                                    "Supports JPG, PNG",
                                    class_name="text-slate-600 text-xs mt-1",
                                ),
                                class_name="flex flex-col items-center justify-center text-center",
                            ),
                            id="proof_upload",
                            accept={"image/png": [".png"], "image/jpeg": [".jpg", ".jpeg"]},
                            max_files=1,
                            class_name="border-2 border-dashed border-slate-700 rounded-xl p-8 hover:border-cyan-500/50 hover:bg-slate-900/50 transition-all cursor-pointer",
                        ),
                        rx.el.div(
                            rx.foreach(
                                rx.selected_files("proof_upload"),
                                lambda file: rx.el.div(
                                    rx.icon(
                                        "file-image",
                                        class_name="h-4 w-4 text-cyan-500 mr-2",
                                    ),
                                    rx.el.span(file, class_name="text-slate-300 text-sm"),
                                    class_name="flex items-center mt-3 p-2 bg-slate-900 rounded-lg border border-slate-800",
                                ),
                            )
                        ),
                        rx.el.div(
                            rx.el.button(
                                "Upload Image",
                                on_click=GlobalState.handle_upload(
                                    rx.upload_files(upload_id="proof_upload")
                                ),
                                class_name="text-sm text-cyan-400 hover:text-cyan-300 font-medium px-4 py-2 rounded-lg hover:bg-cyan-500/10 transition-colors",
                            ),
                            class_name="flex justify-end mt-2",
                        ),
                        class_name="mb-8",
                    ),
                    rx.el.div(
                        rx.el.div(
                            rx.cond(
                                GlobalState.uploaded_image != "",
                                rx.el.div(
                                    rx.icon(
                                        "check_check",
                                        class_name="h-5 w-5 text-green-500 mr-2",
                                    ),
                                    rx.el.span(
                                        "Proof Uploaded",
                                        class_name="text-green-500 text-sm font-medium",
                                    ),
                                    class_name="flex items-center",
                                ),
                                rx.el.div(),
                            ),
                            class_name="flex-1",
                        ),
                        rx.el.button(
                            rx.el.span("Verify Work & Claim Payment"),
                            rx.icon(
                                "arrow-right",
                                class_name="w-4 h-4 ml-2 group-enabled:group-hover:translate-x-1 transition-transform",
                            ),
                            on_click=GlobalState.submit_proof(GlobalState.current_job['job_id']),
                            disabled=GlobalState.uploaded_image == "",
                            class_name="group flex items-center justify-center bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-semibold py-3 px-8 rounded-xl disabled:opacity-50 disabled:cursor-not-allowed enabled:hover:shadow-lg enabled:hover:shadow-cyan-500/20 transition-all enabled:active:scale-95 w-full md:w-auto",
                        ),
                        class_name="flex flex-col md:flex-row items-center justify-end gap-4 pt-6 border-t border-slate-800",
                    ),
                    class_name="bg-slate-950/50 rounded-3xl p-8 border border-slate-800 mb-8",
                ),
            ),
        ),

        # Available jobs section
        rx.el.div(
            rx.el.h3("Available Gigs", class_name="text-xl font-bold text-white mb-6"),
            rx.cond(
                GlobalState.is_loading_jobs,
                rx.el.div(
                    rx.el.span("Loading...", class_name="text-slate-400"),
                    class_name="text-center py-8",
                ),
                rx.cond(
                    GlobalState.available_jobs.length() > 0,
                    rx.el.div(
                        rx.foreach(
                            GlobalState.available_jobs,
                            lambda job: rx.el.div(
                                rx.el.div(
                                    rx.el.div(
                                        rx.el.h4(
                                            f"Job #{job['job_id']}",
                                            class_name="text-xs font-mono text-cyan-400 mb-1",
                                        ),
                                        rx.el.h3(
                                            job['description'],
                                            class_name="text-base font-semibold text-white mb-3",
                                        ),
                                    ),
                                    rx.el.div(
                                        rx.el.div(
                                            rx.icon("coins", class_name="h-4 w-4 text-purple-400 mr-2"),
                                            rx.el.span(
                                                f"{job['amount']} GAS",
                                                class_name="text-slate-300 font-semibold"
                                            ),
                                            class_name="flex items-center",
                                        ),
                                        rx.el.button(
                                            "Claim Job",
                                            on_click=GlobalState.claim_job(job['job_id']),
                                            class_name="bg-cyan-500 hover:bg-cyan-600 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors",
                                        ),
                                        class_name="flex justify-between items-center",
                                    ),
                                    class_name="bg-slate-900/80 p-5 rounded-xl border border-slate-700 hover:border-cyan-500/50 transition-colors",
                                ),
                            ),
                        ),
                        class_name="grid grid-cols-1 md:grid-cols-2 gap-4",
                    ),
                    rx.el.div(
                        rx.el.p("No available jobs at the moment. Check back soon!", class_name="text-slate-400"),
                        class_name="text-center py-8 bg-slate-900/30 border border-slate-800 rounded-xl",
                    ),
                ),
            ),
            class_name="bg-slate-950/50 rounded-3xl p-8 border border-slate-800",
        ),

        class_name="animate-in fade-in duration-500",
    )

