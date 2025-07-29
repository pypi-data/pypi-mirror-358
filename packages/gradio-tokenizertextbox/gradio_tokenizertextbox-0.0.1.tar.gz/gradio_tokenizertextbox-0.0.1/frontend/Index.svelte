<svelte:options accessors={true} />

<script context="module" lang="ts">
	export { default as BaseTextbox } from "./shared/Textbox.svelte";
	export { default as BaseExample } from "./Example.svelte";
</script>

<script lang="ts">
	import { onMount } from "svelte";
	import type { Gradio } from "@gradio/utils";
	import TextBox from "./shared/Textbox.svelte";
	import { Block } from "@gradio/atoms";
	import type { LoadingStatus } from "@gradio/statustracker";
	import { AutoTokenizer, env } from "@xenova/transformers";
	env.allowLocalModels = false;
	
	export let gradio: Gradio<{ change: never; /* ... */ }>;
	export let value: { text: string; tokens: string[]; token_ids: number[]; } = { text: "", tokens: [], token_ids: [] };	
	export let label: string = "Textbox";
	export let info: string | undefined = undefined;
	export let elem_id: string = "";
	export let elem_classes: string[] = [];
	export let visible: boolean = true;
	export let lines: number;
	export let placeholder: string = "";
	export let show_label: boolean;
	export let max_lines: number | undefined = undefined;
	export let type: "text" | "password" | "email" = "text";
	export let container: boolean = true;
	export let scale: number | null = null;
	export let min_width: number | undefined = undefined;
	export let submit_btn: string | boolean | null = null;
	export let stop_btn: string | boolean | null = null;
	export let show_copy_button: boolean = false;
	export const loading_status: LoadingStatus | undefined = undefined;
	export let rtl: boolean = false;
	export let text_align: "left" | "right" | undefined = undefined;
	export let autofocus: boolean = false;
	export let autoscroll: boolean = true;
	export let interactive: boolean;
	export let max_length: number | undefined = undefined;
	export let model: string = "Xenova/gpt-2"; 
	export let display_mode: 'text' | 'token_ids' | 'hidden' = 'text';


	let tokenizer: any = null;
	let status: string = "Initializing...";
	let currentModel: string = "";
	let showVisualization = true;
	const colors = ["#d8b4fe", "#bbf7d0", "#fde047", "#fca5a5", "#93c5fd"];
	let debounceTimer: ReturnType<typeof setTimeout>;
	let lastProcessedText: string | undefined = undefined;


	async function tokenizeAndUpdate() {
		if (!tokenizer || value.text === lastProcessedText) {
			return; // Exit if the text is the same, breaking the loop.
		}

		// If the text is new, update our tracker immediately.
		lastProcessedText = value.text;

		try {
			const ids = tokenizer.encode(value.text);
			const tokens = ids.map((id: number) => tokenizer.decode([id]));
			value.tokens = tokens;
			value.token_ids = ids;
			gradio.dispatch("change");
		} catch (e: any) {
			status = `Tokenization error: ${e.message}`;
			value = value; // Force Svelte to re-render the status message
		}
	}

	async function loadTokenizer(model_name: string) {
		if (currentModel === model_name && tokenizer) return;
		status = `Loading tokenizer: ${model_name}...`;
		currentModel = model_name;
		tokenizer = null;
		
		try {
			tokenizer = await AutoTokenizer.from_pretrained(model_name);
			status = `Tokenizer "${model_name}" loaded.`;
			// After loading, reset the tracker and tokenize the current text.
			lastProcessedText = undefined; 
			await tokenizeAndUpdate(); 
		} catch (e: any) {
			status = `Error loading model: ${e.message}`;
		}
	}
	
	onMount(() => {
		loadTokenizer(model);
	});

	$: if (value && value.text !== undefined) {
		clearTimeout(debounceTimer);
		debounceTimer = setTimeout(tokenizeAndUpdate, 300);
	}

	$: if (model && model !== currentModel) {
		loadTokenizer(model);
	}
</script>

<Block {visible} {elem_id} {elem_classes} {scale} {min_width} allow_overflow={false} padding={container}>
	<!-- ... (Header with counters and toggle) ... -->
	<div class="component-header">
		{#if display_mode !== 'hidden'}
			<div class="visualization-toggle">
				<input type="checkbox" id="show-viz-{elem_id}" bind:checked={showVisualization}>
				<label for="show-viz-{elem_id}">Show visualization</label>
			</div>
			<div class="counters">
				<span>Tokens: {value?.tokens?.length || 0}</span>
				<span>Characters: {value?.text?.length || 0}</span>
			</div>
		{/if}
	</div>
	
	<!-- ... (Textbox) ... -->
	<TextBox
		bind:value={value.text}
		{label} {info} {show_label} {lines} {type} {rtl} {text_align} {max_lines} {placeholder}
		{submit_btn} {stop_btn} {show_copy_button} {autofocus} {container} {autoscroll} {max_length}
		disabled={!interactive}
	/>

	<!-- ... (Visualization Panel) ... -->
	{#if showVisualization && display_mode !== 'hidden'}
		<div class="token-visualization-container">
			{#if display_mode === 'text'}
				<div class="token-display">
					{#if value?.tokens?.length > 0}
						{#each value.tokens as token, i}
							<span class="token" style="background-color: {colors[i % colors.length]};">
								{token.replace(/ /g, '\u00A0')}
							</span>
						{/each}
					{:else}
						<span class="status">{status}</span>
					{/if}
				</div>
			{:else if display_mode === 'token_ids'}
				<div class="token-display token-ids">
					{#if value?.token_ids?.length > 0}
						[{value.token_ids.join(", ")}]
					{:else}
						<span class="status">{status}</span>
					{/if}
				</div>
			{/if}
		</div>
	{/if}
</Block>

<style>	
	.component-header { 
		display: flex; 
		justify-content: space-between; 
		align-items: center; 
		margin-bottom: 4px; 
		min-height: 20px; 
	}
	.visualization-toggle { 
		display: flex; 
		align-items: center; 
		gap: 6px; 
		font-size: 14px; 
		color: #4B5563; 
	}
	.visualization-toggle input, .visualization-toggle label { 
		cursor: pointer; 
		user-select: none; 
	}
	.counters { 
		display: flex; 
		gap: 16px;
		font-size: 14px; 
		color: #6B7280; 
		font-family: sans-serif; 
	}
	.token-visualization-container { 
		margin-top: 12px; 
	}
	.token-display { 
		color: #212529 !important; 
		padding: 10px; 
		border: 1px solid #e5e7eb; 
		background-color: #f9fafb; 
		border-radius: 8px; 
		min-height: 70px; 
		line-height: 1.8; 
		white-space: pre-wrap; 
		overflow-y: auto; 
		font-family: monospace; 
		font-size: 1rem; }
	.token { 
		display: inline-block; 
		padding: 2px 6px; 
		border-radius: 4px; 
		margin: 2px; 
	}
	.token-ids { 
		word-break: break-all; 
	}
</style>