<p align="center">
  <img src="assets/logo.png" width="128">
  <br>
</p>

# Gesture Maestro

**Gesture Maestro** is an open-source application that enables device interaction through real-time hand gesture recognition. Using **MediaPipe** for precise gesture detection and **pynput** for simulating keyboard inputs, this tool allows users to map custom actions to specific gestures.

## Table of contents

- [Gesture Maestro](#gesture-maestro)
  - [Table of contents](#table-of-contents)
  - [Requirements](#requirements)
  - [Getting started](#getting-started)
    - [Setting up the project](#setting-up-the-project)
    - [Running the project](#running-the-project)
  - [License](#license)

## Requirements

Gesture Maestro requires **Python version >= 3.9, < 3.13**. You can check your Python version by running:

```bash
python --version
```

## Getting started

Follow these steps to set up and run the project on your local machine.

### Setting up the project

1. **Clone the repository:**
    
    If you haven't already cloned the repository, run the following command to do so:

    ```bash
    git clone https://github.com/alejandrojggo/gesture-maestro.git
    ```

2. **Navigate to the project directory:**

    ```bash
    cd gesture-maestro
    ```
    
3. **Create a virtual environment (optional but recommended):**
    
    You can create a virtual environment to keep dependencies isolated:

    ```bash
    python -m venv .venv
    ```

4. **Activate the virtual environment:**
    - On Windows:

        ```bash
        .venv\Scripts\activate
        ```

    - On macOS/Linux:

        ```bash
        source .venv/bin/activate
        ```

5. **Install dependencies:**
    
    Install the required dependencies listed in the `requirements.txt` file:

    ```bash
    pip install -r requirements.txt
    ```

### Running the project

Once the dependencies are installed, you can run the project by using the following command:

```bash
python app.py
```

## License

This project is licensed under the [Apache License, Version 2.0 (Apache-2.0)](./LICENSE).