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
        f'<div class="user-msg">{msg["message"]}</div>' if msg["sender"] == "user" else
        f'<div class="bot-msg">{msg["message"]}</div>'
        for msg in chat_history
    ), ""  # Clear input field

def gr_interface():
    """
    Create the Gradio interface with enhanced design and functionality.
    """
    with gr.Blocks(css=""" 
        html, body {
            font-family: 'Arial', sans-serif;
            background-color: #f0f8ff;
            margin: 0;
            padding: 0;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }

        .gradio-container {
            background-color: #2A0944 !important;
            color: #000000 !important;
        }

        .header {
            text-align: center;
            background-color: #ffffff;
            color: #2A0944;
            padding: 15px 0;
            font-size: 30px;
            font-weight: bold;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2);
        }

        .chat-container {
            flex-grow: 1;
            max-width: 1300px;
            margin: 20px auto;
            padding: 15px;
            background-color: #fff5f8;
            border-radius: 15px;
            overflow-y: auto;
            height: calc(100vh - 350px);
            display: flex;
            flex-direction: column-reverse;
            background-image: url('https://motopress.com/wp-content/uploads/2024/05/17-base-fit_gym-website-design.jpg');
            background-size: cover;
            background-position: center;
        }

        .user-msg {
            color: #2A0944;
            font-size: 18px;
            text-align: right;
            background-color: #E6E6FA;
            padding: 10px;
            border-radius: 10px;
            margin: 5px 0;
        }

        .bot-msg {
            color: #000000;
            font-size: 18px;
            text-align: left;
            background-color: #F0F8FF;
            padding: 10px;
            border-radius: 10px;
            margin: 5px 0;
        }

        .footer {
            text-align: center;
            background-color: #ffffff;
            color: #000000;
            padding: 10px 0;
            font-size: 18px;
            font-weight: bold;
        }

        .input-container {
            position: sticky;
            bottom: 0;
            background-color: #F5F5F5;
            padding: 15px;
            display: flex;
            justify-content: space-between;
            gap: 10px;
        }

        textarea {
            font-size: 16px !important;
            font-weight: bold !important;
            padding: 10px;
        }
    """) as interface:
        user_id = assign_user_id()

        # Header
        gr.Markdown("<div class='header'>Get Fit With AI</div>")

        # Chat container
        chat_history = gr.Markdown(
            elem_id="chat-container",
            value="<div class='chat-container'></div>"
        )

        # Input container
        with gr.Row(elem_id="input-container"):
            chat_input = gr.Textbox(
                placeholder="Type your message here...",
                lines=1,
                interactive=True,
                show_label=False,
            )
            chat_input.submit(
                update_chat_history,
                inputs=[gr.State(user_id), chat_input],
                outputs=[chat_history, chat_input],
            )

            speech_input = gr.Audio(type="filepath", label="Speech Input")
            speech_input.change(
                lambda audio: update_chat_history(user_id, speech_to_text(audio)),
                inputs=speech_input,
                outputs=[chat_history, chat_input],
            )

        # Footer
        gr.Markdown(
            "<div class='footer'>\"Your fitness journey starts today!\"</div>"
        )

    return interface

if __name__ == "__main__":
    gr_interface().launch()
