import os
import subprocess
import tempfile

import sounddevice as sd
import soundfile as sf
from faster_whisper import WhisperModel


class LenoVoice:
    def __init__(self):
        print("🎤 Loading local Whisper model...")

        self.whisper = WhisperModel(
            "small.en",
            device="cpu",
            compute_type="int8"
        )

        self.sample_rate = 16000
        self.channels = 1

    def listen(self):
        print("\n🎤 LENO is listening... Speak now.")

        duration = 8

        try:
            audio = sd.rec(
                int(duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype="float32"
            )

            sd.wait()

            with tempfile.NamedTemporaryFile(
                suffix=".wav",
                delete=False
            ) as temp:
                audio_file = temp.name

            sf.write(
                audio_file,
                audio,
                self.sample_rate
            )

            segments, _ = self.whisper.transcribe(
                audio_file,
                language="en",
                beam_size=5,
                temperature=0,
                vad_filter=True,
                condition_on_previous_text=False
            )

            text = " ".join(
                segment.text.strip()
                for segment in segments
                if segment.text.strip()
            ).strip()

            os.remove(audio_file)

            if text:
                print(f"👤 You: {text}")
                return text

            print("❓ I couldn't hear a clear command.")
            return None

        except Exception as error:
            print(f"❌ Speech recognition error: {error}")
            return None

    def speak(self, text):
        print(f"\n🤖 LENO: {text}")

        try:
            # Escape text safely for PowerShell
            safe_text = text.replace("'", "''")

            command = (
                "Add-Type -AssemblyName System.Speech; "
                "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
                f"$s.Speak('{safe_text}'); "
                "$s.Dispose()"
            )

            subprocess.run(
                [
                    "powershell.exe",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-Command",
                    command
                ],
                check=True
            )

        except Exception as error:
            print(f"❌ Voice output error: {error}")