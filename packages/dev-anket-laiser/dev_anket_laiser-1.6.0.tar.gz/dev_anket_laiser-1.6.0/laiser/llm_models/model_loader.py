from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from transformers.utils import EntryNotFoundError, RepositoryNotFoundError

DEFAULT_MODEL_ID = "google/gemma-2-9b-it"

def load_model(token: str = "", model_id: str = None):
    model_id = model_id or DEFAULT_MODEL_ID
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
        print(f"[INFO] Falling back to default model: {DEFAULT_MODEL_ID}")
        tokenizer = AutoTokenizer.from_pretrained(DEFAULT_MODEL_ID, use_auth_token=token)
        model = AutoModelForCausalLM.from_pretrained(
            DEFAULT_MODEL_ID,
            use_auth_token=token,
            quantization_config=quantization_config,
            device_map="auto"
        )

    return tokenizer, model
