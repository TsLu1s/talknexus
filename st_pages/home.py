import streamlit as st

def display_model_capabilities():
    """Displays model capabilities section"""
    st.markdown("### Install Ollama API")
    
    # Styled download button for Ollama installation
    st.markdown("""
        <p> After download PC Restart may be necessary.</p>
        <a href="https://ollama.com/download" target="_blank" class="custom-download-button2">
            Download Ollama
        </a>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("## Examples of Relevant Models: Capabilities & Specializations")
    
    capabilities = {
        "Language Models": {
            "Deepseek-R1": {
                "capabilities": ["Advanced Reasoning", "General Intelligence", "Code Understanding"],
                "description": "Flagship reasoning model family with state-of-the-art performance, featuring six dense models optimized for advanced reasoning",
                "icon": "🧠",
                "tags": ["1.5B, 7B, 8B, 14B, 32B, 70B, 671B", "Reasoning", "High Performance"]
            },
            "Llama 3.1": {
                "capabilities": ["General Purpose AI", "Text Generation", "Advanced Reasoning"],
                "description": "State-of-the-art model from Meta with impressive performance across a wide range of tasks",
                "icon": "🦙",
                "tags": ["8B, 70B, 405B", "Versatile", "High Performance"]
            }
        },
        "Specialized Models": {
            "Phi 3": {
                "capabilities": ["Code Generation", "Scientific Tasks", "Educational Use"],
                "description": "Microsoft's compact model optimized for coding and scientific applications",
                "icon": "🔬",
                "tags": ["3.8B", "Compact", "Scientific"]
            },
            "Mistral": {
                "capabilities": ["Text Generation", "Code Completion", "Analysis"],
                "description": "Advanced model with state-of-the-art performance in multiple domains",
                "icon": "🌪️",
                "tags": ["7B", "Advanced", "Multi-domain"]
            }
        },
        "Task-Specific Models": {
            "Moondream 2": {
                "capabilities": ["Vision-Language Tasks", "Image Understanding", "Visual Analysis"],
                "description": "Specialized in vision-language understanding and processing",
                "icon": "🌙",
                "tags": ["1.4B", "Vision-Language", "Lightweight"]
            },
            "Neural Chat": {
                "capabilities": ["Conversational AI", "Task Completion", "User Assistance"],
                "description": "Optimized for natural conversations and user interactions",
                "icon": "💬",
                "tags": ["7B", "Conversational", "User-friendly"]
            }
        },
        "Domain-Specific Models": {
            "Code Llama": {
                "capabilities": ["Code Generation", "Programming Tasks", "Technical Documentation"],
                "description": "Specialized in software development and coding tasks",
                "icon": "👨‍💻",
                "tags": ["7B", "Coding", "Development"]
            },
            "Solar": {
                "capabilities": ["Scientific Computing", "Research Tasks", "Technical Analysis"],
                "description": "Focused on scientific applications and research tasks",
                "icon": "☀️",
                "tags": ["10.7B", "Scientific", "Research"]
            }
        }
    }

    # Display models by category
    for category, models in capabilities.items():
        st.markdown(f"### {category}")
        cols = st.columns(2)
        
        for idx, (model_name, details) in enumerate(models.items()):
            with cols[idx % 2]:
                st.markdown(f"""
                <div class="capability-card">
                    <div class="model-header">
                        <div class="model-icon">{details['icon']}</div>
                        <div class="model-name">{model_name}</div>
                    </div>
                    <p class="model-description">{details['description']}</p>
                    <div class="capability-tags">
                        {' '.join(f'<span class="capability-tag">{tag}</span>' for tag in details['tags'])}
                    </div>
                    <div class="capabilities-list">
                        <small><strong>Key Capabilities:</strong></small><br>
                        {' • '.join(details['capabilities'])}
                    </div>
                </div>
                """, unsafe_allow_html=True)

def run():
    
    # Main title
    st.markdown('''
    <p class="header-subtitle">
    🤖 Explore and Analyze State-Of-The-Art Open-Source Language Models
    </p>
    ''', unsafe_allow_html=True)

    # Create tabs
    tab1, tab2 = st.tabs(["📊 Ollama Model Ecosystem", "📚 References & Documentation"])

    with tab1:
       
        # Display model capabilities
        display_model_capabilities()

        st.markdown("---")
        
        # Hardware Requirements
        st.markdown("### Hardware Requirements")
        st.markdown(
        """
        <div style='padding: 1rem; background-color: #374B5D; color: white; border-radius: 0.5rem'>
        <p>
        Minimum RAM requirements by model size:
        <ul>
        <li>1B-7B models: 8GB RAM</li>
        <li>8B-13B models: 16GB RAM</li>
        <li>14B-33B models: 32GB RAM</li>
        <li>34B+ models: 64GB+ RAM</li>
        </ul>
        Note: Having a GPU will make the models run much faster, but it's not required - they will still work on CPU.
        </p>
        </div>
        """, 
        unsafe_allow_html=True
        )
        st.markdown("---")

    with tab2:
        pass 

    # References section
    st.markdown("""
    ### 📚 References & Documentation
    
    - [Ollama Model Library](https://ollama.com/library)
    - [Ollama GitHub Repository](https://github.com/ollama/ollama)
    - [Installation Guide](https://ollama.ai/download)
    - [API Documentation](https://github.com/ollama/ollama/blob/main/docs/api.md)
    """)
