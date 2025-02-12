import pandas as pd
from pandas.io.formats.style import Styler
import streamlit as st
import subprocess
import requests

def get_ollama_models() -> list:
    """
    Retrieves available models from Ollama API.
    
    Sends GET request to Ollama API endpoint and processes response to extract
    valid model names, filtering out failed or invalid models.
    
    Returns:
        list: List of available model names, empty if API unreachable
    """
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            models = response.json()
            return [model['name'] for model in models['models']
                    if all(keyword not in model['name'].lower()
                        for keyword in ('failed', 'embed', 'bge'))]
        return []
    except:
        return []


def create_models_dataframe():
    models_info = {
        'deepseek-r1': {
            'description': "DeepSeek's first-generation of reasoning models with comparable performance to OpenAI-o1, including six dense models distilled from DeepSeek-R1 based on Llama and Qwen.",
            'params': "1.5B, 7B, 8B, 14B, 32B, 70B, 671B"
        },
        'llama3.2': {
            'description': "Meta's Llama 3.2 goes small with 1B and 3B models.",
            'params': "1B, 3B"
        },
        'llama3.1': {
            'description': "Llama 3.1 is a new state-of-the-art model from Meta available in 8B, 70B and 405B parameter sizes.",
            'params': "8B, 70B, 405B"
        },
        'gemma2': {
            'description': "Google Gemma 2 is a high-performing and efficient model available in three sizes: 2B, 9B, and 27B.",
            'params': "2B, 9B, 27B"
        },
        'qwen2.5': {
            'description': "Qwen2.5 models are pretrained on Alibaba's latest large-scale dataset with up to 128K tokens support.",
            'params': "0.5B, 1.5B, 3B, 7B, 14B, 32B, 72B"
        },
        'phi3.5': {
            'description': "A lightweight AI model with 3.8 billion parameters with performance overtaking similarly and larger sized models.",
            'params': "3.8B"
        },
        'nemotron-mini': {
            'description': "A commercial-friendly small language model by NVIDIA optimized for roleplay, RAG QA, and function calling.",
            'params': "4B"
        },
        'mistral-small': {
            'description': "Mistral Small is a lightweight model designed for cost-effective use in tasks like translation and summarization.",
            'params': "22B"
        },
        'mistral-nemo': {
            'description': "A state-of-the-art 12B model with 128k context length, built by Mistral AI in collaboration with NVIDIA.",
            'params': "12B"
        },
        'deepseek-coder-v2': {
            'description': "An open-source Mixture-of-Experts code language model comparable to GPT4-Turbo in code-specific tasks.",
            'params': "16B, 236B"
        },
        'mistral': {
            'description': "The 7B model released by Mistral AI, updated to version 0.3.",
            'params': "7B"
        },
        'mixtral': {
            'description': "A set of Mixture of Experts (MoE) model with open weights by Mistral AI.",
            'params': "8x7B, 8x22B"
        },
        'codegemma': {
            'description': "Collection of powerful, lightweight models for coding tasks and math reasoning.",
            'params': "2B, 7B"
        },
        'command-r': {
            'description': "LLM optimized for conversational interaction and long context tasks.",
            'params': "35B"
        },
        'command-r-plus': {
            'description': "Powerful, scalable LLM for enterprise use cases.",
            'params': "104B"
        },
        'llava': {
            'description': "🌋 Multimodal model combining vision encoder and Vicuna for visual and language understanding.",
            'params': "7B, 13B, 34B"
        },
        'llama3': {
            'description': "Meta Llama 3: The most capable openly available LLM to date",
            'params': "8B, 70B"
        },
        'gemma': {
            'description': "Family of lightweight, state-of-the-art open models by Google DeepMind.",
            'params': "2B, 7B"
        },
        'qwen': {
            'description': "Series of LLMs by Alibaba Cloud spanning from 0.5B to 110B parameters",
            'params': "0.5B, 1.8B, 4B, 7B, 14B, 32B, 72B, 110B"
        },
        'qwen2': {
            'description': "New series of large language models from Alibaba group",
            'params': "0.5B, 1.5B, 7B, 72B"
        },
        'phi3': {
            'description': "Family of lightweight 3B (Mini) and 14B (Medium) state-of-the-art open models by Microsoft.",
            'params': "3.8B, 14B"
        },
        'llama2': {
            'description': "Collection of foundation language models ranging from 7B to 70B parameters.",
            'params': "7B, 13B, 70B"
        },
        'codellama': {
            'description': "Code-specialized language model for text-to-code generation and discussion.",
            'params': "7B, 13B, 34B, 70B"
        },
        'nomic-embed-text': {
            'description': "High-performing open embedding model with large token context window.",
            'params': "Embedding"
        },
        'mxbai-embed-large': {
            'description': "State-of-the-art large embedding model from mixedbread.ai",
            'params': "335M"
        },
        'dolphin-mixtral': {
            'description': "Uncensored Mixtral-based models excelling at coding tasks.",
            'params': "8x7B, 8x22B"
        },
        'starcoder2': {
            'description': "Next generation of transparently trained open code LLMs.",
            'params': "3B, 7B, 15B"
        },
        'phi': {
            'description': "2.7B language model with outstanding reasoning capabilities.",
            'params': "2.7B"
        },
        'deepseek-coder': {
            'description': "Capable coding model trained on two trillion tokens.",
            'params': "1.3B, 6.7B, 33B"
        },
        'llama2-uncensored': {
            'description': "Uncensored Llama 2 model variant.",
            'params': "7B, 70B"
        },
        'dolphin-mistral': {
            'description': "Uncensored Dolphin model based on Mistral, excelling at coding.",
            'params': "7B"
        },
        'qwen2.5-coder': {
            'description': "Code-Specific Qwen models for code generation and reasoning.",
            'params': "1.5B, 7B"
        },
        'yi': {
            'description': "High-performing, bilingual language model.",
            'params': "6B, 9B, 34B"
        },
        'dolphin-llama3': {
            'description': "Dolphin 2.9 based on Llama 3 with various skills.",
            'params': "8B, 70B"
        },
        'orca-mini': {
            'description': "General-purpose model suitable for entry-level hardware.",
            'params': "3B, 7B, 13B, 70B"
        },
        'zephyr': {
            'description': "Fine-tuned versions of Mistral and Mixtral models.",
            'params': "7B, 141B"
        },
        'llava-llama3': {
            'description': "LLaVA model fine-tuned from Llama 3 Instruct.",
            'params': "8B"
        },
        'snowflake-arctic-embed': {
            'description': "Text embedding models suite by Snowflake.",
            'params': "22M, 33M, 110M, 137M, 335M"
        },
        'tinyllama': {
            'description': "Compact 1.1B Llama model trained on 3 trillion tokens.",
            'params': "1.1B"
        },
        'mistral-openorca': {
            'description': "7B parameter model fine-tuned on OpenOrca dataset.",
            'params': "7B"
        },
        'starcoder': {
            'description': "Code generation model trained on 80+ programming languages.",
            'params': "1B, 3B, 7B, 15B"
        },
        'codestral': {
            'description': "Mistral AI's first code model for code generation.",
            'params': "22B"
        },
        'vicuna': {
            'description': "General use chat model based on Llama and Llama 2.",
            'params': "7B, 13B, 33B"
        },
        'granite-code': {
            'description': "Family of open foundation models by IBM for Code Intelligence",
            'params': "3B, 8B, 20B, 34B"
        },
        'llama2-chinese': {
            'description': "Llama 2 model fine-tuned for Chinese dialogue.",
            'params': "7B, 13B"
        },
        'wizard-vicuna-uncensored': {
            'description': "Uncensored Llama 2-based model series.",
            'params': "7B, 13B, 30B"
        },
        'wizardlm2': {
            'description': "Microsoft AI LLM for complex chat and reasoning.",
            'params': "7B, 8x22B"
        },
        'codegeex4': {
            'description': "Versatile model for AI software development.",
            'params': "9B"
        },
        'all-minilm': {
            'description': "Embedding models for sentence-level datasets.",
            'params': "22M, 33M"
        },
        'nous-hermes2': {
            'description': "Nous Research models for scientific discussion and coding.",
            'params': "10.7B, 34B"
        },
        'openchat': {
            'description': "Open-source models surpassing ChatGPT on various benchmarks.",
            'params': "7B"
        },
        'aya': {
            'description': "Cohere's multilingual models supporting 23 languages.",
            'params': "8B, 35B"
        },
        'codeqwen': {
            'description': "LLM pretrained on large amount of code data.",
            'params': "7B"
        },
        'tinydolphin': {
            'description': "1.1B parameter model based on TinyLlama.",
            'params': "1.1B"
        },
        'wizardcoder': {
            'description': "State-of-the-art code generation model",
            'params': "33B"
        },
        'stable-code': {
            'description': "3B coding model competing with larger models.",
            'params': "3B"
        },
        'openhermes': {
            'description': "7B model fine-tuned on Mistral with open datasets.",
            'params': "7B"
        },
        'mistral-large': {
            'description': "Mistral's flagship model with 128k context window.",
            'params': "123B"
        },
        'qwen2-math': {
            'description': "Specialized math models outperforming many others.",
            'params': "1.5B, 7B, 72B"
        },
        'reflection': {
            'description': "Model trained with Reflection-tuning for self-correction.",
            'params': "70B"
        },
        'bakllava': {
            'description': "BakLLaVA is a multimodal model with Mistral 7B base and LLaVA architecture",
            'params': "7B"
        },
        'stablelm2': {
            'description': "Multilingual model trained in 7 European languages",
            'params': "1.6B, 12B"
        },
        'llama3-gradient': {
            'description': "Extended LLama-3 with 1M token context",
            'params': "8B, 70B"
        },
        'deepseek-llm': {
            'description': "Advanced bilingual model with 2T tokens",
            'params': "7B, 67B"
        },
        'wizard-math': {
            'description': "Specialized for math and logic problems",
            'params': "7B, 13B, 70B"
        },
        'glm4': {
            'description': "Strong multi-lingual general language model",
            'params': "9B"
        },
        'neural-chat': {
            'description': "Mistral-based model with good domain coverage",
            'params': "7B"
        },
        'moondream': {
            'description': "Small vision language model for edge devices",
            'params': "1.8B"
        },
        'llama3-chatqa': {
            'description': "NVIDIA's Llama 3 model for QA and RAG",
            'params': "8B, 70B"
        },
        'xwinlm': {
            'description': "Competitive conversational model based on Llama 2",
            'params': "7B, 13B"
        },
        'smollm': {
            'description': "Family of small models from 135M to 1.7B parameters",
            'params': "135M, 360M, 1.7B"
        },
        'nous-hermes': {
            'description': "General purpose models from Nous Research",
            'params': "7B, 13B"
        },
        'sqlcoder': {
            'description': "SQL completion model based on StarCoder",
            'params': "7B, 15B"
        },
        'phind-codellama': {
            'description': "Code generation model based on Code Llama",
            'params': "34B"
        },
        'yarn-llama2': {
            'description': "Extended Llama 2 with 128k context",
            'params': "7B, 13B"
        },
        'dolphincoder': {
            'description': "Uncensored StarCoder2-based coding model",
            'params': "7B, 15B"
        },
        'wizardlm': {
            'description': "General purpose Llama 2 model",
            'params': "7B"
        },
        'deepseek-v2': {
            'description': "Strong and efficient MoE language model",
            'params': "16B, 236B"
        },
        'starling-lm': {
            'description': "RL-trained model for improved chatbot helpfulness",
            'params': "7B"
        },
        'samantha-mistral': {
            'description': "Companion assistant with psychology focus",
            'params': "7B"
        },
        'falcon': {
            'description': "TII's model for text tasks and chatbots",
            'params': "7B, 40B, 180B"
        },
        'solar': {
            'description': "Compact 10.7B model for single-turn chat",
            'params': "10.7B"
        },
        'orca2': {
            'description': "Microsoft's reasoning-focused Llama 2 variant",
            'params': "7B, 13B"
        },
        'stable-beluga': {
            'description': "Orca-style dataset fine-tuned model",
            'params': "7B, 13B, 70B"
        },
        'yi-coder': {
            'description': "State-of-the-art code model under 10B parameters",
            'params': "1.5B, 9B"
        },
        'hermes3': {
            'description': "Latest Hermes model by Nous Research",
            'params': "8B, 70B, 405B"
        },
        'internlm2': {
            'description': "Practical model with strong reasoning",
            'params': "1M, 1.8B, 7B, 20B"
        },
        'dolphin-phi': {
            'description': "Uncensored Phi-based Dolphin model",
            'params': "2.7B"
        },
        'llava-phi3': {
            'description': "Small LLaVA model from Phi 3 Mini",
            'params': "3.8B"
        },
        'wizardlm-uncensored': {
            'description': "Uncensored Wizard LM variant",
            'params': "13B"
        },
        'yarn-mistral': {
            'description': "Extended Mistral with 128K context",
            'params': "7B"
        },
        'llama-pro': {
            'description': "Specialized Llama 2 with domain knowledge",
            'params': "N/A"
        },
        'medllama2': {
            'description': "Medical-focused Llama 2 model",
            'params': "7B"
        },
        'meditron': {
            'description': "Medical domain-adapted Llama 2",
            'params': "7B, 70B"
        },
        'nexusraven': {
            'description': "Function calling specialized model",
            'params': "13B"
        },
        'nous-hermes2-mixtral': {
            'description': "Nous Hermes 2 on Mixtral architecture",
            'params': "8x7B"
        },
        'llama3-groq-tool-use': {
            'description': "Advanced models for tool use/function calling",
            'params': "8B, 70B"
        },
        'codeup': {
            'description': "Llama2-based code generation model",
            'params': "13B"
        },
        'minicpm-v': {
            'description': "Vision-language understanding model",
            'params': "8B"
        },
        'everythinglm': {
            'description': "Uncensored Llama2 with 16K context",
            'params': "13B"
        },
        'magicoder': {
            'description': "Family of 7B code-focused models",
            'params': "7B"
        },
        'stablelm-zephyr': {
            'description': "Lightweight responsive chat model",
            'params': "3B"
        },
        'codebooga': {
            'description': "Merged high-performance code model",
            'params': "34B"
        },
        'wizard-vicuna': {
            'description': "Llama 2 based chat model",
            'params': "13B"
        },
        'mistrallite': {
            'description': "Extended context Mistral variant",
            'params': "7B"
        },
        'falcon2': {
            'description': "11B parameter model by TII",
            'params': "11B"
        },
        'bge-m3': {
            'description': "Versatile embedding model from BAAI",
            'params': "567M"
        },
        'duckdb-nsql': {
            'description': "Specialized SQL generation model",
            'params': "7B"
        },
        'megadolphin': {
            'description': "Enhanced large Dolphin variant",
            'params': "120B"
        },
        'notux': {
            'description': "High-quality MoE model",
            'params': "8x7B"
        },
        'open-orca-platypus2': {
            'description': "Merged chat and code generation model",
            'params': "13B"
        },
        'goliath': {
            'description': "Combined Llama 2 70B model",
            'params': "N/A"
        },
        'notus': {
            'description': "High-quality Zephyr-based chat model",
            'params': "7B"
        },
        'mathstral': {
            'description': "Specialized math reasoning model",
            'params': "7B"
        },
        'nemotron': {
            'description': "NVIDIA's customized Llama 3.1 variant",
            'params': "70B"
        },
        'solar-pro': {
            'description': "Advanced 22B single-GPU model",
            'params': "22B"
        },
        'dbrx': {
            'description': "Databricks' general-purpose LLM",
            'params': "132B"
        },
        'nuextract': {
            'description': "Information extraction model based on Phi-3",
            'params': "3.8B"
        },
        'reader-lm': {
            'description': "HTML to Markdown conversion model",
            'params': "0.5B, 1.5B"
        },
        'firefunction-v2': {
            'description': "Advanced function calling model",
            'params': "70B"
        },
        'alfred': {
            'description': "Robust conversational model",
            'params': "40B"
        },
        'bge-large': {
            'description': "BAAI's text embedding model",
            'params': "335M"
        },
        'deepseek-v2.5': {
            'description': "Upgraded DeepSeek with combined abilities",
            'params': "236B"
        },
        'bespoke-minicheck': {
            'description': "Specialized fact-checking model",
            'params': "7B"
        },
        'granite3-dense': {
            'description': "IBM's tool-optimized model",
            'params': "2B, 8B"
        },
        'paraphrase-multilingual': {
            'description': "Multilingual sentence embedding model",
            'params': "278M"
        },
        'granite3-moe': {
            'description': "IBM's first MoE model series",
            'params': "1B, 3B"
        },
        'shieldgemma': {
            'description': "Safety-focused instruction model",
            'params': "2B, 9B, 27B"
        },
        'llama-guard3': {
            'description': "Content safety classification model",
            'params': "1B, 8B"
        },
        'aya-expanse': {
            'description': "Multilingual performance model",
            'params': "8B, 32B"
        },
        'dolphin3': {
            'description': "Next generation of the Dolphin series designed to be the ultimate general purpose local model, enabling coding, math, agentic, function calling, and general use cases.",
            'params': "8B"
        },
        'smallthinker': {
            'description': "A new small reasoning model fine-tuned from the Qwen 2.5 3B Instruct model.",
            'params': "3B"
        },
        'granite3.1-dense': {
            'description': "IBM Granite text-only dense LLMs trained on over 12 trillion tokens of data, with significant improvements over predecessors in performance and speed.",
            'params': "2B, 8B"
        },
        'granite3.1-moe': {
            'description': "Long-context mixture of experts (MoE) Granite models from IBM designed for low latency usage.",
            'params': "1B, 3B"
        },
        'falcon3': {
            'description': "A family of efficient AI models under 10B parameters performant in science, math, and coding through innovative training techniques.",
            'params': "1B, 3B, 7B, 10B"
        },
        'granite-embedding': {
            'description': "IBM Granite text-only dense biencoder embedding models, with 30M in English and 278M for multilingual use cases.",
            'params': "30M, 278M"
        },
        'exaone3.5': {
            'description': "Collection of instruction-tuned bilingual (English and Korean) generative models by LG AI Research.",
            'params': "2.4B, 7.8B, 32B"
        },
        'llama3.3': {
            'description': "New state of the art 70B model offering similar performance compared to the Llama 3.1 405B model.",
            'params': "70B"
        },
        'snowflake-arctic-embed2': {
            'description': "Snowflake's frontier embedding model with multilingual support without sacrificing English performance or scalability.",
            'params': "568M"
        },
        'sailor2': {
            'description': "Multilingual language models made for South-East Asia.",
            'params': "1B, 8B, 20B"
        },
        'qwq': {
            'description': "Experimental research model focused on advancing AI reasoning capabilities.",
            'params': "32B"
        },
        'marco-o1': {
            'description': "An open large reasoning model for real-world solutions by the Alibaba International Digital Commerce Group.",
            'params': "7B"
        },
        'tulu3': {
            'description': "Leading instruction following model family, offering fully open-source data, code, and recipes by The Allen Institute for AI.",
            'params': "8B, 70B"
        },
        'athene-v2': {
            'description': "72B parameter model which excels at code completion, mathematics, and log extraction tasks.",
            'params': "72B"
        },
        'opencoder': {
            'description': "Open and reproducible code LLM family supporting chat in English and Chinese languages.",
            'params': "1.5B, 8B"
        },
        'llama3.2-vision': {
            'description': "Collection of instruction-tuned image reasoning generative models.",
            'params': "11B, 90B"
        },
        'smollm2': {
            'description': "Family of compact language models in three sizes.",
            'params': "135M, 360M, 1.7B"
        },
        'granite3-guardian': {
            'description': "IBM Granite Guardian models designed to detect risks in prompts and/or responses.",
            'params': "2B, 8B"
        }
    }

    # Create DataFrame from the dictionary
    df = pd.DataFrame([
        {
            'Model Name': name,
            'Description': info['description'],
            'Parameter Sizes': info['params']
        }
        for name, info in models_info.items()
    ])
    
    return df

def style_dataframe(df: pd.DataFrame) -> Styler:
    """Apply sophisticated styling to the DataFrame with wider cells"""
    
    styles = [
        # Table-wide styles
        {'selector': 'table', 
         'props': [
             ('border-collapse', 'separate'),
             ('border-spacing', '0 4px'),
             ('margin', '25px 0'),
             ('width', '100%'),
             ('border-radius', '8px'),
             ('overflow', 'hidden'),
             ('table-layout', 'fixed'),  # Added for better column width control
             ('box-shadow', '0 4px 6px rgba(0, 0, 0, 0.1)')
         ]},
        
        # Header styles
        {'selector': 'thead th', 
         'props': [
             ('background-color', '#374B5D'),
             ('color', '#FFFAE5'),
             ('padding', '18px 20px'),
             ('font-weight', '800'),
             ('text-transform', 'uppercase'),
             ('letter-spacing', '0.5px'),
             ('font-size', '20px'),
             ('border-bottom', '3px solid #56382D'),
             ('position', 'sticky'),
             ('top', '0')
         ]},
        
        # Index styling
        {'selector': 'tbody th', 
         'props': [
             ('background-color', '#935F4C'),
             ('color', '#FFFAE5'),
             ('padding', '12px 15px'),
             ('font-weight', '600'),
             ('text-align', 'center'),
             ('border-bottom', '1px solid rgba(255, 250, 229, 0.1)'),
             ('font-size', '17px'),
             ('width', '50px')  # Fixed width for index
         ]},
        
        # Cell styles
        {'selector': 'td', 
         'props': [
             ('padding', '12px 15px'),
             ('background-color', '#FFFAE5'),
             ('border-bottom', '1px solid rgba(55, 75, 93, 0.1)'),
             ('font-size', '17px'),
             ('transition', 'all 0.2s ease'),
             ('line-height', '1.6')  # Improved line height for readability
         ]},
        
        # Row hover effect
        {'selector': 'tbody tr:hover td', 
         'props': [
             ('background-color', '#F1E2AD'),
             ('transform', 'scale(1.01)'),
             ('box-shadow', '0 2px 4px rgba(0, 0, 0, 0.05)')
         ]},
        
        # Row hover effect for index
        {'selector': 'tbody tr:hover th', 
         'props': [
             ('transform', 'scale(1.01)'),
             ('box-shadow', '0 2px 4px rgba(0, 0, 0, 0.05)')
         ]},
        
        # Model name column
        {'selector': 'td:first-child', 
         'props': [
             ('font-weight', '600'),
             ('color', '#374B5D'),
             ('width', '100px')  # Fixed width for model name
         ]},
        
        # Description column
        {'selector': 'td:nth-child(2)', 
         'props': [
             ('text-align', 'left'),
             ('line-height', '1.6'),
             ('width', '250px'),  # Increased width for description
             ('white-space', 'normal'),
             ('padding-right', '20px')
         ]},
        
        # Parameter Sizes column
        {'selector': 'td:nth-child(3)', 
         'props': [
             ('width', '1000px'),  # Increased width for parameter sizes
             ('text-align', 'left'),
             ('white-space', 'normal')
         ]},
        
        {'selector': 'td:nth-child(5)', 
         'props': [
             ('width', '200px'),
             ('text-align', 'center')
         ]}

    ]

    return (df.style
            .set_table_styles(styles)
            .set_properties(**{
                'overflow': 'hidden',
                'text-overflow': 'ellipsis'
            })
            .set_table_attributes('class="dataframe hover-effect"'))

# Usage in Streamlit
def display_models_library(df: pd.DataFrame):

    st.markdown("""
        <div class="section-header">
            <h2>Ollama Models Library</h2>
            <p>Browse and explore available language models</p>
        </div>
    """, unsafe_allow_html=True)

    # Apply styling and display
    styled_df = style_dataframe(df)
    st.markdown(styled_df.to_html(escape=False), unsafe_allow_html=True)

def get_model_info(model_name):
    try:
        result = subprocess.run(['ollama', 'show', model_name], capture_output=True, text=True)

        if result.returncode != 0 or not result.stdout:
            return "\n".join([
                "",
                "⚠️ Model Information Unavailable",
                "-------------------------",
                "Unable to fetch model details. The model might be:",
                "• Still downloading",
                "• Partially downloaded",
                "• Not properly installed",
                "",
                f"You can try: 'ollama show {model_name}' in terminal for more details."
            ])

        raw_info = result.stdout.strip()
        
        def get_value(key):
            try:
                return raw_info.split(key)[1].split('\n')[0].strip()
            except:
                return 'N/A'
                
        def get_section(start_key, end_key='Parameters'):
            try:
                return raw_info.split(start_key)[1].split(end_key)[0].strip()
            except:
                return 'N/A'

        # Build the display text piece by piece
        display_text = [
            "",
            "📱 Model Architecture",
            "-------------------",
            f"• Architecture: {get_value('architecture')}",
            f"• Parameters: {get_value('parameters')}",
            f"• Quantization: {get_value('quantization')}",
            "",
            "🔄 Context Settings",
            "----------------",
            f"• Context Length: {get_value('context length')}",
            f"• Embedding Length: {get_value('embedding length')}",
            "",
        ]
        
        return "\n".join(display_text)
        
    except Exception as e:
        st.error(f"Error fetching model info: {e}")
        return None


