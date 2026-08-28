import cv2
from dataset import sign_dataset

def play_video(video_path):
    """Play a video file using OpenCV."""
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("❌ Error: Cannot open video file:", video_path)
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        cv2.imshow("Sign Language Video", frame)

    
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


text_input = input("Enter a sentence: ").lower().strip()

if text_input in sign_dataset:
    video_path = sign_dataset[text_input]
    print(f"🎥 Playing sign language video for: '{text_input}'")
    play_video(video_path)
else:
    print("⚠ No sign video found for this sentence.")