from laiser.llm_models.gemini import gemini_generate
from laiser.llm_models.hugging_face_llm import llm_generate

def llm_router(prompt: str, model_id: str, use_gpu: bool, tokenizer=None, model=None):
    if model_id == 'gemini':
        return gemini_generate(prompt)

    # Fallback: Hugging Face LLM
    return llm_generate(prompt, tokenizer, model, model_id, use_gpu)
