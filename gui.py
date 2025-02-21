import tkinter as tk
import time, threading, queue, gesture_recognizer, gesture_handler, config_file
from tkinter import ttk, messagebox
from PIL import Image, ImageDraw, ImageFont, ImageTk
from pynput.keyboard import Key, Listener

# Constants
ICON_PATH = "assets/icon.ico"
FONT_PATH = "assets/Roboto-Medium.ttf"

# Custom exception class for handling unexpected negative values
class NegativeValueError(Exception):
    pass

# Graphical User Interface class
class GUI(tk.Tk):
    def __init__(self, stop_recognizer: threading.Event, frame_queue: queue.Queue, executed_action_queue: queue.Queue, recognizer_thread: gesture_recognizer.LiveRecognizer,
                 handler_thread: gesture_handler.GestureHandler):
        super().__init__()

        # Event that, when set before tkinter's thread end, means that the capture device is not working properly
        self.stop_recognizer = stop_recognizer
        
        # Queue where the frames processed by the gesture recognizer will be put
        self.frame_queue = frame_queue

        # Queue where the actions executed by the gesture handler will be put
        self.executed_action_queue = executed_action_queue

        # Gesture recognizer and handler threads that will be started when the launch button is pressed
        self.recognizer_thread = recognizer_thread
        self.handler_thread = handler_thread

        # Tkinter frames that will be used for changing the interface
        self.main_frame = tk.Frame(self)
        self.loading_frame = tk.Frame(self)

        # Label widget for displaying images
        self.display_label = tk.Label(self)
        
        # String that will store the last executed action
        self.last_action = ""
        
        self.setup_main_window()

    # Sets up the application's main window
    def setup_main_window(self):
        self.title("Gesture Maestro")
        self.resizable(False, False)

        win_width = 400
        win_height = 150
        self.geometry(f"{win_width}x{win_height}")
        
        self.center_window(self, win_width, win_height)
        
        self.setup_main_frame()

        self.iconbitmap(ICON_PATH)

    # Sets up the application's main Tkinter frame and packs it inside the main window
    def setup_main_frame(self):
        self.main_frame.pack(expand=True)
        
        # Create the start and settings buttons, and place them side by side inside the main frame using the grid layout
        start_btn = tk.Button(self.main_frame, text="Launch model", command=self.launch_model)
        start_btn.grid(row=0, column=0, padx=5)
        
        settings_btn = tk.Button(self.main_frame, text="Gesture settings", command=self.setup_settings_window)
        settings_btn.grid(row=0, column=1, padx=5)

    # Sets up the application's loading Tkinter frame and packs it inside the main window after removing the main frame
    def setup_loading_frame(self):
        self.main_frame.pack_forget()
        self.loading_frame.pack(expand=True)
        
        # Create the progress bar and loading label, and pack them inside the loading frame
        progress = ttk.Progressbar(self.loading_frame, orient="horizontal", length=300, mode="indeterminate")
        progress.pack(pady=10)
        progress.start(20)

        label = tk.Label(self.loading_frame, text="Loading model...")
        label.pack()

    # Sets up the application's settings window
    def setup_settings_window(self):
        settings_window = tk.Toplevel(self)

        settings_window.title("Settings")
        settings_window.resizable(False, False)

        win_width = 265
        win_height = 360
        settings_window.geometry(f"{win_width}x{win_height}")
        
        self.center_window(settings_window, win_width, win_height)

        # Create relationship between settings window and main window, making the first one behave like a pop-up (stay on top, don't appear in the taskbar...)
        settings_window.transient(self)
        
        # Block interaction with the main window while the settings window is opened
        settings_window.grab_set()

        # Give focus to settings window
        settings_window.focus_set()

        self.setup_settings_content(settings_window)
        
        settings_window.iconbitmap(ICON_PATH)

    # Sets up the content inside the settings Tkinter window
    def setup_settings_content(self, settings_window):
        # ACTIONS
        actions_frame = tk.Frame(settings_window)
        actions_frame.pack(expand=True)
        
        # Closed fist gesture
        fist_label = tk.Label(actions_frame, text="Closed fist ✊")
        fist_label.grid(row=0, column=0, padx=5, pady=2.5)
        
        fist_left_btn = tk.Button(actions_frame, text="Left hand", command=lambda:self.setup_edit_action_window(settings_window, "Left", "Closed_Fist"))
        fist_left_btn.grid(row=0, column=1, padx=5, pady=2.5)

        fist_right_btn = tk.Button(actions_frame, text="Right hand", command=lambda:self.setup_edit_action_window(settings_window, "Right", "Closed_Fist"))
        fist_right_btn.grid(row=0, column=2, padx=5, pady=2.5)

        # Open palm gesture
        palm_label = tk.Label(actions_frame, text="Open palm 👋")
        palm_label.grid(row=1, column=0, padx=5, pady=2.5)
        
        palm_left_btn = tk.Button(actions_frame, text="Left hand", command=lambda:self.setup_edit_action_window(settings_window, "Left", "Open_Palm"))
        palm_left_btn.grid(row=1, column=1, padx=5, pady=2.5)

        palm_right_btn = tk.Button(actions_frame, text="Right hand", command=lambda:self.setup_edit_action_window(settings_window, "Right", "Open_Palm"))
        palm_right_btn.grid(row=1, column=2, padx=5, pady=2.5)

        # Pointing up gesture
        pointing_label = tk.Label(actions_frame, text="Pointing up ☝️")
        pointing_label.grid(row=2, column=0, padx=5, pady=2.5)
        
        pointing_left_btn = tk.Button(actions_frame, text="Left hand", command=lambda:self.setup_edit_action_window(settings_window, "Left", "Pointing_Up"))
        pointing_left_btn.grid(row=2, column=1, padx=5, pady=2.5)

        pointing_right_btn = tk.Button(actions_frame, text="Right hand", command=lambda:self.setup_edit_action_window(settings_window, "Right", "Pointing_Up"))
        pointing_right_btn.grid(row=2, column=2, padx=5, pady=2.5)
        
        # Thumbs down gesture
        tdown_label = tk.Label(actions_frame, text="Thumbs down 👎")
        tdown_label.grid(row=3, column=0, padx=5, pady=2.5)
        
        tdown_left_btn = tk.Button(actions_frame, text="Left hand", command=lambda:self.setup_edit_action_window(settings_window, "Left", "Thumb_Down"))
        tdown_left_btn.grid(row=3, column=1, padx=5, pady=2.5)

        tdown_right_btn = tk.Button(actions_frame, text="Right hand", command=lambda:self.setup_edit_action_window(settings_window, "Right", "Thumb_Down"))
        tdown_right_btn.grid(row=3, column=2, padx=5, pady=2.5)

        # Thumbs up gesture
        tup_label = tk.Label(actions_frame, text="Thumbs up 👍")
        tup_label.grid(row=4, column=0, padx=5, pady=2.5)
        
        tup_left_btn = tk.Button(actions_frame, text="Left hand", command=lambda:self.setup_edit_action_window(settings_window, "Left", "Thumb_Up"))
        tup_left_btn.grid(row=4, column=1, padx=5, pady=2.5)

        tup_right_btn = tk.Button(actions_frame, text="Right hand", command=lambda:self.setup_edit_action_window(settings_window, "Right", "Thumb_Up"))
        tup_right_btn.grid(row=4, column=2, padx=5, pady=2.5)

        # Victory gesture
        victory_label = tk.Label(actions_frame, text="Victory ✌️")
        victory_label.grid(row=5, column=0, padx=5, pady=2.5)
        
        victory_left_btn = tk.Button(actions_frame, text="Left hand", command=lambda:self.setup_edit_action_window(settings_window, "Left", "Victory"))
        victory_left_btn.grid(row=5, column=1, padx=5, pady=2.5)

        victory_right_btn = tk.Button(actions_frame, text="Right hand", command=lambda:self.setup_edit_action_window(settings_window, "Right", "Victory"))
        victory_right_btn.grid(row=5, column=2, padx=5, pady=2.5)

        # Love gesture
        love_label = tk.Label(actions_frame, text="Love 🤟")
        love_label.grid(row=6, column=0, padx=5, pady=2.5)
        
        love_left_btn = tk.Button(actions_frame, text="Left hand", command=lambda:self.setup_edit_action_window(settings_window, "Left", "ILoveYou"))
        love_left_btn.grid(row=6, column=1, padx=5, pady=2.5)

        love_right_btn = tk.Button(actions_frame, text="Right hand", command=lambda:self.setup_edit_action_window(settings_window, "Right", "ILoveYou"))
        love_right_btn.grid(row=6, column=2, padx=5, pady=2.5)

        # OTHER SETTINGS
        other_settings_frame = tk.Frame(settings_window)
        other_settings_frame.pack(expand=True)
        
        # Press and release wait time
        pr_wait_label = tk.Label(other_settings_frame, text="Seconds between press and release")
        pr_wait_label.grid(row=0, column=0, padx=5, pady=2.5)

        pr_wait_entry = tk.Entry(other_settings_frame, width=4)
        pr_wait_entry.grid(row=0, column=1, padx=5, pady=2.5)

        # Action cooldown
        action_cooldown_label = tk.Label(other_settings_frame, text="Seconds between each action")
        action_cooldown_label.grid(row=1, column=0, padx=5, pady=2.5)

        action_cooldown_entry = tk.Entry(other_settings_frame, width=4)
        action_cooldown_entry.grid(row=1, column=1, padx=5, pady=2.5)
        
        # Key combination mode
        key_combination_label = tk.Label(other_settings_frame, text="Enable key combinations")
        key_combination_label.grid(row=2, column=0, padx=5, pady=2)

        checkbox_var = tk.BooleanVar()
        key_combination_checkbox = tk.Checkbutton(other_settings_frame, variable=checkbox_var)
        key_combination_checkbox.grid(row=2, column=1, padx=5, pady=2)

        # SAVE BUTTON
        save_btn = tk.Button(settings_window, text="Save", command=lambda:self.save_settings_to_file(pr_wait_entry, action_cooldown_entry, checkbox_var, settings_window))
        save_btn.pack(expand=True, pady=(0, 2.5))

        self.display_settings(pr_wait_entry, action_cooldown_entry, key_combination_checkbox)

    # Displays the settings not related to actions in the corresponding widgets of the settings frame
    def display_settings(self, pr_wait_entry, action_cooldown_entry, key_combination_checkbox):
        current_settings = config_file.retrieve_settings()

        # Change the widgets' input to the saved settings
        pr_wait_entry.insert(0, str(current_settings["PRESS_RELEASE_WAIT_TIME"]))
        action_cooldown_entry.insert(0, str(current_settings["ACTION_COOLDOWN"]))

        if current_settings["COMBINATION_MODE"]:
            key_combination_checkbox.select()

    # Saves the settings to the configuration file (showing an error window if it could not be done) and closes the settings window
    def save_settings_to_file(self, pr_wait_entry, action_cooldown_entry, checkbox_var, settings_window):
        try:
            if checkbox_var.get():
                combination_mode = True
            else:
                combination_mode = False
            
            pr_wait = float(pr_wait_entry.get())
            action_cooldown = float(action_cooldown_entry.get())

            if pr_wait < 0 or action_cooldown < 0:
                raise NegativeValueError
            
            settings = {
                "COMBINATION_MODE": combination_mode,
                "PRESS_RELEASE_WAIT_TIME": pr_wait,
                "ACTION_COOLDOWN": action_cooldown
            }

            if config_file.save_settings(settings):
                settings_window.destroy()
            else:
                messagebox.showerror("Error", "An error occurred while saving the settings to the configuration file.")
        except ValueError:
            messagebox.showerror("Error", "At least one of the values entered is not a valid number.")
        except NegativeValueError:
            messagebox.showerror("Error", "Time values cannot be negative.")

    # Sets up the application's edit gesture action window
    def setup_edit_action_window(self, parent, hand, gesture):
        edit_action_window = tk.Toplevel(parent)

        edit_action_window.title("Edit gesture action")
        edit_action_window.resizable(False, False)

        win_width = 430
        win_height = 130
        edit_action_window.geometry(f"{win_width}x{win_height}")
        
        self.center_window(edit_action_window, win_width, win_height)

        # Create relationship between edit action window and settings window
        edit_action_window.transient(parent)
        
        # Block interaction with the parent window while the edit action window is opened
        edit_action_window.grab_set()

        # Give focus to edit action window
        edit_action_window.focus_set()

        self.setup_edit_action_frame(edit_action_window, hand, gesture)

        edit_action_window.iconbitmap(ICON_PATH)

    # Sets up the application's edit gesture action Tkinter frame and packs it inside the edit action window
    def setup_edit_action_frame(self, edit_action_window, hand, gesture):
        edit_action_frame = tk.Frame(edit_action_window)
        edit_action_frame.pack(expand=True)

        current_action = config_file.retrieve_action(hand, gesture)

        if current_action:
            hint = "Your currently saved action for this hand gesture is:\n"+str(current_action)+"\n\n"
        else:
            hint = "You have not set an action for this hand gesture yet.\n\n"
        
        hint_label = tk.Label(edit_action_frame, text=hint+"To edit this action, click the following button and press up to three keys.\nYou can press Esc to stop the capture before reaching the limit.")
        hint_label.pack()

        edit_button = tk.Button(edit_action_frame, text="Edit action", command=lambda:self.setup_action_capture(hand, gesture, edit_action_window, hint_label, edit_button))
        edit_button.pack(pady=5)

    # Starts a thread that executes the capture_action method and changes the edit action window button to indicate the user that the key capture has started
    def setup_action_capture(self, hand, gesture, edit_action_window, hint_label, edit_button):
        capture_thread = threading.Thread(target=self.capture_action, args=(hand, gesture, edit_action_window, hint_label, edit_button))
        capture_thread.start()
        
        edit_button.config(text="Capturing...", state="disabled")
    
    # Starts a pynput keyboard listener that runs until 3 keys have been pressed, Esc has been pressed or the edit action window is closed, storing the name of
    # the pressed keys (the action) in a list
    def capture_action(self, hand, gesture, edit_action_window, hint_label, edit_button):
        captured_keys = []

        # Method executed by the listener when a key is pressed
        def on_press(key):
            if key != None and key != Key.esc:
                try:
                    pressed_key = key.char
                except AttributeError:
                    pressed_key = key.name
                
                captured_keys.append(pressed_key)
                
                if len(captured_keys) == 3:
                    return False

        # Method executed by the listener when a key is released
        def on_release(key):
            if key == Key.esc:
                return False
            
        listener = Listener(on_press=on_press, on_release=on_release)
        listener.start()

        while listener.is_alive() and edit_action_window.winfo_exists():
            time.sleep(0.1)

        if not edit_action_window.winfo_exists():
            listener.stop()
        else:
            self.after(0, self.update_after_action_capture, hand, gesture, captured_keys, edit_action_window, hint_label, edit_button)

    # Updates the edit action window widgets to notify the user that the key capture has finished, and changes the button command for the save_action method
    def update_after_action_capture(self, hand, gesture, action, edit_action_window, hint_label, edit_button):
        if not action:
            hint_label.config(text="You have not pressed any key.\n\nWould you like to leave this hand gesture without action?")
        else:
            hint_label.config(text="You have pressed the following keys:\n"+str(action)+"\n\nWould you like to save them as the new action?")
            
        edit_button.config(text="Confirm", state="active", command=lambda:self.save_action_to_file(hand, gesture, action, edit_action_window))

    # Saves the captured action to the configuration file (showing an error window if it could not be done) and closes the edit action window
    def save_action_to_file(self, hand, gesture, action, edit_action_window):
        if not config_file.save_action(hand, gesture, action):
            messagebox.showerror("Error", "An error occurred while saving the action to the configuration file.")

        edit_action_window.destroy()

    # Launches the model, as well as the gesture functions of the application
    def launch_model(self):
        self.setup_loading_frame()
        
        def configuration_file_error():
            messagebox.showerror("Error", "Configuration file could not be accessed. Check your permissions.")
            self.destroy()
        
        # Create the application's configuration JSON file if necessary
        if not config_file.check() and not config_file.create():
            configuration_file_error()
        else:
            config = config_file.retrieve_configuration()

            if config:
                # Load the current application configuration into the gesture handler
                self.handler_thread.load_config(config)
                
                # Start the gesture recognizer and handler threads
                self.recognizer_thread.start()
                self.handler_thread.start()
                
                # Execute update_image in the Tkinter thread after 10ms
                self.after(10, self.update_image)
            else:
                configuration_file_error()

    # Centers a window on the screen
    def center_window(self, window, win_width, win_height):
        # Get screen's width and height
        scr_width = self.winfo_screenwidth()
        scr_height = self.winfo_screenheight()
        
        # Calculate x and y position to center the window
        x_pos = (scr_width - win_width) // 2
        y_pos = (scr_height - win_height) // 2

        window.geometry(f"+{x_pos}+{y_pos}")

    # Updates the image currently on display by changing it for the next processed frame in the queue
    def update_image(self):
        if self.stop_recognizer.is_set():
            messagebox.showerror("Error", "Gesture recognizer error: Ensure your capture device is connected and functioning correctly.")
            self.destroy()
        
        try:
            image_array = self.frame_queue.get(False)
            
            # Convert the NumPy array to a Pillow image
            image_pil = Image.fromarray(image_array)

            # Draw the last executed action on the image
            draw = ImageDraw.Draw(image_pil)
            draw.text((20, 20), self.last_action, font=ImageFont.truetype(FONT_PATH, 18), fill=(255, 0, 0))

            # Convert the Pillow image to a Tkinter compatible format
            image_tk = ImageTk.PhotoImage(image_pil)
            
            # Display the captured frame, changing the Label's image while keeping a reference to that image so that the garbage collector doesn't remove it
            self.display_label.config(image=image_tk)
            self.display_label.image = image_tk
            
            # Remove the loading frame and pack the label used for displaying images inside the main window, if this is the first time that an image is taken from
            # the queue. After that, use the image's resolution as the window's size and center it again.
            if self.loading_frame.winfo_ismapped():
                self.loading_frame.pack_forget()
                self.display_label.pack()

                img_width = image_tk.width()
                img_height = image_tk.height()
                self.geometry(f"{img_width}x{img_height}")
                
                self.center_window(self, img_width, img_height)

                # Execute update_last_action in the Tkinter thread after 10ms
                self.after(10, self.update_last_action)
        except queue.Empty:
            pass
            
        self.after(10, self.update_image)

    # Updates the last executed action variable
    def update_last_action(self):
        try:
            action = self.executed_action_queue.get(False)
            self.last_action = str(action)
        except queue.Empty:
            pass

        self.after(10, self.update_last_action)