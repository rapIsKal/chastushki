# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A Telegram bot (aiogram 3, long polling) that turns a user's message into a "частушка": the text is read aloud by a Russian Piper TTS voice, then the accordion tune `otbivka.mp3` is appended, and the result is sent back as an mp3. User-facing strings are in Russian.

## Commands

All commands run from the repo root using the local `venv`.

```bash
venv/bin/python main.py          # run the bot (needs BOT_TOKEN in .env)
venv/bin/python test_audio.py    # full pipeline without Telegram: test.txt -> test_tts.wav + test_final.mp3
bash lint.sh                     # flake8 . --exclude=venv (the only CI check, .github/workflows/lint.yml)
```

Check stress handling without generating audio (`ˈ` precedes the stressed vowel):

```bash
venv/bin/python -c "from main import text_to_phonemes; print(text_to_phonemes(\"за'мок замо'к\"))"
```

There is no test suite; `test_audio.py` and `piper_exper.py` are manual scripts. Importing `main` does not need `BOT_TOKEN` (the `Bot` is only created under `__main__`), but it does load the Piper voice model.

Docker: `docker build -t chastushki .` then `docker run --rm --env-file .env chastushki`. Don't run a second copy with the same token while the local bot is polling (`TelegramConflictError`).

## Architecture (all in `main.py`)

Message flow: `handle_text` → `text_to_speech` → `mix_audio` → `answer_audio`.

**Stress marks.** Users mark stress with `'` after the vowel (`бере'за`). Piper can't take stress hints in text: `<stress>` tags get read aloud as English words, and the U+0301 combining accent is silently ignored by its espeak-ng phonemizer. So stress is applied at the phoneme level:

1. `parse_stress` strips the `'` marks and records `{word index: vowel index within word}`.
2. `text_to_phonemes` calls `voice.phonemize()` on the clean text (returns a list of sentences, each a list of single phoneme chars, words separated by `" "`), then aligns written words with phoneme words **by position**.
3. `restress_word` removes the existing `ˈ`/`ˌ`, inserts `ˈ` before the chosen vowel phoneme, and replaces a reduced vowel (`REDUCED_PHONEMES`) with the full one for that letter (`STRESSED_PHONEME`).
4. `text_to_speech` bypasses `synthesize_wav` and feeds the phonemes through `phonemes_to_ids` → `phoneme_ids_to_audio`, doing the same peak normalization Piper does internally.

If word counts don't line up (e.g. espeak expands `125` into several words) or a word's vowel-phoneme count doesn't match its vowel letters, stress is skipped with a printed warning rather than applied to the wrong syllable. Keep that fallback when changing the alignment logic.

`mix_audio` concatenates voice then melody (`voice + melody`); it does not overlay them despite its docstring.

## Gotchas

- `handle_text` writes its `tts.wav` / `final.mp3` into a per-request `tempfile.TemporaryDirectory`. TTS and mixing are synchronous, so they block the event loop while they run.
- espeak-ng (bundled in `piper-tts`) fails with `.../piper//phontab: No such file or directory` when the venv path is too long (~170+ chars to `piper/espeak-ng-data`). This is a path-length limit, not a broken install or a version problem.
- pydub needs `ffmpeg` on PATH; `main.py` appends `/opt/homebrew/bin` for macOS.
- Voice models live in `piper_models/` (`irina` is used by the bot, `ruslan` only in `piper_exper.py`).
- Generated audio and `test*.txt` are gitignored; `otbivka.mp3` is tracked and must stay that way (`!otbivka.mp3` in `.gitignore` and `.dockerignore`).
