---
tags: [gradio-custom-component, TextBox, textbox]
title: gradio_tokenizertextbox
short_description: Textbox tokenizer
colorFrom: blue
colorTo: yellow
sdk: gradio
pinned: false
app_file: space.py
---

# `gradio_tokenizertextbox`
<img alt="Static Badge" src="https://img.shields.io/badge/version%20-%200.0.1%20-%20orange">  

Textbox tokenizer

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

```

## `TokenizerTextBox`

### Initialization

<table>
<thead>
<tr>
<th align="left">name</th>
<th align="left" style="width: 25%;">type</th>
<th align="left">default</th>
<th align="left">description</th>
</tr>
</thead>
<tbody>
<tr>
<td align="left"><code>value</code></td>
<td align="left" style="width: 25%;">

```python
typing.Union[str, dict, typing.Callable, NoneType][
    str, dict, Callable, None
]
```

</td>
<td align="left"><code>None</code></td>
<td align="left">The initial value. Can be a string to initialize the text, or a dictionary for full state. If a function is provided, it will be called when the app loads to set the initial value.</td>
</tr>

<tr>
<td align="left"><code>model</code></td>
<td align="left" style="width: 25%;">

```python
str
```

</td>
<td align="left"><code>"Xenova/gpt-3"</code></td>
<td align="left">The name of a Hugging Face tokenizer to use (must be compatible with Transformers.js). Defaults to "Xenova/gpt-2".</td>
</tr>

<tr>
<td align="left"><code>display_mode</code></td>
<td align="left" style="width: 25%;">

```python
"text" | "token_ids" | "hidden"
```

</td>
<td align="left"><code>"text"</code></td>
<td align="left">Controls the content of the token visualization panel. Can be 'text' (default), 'token_ids', or 'hidden'.</td>
</tr>

<tr>
<td align="left"><code>lines</code></td>
<td align="left" style="width: 25%;">

```python
int
```

</td>
<td align="left"><code>2</code></td>
<td align="left">The minimum number of line rows for the textarea.</td>
</tr>

<tr>
<td align="left"><code>max_lines</code></td>
<td align="left" style="width: 25%;">

```python
int | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">The maximum number of line rows for the textarea.</td>
</tr>

<tr>
<td align="left"><code>placeholder</code></td>
<td align="left" style="width: 25%;">

```python
str | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">A placeholder hint to display in the textarea when it is empty.</td>
</tr>

<tr>
<td align="left"><code>autofocus</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>False</code></td>
<td align="left">If True, will focus on the textbox when the page loads.</td>
</tr>

<tr>
<td align="left"><code>autoscroll</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">If True, will automatically scroll to the bottom of the textbox when the value changes.</td>
</tr>

<tr>
<td align="left"><code>text_align</code></td>
<td align="left" style="width: 25%;">

```python
typing.Optional[typing.Literal["left", "right"]][
    "left" | "right", None
]
```

</td>
<td align="left"><code>None</code></td>
<td align="left">How to align the text in the textbox, can be: "left" or "right".</td>
</tr>

<tr>
<td align="left"><code>rtl</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>False</code></td>
<td align="left">If True, sets the direction of the text to right-to-left.</td>
</tr>

<tr>
<td align="left"><code>show_copy_button</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>False</code></td>
<td align="left">If True, a copy button will be shown.</td>
</tr>

<tr>
<td align="left"><code>max_length</code></td>
<td align="left" style="width: 25%;">

```python
int | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">The maximum number of characters allowed in the textbox.</td>
</tr>

<tr>
<td align="left"><code>label</code></td>
<td align="left" style="width: 25%;">

```python
str | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">The label for this component, displayed above the component.</td>
</tr>

<tr>
<td align="left"><code>info</code></td>
<td align="left" style="width: 25%;">

```python
str | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">Additional component description, displayed below the label.</td>
</tr>

<tr>
<td align="left"><code>every</code></td>
<td align="left" style="width: 25%;">

```python
float | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">If `value` is a callable, this sets a timer to run the function repeatedly.</td>
</tr>

<tr>
<td align="left"><code>show_label</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">If False, the label is not displayed.</td>
</tr>

<tr>
<td align="left"><code>container</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">If False, the component will not be wrapped in a container.</td>
</tr>

<tr>
<td align="left"><code>scale</code></td>
<td align="left" style="width: 25%;">

```python
int | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">The relative size of the component compared to others in a `gr.Row` or `gr.Column`.</td>
</tr>

<tr>
<td align="left"><code>min_width</code></td>
<td align="left" style="width: 25%;">

```python
int
```

</td>
<td align="left"><code>160</code></td>
<td align="left">The minimum-width of the component in pixels.</td>
</tr>

<tr>
<td align="left"><code>interactive</code></td>
<td align="left" style="width: 25%;">

```python
bool | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">If False, the user will not be able to edit the text.</td>
</tr>

<tr>
<td align="left"><code>visible</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">If False, the component will be hidden.</td>
</tr>

<tr>
<td align="left"><code>elem_id</code></td>
<td align="left" style="width: 25%;">

```python
str | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">An optional string that is assigned as the id of this component in the HTML DOM.</td>
</tr>

<tr>
<td align="left"><code>elem_classes</code></td>
<td align="left" style="width: 25%;">

```python
list[str] | str | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">An optional list of strings that are assigned as the classes of this component in the HTML DOM.</td>
</tr>
</tbody></table>


### Events

| name | description |
|:-----|:------------|
| `change` | Triggered when the value of the TokenizerTextBox changes either because of user input (e.g. a user types in a textbox) OR because of a function update (e.g. an image receives a value from the output of an event trigger). See `.input()` for a listener that is only triggered by user input. |
| `input` | This listener is triggered when the user changes the value of the TokenizerTextBox. |
| `submit` | This listener is triggered when the user presses the Enter key while the TokenizerTextBox is focused. |
| `blur` | This listener is triggered when the TokenizerTextBox is unfocused/blurred. |
| `select` | Event listener for when the user selects or deselects the TokenizerTextBox. Uses event data gradio.SelectData to carry `value` referring to the label of the TokenizerTextBox, and `selected` to refer to state of the TokenizerTextBox. See EventData documentation on how to use this event data |



### User function

The impact on the users predict function varies depending on whether the component is used as an input or output for an event (or both).

- When used as an Input, the component only impacts the input signature of the user function.
- When used as an output, the component only impacts the return signature of the user function.

The code snippet below is accurate in cases where the component is used as both an input and an output.

- **As output:** Is passed, a dictionary enriched with 'char_count' and 'token_count'.
- **As input:** Should return, the value to set for the component, can be a string or a dictionary.

 ```python
 def predict(
     value: dict | None
 ) -> str | dict | None:
     return value
 ```
 
