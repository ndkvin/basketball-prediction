import cv2
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.utils import custom_object_scope
import tensorflow_hub as hub

class BasketballActionClassifier:
    model = None 
    class_names = ['layup', 'freethrow', 'jumpshoot']
    frame_size = (224, 224)
    max_frames = 10
    

    def __init__(self):
        if BasketballActionClassifier.model is None:
            with custom_object_scope({'KerasLayer': hub.KerasLayer}):
                BasketballActionClassifier.model = load_model('./model/basket.h5')

    def extract_frame(self, video_path):
        frame_list = []
        video = cv2.VideoCapture(video_path)
        frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        for count in range(self.max_frames):
            video.set(cv2.CAP_PROP_POS_FRAMES, count * max(int(frame_count / self.max_frames), 1))
            flag, frame = video.read()
            if not flag:
                break
            frame = cv2.resize(frame, self.frame_size)
            frame_list.append(frame/255.0)
        video.release()
        return np.array(frame_list)

    def predict(self, video_path):
        # Ekstrak frame dari video
        frames = self.extract_frame(video_path)

        # Ubah dimensi menjadi (1, max_frames, 224, 224, 3)
        frames_batch = np.expand_dims(frames, axis=0)
        
        # Prediksi
        predictions = BasketballActionClassifier.model.predict(frames_batch)
       
        predicted_index = np.argmax(predictions, axis=-1)

        confidence = predictions[0][predicted_index][0]
        
        # Use the index to get the class name
        class_name = self.class_names[int(predicted_index)]
        
        return class_name, float(confidence)