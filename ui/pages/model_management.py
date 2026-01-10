import streamlit as st

from core.ollama_client import OllamaClient, ModelLibrary, get_ollama_models, get_model_info
from utils.formatters import style_dataframe, create_models_dataframe, format_hardware_requirements


def display_models_library() -> None:
    """Display the Ollama models library table."""
    st.markdown(
        """
        <div class="section-header">
            <h2>Ollama Models Library</h2>
            <p>Browse and explore available language models</p>
        </div>
    """,
        unsafe_allow_html=True,
    )

    model_data = ModelLibrary.get_dataframe_data()
    df = create_models_dataframe(model_data)
    styled_df = style_dataframe(df)
    st.markdown(styled_df.to_html(escape=False), unsafe_allow_html=True)


def run() -> None:
    """Render the model management page."""
    ollama_client = OllamaClient()

    st.markdown(
    """
    <div class="header-container">
        <p class="header-subtitle"> 🤖 Explore, Download, and Manage State-of-the-Art Language Models</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Model Installation Section
    st.markdown(
    """
    <div class="section-header">
        <h2>Download New Language Models</h2>
        <p>Install models from the Ollama Library</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([3, 6])
    with col1:
        new_model = st.text_input(
            "Enter the name of the model you want to download:",
            placeholder="e.g., llama2, mistral, gemma... (Press Enter to download)",
            key="model_input",
        )
        if new_model:
            with st.spinner(
                f"🤖 Downloading {new_model}... This may take a bit depending on the model size"
            ):
                success, message = ollama_client.pull_model(new_model)
                if success:
                    st.success(f"✅ {message}")
                else:
                    st.error(f"❌ {message}")

    with col2:
        pass

    st.markdown("---")

    # Local Models Section
    st.markdown(
        """
    <div class="section-header">
        <h2>Downloaded Language Models</h2>
        <p>Manage your local model collection</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    available_models = get_ollama_models()
    if available_models:
        for model in available_models:
            with st.expander(f"📦 {model}"):
                model_info = get_model_info(model)
                if model_info:
                    st.code(model_info, language="yaml")
    else:
        st.info("No models currently installed. Use the Download tab to install models.")

    st.markdown("---")

    # Display models library
    display_models_library()

    # Display hardware requirements
    st.markdown("### Hardware Requirements")
    st.markdown(format_hardware_requirements(), unsafe_allow_html=True)

    st.markdown("---")

    # Tips section
    st.subheader("Tips for Using Models")
    st.markdown(
        """
    - Different models have different capabilities and are suited for various tasks.
    - Larger models generally perform better but require more computational resources.
    - Some models are specialized for certain languages or domains.
    - Be aware of model biases and limitations in your applications.
    - It's advisable to start with smaller models and scale up as needed for your usage.
    """
    )