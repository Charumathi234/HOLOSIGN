import speech_recognition as sr

# Initialize recognizer
recognizer = sr.Recognizer()

# Use microphone as source
with sr.Microphone() as source:
    print("🎤 Say something... (press Ctrl+C to stop)")
    # Adjust for ambient noise for better accuracy
    recognizer.adjust_for_ambient_noise(source)
    # Listen to user input
    audio = recognizer.listen(source)

try:
    # Convert speech to text using Google Web Speech API
    text = recognizer.recognize_google(audio)
    print("🗣 You said:", text)
except sr.UnknownValueError:
    print("❌ Sorry, I couldn't understand your speech.")
except sr.RequestError:
    print("⚠ Could not request results — check your internet connection.")