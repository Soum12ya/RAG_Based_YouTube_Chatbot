from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled

def get_transcript(video_url: str) -> str:
    try:
        # Extract video ID
        video_id = video_url.split("v=")[-1].split("&")[0] if "v=" in video_url else video_url.split("/")[-1]

        # Instantiate the API class and fetch transcript
        api = YouTubeTranscriptApi()
        transcript_list = api.fetch(video_id=video_id, languages=['en'])

        # Use .text to access the actual text from each FetchedTranscriptSnippet
        transcript = " ".join(chunk.text for chunk in transcript_list)

        return transcript

    except TranscriptsDisabled:
        raise ValueError("Transcripts are disabled for this video.")
    except Exception as e:
        raise RuntimeError(f"Transcript loading error: {e}")