import warnings
warnings.filterwarnings("ignore", category=Warning)

import streamlit as st
import imgs
import st_pages.home
import st_pages.ai_chatbot
import st_pages.model_management # required modules
import asyncio

# Set page config
st.set_page_config(page_title="Anti-Parasocial Chaperones", layout="wide", page_icon="🤖")

# Load custom CSS from file
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css('styles.css')

# Initialize session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = "AI Conversation"

# Header
st.markdown(f"""
<div class="header">
    <div class="animated-bg"></div>
    <div class="header-content">
        <h1 class="header-title">Anti-Parasocial Chaperones</h1> 
        <p class="header-subtitle">A side-by-side comparison</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Enhanced pages definition
PAGES = {
    
   
    "AI Conversation": {
        "icon": "chat-dots",
        "func": st_pages.ai_chatbot,
        "description": "Interactive AI Chat",
        "badge": "Application",
        "color": "var(--highlight-color)"
    },
  
}

st.markdown("""
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css">
""", unsafe_allow_html=True)

def navigate():
    with st.sidebar:
        st.markdown('''
        <a href="https://github.com/TsLu1s/talknexus" target="_blank" style="text-decoration: none; color: inherit; display: block;">
            <div class="header-container" style="cursor: pointer;">
                <div class="profile-section">
                    <div class="profile-info">
                        <h1 style="font-size: 38px;">TalkNexus</h1>
                        <span class="active-badge" style="font-size: 20px;"></span>
                    </div>
                </div>
            </div>
        </a>
        ''', unsafe_allow_html=True)

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
    pass
    #st.error(f"Error loading page: {str(e)}")

# Display the footer
st.markdown("""
""", unsafe_allow_html=True)
