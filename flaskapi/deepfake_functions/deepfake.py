# Use a pipeline as a high-level helper
from transformers import pipeline
import cv2
import random

# Load the image
from PIL import Image    

def detect_deepfake_video(video_path):
    """SELECT 3 frames from the video and classify them"""
    
    # Open the video file
    cap = cv2.VideoCapture(video_path)
    
    # Get total number of frames
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Select 3 random frames
    frame_indices = sorted(random.sample(range(total_frames), 3))
    
    results = []
    
    pipe = pipeline("image-classification", model="dima806/deepfake_vs_real_image_detection")
    
    for idx in frame_indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if ret:
            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Save the frame temporarily
            temp_frame_path = f"temp_frame_{idx}.jpg"
            cv2.imwrite(temp_frame_path, frame_rgb)
            
            img = Image.open(temp_frame_path).convert("RGB")
            # Classify the frame
            result = pipe(img)
            results.append(result)
    
    cap.release()
    
    # mean real and fake scores
    real_score_mean = 0
    fake_score_mean = 0
    for result in results:
        for res in result:
            if res['label'] == 'Real':
                real_score_mean += res['score']
            elif res['label'] == 'Fake':
                fake_score_mean += res['score']
                
    real_score_mean /= len(results)
    fake_score_mean /= len(results)
    
    if real_score_mean > fake_score_mean:
        return "Real"
    else:
        return "Fake"