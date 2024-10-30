import streamlit as st

# Set page config
st.set_page_config(page_title="Ollama Chat Interface", layout="wide", page_icon="🤖")

# Load custom CSS from file
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css('styles.css')

# Initialize session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Home"

# Header
# Change COLOR ##############################################################################
st.markdown(f"""
<div class="header">
    <div class="animated-bg"></div>
    <div class="header-content">
        <h1 class="header-title">Ollama Chatbot Multi-Model Interface</h1> 
        <p class="header-subtitle">Advanced Language Models & Intelligent Conversations</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Import required modules
import st_pages

# Enhanced pages definition
PAGES = {
    "Home": {
        "icon": "house-door",
        "func": st_pages.home,
        "description": "Guidelines & Overview",
        "badge": "Informative",
        "color": "var(--primary-color)"
    },
    "Language Models Management": {
        "icon": "gear",
        "func": st_pages.model_management,
        "description": "Download Models",
        "badge": "Configurations",
        "color": "var(--secondary-color)"
    },
    "AI Conversation": {
        "icon": "chat-dots",
        "func": st_pages.ai_chatbot,
        "description": "Interactive AI Chat",
        "badge": "Application",
        "color": "var(--highlight-color)"
    }
}

st.markdown("""
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css">
""", unsafe_allow_html=True)

def navigate():
    with st.sidebar:
        st.markdown("""
        <div class="profile-section">
            <div class="profile-image">🧠</div>
            <div class="profile-info">
                <h4> </h4>
                <h2>Navigation Menu</h2>
                <span class="active-badge">AI Chatbot Multi-Model Application</span>
                <h3> </h3>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('---')

        # Create menu items
        for page, info in PAGES.items():
            selected = st.session_state.current_page == page
            
            # Create the button (invisible but clickable)
            if st.button(
                f"{page}",
                key=f"nav_{page}",
                use_container_width=True,
                type="secondary" if selected else "primary"
            ):
                st.session_state.current_page = page
                st.rerun()

            # Visual menu item
            st.markdown(f"""
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
            """, unsafe_allow_html=True)

        # Close navigation container
        st.markdown('</div>', unsafe_allow_html=True)
        
        return st.session_state.current_page

# Get selected page and run its function
try:
    selected_page = navigate()
    # Update session state
    if selected_page != st.session_state.current_page:
        st.session_state.current_page = selected_page
        st.rerun()
    
    # Run the selected function
    page_function = PAGES[selected_page]["func"]
    page_function()
except Exception as e:
    st.error(f"Error loading page: {str(e)}")
    st_pages.home.run()

# Display the footer
st.markdown("""
<div class="footer">
    <div class="footer-content">
        <p>© 2024 Powered by <a href="https://github.com/TsLu1s" target="_blank">TsLu1s </a>. 
        Advanced Language Models & Intelligent Conversations.
        | Source Code: <a href="https://github.com/TsLu1s/ollama-chatbot-interface" target="_blank"> Ollama Chatbot Interface</p>
    </div>
</div>
""", unsafe_allow_html=True)