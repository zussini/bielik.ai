from vllm import LLM, SamplingParams

engine = LLM("gpt2", dtype="auto")
prompt = "Hello world"
sampling_params = SamplingParams(n=1, temperature=1.0)
result = engine.generate(prompt, sampling_params)
print(result)

