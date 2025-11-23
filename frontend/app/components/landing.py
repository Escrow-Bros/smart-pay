import reflex as rx
from app.states.global_state import GlobalState

def landing_page() -> rx.Component:
    """Landing page with role selection for GigShield."""
    return rx.box(
        # Background gradient
        rx.box(
            position="fixed",
            top="0",
            left="0",
            width="100%",
            height="100%",
            background="linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            z_index="-1",
        ),
        
        # Main container
        rx.center(
            rx.vstack(
                # Logo and Title
                rx.vstack(
                    rx.icon(
                        tag="shield_check",
                        size=60,
                        color="white",
                    ),
                    rx.heading(
                        "GigShield",
                        size="9",
                        color="white",
                        font_weight="700",
                        letter_spacing="-0.02em",
                    ),
                    rx.text(
                        "Secure Your Gig Work with Blockchain-Powered Escrow",
                        size="5",
                        color="rgba(255, 255, 255, 0.9)",
                        text_align="center",
                        max_width="600px",
                    ),
                    spacing="3",
                    align="center",
                    margin_bottom="60px",
                ),
                
                # Role Selection Cards
                rx.hstack(
                    # Client Card
                    rx.box(
                        rx.vstack(
                            rx.icon(
                                tag="briefcase",
                                size=50,
                                color="#667eea",
                            ),
                            rx.heading(
                                "Login as Client",
                                size="7",
                                color="#1a202c",
                                font_weight="600",
                            ),
                            rx.text(
                                "Post gigs, escrow payments, and verify work completion with AI-powered validation.",
                                size="3",
                                color="#4a5568",
                                text_align="center",
                                line_height="1.6",
                            ),
                            rx.button(
                                "Get Started",
                                size="3",
                                width="100%",
                                on_click=GlobalState.select_role(True),
                                cursor="pointer",
                                background="linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                                color="white",
                                _hover={
                                    "transform": "translateY(-2px)",
                                    "box_shadow": "0 10px 25px rgba(102, 126, 234, 0.4)",
                                },
                                transition="all 0.3s ease",
                            ),
                            spacing="4",
                            align="center",
                            padding="40px",
                        ),
                        background="white",
                        border_radius="20px",
                        box_shadow="0 20px 60px rgba(0, 0, 0, 0.3)",
                        width="350px",
                        _hover={
                            "transform": "translateY(-8px)",
                            "box_shadow": "0 25px 70px rgba(0, 0, 0, 0.4)",
                        },
                        transition="all 0.3s ease",
                        cursor="pointer",
                    ),
                    
                    # Worker Card
                    rx.box(
                        rx.vstack(
                            rx.icon(
                                tag="user_check",
                                size=50,
                                color="#667eea",
                            ),
                            rx.heading(
                                "Login as Gig Worker",
                                size="7",
                                color="#1a202c",
                                font_weight="600",
                            ),
                            rx.text(
                                "Find gigs, complete tasks, submit proof, and receive instant payments securely.",
                                size="3",
                                color="#4a5568",
                                text_align="center",
                                line_height="1.6",
                            ),
                            rx.button(
                                "Get Started",
                                size="3",
                                width="100%",
                                on_click=GlobalState.select_role(False),
                                cursor="pointer",
                                background="linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                                color="white",
                                _hover={
                                    "transform": "translateY(-2px)",
                                    "box_shadow": "0 10px 25px rgba(102, 126, 234, 0.4)",
                                },
                                transition="all 0.3s ease",
                            ),
                            spacing="4",
                            align="center",
                            padding="40px",
                        ),
                        background="white",
                        border_radius="20px",
                        box_shadow="0 20px 60px rgba(0, 0, 0, 0.3)",
                        width="350px",
                        _hover={
                            "transform": "translateY(-8px)",
                            "box_shadow": "0 25px 70px rgba(0, 0, 0, 0.4)",
                        },
                        transition="all 0.3s ease",
                        cursor="pointer",
                    ),
                    
                    spacing="8",
                    wrap="wrap",
                    justify="center",
                ),
                
                # Features Section
                rx.vstack(
                    rx.hstack(
                        rx.hstack(
                            rx.icon(tag="shield", size=24, color="white"),
                            rx.text(
                                "Blockchain Security",
                                size="3",
                                color="white",
                                font_weight="500",
                            ),
                            spacing="2",
                        ),
                        rx.hstack(
                            rx.icon(tag="zap", size=24, color="white"),
                            rx.text(
                                "Instant Payments",
                                size="3",
                                color="white",
                                font_weight="500",
                            ),
                            spacing="2",
                        ),
                        rx.hstack(
                            rx.icon(tag="check_check", size=24, color="white"),
                            rx.text(
                                "AI Verification",
                                size="3",
                                color="white",
                                font_weight="500",
                            ),
                            spacing="2",
                        ),
                        spacing="8",
                        wrap="wrap",
                        justify="center",
                    ),
                    margin_top="60px",
                    opacity="0.9",
                ),
                
                spacing="5",
                align="center",
                padding="40px",
            ),
            min_height="100vh",
            width="100%",
        ),
    )
