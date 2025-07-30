import torch
from vllm import LLM
from vllm import SamplingParams

sampling_params = SamplingParams(max_tokens=200, seed=42)


def llm_generate(prompt, model_id, use_gpu):
    if torch.cuda.is_available() and use_gpu:
            print("GPU is available. Using GPU for Large Language model initialization...")
            
            try:
                torch.cuda.empty_cache()
                llm = None
                # Use quantization to reduce the model size and memory usage
                if model_id:
                    llm = LLM(model=model_id, dtype="float16", quantization='gptq')
                else:
                    llm = LLM(model="marcsun13/gemma-2-9b-it-GPTQ", dtype="float16", quantization='gptq')   
                
                result = llm.generate([prompt], sampling_params=sampling_params)
                raw_text = result[0].outputs[0].text.strip()
                return raw_text
            except Exception as e:
                print(f"Failed to initialize LLM: {e}")
                raise
    else:
        print("GPU is not available. Using CPU for SkillNer model initialization...")
       