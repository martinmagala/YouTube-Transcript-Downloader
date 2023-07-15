from flask import Flask, request, jsonify, render_template
import os
import re
from pytube import Playlist, YouTube
from youtube_transcript_api import YouTubeTranscriptApi

app = Flask(__name__)

# Create a folder to store the transcripts if it does not exist
if not os.path.exists("transcripts"):
    os.mkdir("transcripts")


@app.route('/', methods=['GET'])
def index():
    # Extract YouTube playlist URL from the form data
    playlist_url = request.args.get('playlist_url')

    if playlist_url:
        # Validate the playlist URL
        if not playlist_url.startswith("https://www.youtube.com/playlist?"):
            return jsonify({'error': 'Invalid playlist URL.'})

        # Create Playlist object
        playlist = Playlist(playlist_url)
        playlist._video_regex = re.compile(r"\"url\":\"(/watch\?v=[\w-]*)")

        # Iterate over videos in the playlist
        for video_url in playlist.video_urls:
            video = YouTube(video_url)
            video_id = video.video_id

            # Download transcript
            transcript = get_transcript(video_id)
            if transcript:
                # Save transcript to file
                save_transcript(transcript, video.title)

        return jsonify({'message': 'Transcripts have been successfully downloaded and saved.'})

    # Render the index.html template
    return render_template('index.html')


def get_transcript(video_id):
    """Downloads the transcript for a YouTube video."""

    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = "\n".join([item['text'] for item in transcript_list])
        return transcript
    except Exception as e:
        print(f"Failed to retrieve transcript for video ID: {video_id}")
        print(e)
        return None


def save_transcript(transcript, video_title):
    """Saves the transcript for a YouTube video to a text file."""
    # Replace any invalid characters in the file name with underscores
    video_title = re.sub(r"[/:*?\"<>|]", "_", video_title)
    transcript_file = os.path.join("transcripts", video_title + ".txt")
    with open(transcript_file, "w", encoding="utf-8") as f:
        f.write(transcript)


if __name__ == '__main__':
    app.run(debug=True)
