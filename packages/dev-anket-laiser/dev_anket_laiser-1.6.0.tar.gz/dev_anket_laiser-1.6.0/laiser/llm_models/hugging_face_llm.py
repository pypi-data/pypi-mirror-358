from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

def llm_generate(prompt: str, tokenizer, model, model_id: str, use_gpu: bool):
    if tokenizer is None or model is None:
        quantization_config = BitsAndBytesConfig(load_in_8bit=True)

        tokenizer = AutoTokenizer.from_pretrained(model_id)
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            quantization_config=quantization_config,
            device_map="auto"
        )

    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    outputs = model.generate(
        **inputs,
        max_new_tokens=100,
        pad_token_id=tokenizer.pad_token_id,
        eos_token_id=tokenizer.eos_token_id
    )

    return tokenizer.decode(outputs[0], skip_special_tokens=True)
