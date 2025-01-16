import streamlit as st
import assemblyai as aai
import requests
# from xyz import ASSEMBLYAI_API_KEY  # Importing API key from xyz module

aai.settings.api_key = ASSEMBLYAI_API_KEY

def upload_to_assemblyai(file):
    """Uploads an MP3 file to AssemblyAI's servers."""
    headers = {'authorization': ASSEMBLYAI_API_KEY}
    response = requests.post(
        'https://api.assemblyai.com/v2/upload',
        headers=headers,
        files={'file': file}
    )
    if response.status_code == 200:
        return response.json()['upload_url']
    else:
        st.error(f"File upload failed: {response.text}")
        return None

st.title("Audio Transcription with Timestamps")
st.subheader("Upload an MP3 file for transcription with speaker timestamps")

# File upload widget
uploaded_file = st.file_uploader("Choose an MP3 file", type=["mp3"])

if uploaded_file:
    st.info("File uploaded successfully. Click 'Transcribe' to start.")

    if st.button("Transcribe"):
        try:
            with st.spinner("Uploading the file to AssemblyAI..."):
                # Upload file to AssemblyAI
                upload_url = upload_to_assemblyai(uploaded_file)
                if not upload_url:
                    st.error("Failed to upload the file. Please try again.")
                else:
                    # Transcription configuration
                    config = aai.TranscriptionConfig(speaker_labels=True)

                    with st.spinner("Transcribing the audio file..."):
                        # Transcribe the uploaded file
                        transcript = aai.Transcriber().transcribe(upload_url, config)

                    st.success("Transcription complete!")
                    st.subheader("Transcription Results with Start-End Timestamps")
                    
                    for utterance in transcript.utterances:  # type: ignore
                        # Convert start and end timestamps (in ms) to minutes:seconds format
                        start_time = int(utterance.start) // 1000  # Convert ms to seconds
                        end_time = int(utterance.end) // 1000  # Convert ms to seconds
                        
                        start_minutes = start_time // 60
                        start_seconds = start_time % 60
                        end_minutes = end_time // 60
                        end_seconds = end_time % 60
                        
                        formatted_start = f"{start_minutes:02}:{start_seconds:02}"
                        formatted_end = f"{end_minutes:02}:{end_seconds:02}"
                        
                        st.write(
                            f"**[{formatted_start}-{formatted_end}] Speaker {utterance.speaker}:** {utterance.text}"
                        )
        except Exception as e:
            st.error(f"An error occurred: {e}")
