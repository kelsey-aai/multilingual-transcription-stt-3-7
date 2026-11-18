# Multilingual transcription with AssemblyAI-STT-3.7

Companion code for the AssemblyAI blog post
[Multilingual transcription: how to detect, diarize, and transcribe audio across languages](https://www.assemblyai.com/blog/multilingual-transcription).

| Script | Model | What it does |
|---|---|---|
| `transcribe_multilingual.py` | `assemblyai-stt-3-7` (+ `universal-2`) | Recorded audio: language detection, native code switching, speaker labels. `--languages` constrains the set with `language_codes`. |
| `stream_multilingual.py` | `assemblyai-stt-3-7-realtime` | Live audio: prints each final turn with its detected language. `--steer` updates `language_codes` mid-stream. |

## Run it

Requires Python 3.9+.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export ASSEMBLYAI_API_KEY=your_api_key_here
python transcribe_multilingual.py https://assembly.ai/code-switching-3
python stream_multilingual.py call.wav --steer en es
```

Convert audio for streaming with:

```bash
ffmpeg -i input.mp3 -ac 1 -ar 16000 -sample_fmt s16 call.wav
```

## Fallback behavior on AssemblyAI-STT-3.7

- `language_detection: true` with only `assemblyai-stt-3-7` in `speech_models`: no fallback.
  Add `universal-2` to the list to cover all 99 languages.
- `language_code` set to a language AssemblyAI-STT-3.7 doesn't support: the request falls back to Universal-2.
- `assemblyai-stt-3-7` takes priority wherever it appears in `speech_models`.
- `disfluencies` defaults to `true` whenever `assemblyai-stt-3-7` is in the list. Set it to `false` for clean transcripts.

See the [migration guide](https://www.assemblyai.com/docs/pre-recorded-audio/assemblyai-stt-3-7-migration-guide).

## SDK note

The streaming docs show `client.update_configuration(...)`. In the Python SDK 1.10.1 the method is
`client.set_params(RealTimeSessionParameters(...))`, which this script uses. Pass an empty list to
clear steering and return to full code switching.
