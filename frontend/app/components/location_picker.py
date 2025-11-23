import reflex as rx
from app.states.global_state import GlobalState

def location_picker() -> rx.Component:
    """Address input with autocomplete for selecting job location."""
    
    return rx.el.div(
        rx.el.label(
            "Job Location",
            class_name="block text-sm font-medium text-slate-300 mb-2",
        ),
        
        # Address input with autocomplete
        rx.el.div(
            rx.el.input(
                id="location-autocomplete-input",
                type="text",
                placeholder="Start typing an address (e.g., '123 Main St, San Francisco')...",
                class_name="w-full bg-slate-900/50 border border-slate-700 rounded-xl p-4 text-slate-200 focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 outline-none transition-all placeholder:text-slate-600 text-sm",
                on_change=GlobalState.set_job_location,
                value=GlobalState.job_location,
                autocomplete="off",
            ),
            rx.el.div(
                id="location-suggestions",
                class_name="mt-2 bg-slate-900 border border-slate-700 rounded-xl overflow-hidden hidden",
            ),
            class_name="relative",
        ),
        
        rx.el.p(
            "💡 Start typing to search for an address. Select from suggestions for precise coordinates.",
            class_name="text-xs text-slate-500 mt-2",
        ),
        
        class_name="mb-6",
    )
