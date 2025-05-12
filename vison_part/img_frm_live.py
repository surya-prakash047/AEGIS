import subprocess
import cv2

def get_youtube_stream_url(youtube_url):
    """Use streamlink to get the direct stream URL"""
    try:
        result = subprocess.run(
            ['streamlink', '--stream-url', youtube_url, 'best'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stream_url = result.stdout.strip()
        if stream_url:
            return stream_url
        else:
            print("Failed to get stream URL:", result.stderr)
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

# Replace with your YouTube live URL
youtube_url = "https://www.youtube.com/watch?v=Tow9VJjl2Zw"

stream_url = get_youtube_stream_url(youtube_url)
if stream_url:
    cap = cv2.VideoCapture(stream_url)
    print("🔴 Live stream started. Press 'q' to exit.")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("⚠️ Frame not received.")
            break

        cv2.imshow("YouTube Live", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
else:
    print("❌ Could not load stream URL.")
