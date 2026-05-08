"""
Jarvis Phase 1 — Text-based AI assistant for an Obsidian vault.

Local Ollama version. Runs entirely on your machine — no API keys, no internet
needed (after model download), no per-query costs. Uses qwen2.5:14b by default
for excellent multilingual (incl. Swedish) quality on RTX-class GPUs.

Usage:
    python jarvis.py

Requires:
    pip install ollama
    Ollama service running locally (https://ollama.com)
    Model pulled: ollama pull qwen2.5:14b
"""
from __future__ import annotations

import sys
import datetime
from pathlib import Path

try:
    import ollama
except ImportError:
    print("Error: ollama SDK not installed. Run: pip install ollama")
    sys.exit(1)


# ─────────────────────────────────────────────────────────────────────
# CONFIG — customize these
# ─────────────────────────────────────────────────────────────────────

VAULT_ROOT = Path(r"C:\Users\jakob\claude-obsidian")
SCAN_DIRS = ["wiki", "projects"]
MAX_VAULT_TOKENS = 8000  # rough budget for vault context per query
MODEL = "qwen2.5:14b"    # local Ollama model. Other options:
                          #   qwen2.5:7b      faster, slightly lower quality
                          #   llama3.1:8b     good general model
                          #   gemma2:27b      excellent multilingual, larger
                          #   llama3.3:70b    smartest, slow on consumer GPUs
OLLAMA_HOST = "http://localhost:11434"  # default Ollama port
LOG_DIR = VAULT_ROOT / "wiki" / "jarvis-log"

SYSTEM_PROMPT = """Du är Jarvis, en personlig AI-assistent för Jakob.

Du har tillgång till hans Obsidian-vault som innehåller:
- Wiki om Claude+Obsidian-ekosystemet, DragonScale Memory, LLM-mönster
- Projekt-anteckningar om hans UV-printverkstad (Bergstein Digi 7)
- Substrat-databas (dopplackad metall, anodiserad aluminium, glas, etc.)
- Brainstorming-projekt om 3D-print + hållbarhet
- Lärande-projekt om ESP32 och elektronik

Du svarar på svenska som standard. Du är konkret och rakt på sak — inga onödiga
artighets-fraser, inga "som AI-assistent..."-disclaimers. Om du inte vet något
säger du det rakt ut.

Du citerar källan när du hämtar information från vaulten, t.ex.
"enligt [[dopplackad-metall]]: primer 30%". Wiki-länkar i Obsidian-format.

Om frågan inte täcks av vault-innehållet svarar du baserat på allmän kunskap men
flaggar det: "(inte från din vault, allmän kunskap)"."""


# ─────────────────────────────────────────────────────────────────────
# Vault indexing
# ─────────────────────────────────────────────────────────────────────

def index_vault() -> list[dict]:
    """Walk SCAN_DIRS, return [{path, snippet, full_path, size}, ...]."""
    notes = []
    for sub in SCAN_DIRS:
        base = VAULT_ROOT / sub
        if not base.is_dir():
            continue
        for md_file in base.rglob("*.md"):
            try:
                content = md_file.read_text(encoding="utf-8")
            except Exception:
                continue
            rel_path = md_file.relative_to(VAULT_ROOT).as_posix()
            snippet = content[:500].replace("\n", " ")
            notes.append({
                "path": rel_path,
                "snippet": snippet,
                "full_path": md_file,
                "size": len(content),
            })
    return notes


def select_relevant(notes: list[dict], query: str, budget: int = MAX_VAULT_TOKENS) -> list[dict]:
    """Pick notes whose path or snippet best matches the query.

    Crude keyword scoring. Phase 2 could replace with embeddings.
    """
    query_terms = [t.lower() for t in query.split() if len(t) > 2]
    scored = []
    for n in notes:
        haystack = (n["path"] + " " + n["snippet"]).lower()
        score = sum(haystack.count(t) for t in query_terms)
        if score > 0:
            scored.append((score, n))
    scored.sort(key=lambda x: -x[0])

    picked = []
    used = 0
    for _, n in scored:
        size = n["size"] // 4  # rough char-to-token estimate
        if used + size > budget:
            continue
        try:
            full = n["full_path"].read_text(encoding="utf-8")
            picked.append({"path": n["path"], "content": full})
            used += size
        except Exception:
            continue
        if len(picked) >= 8:
            break
    return picked


def format_context(picked: list[dict]) -> str:
    if not picked:
        return "(Inga relevanta vault-noter hittades för den här frågan.)"
    parts = ["Relevanta vault-noter:\n"]
    for note in picked:
        parts.append(f"\n=== {note['path']} ===\n{note['content']}\n")
    return "\n".join(parts)


# ─────────────────────────────────────────────────────────────────────
# Conversation logging
# ─────────────────────────────────────────────────────────────────────

def log_turn(question: str, answer: str) -> None:
    today = datetime.date.today().isoformat()
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOG_DIR / f"jarvis-{today}.md"

    if not log_file.exists():
        header = (
            "---\n"
            "type: meta\n"
            f"title: \"Jarvis-konversation {today}\"\n"
            f"created: {today}\n"
            f"model: {MODEL}\n"
            "tags:\n  - jarvis\n  - conversation-log\n---\n\n"
            f"# Jarvis-konversation {today}\n\n"
        )
        log_file.write_text(header, encoding="utf-8")

    timestamp = datetime.datetime.now().strftime("%H:%M")
    entry = (
        f"---\n\n"
        f"## {timestamp}\n\n"
        f"**Q:** {question}\n\n"
        f"**A:** {answer}\n\n"
    )
    with log_file.open("a", encoding="utf-8") as f:
        f.write(entry)


# ─────────────────────────────────────────────────────────────────────
# Main loop
# ─────────────────────────────────────────────────────────────────────

def check_ollama_running() -> bool:
    """Verify Ollama service is reachable and the model is pulled."""
    try:
        client = ollama.Client(host=OLLAMA_HOST)
        models_response = client.list()
        # The response shape varies by SDK version; handle both
        if hasattr(models_response, "models"):
            available = [m.model for m in models_response.models]
        else:
            available = [m.get("name", m.get("model", "")) for m in models_response.get("models", [])]
        if MODEL not in available and not any(MODEL in a for a in available):
            print(f"⚠️  Modell '{MODEL}' inte hittad lokalt.")
            print(f"   Kör: ollama pull {MODEL}")
            print(f"   Tillgängliga modeller: {available}")
            return False
        return True
    except Exception as e:
        print(f"⚠️  Kan inte ansluta till Ollama på {OLLAMA_HOST}")
        print(f"   Är Ollama-servicen igång? (Den startas oftast automatiskt vid installation.)")
        print(f"   Om inte: starta 'Ollama' från Start-menyn.")
        print(f"   Detalj: {e}")
        return False


def main() -> None:
    print(f"🤖 Jarvis vaknar... Modell: {MODEL} (lokal via Ollama)")
    print(f"   Läser vault: {VAULT_ROOT}")

    if not check_ollama_running():
        sys.exit(1)

    notes = index_vault()
    print(f"📚 Indexerade {len(notes)} filer.")
    print("Hej. Vad vill du veta? (skriv 'exit' för att avsluta)\n")

    client = ollama.Client(host=OLLAMA_HOST)
    history: list[dict] = []

    while True:
        try:
            question = input(">>> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n🤖 Hej då.")
            break

        if not question:
            continue
        if question.lower() in {"exit", "quit", "hej då", "bye"}:
            print("🤖 Hej då.")
            break

        # Pick relevant vault notes for this question
        picked = select_relevant(notes, question)
        context = format_context(picked)

        # Build the user message: vault context + the question
        user_message = f"{context}\n\n---\n\nFråga: {question}"

        # Build messages array: system + history + new user turn
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend(history)
        messages.append({"role": "user", "content": user_message})

        try:
            response = client.chat(
                model=MODEL,
                messages=messages,
                options={
                    "temperature": 0.6,
                    "num_predict": 2048,
                },
            )
        except Exception as e:
            print(f"⚠️  Ollama-fel: {e}\n")
            continue

        answer = response["message"]["content"]
        print(f"\n{answer}\n")

        # Keep only the bare question in history (drop the bulky context)
        history.append({"role": "user", "content": question})
        history.append({"role": "assistant", "content": answer})

        # Trim if it grows too long
        if len(history) > 20:
            history = history[-20:]

        log_turn(question, answer)


if __name__ == "__main__":
    main()
