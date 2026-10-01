from transformers import AutoTokenizer, AutoModelForCausalLM
from dataclasses import dataclass
import time
from logging import getLogger
from typing import Optional
logger = getLogger()

@dataclass
class ModelConfig:
    model_name: str
    tokenizer_name: Optional[str]    
    lazy_load: bool = False
    device_map: str = "auto"
    torch_dtype: str = "auto"

@dataclass
class QueryConfig:
    messages: dict
    max_new_tokens: int = 40



class QueryModel:
    def __init__(self, config = ModelConfig):
        self.model = None
        self.tokenizer = None
        self.model_name = config.model_name
        self.tokenizer_name = config.tokenizer_name if config.tokenizer_name else config.model_name
        self.lazy_load = config.lazy_load
        self.device_map = config.device_map
        self.torch_dtype = config.torch_dtype
        if not config.lazy_load:
            self.load()

    def load(self):
        self.model = AutoModelForCausalLM.from_pretrained(self.model_name, device_map = self.device_map, torch_dtype = self.torch_dtype)
        self.tokenizer = AutoTokenizer.from_pretrained(self.tokenizer_name)
        

    def unload(self):
        self.model = None
        self.tokenizer = None

    def query(self, config: QueryConfig, **args):
        if not (self.model and self.tokenizer):
            self.load()
        
        logger.info("Encoding The query")
        inputs = self.tokenizer.apply_chat_template(
            config.messages,
            **args
        ).to(self.model.device)

        outputs = self.model.generate(max_new_tokens = config.max_new_tokens, **inputs)

        response = self.tokenizer.decode(outputs[0][inputs["input_ids"].shape[-1]:])

        if self.lazy_load:
            self.unload()
        logger.info("Generated Output")
        return response

if __name__ == "__main__":

    messages1 = [
    {"role": "user", "content": "Hi there! Let's have a conversation. Let's start talking about legal way to make easy money"},
    ]


    model_config = ModelConfig(model_name="Qwen/Qwen2.5-3B-Instruct", tokenizer_name=None, lazy_load = False, device_map="auto")
    query_config = QueryConfig(messages=messages1, max_new_tokens=500)

    model_class = QueryModel(config = model_config)

    # while True:
    #     query_output = model_class.query(
    #         config = query_config, 
    #         add_generation_prompt=True,
    #         tokenize=True,
    #         return_dict=True,
    #         return_tensors="pt",
    #         )
    #     print(query_output)
    

    # count = 0
    # while True:
    #     query_output = model_class.query(
    #         config = query_config, 
    #         add_generation_prompt=True,
    #         tokenize=True,
    #         return_dict=True,
    #         return_tensors="pt",
    #         )
    #     print(f"Person {count%2}: {query_output}")
    #     query_config.messages = [{"role": "user", "content": query_output}]
    #     count += 1





