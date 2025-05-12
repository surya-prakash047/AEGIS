import subprocess
import cv2
import os
import time

from vison_part.vison2txt import vision2txt

from db import PushToMongo
class VisionLive:
    def __init__(self):
        self.vision = vision2txt()
        self.video_path = os.path.join(os.getcwd(), "videos\\bbc.mp4")
        self.frame_interval_seconds = 10
        self.db = PushToMongo(db="Aegis",col="raw_data")




    def run_extractor(self):
        stream_path = self.video_path
        if stream_path:
            cap = cv2.VideoCapture(stream_path)
            print(" Live stream started. Press 'q' to exit.")
            # Get frames per second (FPS)
            fps = cap.get(cv2.CAP_PROP_FPS)
            if fps == 0 or fps is None:
                fps = 25  # default fallback
                frame_interval = int(fps * 10)  # capture every 10 seconds

            frame_count = 0
            # Set the time interval for saving frames
            last_saved_time = time.time()


            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    print("⚠️ Frame not received.")
                    break

                current_time = time.time()
                if current_time - last_saved_time >= self.frame_interval_seconds:

                    # Crop using fixed coordinates from the HTML map
                    crop = frame[62:663, 0:1279]
                    print("Extracting text from frame...")
                    text = self.vision.extract(crop)
                    print("Extracted Text:", text)

                    # Save the extracted text to MongoDB
                    json_data = {
                        "raw_data":text
                    }
                    self.db.push_json(json_data=json_data)
                    last_saved_time = current_time

                    frame_count += 1

                cv2.imshow("YouTube Live", frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            cap.release()
            cv2.destroyAllWindows()
        else:
            print("❌ Could not load stream URL.")


if __name__ == "__main__":

    vision = VisionLive()
    vision.run_extractor()