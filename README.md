# Text-to-Speech GUI (Tkinter)

This project is a fork of a **Text-to-Speech CLI application**, extended with a **graphical user interface (GUI)** built using **Tkinter**.
It is designed to run on **Linux-based distributions**, with primary testing on **Arch Linux**.

The application supports both **online** and **offline** text-to-speech modes.

## Features

* GUI built with Tkinter
* CLI support
* Online and offline text-to-speech
* MP3 audio output
* Cross-distro Linux support

## Online vs Offline Mode

* **Online mode**: Audio is generated and played automatically.
* **Offline mode**: Audio is generated but **not played automatically**.
  You must save the audio file first and then play it manually.

## Dependencies

### Python Packages

Install the required Python libraries:

```bash
pip install gTTS pyttsx3 --break-system-packages
```

### System Packages

#### Arch Linux

```bash
sudo pacman -S espeak-ng
```

#### Debian / Ubuntu

```bash
sudo apt update
sudo apt install espeak ffmpeg python3-tk python3 tk
```

#### Fedora

```bash
sudo dnf install espeak-ng ffmpeg tk python3
```

> `espeak` / `espeak-ng` is required for offline text-to-speech.
> `python3-tk` / `python3-tkinter` is required for the GUI.

## Usage

### CLI (Terminal / TTY)

```bash
python main.py "Your text here" --file name.mp3
```

This command converts the text to speech and saves it as an MP3 file.

### GUI

Run the installation script:

```bash
chmod +x install.sh
```

```bash
./install.sh
```

The script installs the application automatically and sets it up for GUI usage.

## Compatibility

* Arch Linux
* Debian / Ubuntu
* Fedora
* Other Linux-based distributions may work

## Credits

Made by great contributors:

* **ghvbb**
* **wachawo**

---
* includes Tkinter packa
