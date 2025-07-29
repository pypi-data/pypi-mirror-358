#
# demo/app.py
#
import gradio as gr
from gradio_tokenizertextbox import TokenizerTextBox 
import json



TOKENIZER_OPTIONS = {
    "Xenova/clip-vit-large-patch14": "CLIP ViT-L/14",
    "Xenova/gpt-4": "gpt-4 / gpt-3.5-turbo / text-embedding-ada-002",
    "Xenova/text-davinci-003": "text-davinci-003 / text-davinci-002",
    "Xenova/gpt-3": "gpt-3",
    "Xenova/grok-1-tokenizer": "Grok-1",
    "Xenova/claude-tokenizer": "Claude",
    "Xenova/mistral-tokenizer-v3": "Mistral v3",
    "Xenova/mistral-tokenizer-v1": "Mistral v1",
    "Xenova/gemma-tokenizer": "Gemma",
    "Xenova/llama-3-tokenizer": "Llama 3",
    "Xenova/llama-tokenizer": "LLaMA / Llama 2",
    "Xenova/c4ai-command-r-v01-tokenizer": "Cohere Command-R",
    "Xenova/t5-small": "T5",
    "Xenova/bert-base-cased": "bert-base-cased",
  
}

# 2. Prepare the choices for the gr.Dropdown component
# The format is a list of tuples: [(display_name, internal_value)]
dropdown_choices = [
    (display_name, model_name) 
    for model_name, display_name in TOKENIZER_OPTIONS.items()
]

def process_output(tokenization_data):
    """
    This function receives the full dictionary from the component.
    """
    if not tokenization_data:
        return {"status": "Waiting for input..."}
    return tokenization_data

# --- Gradio Application ---
with gr.Blocks() as demo:
    gr.Markdown("# TokenizerTextBox Component Demo")
    gr.Markdown("# Component idea taken from the original example application on [Xenova Tokenizer Playground](https://github.com/huggingface/transformers.js-examples/tree/main/the-tokenizer-playground) ")
    gr.Markdown("## Select a tokenizer from the dropdown menu to see how it processes your text in real-time.")
    gr.Markdown("## For more models, check out the [Xenova Transformers Models](https://huggingface.co/Xenova/models) page.")
    
    with gr.Row():
        # 3. Create the Dropdown for model selection
        model_selector = gr.Dropdown(
            label="Select a Tokenizer",
            choices=dropdown_choices,
            value="Xenova/clip-vit-large-patch14", # Set a default value
        )
        
        display_mode_radio = gr.Radio(
            ["text", "token_ids", "hidden"],
            label="Display Mode",
            value="text"
        )
    
    # 4. Initialize the component with a default model
    tokenizer_input = TokenizerTextBox(
        label="Type your text here",
        value="Gradio is an awesome tool for building ML demos!",
        model="Xenova/clip-vit-large-patch14", # Must match the dropdown's default value
        display_mode="text",
    )
    
    output_info = gr.JSON(label="Component Output (from preprocess)")

    # --- Event Listeners ---

    # A. When the tokenizer component changes, update the JSON output
    tokenizer_input.change(
        fn=process_output, 
        inputs=tokenizer_input, 
        outputs=output_info
    )

    # B. When the dropdown value changes, update the 'model' prop of our component
    def update_tokenizer_model(selected_model):
        return gr.update(model=selected_model)

    model_selector.change(
        fn=update_tokenizer_model,
        inputs=model_selector,
        outputs=tokenizer_input
    )

    # C. When the radio button value changes, update the 'display_mode' prop
    def update_display_mode(mode):
        return gr.update(display_mode=mode)

    display_mode_radio.change(
        fn=update_display_mode,
        inputs=display_mode_radio,
        outputs=tokenizer_input
    )

if __name__ == '__main__':
    demo.launch()
