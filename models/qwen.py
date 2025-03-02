from transformers import Qwen2_5_VLForConditionalGeneration, AutoTokenizer, AutoProcessor
from qwen_vl_utils import process_vision_info
import torch

# Wyczyść cache GPU
torch.cuda.empty_cache()

print("Ładowanie modelu (Qwen2.5-VL-3B-Instruct)...")
model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
    "Qwen/Qwen2.5-VL-3B-Instruct",
    torch_dtype="auto",
    device_map="auto"
)
print("Model Qwen został załadowany.")

# Ustawienia procesora – zmniejszamy zakres wizualnych tokenów, by zmniejszyć zużycie pamięci
min_pixels = 256 * 14 * 14
max_pixels = 1280 * 14 * 14
processor = AutoProcessor.from_pretrained("Qwen/Qwen2.5-VL-3B-Instruct", min_pixels=min_pixels, max_pixels=max_pixels)

def process_prompt(prompt: str):
    """
    Przetwarza prompt przy użyciu modelu Qwen.
    Zwraca wynik inferencji.
    """
    # Przygotuj wiadomość w formacie wymaganym przez model – tutaj tylko tekstowy prompt.
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt}
            ]
        }
    ]
    # Używamy procesora do przygotowania danych wejściowych
    text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    image_inputs, video_inputs = process_vision_info(messages)
    inputs = processor(
        text=[text],
        images=image_inputs,
        videos=video_inputs,
        padding=True,
        return_tensors="pt"
    )
    # Przenieś dane wejściowe na GPU
    inputs = inputs.to("cuda" if torch.cuda.is_available() else "cpu")
    
    # Generacja wyników – ograniczamy do 128 tokenów
    generated_ids = model.generate(**inputs, max_new_tokens=128)
    generated_ids_trimmed = [
        out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
    ]
    output_text = processor.batch_decode(
        generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
    )
    return output_text
