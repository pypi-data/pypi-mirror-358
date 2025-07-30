
from laiser.llm_models.gemini import gemini_generate
# from laiser.llm_models.hugging_face_llm import llm_generate

def llm_router(prompt: str,model_id, use_gpu):
    if model_id == 'gemini': 
        return gemini_generate(prompt)
    # return llm_generate(prompt, model_id, use_gpu)
