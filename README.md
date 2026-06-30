# Lab 13 — instrukcja krok po kroku (PL)

## Uwaga o zmianie technologii

Zadanie zakłada użycie **vLLM** (serwer do uruchamiania modeli LLM lokalnie). Niestety
**vLLM nie działa natywnie na Windows** — wymaga Linuksa (WSL2 lub Docker). Zgodnie
z instrukcją zadania ("jeśli napotkasz poważne problemy [...] możesz użyć ChatGPT lub
innego modelu w chmurze, ale zaznacz to w raporcie"), zamiast lokalnego vLLM używamy
**Ollama** — to też lokalny serwer LLM (działa natywnie na Windows, na CPU, **za darmo**,
bez konta i bez płacenia), z modelem **Qwen3** (dokładnie tym, którego chce zadanie!)
i z API zgodnym z OpenAI SDK.

To jest uczciwe i tanie podejście, bo:
- kod jest **prawie identyczny** jak w instrukcji — używamy tego samego `OpenAI` SDK,
  zmienia się tylko `base_url` (wskazuje na `localhost:11434` zamiast `localhost:8000`),
- używamy **dokładnie modelu Qwen3**, którego chce zadanie — różni się tylko silnik
  serwujący model (Ollama zamiast vLLM),
- nic nie kosztuje i działa offline,
- **to musi być jasno napisane w raporcie** (zrobimy to razem na końcu) — jako
  uzasadniona zamiana technologii serwującej (Ollama zamiast vLLM) ze względu na brak
  wsparcia vLLM dla Windows.

---

## Krok 0 — Instalacja `uv`

`uv` to narzędzie do zarządzania środowiskiem Python (szybszy odpowiednik `pip`).

1. Otwórz PowerShell.
2. Wklej i uruchom:
   ```powershell
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```
3. Zamknij i otwórz PowerShell ponownie.
4. Sprawdź instalację:
   ```powershell
   uv --version
   ```
   Powinieneś zobaczyć numer wersji (np. `uv 0.5.x`).

**Zrzut ekranu nr 1**: wynik komendy `uv --version`.

---

## Krok 1 — Instalacja zależności projektu

1. Otwórz PowerShell **w folderze projektu** `LAB 13` (ten, w którym jest `pyproject.toml`):
   ```powershell
   cd "C:\Users\annai\Desktop\Pawlos\Travail privé\AI\AGH STUDIA\LAB 13"
   ```
2. Zainstaluj zależności:
   ```powershell
   uv sync
   ```
   To stworzy folder `.venv` i pobierze wszystkie potrzebne biblioteki (chwilę to potrwa,
   `torch` jest duży, ~2GB).

**Zrzut ekranu nr 2**: koniec działania `uv sync` (bez błędów).

---

## Krok 2 — Instalacja Ollama i pobranie modelu Qwen3

Ollama to darmowy program, który uruchamia modele LLM lokalnie na Twoim komputerze
(na CPU, bez GPU) i udostępnia je przez API zgodne z OpenAI SDK — nic nie kosztuje,
nie trzeba zakładać konta ani podawać karty płatniczej.

1. Wejdź na https://ollama.com/download i pobierz instalator dla Windows.
2. Zainstaluj (zwykłe "Next, Next, Finish"). Po instalacji Ollama działa w tle
   (zobaczysz ikonkę w zasobniku systemowym, obok zegara).
3. Otwórz **nowe** okno PowerShell i pobierz model Qwen3 (komenda sama go ściągnie,
   ~1.4 GB):
   ```
   ollama pull qwen3:1.7b
   ```
4. Sprawdź, czy model jest gotowy:
   ```
   ollama list
   ```
   Powinieneś zobaczyć `qwen3:1.7b` na liście.

**Zrzut ekranu nr 3**: wynik komendy `ollama list` z widocznym modelem `qwen3:1.7b`.

Nie potrzebujemy już pliku `.env` ani żadnego klucza API — Ollama działa lokalnie
i nie wymaga autoryzacji.

---

## Krok 4 — Inicjalizacja repo Git

```powershell
git init
git add .
git commit -m "Lab 13: initial setup"
```

**Zrzut ekranu nr 4**: wynik `git log --oneline`.

---

## Dalsze kroki (Exercise 1-5)

Każde ćwiczenie ma swój plik `.py` w tym folderze, z komentarzami "TU URUCHOM" i
instrukcją co zrobić i jaki zrzut ekranu zrobić. Idziemy po kolei:

1. `ex1_quantization.py` — porównanie kwantyzacji (Exercise 1)
2. `ex2_csv_parquet_tools.py` — narzędzia do czytania plików CSV/Parquet (Exercise 2)
3. `ex3_mcp_datetime_server.py` + `ex3_mcp_client.py` — serwer MCP z datą/czasem (Exercise 3)
4. `ex4_mcp_plot_server.py` + `ex4_mcp_plot_client.py` — serwer MCP z wykresami (Exercise 4)
5. `ex5_guardrails_fishing.py` — guardrails (Exercise 5)

Na końcu: `raport/` — folder na zrzuty ekranu i finalny raport.
