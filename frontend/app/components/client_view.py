import reflex as rx

from app.states.global_state import GlobalState

def client_view() -> rx.Component:

    """The dashboard view for Client mode (Job Creation)."""

    return rx.el.div(

        rx.el.div(

            rx.el.h2("Create New Job", class_name="text-3xl font-bold text-white mb-2"),

            rx.el.p(

                "Define the parameters for your new blockchain task.",

                class_name="text-slate-400",

            ),

            class_name="mb-10",

        ),

        rx.el.div(

            rx.el.div(

                rx.el.label(

                    "Job Description",

                    class_name="block text-sm font-medium text-slate-300 mb-2",

                ),

                rx.el.textarea(

                    placeholder="Describe your task details, requirements, and reward (e.g., 'Validate transaction #1234 - 0.5 ETH')...",

                    class_name="w-full bg-slate-900/50 border border-slate-700 rounded-xl p-4 text-slate-200 focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 outline-none min-h-[200px] transition-all placeholder:text-slate-600 font-mono text-sm",

                    on_change=GlobalState.set_job_description,

                    default_value=GlobalState.job_description,

                ),

                class_name="mb-6",

            ),

            rx.el.div(

                rx.el.label(

                    "Job Images (Optional)",

                    class_name="block text-sm font-medium text-slate-300 mb-3",

                ),

                rx.upload.root(

                    rx.el.div(

                        rx.icon(

                            "image", class_name="h-10 w-10 text-slate-500 mb-3"

                        ),

                        rx.el.p(

                            "Drop job images here or click to select",

                            class_name="text-slate-400 text-sm",

                        ),

                        rx.el.p(

                            "Supports JPG, PNG - Images upload automatically",

                            class_name="text-slate-600 text-xs mt-1",

                        ),

                        class_name="flex flex-col items-center justify-center text-center",

                    ),

                    id="job_images_upload",

                    accept={"image/png": [".png"], "image/jpeg": [".jpg", ".jpeg"]},

                    max_files=5,

                    on_drop=GlobalState.auto_upload_files,

                    class_name="border-2 border-dashed border-slate-700 rounded-xl p-8 hover:border-cyan-500/50 hover:bg-slate-900/50 transition-all cursor-pointer",

                ),


                rx.cond(

                    GlobalState.client_uploaded_images.length() > 0,

                    rx.el.div(

                        rx.el.p(

                            "Uploaded Images",

                            class_name="text-sm font-medium text-slate-300 mb-3",

                        ),

                        rx.foreach(

                            GlobalState.client_uploaded_images,

                            lambda filename, index: rx.el.div(

                                rx.icon(

                                    "file-image",

                                    class_name="h-4 w-4 text-cyan-500 mr-2",

                                ),

                                rx.el.span(

                                    filename,

                                    class_name="text-slate-300 text-sm flex-1",

                                ),

                                rx.el.button(

                                    rx.icon(

                                        "x",

                                        class_name="h-4 w-4 text-red-400 hover:text-red-300",

                                    ),

                                    on_click=GlobalState.delete_client_image_by_index(index),

                                    class_name="ml-2 p-1 hover:bg-red-500/10 rounded transition-colors",

                                ),

                                class_name="flex items-center mt-3 p-3 bg-slate-900 rounded-lg border border-slate-800 hover:border-slate-700 transition-colors",

                            ),

                        ),

                        class_name="mt-3",

                    ),

                ),

                class_name="mb-6",

            ),

            rx.el.div(

                rx.el.button(

                    rx.el.span("Create Job"),

                    rx.icon("arrow-right", class_name="w-4 h-4 ml-2"),

                    on_click=GlobalState.create_job,

                    class_name="flex items-center justify-center bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-semibold py-3 px-8 rounded-xl hover:shadow-lg hover:shadow-cyan-500/20 transition-all active:scale-95 w-full md:w-auto",

                ),

                class_name="flex justify-end",

            ),

            class_name="bg-slate-950/50 rounded-3xl p-8 border border-slate-800",

        ),

        class_name="animate-in fade-in duration-500",

    )

