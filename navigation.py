import warnings
warnings.filterwarnings("ignore", category=Warning)

import streamlit as st

from config import APP_TITLE, APP_ICON, APP_LAYOUT, STYLES_FILE
from config.constants import PageName, PAGE_CONFIG
from ui.pages import home, model_management, ai_chatbot, rag_chat


# =============================================================================
# Page Configuration
# =============================================================================

st.set_page_config(
    page_title=APP_TITLE,
    layout=APP_LAYOUT,
    page_icon=APP_ICON,
)


# =============================================================================
# CSS Loading
# =============================================================================

def load_css() -> None:
    """Load custom CSS styles."""
    try:
        with open(STYLES_FILE) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass  # Gracefully handle missing CSS


load_css()


# =============================================================================
# Session State Initialization
# =============================================================================

if "current_page" not in st.session_state:
    st.session_state.current_page = PageName.HOME.value


# =============================================================================
# Header
# =============================================================================

st.markdown(
    """
<div class="header">
    <div class="animated-bg"></div>
    <div class="header-content">
        <h1 class="header-title">Ollama Chatbot Multi-Model Interface</h1>
        <p class="header-subtitle">Advanced Language Models & Intelligent Conversations</p>
    </div>
</div>
""",
    unsafe_allow_html=True,
)


# =============================================================================
# Page Registry
# =============================================================================

PAGES = {
    PageName.HOME.value: {
        "icon": PAGE_CONFIG[PageName.HOME]["icon"].value,
        "func": home.run,
        "description": PAGE_CONFIG[PageName.HOME]["description"],
        "badge": PAGE_CONFIG[PageName.HOME]["badge"].value,
    },
    PageName.MODEL_MANAGEMENT.value: {
        "icon": PAGE_CONFIG[PageName.MODEL_MANAGEMENT]["icon"].value,
        "func": model_management.run,
        "description": PAGE_CONFIG[PageName.MODEL_MANAGEMENT]["description"],
        "badge": PAGE_CONFIG[PageName.MODEL_MANAGEMENT]["badge"].value,
    },
    PageName.AI_CONVERSATION.value: {
        "icon": PAGE_CONFIG[PageName.AI_CONVERSATION]["icon"].value,
        "func": ai_chatbot.run,
        "description": PAGE_CONFIG[PageName.AI_CONVERSATION]["description"],
        "badge": PAGE_CONFIG[PageName.AI_CONVERSATION]["badge"].value,
    },
    PageName.RAG_CONVERSATION.value: {
        "icon": PAGE_CONFIG[PageName.RAG_CONVERSATION]["icon"].value,
        "func": rag_chat.run,
        "description": PAGE_CONFIG[PageName.RAG_CONVERSATION]["description"],
        "badge": PAGE_CONFIG[PageName.RAG_CONVERSATION]["badge"].value,
    },
}


# =============================================================================
# Bootstrap Icons
# =============================================================================

st.markdown(
    """
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css">
""",
    unsafe_allow_html=True,
)


# =============================================================================
# Navigation
# =============================================================================

def navigate() -> str:
    """Render navigation sidebar and return selected page."""
    with st.sidebar:
        # Header with GitHub link
        st.markdown(
            """
        <a href="https://github.com/TsLu1s/talknexus" target="_blank" style="text-decoration: none; color: inherit; display: block;">
            <div class="header-container" style="cursor: pointer;">
                <div class="profile-section">
                    <div class="profile-info">
                        <h1 style="font-size: 38px;">TalkNexus</h1>
                        <span class="active-badge" style="font-size: 20px;">AI Chatbot Multi-Model Application</span>
                    </div>
                </div>
            </div>
        </a>
        """,
            unsafe_allow_html=True,
        )

        st.markdown("---")

        # Navigation menu items
        for page, info in PAGES.items():
            selected = st.session_state.current_page == page

            # Clickable button
            if st.button(
                f"{page}",
                key=f"nav_{page}",
                use_container_width=True,
                type="secondary" if selected else "primary",
            ):
                st.session_state.current_page = page
                st.rerun()

            # Visual menu item
            st.markdown(
                f"""
                <div class="menu-item {'selected' if selected else ''}">
                    <div class="menu-icon">
                        <i class="bi bi-{info['icon']}"></i>
                    </div>
                    <div class="menu-content">
                        <div class="menu-title">{page}</div>
                        <div class="menu-description">{info['description']}</div>
                    </div>
                    <div class="menu-badge">{info['badge']}</div>
                </div>
            """,
                unsafe_allow_html=True,
            )

        st.markdown("</div>", unsafe_allow_html=True)

        return st.session_state.current_page


# =============================================================================
# Main Application
# =============================================================================

try:
    selected_page = navigate()

    if selected_page != st.session_state.current_page:
        st.session_state.current_page = selected_page
        st.rerun()

    # Run selected page
    page_function = PAGES[selected_page]["func"]
    page_function()

except Exception as e:
    st.error(f"Error loading page: {str(e)}")
    home.run()


# =============================================================================
# Footer
# =============================================================================

st.markdown(
    """
<div class="footer">
    <div class="footer-content">
        <p>© 2024 Powered by <a href="https://github.com/TsLu1s" target="_blank">TsLu1s </a>.
        Advanced Language Models & Intelligent Conversations
        | Project Source: <a href="https://github.com/TsLu1s/talknexus" target="_blank"> TalkNexus</p>
    </div>
</div>
""",
    unsafe_allow_html=True,
)