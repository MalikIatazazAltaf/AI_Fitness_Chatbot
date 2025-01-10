






import uuid
import speech_recognition as sr
import pyttsx3
from services.openai_service import fitness_chatbot
from services.nutritionix_service import get_food_info, format_food_info
from services.mongo_service import save_chat, fetch_chat

# Initialize Text-to-Speech (TTS) engine
tts_engine = pyttsx3.init()

def speech_to_text():
    """
    Converts user speech into text using SpeechRecognition.
    """
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
        try:
            return recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            return "Sorry, I could not understand that."

def text_to_speech(text):
    """
    Converts text into speech using pyttsx3.
    """
    tts_engine.say(text)
    tts_engine.runAndWait()

def assign_user_id():
    return str(uuid.uuid4())

def main():
    print("Fitness Chatbot: Hi! Ask me about workouts, nutrition, or fitness goals. (Say 'quit' to exit)")
    user_id = assign_user_id()

    while True:
        print("\n1. Type your query\n2. Speak your query")
        choice = input("Choose an option (1/2): ")

        if choice == "1":
            user_input = input("You: ")
        elif choice == "2":
            user_input = speech_to_text()
            print(f"You: {user_input}")
        else:
            print("Invalid choice. Try again.")
            continue

        if user_input.lower() == "quit":
            print("Fitness Chatbot: Goodbye! Stay healthy!")
            break

        if "nutrition for" in user_input.lower():
            food_name = user_input.lower().replace("nutrition for", "").strip()
            food_data = get_food_info(food_name)
            response = format_food_info(food_data)
        else:
            response = fitness_chatbot(user_input)

        save_chat({"user_id": user_id, "message": user_input, "sender": "user"})
        save_chat({"user_id": user_id, "message": response, "sender": "bot"})

        print(f"Fitness Chatbot: {response}")
        text_to_speech(response)

if __name__ == "__main__":
    main()
