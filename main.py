import streamlit as st
import requests
import time


ASSEMBLYAI_API_KEY= st.secrets['ASSEMBLYAI_API_KEY']
# Set API Key for AssemblyAI
headers = {'authorization': ASSEMBLYAI_API_KEY}

class AudioProcessor:
    def __init__(self):
        self.headers = headers
    
    def upload_to_assemblyai(self, file):
        """Upload audio file to AssemblyAI"""
        upload_url = 'https://api.assemblyai.com/v2/upload'
        try:
            response = requests.post(upload_url, headers=self.headers, files={'file': file})
            response.raise_for_status()
            return response.json()['upload_url']
        except Exception as e:
            st.error(f"File upload failed: {str(e)}")
            return None

    def request_transcription(self, audio_url):
        """Request transcription with speaker labels"""
        transcript_endpoint = 'https://api.assemblyai.com/v2/transcript'
        json_data = {
            'audio_url': audio_url,
            'speaker_labels': True,
            'language_code': 'en_us'
        }
        
        try:
            response = requests.post(transcript_endpoint, headers=self.headers, json=json_data)
            response.raise_for_status()
            return response.json()['id']
        except Exception as e:
            st.error(f"Transcription request failed: {str(e)}")
            return None

    def poll_transcription(self, transcript_id):
        """Poll for transcription completion"""
        status_endpoint = f"https://api.assemblyai.com/v2/transcript/{transcript_id}"
        
        while True:
            try:
                response = requests.get(status_endpoint, headers=self.headers)
                response.raise_for_status()
                result = response.json()
                
                if result['status'] == 'completed':
                    return result
                elif result['status'] == 'error':
                    st.error(f"Transcription failed: {result.get('error', 'Unknown error')}")
                    return None
                
                time.sleep(5)
            except Exception as e:
                st.error(f"Error polling transcription: {str(e)}")
                return None

def main():
    st.set_page_config(page_title="Speaker Separation & Transcription", layout="wide")
    
    st.title("Speaker Separation & Audio Transcription")
    st.subheader("Upload an audio file for speaker diarization and transcription")
    
    # Initialize processor
    processor = AudioProcessor()
    
    # File uploader
    uploaded_file = st.file_uploader("Choose an audio file", type=["mp3", "wav", "m4a"])
    
    if uploaded_file:
        st.info("File uploaded successfully. Click 'Process Audio' to start.")
        
        if st.button("Process Audio"):
            # Process the audio file
            with st.spinner("Uploading audio file..."):
                audio_url = processor.upload_to_assemblyai(uploaded_file)
            
            if audio_url:
                with st.spinner("Starting transcription..."):
                    transcript_id = processor.request_transcription(audio_url)
                
                if transcript_id:
                    with st.spinner("Processing... (this may take a few minutes)"):
                        result = processor.poll_transcription(transcript_id)
                    
                    if result:
                        st.success("Processing completed!")
                        
                        # Create tabs for different views
                        tab1, tab2 = st.tabs(["Transcript", "Statistics"])
                        
                        with tab1:
                            st.subheader("Speaker Separated Transcription")
                            for utterance in result.get('utterances', []):
                                start_time = int(utterance['start']) // 1000
                                end_time = int(utterance['end']) // 1000

                                minutes_end = end_time // 60
                                seconds_end = end_time % 60
                                minutes_start = start_time // 60
                                seconds_start = start_time % 60
                                formatted_time_start = f"{minutes_start:02}:{seconds_start:02}"
                                formatted_time_end = f"{minutes_end:02}:{seconds_end:02}"

                                
                                st.write(
                                    f"[{formatted_time_start}-{formatted_time_end}] Speaker {utterance['speaker']}: {utterance['text']}"
                                )
                        
                        with tab2:
                            st.subheader("Speaker Statistics")
                            speakers = {}
                            for utterance in result.get('utterances', []):
                                speaker = utterance['speaker']
                                if speaker not in speakers:
                                    speakers[speaker] = {
                                        'word_count': 0,
                                        'duration': 0
                                    }
                                speakers[speaker]['word_count'] += len(utterance['text'].split())
                                speakers[speaker]['duration'] += (utterance['end'] - utterance['start']) / 1000
                            
                            for speaker, stats in speakers.items():
                                st.write(f"Speaker {speaker}:")
                                st.write(f"- Words spoken: {stats['word_count']}")
                                st.write(f"- Speaking time: {stats['duration']:.2f} seconds")

if __name__ == "__main__":
    main()