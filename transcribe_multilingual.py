"""Transcribe mixed-language audio with AssemblyAI-STT-3.7, falling back to Universal-2.

Usage:
    export ASSEMBLYAI_API_KEY=your_api_key_here
    python transcribe_multilingual.py https://assembly.ai/code-switching-3
    python transcribe_multilingual.py meeting.mp3 --languages es fr
"""
import argparse
import os
import sys

from assemblyai.prerecorded.v2 import Transcriber, TranscriptionConfig


def build_config(languages=None):
    if languages:
        # Constrain to a known set. Can't be combined with language_code or language_detection.
        return TranscriptionConfig(
            speech_models=["assemblyai-stt-3-7"],
            language_codes=languages,
            speaker_labels=True,
        )
    # AssemblyAI-STT-3.7 handles its 32 languages; Universal-2 covers the rest of the 99.
    return TranscriptionConfig(
        speech_models=["assemblyai-stt-3-7", "universal-2"],
        language_detection=True,
        speaker_labels=True,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("audio", help="Local path or public URL")
    parser.add_argument("--languages", nargs="+", help="Language codes, e.g. es fr")
    args = parser.parse_args()

    api_key = os.environ.get("ASSEMBLYAI_API_KEY")
    if not api_key:
        sys.exit("Set ASSEMBLYAI_API_KEY first.")

    transcript = Transcriber(api_key=api_key, config=build_config(args.languages)).transcribe(args.audio)

    if transcript.status == "error":
        sys.exit(f"Transcription failed: {transcript.error}")

    print(f"Model used: {transcript.speech_model_used}")
    print(f"Language: {transcript.json_response.get('language_code')}")
    for utterance in transcript.utterances:
        print(f"Speaker {utterance.speaker}: {utterance.text}")


if __name__ == "__main__":
    main()
