from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound, VideoUnavailable

video_name = 'matplotlib'
video_id='3Xc3CA655Y4'

try:
    # Fetch the transcript
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    
    # Open a file to write the transcript to
    with open(f"{video_name}.txt", "w", encoding="utf-8") as f:
        for entry in transcript:
            start_time = entry['start']
            duration = entry['duration']
            text = entry['text']
            f.write(f"{start_time} - {start_time + duration}: {text}\n")
    
    print(f"Transcript has been saved to {video_name}.txt")

except TranscriptsDisabled:
    print("Transcripts are disabled for this video.")
except NoTranscriptFound:
    print("No transcript found for this video.")
except VideoUnavailable:
    print("The video is unavailable.")
except Exception as e:
    print(f"An error occurred: {str(e)}")


def split_transcript(file_path, max_size=5000, output_prefix="transcript_part"):
    """
    Splits a large transcript file into smaller files.

    :param file_path: Path to the input transcript file.
    :param max_size: Maximum size (in characters) for each output file.
    :param output_prefix: Prefix for the output files.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Calculate the number of parts needed
    total_length = len(content)
    num_parts = total_length // max_size + 1

    for i in range(num_parts):
        start_index = i * max_size
        end_index = min((i + 1) * max_size, total_length)
        part_content = content[start_index:end_index]

        # Write each part to a separate file
        output_file = f"{output_prefix}{i + 1}.txt"
        with open(output_file, 'w', encoding='utf-8') as output:
            output.write(part_content)

        print(f"Created {output_file} with size {len(part_content)} characters.")

# Example usage
split_transcript(f"{video_name}.txt", max_size=10000)