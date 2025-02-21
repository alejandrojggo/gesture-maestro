import threading, queue, time
from pynput.keyboard import Key, Controller

# Gesture handler class
class GestureHandler(threading.Thread):
    def __init__(self, stop_recognizer: threading.Event, gesture_queue: queue.Queue, executed_action_queue: queue.Queue):
        super().__init__()
        
        # Event that, when set, will be used to stop this thread, as it means that the recognizer is not working anymore
        self.stop_recognizer = stop_recognizer

        # Queue where the gesture recognizer's callback method will put the recognized gestures
        self.gesture_queue = gesture_queue

        # Queue where this gesture handler will put the executed actions
        self.executed_action_queue = executed_action_queue

        # Create a pynput controller for the keyboard
        self.keyboard = Controller()
        
        # Variables used for storing the application configuration; they need to be set using the load_config method before executing the thread
        self.actions = None
        self.combination_mode = None
        self.press_release_wait_time = None
        self.action_cooldown = None

        # Timestamp that marks the end of the last executed action plus the chosen action cooldown (in milliseconds)
        self.resume_timestamp = 0

    # When the thread is started, the gesture handler is initialized
    def run(self):
        while not self.stop_recognizer.is_set():
            try:
                gesture_info = self.gesture_queue.get(False)
                
                if gesture_info["timestamp"] >= self.resume_timestamp:
                    gesture_hand = gesture_info["hand"]
                    gesture_name = gesture_info["name"]
                    
                    action = self.actions[gesture_hand][gesture_name]

                    if action:
                        if self.combination_mode and self.action_is_combination(action):
                            self.execute_combination(action)
                        else:
                            self.execute_action(action)

                        self.executed_action_queue.put(action)
                        
                        self.resume_timestamp = int(time.time() * 1000) + int(self.action_cooldown * 1000)
            except queue.Empty:
                time.sleep(0.1)

    # Returns True if the provided action is a combination (first key is a modifier); otherwise, returns False
    def action_is_combination(self, action):
        action_first_key = action[0]
        modifier_list = ["ctrl", "alt", "shift", "cmd"]

        for modifier in modifier_list:
            if modifier in action_first_key:
                return True
        
        return False
    
    # Executes an action key by key, not as a combination of them
    def execute_action(self, action):
        for key in action:
            try:
                self.keyboard.press(key)
                time.sleep(self.press_release_wait_time)
                self.keyboard.release(key)
            except ValueError:
                try:
                    key = getattr(Key, key)
                    
                    self.keyboard.press(key)
                    time.sleep(self.press_release_wait_time)
                    self.keyboard.release(key)
                except AttributeError:
                    pass
            except Controller.InvalidKeyException:
                pass

    # Executes an action as a combination of keys
    def execute_combination(self, action):
        for key in action:
            try:
                self.keyboard.press(key)
            except ValueError:
                try:
                    key = getattr(Key, key)
                    
                    self.keyboard.press(key)
                except AttributeError:
                    pass
            except Controller.InvalidKeyException:
                pass

        time.sleep(self.press_release_wait_time)

        for key in action:
            try:
                self.keyboard.release(key)
            except ValueError:
                try:
                    key = getattr(Key, key)
                    
                    self.keyboard.release(key)
                except AttributeError:
                    pass
            except Controller.InvalidKeyException:
                pass
    
    # Loads the application configuration from a dictionary into the corresponding variables
    def load_config(self, config):
        self.actions = config["Actions"]
        self.combination_mode = config["Settings"]["COMBINATION_MODE"]
        self.press_release_wait_time = config["Settings"]["PRESS_RELEASE_WAIT_TIME"]
        self.action_cooldown = config["Settings"]["ACTION_COOLDOWN"]