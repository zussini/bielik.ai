from vllm import LLMEngine
from vllm.executor import default_executor_class

# Inicjalizacja engine z modelem 'gpt2'
engine = LLMEngine("gpt2", executor_class=default_executor_class, log_stats=False)

# Przykładowe użycie
prompt = "Hello world"
result = engine.generate(prompt, max_tokens=50)
print(result)

