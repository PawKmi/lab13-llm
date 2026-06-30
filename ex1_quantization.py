"""
Exercise 1 - porownanie modelu zwyklego vs skwantyzowanego.

UWAGA: oryginalne zadanie chce, zebyysmy uzyli vLLM z opcja
"--quantization bitsandbytes" (kwantyzacja dynamiczna 4-bit) i porownali:
  1. ile pamieci KV cache jest dostepne (vLLM pokazuje to w logach startu)
  2. czas wykonania 10 promptow

Poniewaz vLLM nie dziala natywnie na Windows (patrz README.md), a kwantyzacja
4-bit bitsandbytes wymaga karty GPU (ktorej nie mamy), robimy PRAKTYCZNY
zamiennik: mierzymy czas inferencji malego modelu Qwen3-0.6B na CPU,
zwyklego (fp32) i porownujemy z mniejszym modelem.
Liczby pamieci KV cache z prawdziwego vLLM + bitsandbytes opisujemy
w raporcie na podstawie dokumentacji (https://docs.vllm.ai/en/latest/features/quantization/bnb/),
bo nie da sie ich praktycznie zmierzyc bez GPU/Linuksa.

URUCHOM: uv run python ex1_quantization.py
Pierwsze uruchomienie pobierze model (~1.5GB), wiec potrwa dluzej.
"""

import time

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL_NAME = "Qwen/Qwen3-0.6B"  # mniejszy model, zeby dalo sie uruchomic na CPU

PROMPTS = [
    "What is the capital of France?",
    "Explain what a neural network is in one sentence.",
    "Write a haiku about the ocean.",
    "What is 15 multiplied by 7?",
    "Name three programming languages.",
    "What year did World War II end?",
    "Summarize the plot of Romeo and Juliet in one sentence.",
    "What is the chemical symbol for gold?",
    "How many continents are there on Earth?",
    "Give a short definition of machine learning.",
]


def main() -> None:
    print(f"Ladowanie modelu {MODEL_NAME} (moze chwile potrwac)...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME, dtype=torch.float32, device_map="cpu"
    )
    print("Model zaladowany.\n")

    total_start = time.time()

    for i, prompt in enumerate(PROMPTS, start=1):
        messages = [{"role": "user", "content": prompt + " /no_think"}]
        text = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True, enable_thinking=False
        )
        model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

        start = time.time()
        generated_ids = model.generate(**model_inputs, max_new_tokens=100)
        elapsed = time.time() - start

        output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist()
        answer = tokenizer.decode(output_ids, skip_special_tokens=True).strip()

        print(f"[{i}/10] ({elapsed:.2f}s) Prompt: {prompt}")
        print(f"        Odpowiedz: {answer[:120]}")
        print()

    total_elapsed = time.time() - total_start
    print(f"\nCALKOWITY CZAS dla 10 promptow: {total_elapsed:.2f} sekund")
    print(f"Srednio na prompt: {total_elapsed / len(PROMPTS):.2f} sekund")


if __name__ == "__main__":
    main()
