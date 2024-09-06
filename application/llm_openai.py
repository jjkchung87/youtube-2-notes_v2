import os
import openai

# Get API key from environment variable
api_key = os.getenv("OPENAI_API_KEY_YOUTUBE_TO_NOTES")

client = openai.OpenAI(api_key=api_key)

# Define token limit (for context, LLaMA 3.1 has 128K tokens)
TOKEN_LIMIT = 128000

def calculate_token_length(messages):
    """Estimate the token length of the message list."""
    total_length = 0
    for message in messages:
        total_length += len(message['content'].split())  # Token estimation based on word count
    return total_length

def generate_notes(folder_name, video_name, video_id):
    '''Generates notes based on the transcript files provided'''

    # Retrieve transcript files found in the folder named after the video
    transcript_files = [os.path.join(folder_name, file) for file in os.listdir(folder_name) if file.endswith('.txt')]
    transcript_files.sort()

    # Access the example notes file called "example_notes_1.md" and store the content in a variable
    with open('example_good_1.md', 'r', encoding='utf-8') as f:
        example_content = f.read()

    system_prompt = f"""
        You are an assistant that receives the transcript from YouTube videos and creates notes in markdown format based on the transcript. 
        The transcript may come in multiple `.txt` chunks, but treat it as one continuous conversation. Your response each time you are sent a new chunk should only include notes for that particular chunk. Do not include notes from a previous chunk in your response. 
        Follow the format exactly as shown in the {example_content}. Make the notes as detailed and informative as the example, covering the key points discussed in the conversation.
        
        In each transcript chunk, you will see timestamps for different sections of the conversation in seconds. Use these timestamps to create a hyperlink at the top of each corresponding section in the notes. The format of the hyperlink should be:

        `[Section Title](https://www.youtube.com/watch?v={video_id}&t=[seconds])`

        - **Section Title:** The title of the section you are linking to, derived from the content of that part of the transcript.
        - **seconds:** The exact timestamp in seconds, represented as an integer (without a trailing 's').

        Ensure that the URL is correctly formatted with the video ID and timestamp, and that each section's hyperlink is correctly labeled with its corresponding title.
    """

    # Initialize the messages list with the system prompt
    messages = [
        {"role": "system", "content": system_prompt}
    ]

    # Create a list to store the notes
    notes = []

    # Loop through each transcript file and maintain the conversation context
    for file in transcript_files:
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Add the transcript chunk to the conversation
        new_message = {"role": "user", "content": f"Transcript chunk:\n{content}"}
        messages.append(new_message)

        # Calculate token length and prune messages if token limit is exceeded
        token_length = calculate_token_length(messages)
        print("Token length:", token_length)
        while token_length > TOKEN_LIMIT:
            # Keep the system prompt but remove the oldest user-assistant pair
            messages.pop(1)  # Remove the first user or assistant message after the system message
            token_length = calculate_token_length(messages)
            print("Pruned messages due to token limit exceeding.")

        # Generate notes based on the ongoing conversation
        response = client.chat.completions.create(
            model="gpt-4o",  # Specify the model you are using
            messages=messages
        )

        # Extract the generated notes
        note_content = response.choices[0].message.content

        # Ensure the video ID is inserted correctly in the URLs
        note_content = note_content.replace('https://www.youtube.com/watch?v=&t=', f'https://www.youtube.com/watch?v={video_id}&t=')
    
        # Append notes to the list
        notes.append(note_content)

        # Add the assistant's response to the conversation for context
        messages.append({"role": "assistant", "content": note_content})

    # After processing all chunks, finalize the notes
    with open(os.path.join(folder_name, f"{video_name}_notes.md"), 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(notes))

    print(f"Notes have been generated and saved to {video_name}_notes.md")

