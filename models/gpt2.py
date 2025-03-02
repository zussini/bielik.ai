from vllm import LLM, SamplingParams

print("Ładowanie modelu GPT-2...")
# Inicjalizacja modelu GPT-2 – dostosuj parametry (dtype, device) według potrzeb
engine = LLM("gpt2", dtype="auto", device="cuda")  # lub "cpu", w zależności od środowiska
print("Model GPT-2 został załadowany.")

def process_prompt(prompt: str):
    """
    Przetwarza prompt przy użyciu modelu GPT-2 i zwraca wynik.
    """
    sampling_params = SamplingParams(n=1, temperature=1.0)
    result = engine.generate(prompt, sampling_params)
    return result
