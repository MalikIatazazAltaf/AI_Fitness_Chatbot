import gradio as gr
from services.openai_service import fitness_chatbot
from services.mongo_service import save_chat, fetch_chat
import uuid
import re
import speech_recognition as sr
import pyttsx3
from pydub import AudioSegment
import os

# Initialize Text-to-Speech (TTS) engine
tts_engine = pyttsx3.init()

# Dictionary to store user sessions
user_sessions = {}

def assign_user_id():
    return str(uuid.uuid4())  # Generate a unique UUID for each session

def speech_to_text(audio_file):
    """
    Converts audio input into text using SpeechRecognition.
    """
    recognizer = sr.Recognizer()
    try:
        # Convert audio to PCM WAV format
        audio = AudioSegment.from_file(audio_file)
        wav_file = "temp.wav"
        audio.export(wav_file, format="wav")
        
        # Process the converted WAV file
        with sr.AudioFile(wav_file) as source:
            audio_data = recognizer.record(source)
            return recognizer.recognize_google(audio_data)
    except Exception as e:
        return f"Error: {e}"
    finally:
        # Clean up temporary file
        if os.path.exists("temp.wav"):
            os.remove("temp.wav")

def text_to_speech(text):
    """
    Converts text into speech using pyttsx3.
    """
    output_audio_path = "output.mp3"
    tts_engine.save_to_file(text, output_audio_path)
    tts_engine.runAndWait()
    return output_audio_path

def update_chat_history(user_id, user_input):
    """
    Update and retrieve the chat history for the current user.
    """
    # Fetch existing chat history for the user
    history = fetch_chat(user_id)

    # Generate context from previous chat
    context = "\n".join(
        [f"User: {msg['message']}" if msg["sender"] == "user" else f"Bot: {msg['message']}" for msg in history]
    )
    full_input = f"{context}\nUser: {user_input}"

    # Get response from chatbot
    response = fitness_chatbot(full_input)

    # Add URL styling for chatbot response
    url_pattern = r"(https?://\S+)"
    response = re.sub(
        url_pattern,
        r"<a href='\1' target='_blank' style='color:#008080;'>\1</a>",
        response,
    )

    # Log messages to MongoDB
    save_chat({"user_id": user_id, "message": user_input, "sender": "user"})
    save_chat({"user_id": user_id, "message": response, "sender": "bot"})

    # Convert response to speech
    speech_audio_path = text_to_speech(response)

    # Update chat history for display
    chat_history = history + [
        {"message": user_input, "sender": "user"},
        {"message": response, "sender": "bot"},
    ]
    return "".join(
        f'<div class="user-msg"><span>{msg["message"]}</span></div>' if msg["sender"] == "user" else
        f'<div class="bot-msg"><span>{msg["message"]}</span></div>'
        for msg in chat_history
    ), "", speech_audio_path  # Clear input field and return audio path

def gr_interface():
    """
    Create the Gradio interface with enhanced design and functionality.
    """
    with gr.Blocks(css="""
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');
        
        body {
            font-family: 'Roboto', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }

        .container {
            background-color: rgba(255, 255, 255, 0.9);
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            overflow: hidden;
            width: 90%;
            max-width: 800px;
            margin: 20px;
        }

        .header {
            background-color: #4a5568;
            color: white;
            text-align: center;
            padding: 20px;
            font-size: 24px;
            font-weight: bold;
        }

        .chat-container {
            height: 60vh;
            overflow-y: auto;
            padding: 20px;
            background-image: url('https://images.unsplash.com/photo-1517836357463-d25dfeac3438?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80');
            background-size: cover;
            background-position: center;
        }

        .user-msg, .bot-msg {
            max-width: 80%;
            margin: 10px 0;
            padding: 10px 15px;
            border-radius: 20px;
            line-height: 1.4;
            position: relative;
        }

        .user-msg {
            background-color: #4299e1;
            color: white;
            margin-left: auto;
            border-bottom-right-radius: 0;
        }

        .bot-msg {
            background-color: #e2e8f0;
            color: #2d3748;
            margin-right: auto;
            border-bottom-left-radius: 0;
        }

        .user-msg::after, .bot-msg::after {
            content: '';
            position: absolute;
            bottom: 0;
            width: 0;
            height: 0;
            border: 10px solid transparent;
        }

        .user-msg::after {
            right: -10px;
            border-left-color: #4299e1;
            border-bottom: 0;
        }

        .bot-msg::after {
            left: -10px;
            border-right-color: #e2e8f0;
            border-bottom: 0;
        }

        .input-container {
            display: flex;
            padding: 20px;
            background-color: #edf2f7;
        }

        .input-container > * {
            margin: 0 5px;
        }

        #component-0 {
            flex-grow: 1;
        }

        #component-2 {
            width: auto !important;
        }

        .footer {
            text-align: center;
            padding: 10px;
            background-color: #4a5568;
            color: white;
            font-size: 14px;
        }
    """) as interface:
        user_id = assign_user_id()

        gr.Markdown("<div class='header'>Get Fit With AI</div>")

        chat_history = gr.Markdown(elem_id="chat-container", value="<div class='chat-container'></div>")
        audio_output = gr.Audio(label="AI Response", visible=False)

        with gr.Row(elem_id="input-container"):
            chat_input = gr.Textbox(
                placeholder="Type your message here...",
                lines=1,
                label="Chat Input"
            )
            send_btn = gr.Button("Send", variant="primary")
            speech_input = gr.Audio(type="filepath", label="Voice Input")

        gr.Markdown("<div class='footer'>Your fitness journey starts today!</div>")

        send_btn.click(
            update_chat_history,
            inputs=[gr.State(user_id), chat_input],
            outputs=[chat_history, chat_input, audio_output]
        )
        chat_input.submit(
            update_chat_history,
            inputs=[gr.State(user_id), chat_input],
            outputs=[chat_history, chat_input, audio_output]
        )
        speech_input.change(
            lambda audio: update_chat_history(user_id, speech_to_text(audio)),
            inputs=[speech_input],
            outputs=[chat_history, chat_input, audio_output]
        )

    return interface

if __name__ == "__main__":
    gr_interface().launch()