import cv2
import os
import threading
import queue
import time
import speech_recognition as sr
from fuzzywuzzy import fuzz

# ============================================================
# CONFIG
# ============================================================
VIDEO_FOLDER = "videos"
FRAME_DELAY = 30 # ms (≈33ms = 30 FPS)

# ============================================================
# GLOBALS
# ============================================================
video_cache = {} # word -> list of frames
frame_queue = queue.Queue(maxsize=2000)
stop_event = threading.Event()

# ============================================================
# 1️⃣ PRELOAD ALL VIDEOS INTO RAM (ONE TIME)
# ============================================================
def preload_videos():
    print("📦 Preloading videos into RAM...")
    for file in os.listdir(VIDEO_FOLDER):
        if file.endswith(".mp4"):
            word = file.replace(".mp4", "").lower()
            path = os.path.join(VIDEO_FOLDER, file)

            cap = cv2.VideoCapture(path)
            frames = []

            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                frames.append(frame)

            cap.release()
            video_cache[word] = frames
            print(f" ✔ Loaded '{word}' ({len(frames)} frames)")

    print(f"\n✅ {len(video_cache)} videos loaded into memory\n")

# ============================================================
# 2️⃣ BEST WORD MATCH (WORD > FUZZY > ALPHABET)
# ============================================================
def find_best_match(word, dataset_keys):
    word = word.lower().strip()

    # 1️⃣ Exact match
    if word in dataset_keys:
        return word

    # 2️⃣ Fuzzy match
    best_match = None
    best_score = 0

    for key in dataset_keys:
        if len(key) == 1:
            continue
        score = fuzz.ratio(word, key)
        if score > best_score:
            best_score = score
            best_match = key

    if best_score >= 85:
        return best_match

    # 3️⃣ Alphabet fallback
    if len(word) > 0:
        return list(word)

    return None

# ============================================================
# 3️⃣ ENQUEUE FRAMES
# ============================================================
def enqueue_word(word):
    if word not in video_cache:
        return
    for frame in video_cache[word]:
        frame_queue.put(frame)

def enqueue_sentence(sentence):
    words = sentence.lower().split()
    for w in words:
        match = find_best_match(w, video_cache.keys())

        if isinstance(match, str):
            enqueue_word(match)

        elif isinstance(match, list):
            for ch in match:
                if ch in video_cache:
                    enqueue_word(ch)

# ============================================================
# 4️⃣ VIDEO PLAYER THREAD (ZERO GAP PLAYBACK)
# ============================================================
def video_player():
    cv2.namedWindow("Sign Language", cv2.WINDOW_NORMAL)

    while not stop_event.is_set():
        frame = frame_queue.get()

        if frame is None:
            break

        cv2.imshow("Sign Language", frame)

        if cv2.waitKey(FRAME_DELAY) & 0xFF == ord('q'):
            stop_event.set()
            break

    cv2.destroyAllWindows()

# ============================================================
# 5️⃣ SPEECH LISTENER THREAD (IMPROVED VERSION)
# ============================================================
def speech_listener():
    recognizer = sr.Recognizer()
    recognizer.pause_threshold = 0.8
    recognizer.energy_threshold = 300
    recognizer.dynamic_energy_threshold = True

    mic = sr.Microphone()

    with mic as source:
        print("🎙️ Calibrating microphone...")
        recognizer.adjust_for_ambient_noise(source, duration=1.5)
        print("✅ Calibration done")

    print("\n🎤 Listening... Say 'stop' to exit\n")

    while not stop_event.is_set():
        try:
            with mic as source:
                audio = recognizer.listen(
                    source,
                    timeout=5,
                    phrase_time_limit=6
                )

            text = recognizer.recognize_google(audio)
            text = text.lower().strip()

            print(f"🗣️ You said: {text}")

            if text in ["stop", "exit", "quit"]:
                stop_event.set()
                frame_queue.put(None)
                break

            enqueue_sentence(text)

        except sr.WaitTimeoutError:
            continue # silence

        except sr.UnknownValueError:
            print("❌ Speech unclear, try again")
            time.sleep(0.4)

        except sr.RequestError:
            print("⚠️ Network error")
            time.sleep(1)

# ============================================================
# 6️⃣ MAIN
# ============================================================
def main():
    preload_videos()

    player_thread = threading.Thread(target=video_player, daemon=True)
    listener_thread = threading.Thread(target=speech_listener, daemon=True)

    player_thread.start()
    listener_thread.start()

    while not stop_event.is_set():
        time.sleep(0.1)

    print("\n🛑 Program stopped")

if __name__ == "__main__":
    main()