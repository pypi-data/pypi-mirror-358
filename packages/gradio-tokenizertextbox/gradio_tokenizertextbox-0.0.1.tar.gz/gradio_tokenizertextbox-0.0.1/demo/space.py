
import gradio as gr
from app import demo as app
import os

_docs = {'TokenizerTextBox': {'description': "Creates a textarea for user to enter string input or display string output,\nwith built-in, client-side tokenization visualization powered by Transformers.js.\nThe component's value is a JSON object containing the text and tokenization results.", 'members': {'__init__': {'value': {'type': 'typing.Union[str, dict, typing.Callable, NoneType][\n    str, dict, Callable, None\n]', 'default': 'None', 'description': 'The initial value. Can be a string to initialize the text, or a dictionary for full state. If a function is provided, it will be called when the app loads to set the initial value.'}, 'model': {'type': 'str', 'default': '"Xenova/gpt-3"', 'description': 'The name of a Hugging Face tokenizer to use (must be compatible with Transformers.js). Defaults to "Xenova/gpt-2".'}, 'display_mode': {'type': '"text" | "token_ids" | "hidden"', 'default': '"text"', 'description': "Controls the content of the token visualization panel. Can be 'text' (default), 'token_ids', or 'hidden'."}, 'lines': {'type': 'int', 'default': '2', 'description': 'The minimum number of line rows for the textarea.'}, 'max_lines': {'type': 'int | None', 'default': 'None', 'description': 'The maximum number of line rows for the textarea.'}, 'placeholder': {'type': 'str | None', 'default': 'None', 'description': 'A placeholder hint to display in the textarea when it is empty.'}, 'autofocus': {'type': 'bool', 'default': 'False', 'description': 'If True, will focus on the textbox when the page loads.'}, 'autoscroll': {'type': 'bool', 'default': 'True', 'description': 'If True, will automatically scroll to the bottom of the textbox when the value changes.'}, 'text_align': {'type': 'typing.Optional[typing.Literal["left", "right"]][\n    "left" | "right", None\n]', 'default': 'None', 'description': 'How to align the text in the textbox, can be: "left" or "right".'}, 'rtl': {'type': 'bool', 'default': 'False', 'description': 'If True, sets the direction of the text to right-to-left.'}, 'show_copy_button': {'type': 'bool', 'default': 'False', 'description': 'If True, a copy button will be shown.'}, 'max_length': {'type': 'int | None', 'default': 'None', 'description': 'The maximum number of characters allowed in the textbox.'}, 'label': {'type': 'str | None', 'default': 'None', 'description': 'The label for this component, displayed above the component.'}, 'info': {'type': 'str | None', 'default': 'None', 'description': 'Additional component description, displayed below the label.'}, 'every': {'type': 'float | None', 'default': 'None', 'description': 'If `value` is a callable, this sets a timer to run the function repeatedly.'}, 'show_label': {'type': 'bool', 'default': 'True', 'description': 'If False, the label is not displayed.'}, 'container': {'type': 'bool', 'default': 'True', 'description': 'If False, the component will not be wrapped in a container.'}, 'scale': {'type': 'int | None', 'default': 'None', 'description': 'The relative size of the component compared to others in a `gr.Row` or `gr.Column`.'}, 'min_width': {'type': 'int', 'default': '160', 'description': 'The minimum-width of the component in pixels.'}, 'interactive': {'type': 'bool | None', 'default': 'None', 'description': 'If False, the user will not be able to edit the text.'}, 'visible': {'type': 'bool', 'default': 'True', 'description': 'If False, the component will be hidden.'}, 'elem_id': {'type': 'str | None', 'default': 'None', 'description': 'An optional string that is assigned as the id of this component in the HTML DOM.'}, 'elem_classes': {'type': 'list[str] | str | None', 'default': 'None', 'description': 'An optional list of strings that are assigned as the classes of this component in the HTML DOM.'}}, 'postprocess': {'value': {'type': 'str | dict | None', 'description': 'The value to set for the component, can be a string or a dictionary.'}}, 'preprocess': {'return': {'type': 'dict | None', 'description': "A dictionary enriched with 'char_count' and 'token_count'."}, 'value': None}}, 'events': {'change': {'type': None, 'default': None, 'description': 'Triggered when the value of the TokenizerTextBox changes either because of user input (e.g. a user types in a textbox) OR because of a function update (e.g. an image receives a value from the output of an event trigger). See `.input()` for a listener that is only triggered by user input.'}, 'input': {'type': None, 'default': None, 'description': 'This listener is triggered when the user changes the value of the TokenizerTextBox.'}, 'submit': {'type': None, 'default': None, 'description': 'This listener is triggered when the user presses the Enter key while the TokenizerTextBox is focused.'}, 'blur': {'type': None, 'default': None, 'description': 'This listener is triggered when the TokenizerTextBox is unfocused/blurred.'}, 'select': {'type': None, 'default': None, 'description': 'Event listener for when the user selects or deselects the TokenizerTextBox. Uses event data gradio.SelectData to carry `value` referring to the label of the TokenizerTextBox, and `selected` to refer to state of the TokenizerTextBox. See EventData documentation on how to use this event data'}}}, '__meta__': {'additional_interfaces': {}, 'user_fn_refs': {'TokenizerTextBox': []}}}

abs_path = os.path.join(os.path.dirname(__file__), "css.css")

with gr.Blocks(
    css=abs_path,
    theme=gr.themes.Default(
        font_mono=[
            gr.themes.GoogleFont("Inconsolata"),
            "monospace",
        ],
    ),
) as demo:
    gr.Markdown(
"""
# `gradio_tokenizertextbox`

<div style="display: flex; gap: 7px;">
<img alt="Static Badge" src="https://img.shields.io/badge/version%20-%200.0.1%20-%20orange">  
</div>

Textbox tokenizer
""", elem_classes=["md-custom"], header_links=True)
    app.render()
    gr.Markdown(
"""
## Installation

```bash
pip install gradio_tokenizertextbox
```

## Usage

```python
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
    \"\"\"
    This function receives the full dictionary from the component.
    \"\"\"
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

```
""", elem_classes=["md-custom"], header_links=True)


    gr.Markdown("""
## `TokenizerTextBox`

### Initialization
""", elem_classes=["md-custom"], header_links=True)

    gr.ParamViewer(value=_docs["TokenizerTextBox"]["members"]["__init__"], linkify=[])


    gr.Markdown("### Events")
    gr.ParamViewer(value=_docs["TokenizerTextBox"]["events"], linkify=['Event'])




    gr.Markdown("""

### User function

The impact on the users predict function varies depending on whether the component is used as an input or output for an event (or both).

- When used as an Input, the component only impacts the input signature of the user function.
- When used as an output, the component only impacts the return signature of the user function.

The code snippet below is accurate in cases where the component is used as both an input and an output.

- **As input:** Is passed, a dictionary enriched with 'char_count' and 'token_count'.
- **As output:** Should return, the value to set for the component, can be a string or a dictionary.

 ```python
def predict(
    value: dict | None
) -> str | dict | None:
    return value
```
""", elem_classes=["md-custom", "TokenizerTextBox-user-fn"], header_links=True)




    demo.load(None, js=r"""function() {
    const refs = {};
    const user_fn_refs = {
          TokenizerTextBox: [], };
    requestAnimationFrame(() => {

        Object.entries(user_fn_refs).forEach(([key, refs]) => {
            if (refs.length > 0) {
                const el = document.querySelector(`.${key}-user-fn`);
                if (!el) return;
                refs.forEach(ref => {
                    el.innerHTML = el.innerHTML.replace(
                        new RegExp("\\b"+ref+"\\b", "g"),
                        `<a href="#h-${ref.toLowerCase()}">${ref}</a>`
                    );
                })
            }
        })

        Object.entries(refs).forEach(([key, refs]) => {
            if (refs.length > 0) {
                const el = document.querySelector(`.${key}`);
                if (!el) return;
                refs.forEach(ref => {
                    el.innerHTML = el.innerHTML.replace(
                        new RegExp("\\b"+ref+"\\b", "g"),
                        `<a href="#h-${ref.toLowerCase()}">${ref}</a>`
                    );
                })
            }
        })
    })
}

""")

demo.launch()
