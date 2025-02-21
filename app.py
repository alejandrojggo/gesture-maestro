import gui, gesture_recognizer, gesture_handler, threading, queue

def main():
    # Create queue where the gesture recognizer's callback method will put each processed frame to be displayed
    frame_queue = queue.Queue()
    
    # Create queue where the gesture recognizer's callback method will put the recognized gestures
    gesture_queue = queue.Queue()

    # Create queue where the gesture handler will put the executed actions
    executed_action_queue = queue.Queue()

    # Define an Event that will be used to keep the gesture recognizer working while the main thread (interface) is alive and the capture device is functional
    stop_recognizer = threading.Event()
    
    # Create the gesture recognizer thread
    recognizer_thread = gesture_recognizer.LiveRecognizer(stop_recognizer, frame_queue, gesture_queue)
    
    # Create the gesture handler thread
    handler_thread = gesture_handler.GestureHandler(stop_recognizer, gesture_queue, executed_action_queue)

    # Create the Tkinter window
    interface = gui.GUI(stop_recognizer, frame_queue, executed_action_queue, recognizer_thread, handler_thread)

    # Execute the loop that keeps the Tkinter window running in the main thread
    interface.mainloop()
    
    # Set the Event's internal flag to true after the Tkinter window has been closed
    stop_recognizer.set()

if __name__ == "__main__":
    main()