"""
Exercise 1 - porownanie modelu zwyklego vs skwantyzowanego.

UWAGA: oryginalne zadanie chce, zebysmy uzyli vLLM z opcja
"--quantization bitsandbytes" (kwantyzacja dynamiczna 4-bit) i porownali:
  1. ile pamieci KV cache jest dostepne (vLLM pokazuje to w logach startu)
  2. czas wykonania 10 promptow

Poniewaz vLLM nie dziala natywnie na Windows, a 4-bit bitsandbytes wymaga GPU
(ktorej nie mamy), robimy PRAKTYCZNY ODPOWIEDNIK z uzyciem Ollamy:
Ollama udostepnia ten sam model Qwen3-1.7B w dwoch wersjach:
  - "qwen3:1.7b"      - domyslna, juz skwantyzowana (Q4_K_M, ok. 4-bit)
  - "qwen3:1.7b-fp16" - pelna precyzja (fp16, nieskwantyzowana)
Porownujemy ich rozmiar na dysku (odpowiednik "pamieci modelu") oraz czas
generowania odpowiedzi na 10 promptow (odpowiednik "inference time" z zadania).
Liczby dotyczace KV cache z prawdziwego vLLM + bitsandbytes opisujemy w
raporcie na podstawie dokumentacji (https://docs.vllm.ai/en/latest/features/quantization/bnb/),
bo nie da sie ich praktycznie zmierzyc bez GPU/Linuksa + vLLM.

PRZED URUCHOMIENIEM pobierz wersje pelnej precyzji (w terminalu):
    ollama pull qwen3:1.7b-fp16

URUCHOM: uv run python ex1_quantization.py
"""

import time

from openai import OpenAI

CLIENT = OpenAI(api_key="ollama", base_url="http://localhost:11434/v1")

MODELS = {
    "skwantyzowany (qwen3:1.7b, domyslny Q4_K_M)": "qwen3:1.7b",
    "pelna precyzja (qwen3:1.7b-fp16)": "qwen3:1.7b-fp16",
}

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


def benchmark_model(model_name: str) -> float:
    total_start = time.time()

    for i, prompt in enumerate(PROMPTS, start=1):
        start = time.time()
        response = CLIENT.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            max_completion_tokens=150,
            extra_body={"chat_template_kwargs": {"enable_thinking": False}},
        )
        elapsed = time.time() - start
        answer = response.choices[0].message.content.strip()
        print(f"  [{i}/10] ({elapsed:.2f}s) {prompt}")
        print(f"          -> {answer[:100]}")

    return time.time() - total_start


def main() -> None:
    results = {}
    for label, model_name in MODELS.items():
        print(f"\n=== Testuje model: {label} ({model_name}) ===")
        total_time = benchmark_model(model_name)
        results[label] = total_time
        print(f"CALKOWITY CZAS dla 10 promptow: {total_time:.2f}s "
              f"(srednio {total_time / len(PROMPTS):.2f}s/prompt)")

    print("\n=== PODSUMOWANIE ===")
    for label, total_time in results.items():
        print(f"{label}: {total_time:.2f}s")
    print(
        "\nRozmiar na dysku sprawdz komenda: ollama list "
        "(kolumna SIZE dla qwen3:1.7b vs qwen3:1.7b-fp16)"
    )


if __name__ == "__main__":
    main()
