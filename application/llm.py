import os
import requests
import json

# Function to generate notes using Ollama API with context
def generate_notes_with_ollama(input_text, system_message, context=None):
    url = "http://localhost:11434/api/generate"  # Ollama API endpoint
    headers = {"Content-Type": "application/json"}
    data = {
        "model": "llama3.1",  # Ensure this is the correct model name
        "prompt": input_text,
        "options": {
            "num_ctx": 100000
        },
        "system": system_message,
        "context": context,  # Include the context from previous responses
        "stream": False
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    print("Raw Response:")
    print(response.text)  # Print the raw response text for debugging
    
    if response.status_code == 200:
        try:
            response_json = response.json()
            return response_json["response"], response_json.get("context", None)
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            return None, None
    else:
        print(f"Error: {response.status_code}")
        return None, None

def clean_generated_notes(note_content):
    """Remove lines that do not match expected markdown format"""
    cleaned_content = []
    for line in note_content.splitlines():
        if line.startswith("#") or line.startswith("- ") or line.startswith("[") or line.strip() == "":
            cleaned_content.append(line)
    return "\n".join(cleaned_content)

def generate_notes(folder_name, video_name, video_id):
    '''Generates notes based on the transcript files provided'''

    # Retrieve transcript files from the specified folder
    transcript_files = [os.path.join(folder_name, file) for file in os.listdir(folder_name) if file.endswith('.txt')]
    transcript_files.sort()

    # Access the example notes file and store the content
    with open('example_good_1.md', 'r', encoding='utf-8') as f:
        example_good_1 = f.read()

    # Access the example #2 notes file and store the content
    with open('example_good_2.md', 'r', encoding='utf-8') as f:
        example_good_2 = f.read()

    # Access notes file that is an example not to follow and store the content:
    with open('example_bad.md', 'r', encoding='utf-8') as f:
        example_bad = f.read()

    system_prompt = f"""
        <prompt>
            <instruction>
                You are an assistant that receives the transcript from YouTube videos and creates notes in markdown format based on the transcript. Your task is to:
                - Organize the notes in a structured manner with clear headings and subheadings using markdown syntax.
                - Include detailed and informative notes covering the key points discussed in the conversation.
                - Do not make the notes overly concise or incomplete.

                **Good Examples:**
                Example 1:
                {example_good_1}

                Example 2:
                {example_good_2}

                **Bad Example (Avoid this format):**
                {example_bad}
                
                Ensure the format of the notes strictly follows the style of the good examples, and avoid the structure of the bad example.
            </instruction>
        </prompt>
    """
      
    
    # List to store the generated notes
    notes = []
    context = None  # Initialize the context

    for file in transcript_files:
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Combine the system prompt, example content, and current transcript chunk
        input_text = f"""
            <transcript_chunk>
            {content}
            </transcript_chunk>
        """

        # Generate notes using the Ollama API. note_content
        note_content, context = generate_notes_with_ollama(input_text, system_message=system_prompt, context=context)

        print("note_content:", note_content)

        if note_content:
            note_content = note_content.replace('https://www.youtube.com/watch?v=&t=', f'https://www.youtube.com/watch?v={video_id}&t=')
            notes.append(note_content)

    # Save the finalized notes to a markdown file
    with open(os.path.join(folder_name, f"{video_name}_notes.md"), 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(notes))

    print(f"Notes have been generated and saved to {video_name}_notes.md")

