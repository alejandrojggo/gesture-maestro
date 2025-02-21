import mediapipe as mp
import cv2, time, threading, queue
from mediapipe.framework.formats import landmark_pb2

# Alias
BaseOptions = mp.tasks.BaseOptions
GestureRecognizer = mp.tasks.vision.GestureRecognizer
GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
GestureRecognizerResult = mp.tasks.vision.GestureRecognizerResult
VisionRunningMode = mp.tasks.vision.RunningMode

# Constants
MODEL_PATH = "model/gesture_recognizer.task"
GESTURE_SCORE_THRESHOLD = 0.6

# Live gesture recognizer class
class LiveRecognizer(threading.Thread):
    def __init__(self, stop_recognizer: threading.Event, frame_queue: queue.Queue, gesture_queue: queue.Queue):
        super().__init__()
        
        # Event that, when set, will be used to stop this thread
        self.stop_recognizer = stop_recognizer

        # Queue where this gesture recognizer's callback method will put each processed frame
        self.frame_queue = frame_queue
        
        # Queue where this gesture recognizer's callback method will put the recognized gestures
        self.gesture_queue = gesture_queue

    # When the thread is started, the gesture recognizer is initialized
    def run(self):
        options = GestureRecognizerOptions(
            base_options = BaseOptions(model_asset_path=MODEL_PATH),
            running_mode = VisionRunningMode.LIVE_STREAM,
            num_hands = 2,
            min_hand_detection_confidence = 0.7,
            min_hand_presence_confidence = 0.7,
            result_callback = self.handle_result)
        with GestureRecognizer.create_from_options(options) as recognizer:
            # Open the default camera
            cam = cv2.VideoCapture(0)
            
            while not self.stop_recognizer.is_set():
                ret, frame = cam.read()
                
                if ret:
                    # Retrieve the frame's timestamp in milliseconds
                    frame_timestamp_ms = int(time.time() * 1000)
                    
                    # Convert the frame received from OpenCV to a MediaPipe’s Image object
                    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)

                    # Send live image data to perform gesture recognition
                    recognizer.recognize_async(mp_image, frame_timestamp_ms)
                else:
                    # Stop the recognizer when the capture device is not working properly
                    self.stop_recognizer.set()

            # Release the capture object
            cam.release()

    # Callback method for the gesture recognizer, handles the result for each frame
    def handle_result(self, result: GestureRecognizerResult, output_image: mp.Image, timestamp_ms: int):
        # Get an unwritable NumPy ndarray from the MediaPipe image received
        image_array = output_image.numpy_view()
        
        # Change the image's color space (BGR, used by MediaPipe) to RGB
        image_array = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)

        hand_landmarks_list = result.hand_landmarks

        # Loop through the detected hands to visualize
        for idx in range(len(hand_landmarks_list)):
            hand_landmarks = hand_landmarks_list[idx]

            # Draw the hand landmarks
            hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
            hand_landmarks_proto.landmark.extend([
            landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in hand_landmarks
            ])
            mp.solutions.drawing_utils.draw_landmarks(
            image_array,
            hand_landmarks_proto,
            mp.solutions.hands.HAND_CONNECTIONS,
            mp.solutions.drawing_styles.get_default_hand_landmarks_style(),
            mp.solutions.drawing_styles.get_default_hand_connections_style())

        # Add the frame to the frame queue
        self.frame_queue.put(image_array)
        
        # Add recognized gestures to the gesture queue
        for i in range(len(result.gestures)):
            gesture = result.gestures[i][0]
            hand = result.handedness[i][0]

            if gesture.category_name != "None" and gesture.score >= GESTURE_SCORE_THRESHOLD:
                gesture_dict = {
                    "name": gesture.category_name,
                    "hand": hand.category_name,
                    "timestamp": timestamp_ms
                }
                
                self.gesture_queue.put(gesture_dict)