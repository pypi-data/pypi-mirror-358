from laiser.llm_models.gemini import gemini_generate
from laiser.llm_models.hugging_face_llm import llm_generate_vllm

def llm_router(prompt: str, model_id: str, use_gpu: bool,llm,  tokenizer=None, model=None,api_key=None):
    if model_id == 'gemini':
        return gemini_generate(prompt, api_key)

    # Fallback: Hugging Face LLM
    return llm_generate_vllm(prompt, llm)
