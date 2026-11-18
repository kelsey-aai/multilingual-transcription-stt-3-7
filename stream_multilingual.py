"""Stream a 16 kHz mono PCM WAV file to AssemblyAI-STT-3.7-Realtime and print each
final turn with the language it was spoken in.

Usage:
    export ASSEMBLYAI_API_KEY=your_api_key_here
    python stream_multilingual.py call.wav
    python stream_multilingual.py call.wav --steer en es
"""
import argparse
import os
import sys
import time
import wave

from assemblyai.streaming.v3 import (
    RealTimeEvents,
    RealTimeParameters,
    RealTimeSessionParameters,
    RealTimeTranscriber,
    RealTimeTranscriberOptions,
    TurnEvent,
)


def on_turn(client: RealTimeTranscriber, event: TurnEvent):
    if event.end_of_turn:
        print(f"[{event.language_code}] {event.transcript}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("wav", help="16 kHz, 16-bit mono PCM WAV file")
    parser.add_argument("--steer", nargs="+", help="Steer mid-stream toward these languages")
    args = parser.parse_args()

    api_key = os.environ.get("ASSEMBLYAI_API_KEY")
    if not api_key:
        sys.exit("Set ASSEMBLYAI_API_KEY first.")

    client = RealTimeTranscriber(RealTimeTranscriberOptions(), api_key=api_key)
    client.on(RealTimeEvents.Turn, on_turn)
    client.connect(
        RealTimeParameters(
            sample_rate=16000,
            speech_model="assemblyai-stt-3-7-realtime",
            language_detection=True,  # adds language_code and language_confidence to each turn
        )
    )

    try:
        with wave.open(args.wav, "rb") as wav:
            frames_per_chunk = wav.getframerate() // 10  # 100 ms
            sent = 0
            while chunk := wav.readframes(frames_per_chunk):
                client.stream(chunk)
                time.sleep(0.1)  # send at live speed
                sent += 1
                if args.steer and sent == 50:  # after 5 seconds, steer toward known languages
                    client.set_params(RealTimeSessionParameters(language_codes=args.steer))
    finally:
        client.disconnect(terminate=True)


if __name__ == "__main__":
    main()
