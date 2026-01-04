#!/usr/bin/env python3
import os
import sys
import argparse
import tempfile
import subprocess
import platform
import uuid
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
try:
    from gtts import gTTS
    HAS_GTTS = True
except ImportError:
    HAS_GTTS = False

try:
    import pyttsx3
    HAS_PYTTSX3 = True
except ImportError:
    HAS_PYTTSX3 = False


class TTSManager:
    """Handles the logic for both Online and Offline TTS."""
    
    def __init__(self):
        self.offline_engine = None
        if HAS_PYTTSX3:
            try:
                self.offline_engine = pyttsx3.init()
            except Exception as e:
                print(f"Warning: Could not init pyttsx3: {e}")

    def speak(self, text, engine_type, lang, output_file=None):
        """
        :param text: Text to speak
        :param engine_type: 'online' or 'offline'
        :param lang: Language code (e.g., 'en', 'es')
        :param output_file: Path to save. If None, saves to temp for playback.
        :return: Path to the generated file (or None if direct playback)
        """
        if not text.strip():
            raise ValueError("Text is empty")

        if engine_type == "online":
            return self._speak_online(text, lang, output_file)
        else:
            return self._speak_offline(text, lang, output_file)

    def _speak_online(self, text, lang, output_file):
        if not HAS_GTTS:
            raise ImportError("gTTS is not installed.")
        
        save_path = output_file if output_file else self._get_temp_path()
        
        tts = gTTS(text=text, lang=lang)
        tts.save(save_path)
        return save_path

    def _speak_offline(self, text, lang, output_file):
        if not self.offline_engine:
            raise ImportError("pyttsx3 is not working.")

        self._set_offline_voice(lang)

        if output_file:
            self.offline_engine.save_to_file(text, output_file)
            self.offline_engine.runAndWait()
            return output_file
        else:
            
            save_path = self._get_temp_path()
            self.offline_engine.save_to_file(text, save_path)
            self.offline_engine.runAndWait()
            return save_path

    def _set_offline_voice(self, lang):
        """Try to match requested language to available system voices."""
        try:
            voices = self.offline_engine.getProperty('voices')
            for voice in voices:
                if lang in voice.id or (hasattr(voice, 'languages') and lang in voice.languages):
                    self.offline_engine.setProperty('voice', voice.id)
                    return
        except:
            pass 

    def _get_temp_path(self):
        return os.path.join(tempfile.gettempdir(), f"tts_{uuid.uuid4().hex[:8]}.mp3")

    @staticmethod
    def play_audio(filename):
        """Cross-platform audio player."""
        system = platform.system()
        if system == "Windows":
            os.startfile(filename)
        elif system == "Darwin":  # macOS
            subprocess.call(["afplay", filename])
        else:  
            players = ["mpg123", "aplay", "paplay", "xdg-open", "vlc", "mpv"]
            for player in players:
                if subprocess.call(["which", player], stdout=subprocess.DEVNULL) == 0:
                    subprocess.call([player, filename])
                    return



class TTSApp:
    def __init__(self, root):
        self.manager = TTSManager()
        self.root = root
        self.root.title("Universal Text-to-Speech")
        self.root.geometry("600x500")        
        self.style = ttk.Style()
        self.style.theme_use('clam') 
        
        self.setup_ui()

    def setup_ui(self):
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.pack(fill=tk.X)
        ttk.Label(control_frame, text="Engine:").pack(side=tk.LEFT, padx=5)
        self.engine_var = tk.StringVar(value="online")
        engine_combo = ttk.Combobox(control_frame, textvariable=self.engine_var, 
                                    values=["online", "offline"], state="readonly", width=10)
        engine_combo.pack(side=tk.LEFT, padx=5)

        ttk.Label(control_frame, text="Lang:").pack(side=tk.LEFT, padx=5)
        self.lang_var = tk.StringVar(value="en")
        self.lang_combo = ttk.Combobox(control_frame, textvariable=self.lang_var, 
                                  values=["en", "es", "fr", "de", "it", "pt", "ru", "ja", "ko"], 
                                  width=5)
        self.lang_combo.pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Load Text", command=self.load_text_file).pack(side=tk.RIGHT, padx=5)
        text_frame = ttk.Frame(self.root, padding="10")
        text_frame.pack(fill=tk.BOTH, expand=True)
        ttk.Label(text_frame, text="Enter text below:").pack(anchor=tk.W)
        self.text_area = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, height=15, font=("Arial", 11))
        self.text_area.pack(fill=tk.BOTH, expand=True, pady=5)
        action_frame = ttk.Frame(self.root, padding="20")
        action_frame.pack(fill=tk.X, side=tk.BOTTOM)
        self.progress = ttk.Progressbar(action_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=(0, 10))

        self.btn_play = ttk.Button(action_frame, text="▶ Play ", command=self.on_play)
        self.btn_play.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.btn_save = ttk.Button(action_frame, text="💾 Save to File", command=self.on_save)
        self.btn_save.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def toggle_controls(self, enable):
        state = "normal" if enable else "disabled"
        self.btn_play.config(state=state)
        self.btn_save.config(state=state)
        self.text_area.config(state=state)
        if enable:
            self.progress.stop()
        else:
            self.progress.start(10)

    def load_text_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, "r", encoding="utf-8") as f:
                self.text_area.delete("1.0", tk.END)
                self.text_area.insert(tk.END, f.read())

    def on_play(self):
        text = self.text_area.get("1.0", tk.END).strip()
        if not text: return
        
        self.toggle_controls(False)
        self.status_var.set("Synthesizing...")        
        threading.Thread(target=self._run_play, args=(text,), daemon=True).start()

    def _run_play(self, text):
        try:
            path = self.manager.speak(text, self.engine_var.get(), self.lang_var.get())
            self.status_var.set("Playing...")
            self.manager.play_audio(path)
            self.status_var.set("Done")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.status_var.set("Error")
        finally:
            self.root.after(0, self.toggle_controls, True)

    def on_save(self):
        text = self.text_area.get("1.0", tk.END).strip()
        if not text: return

        file_path = filedialog.asksaveasfilename(defaultextension=".mp3", 
                                                 filetypes=[("MP3", "*.mp3"), ("WAV", "*.wav")])
        if not file_path: return

        self.toggle_controls(False)
        self.status_var.set("Saving...")
        threading.Thread(target=self._run_save, args=(text, file_path), daemon=True).start()

    def _run_save(self, text, filepath):
        try:
            self.manager.speak(text, self.engine_var.get(), self.lang_var.get(), filepath)
            messagebox.showinfo("Success", f"Saved to {filepath}")
            self.status_var.set("Saved")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.status_var.set("Error")
        finally:
            self.root.after(0, self.toggle_controls, True)


def run_cli():
    parser = argparse.ArgumentParser(description="Universal TTS (CLI Mode)")
    parser.add_argument("text", nargs="?", help="Text to speak")
    parser.add_argument("-i", "--input", help="Read text from a file")
    parser.add_argument("--engine", choices=["offline", "online"], default="offline")
    parser.add_argument("--lang", default="en")
    parser.add_argument("--file", help="Save to specific file path")
    parser.add_argument("--play", action="store_true", help="Play audio after generation")
    
    args = parser.parse_args()

    if args.input:
        if not os.path.exists(args.input):
            print(f"Error: File {args.input} not found.")
            sys.exit(1)
        with open(args.input, 'r', encoding='utf-8') as f:
            text = f.read()
    else:
        text = args.text

    if not text:
        print("Error: No text provided. Use arguments or run without arguments for GUI.")
        sys.exit(1)

    manager = TTSManager()
    try:
        print(f"[*] Engine: {args.engine} | Lang: {args.lang}")
        path = manager.speak(text, args.engine, args.lang, args.file)
        
        if args.file:
            print(f"[*] Saved to: {path}")
        
        if args.play:
            print("[*] Playing...")
            manager.play_audio(path)
            
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_cli()
    else:
        root = tk.Tk()
        app = TTSApp(root)
        root.mainloop()
