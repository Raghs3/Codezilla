import os
from pyannote.audio import Pipeline
from pyannote.audio.pipelines.utils import get_devices

# Check available devices
print(get_devices())

# Load the pre-trained speaker diarization pipeline
pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization", use_auth_token="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")

# Define input audio file
audio_file = "path/to/your/audio/file.wav"  # Ensure it's 16kHz WAV format

# Perform speaker diarization
print("Processing audio file...")
diarization = pipeline(audio_file)

# Output diarization result
output_file = "diarization_output.txt"
with open(output_file, "w") as f:
    for segment, _, speaker in diarization.itertracks(yield_label=True):
        f.write(f"{segment.start:.3f} {segment.end:.3f} {speaker}\n")
        print(f"[{segment.start:.3f}s - {segment.end:.3f}s] {speaker}")

print(f"Diarization results saved to {output_file}")
