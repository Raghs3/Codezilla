import librosa
import soundfile as sf

# Load audio file
audio_path = "path/to/your/audio.mp3"
y, sr = librosa.load(audio_path, sr=16000)  # Resample to 16kHz

# Save the resampled audio as a WAV file
output_path = "output.wav"
sf.write(output_path, y, sr)
print(f"Resampled audio saved to {output_path}")
