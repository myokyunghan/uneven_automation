from lib.annotation.import_files import *
from vllm import LLM, SamplingParams
# https://github.com/meta-llama/llama-recipes/blob/main/recipes/quickstart/Prompt_Engineering_with_Llama_3.ipynb
class VLLM:
    def __init__(self):  
        self.llm = LLM( model="/usr/share/d_ollama/.ollama/models/hf_model/Llama-3.2-3B-Instruct",
                   tensor_parallel_size=4,   # or 4, since you have 4 GPUs
                    dtype="auto",
                    gpu_memory_utilization=0.3)
        
        self.params = SamplingParams(temperature=0.01, top_p=0.9, max_tokens=10)


    


               
                
