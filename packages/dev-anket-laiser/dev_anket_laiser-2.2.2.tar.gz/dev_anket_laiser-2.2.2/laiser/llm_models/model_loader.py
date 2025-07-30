from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from transformers.utils import EntryNotFoundError, RepositoryNotFoundError
from vllm import LLM

DEFAULT_TRANSFORMER_MODEL_ID = "google/gemma-2-9b-it"

def load_model_from_transformer( model_id: str = None,token: str = ""):
    model_id = model_id or DEFAULT_TRANSFORMER_MODEL_ID
    quantization_config = BitsAndBytesConfig(load_in_8bit=True)

    try:
        tokenizer = AutoTokenizer.from_pretrained(model_id, use_auth_token=token)
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            use_auth_token=token,
            quantization_config=quantization_config,
            device_map="auto"
        )
    except (RepositoryNotFoundError, EntryNotFoundError, OSError) as e:
        print(f"[WARN] Failed to load model '{model_id}': {e}")
        print(f"[INFO] Falling back to default model: {DEFAULT_TRANSFORMER_MODEL_ID}")
        tokenizer = AutoTokenizer.from_pretrained(DEFAULT_TRANSFORMER_MODEL_ID, use_auth_token=token)
        model = AutoModelForCausalLM.from_pretrained(
            DEFAULT_TRANSFORMER_MODEL_ID,
            use_auth_token=token,
            quantization_config=quantization_config,
            device_map="auto"
        )

    return tokenizer, model


DEFAULT_VLLM_MODEL_ID = "marcsun13/gemma-2-9b-it-GPTQ"

def load_model_from_vllm(model_id: str = None, token: str = None):
    model_id = model_id or DEFAULT_VLLM_MODEL_ID

    try:
        llm = LLM(
            model=model_id,
            dtype="float16",
            quantization="gptq",
            token=token  # Pass HF token here
        )
        print(f"[INFO] Successfully loaded vLLM model: {model_id}")
    except Exception as e:
        print(f"[WARN] Failed to load model '{model_id}': {e}")
        print(f"[INFO] Falling back to default model: {DEFAULT_VLLM_MODEL_ID}")
        llm = LLM(
            model=DEFAULT_VLLM_MODEL_ID,
            dtype="float16",
            quantization="gptq",
            token=token  # Pass HF token here
        )
    
    return llm