import pandas as pd
from pandas.io.formats.style import Styler

from config import HARDWARE_REQUIREMENTS


def style_dataframe(df: pd.DataFrame) -> Styler:
    """
    Apply sophisticated styling to a DataFrame.

    Args:
        df: DataFrame to style

    Returns:
        Styled DataFrame
    """
    styles = [
        # Table-wide styles
        {
            "selector": "table",
            "props": [
                ("border-collapse", "separate"),
                ("border-spacing", "0 4px"),
                ("margin", "25px 0"),
                ("width", "100%"),
                ("border-radius", "8px"),
                ("overflow", "hidden"),
                ("table-layout", "fixed"),
                ("box-shadow", "0 4px 6px rgba(0, 0, 0, 0.1)"),
            ],
        },
        # Header styles
        {
            "selector": "thead th",
            "props": [
                ("background-color", "#374B5D"),
                ("color", "#FFFAE5"),
                ("padding", "18px 20px"),
                ("font-weight", "800"),
                ("text-transform", "uppercase"),
                ("letter-spacing", "0.5px"),
                ("font-size", "20px"),
                ("border-bottom", "3px solid #56382D"),
                ("position", "sticky"),
                ("top", "0"),
            ],
        },
        # Index styling
        {
            "selector": "tbody th",
            "props": [
                ("background-color", "#935F4C"),
                ("color", "#FFFAE5"),
                ("padding", "12px 15px"),
                ("font-weight", "600"),
                ("text-align", "center"),
                ("border-bottom", "1px solid rgba(255, 250, 229, 0.1)"),
                ("font-size", "17px"),
                ("width", "50px"),
            ],
        },
        # Cell styles
        {
            "selector": "td",
            "props": [
                ("padding", "12px 15px"),
                ("background-color", "#FFFAE5"),
                ("border-bottom", "1px solid rgba(55, 75, 93, 0.1)"),
                ("font-size", "17px"),
                ("transition", "all 0.2s ease"),
                ("line-height", "1.6"),
            ],
        },
        # Row hover effect
        {
            "selector": "tbody tr:hover td",
            "props": [
                ("background-color", "#F1E2AD"),
                ("transform", "scale(1.01)"),
                ("box-shadow", "0 2px 4px rgba(0, 0, 0, 0.05)"),
            ],
        },
        # Row hover effect for index
        {
            "selector": "tbody tr:hover th",
            "props": [
                ("transform", "scale(1.01)"),
                ("box-shadow", "0 2px 4px rgba(0, 0, 0, 0.05)"),
            ],
        },
        # Model name column
        {
            "selector": "td:first-child",
            "props": [
                ("font-weight", "600"),
                ("color", "#374B5D"),
                ("width", "100px"),
            ],
        },
        # Description column
        {
            "selector": "td:nth-child(2)",
            "props": [
                ("text-align", "left"),
                ("line-height", "1.6"),
                ("width", "250px"),
                ("white-space", "normal"),
                ("padding-right", "20px"),
            ],
        },
        # Parameter Sizes column
        {
            "selector": "td:nth-child(3)",
            "props": [
                ("width", "1000px"),
                ("text-align", "left"),
                ("white-space", "normal"),
            ],
        },
        {
            "selector": "td:nth-child(5)",
            "props": [
                ("width", "200px"),
                ("text-align", "center"),
            ],
        },
    ]

    return (
        df.style.set_table_styles(styles)
        .set_properties(**{"overflow": "hidden", "text-overflow": "ellipsis"})
        .set_table_attributes('class="dataframe hover-effect"')
    )


def format_hardware_requirements() -> str:
    """
    Format hardware requirements as HTML.

    Returns:
        HTML string for hardware requirements display
    """
    requirements_list = "\n".join(
        f"<li>{size} models: {ram}</li>"
        for size, ram in HARDWARE_REQUIREMENTS.items()
    )

    return f"""
    <div style='padding: 1rem; background-color: #374B5D; color: white; border-radius: 0.5rem'>
    <p>
    Minimum RAM requirements by model size:
    <ul>
    {requirements_list}
    </ul>
    Note: Having a GPU will make the models run much faster, but it's not required - they will still work on CPU.
    </p>
    </div>
    """


def create_models_dataframe(model_data: list[dict]) -> pd.DataFrame:
    """
    Create a DataFrame from model library data.

    Args:
        model_data: List of model dictionaries

    Returns:
        Pandas DataFrame with model information
    """
    return pd.DataFrame(model_data)