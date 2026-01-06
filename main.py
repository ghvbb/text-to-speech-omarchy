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
    def __init__(self):
        self.offline_engine = None
        if HAS_PYTTSX3:
            try:
                self.offline_engine = pyttsx3.init()
            except Exception as e:
                print(f"Warning: Could not init pyttsx3: {e}")

    def speak(self, text, engine_type, lang, output_file=None, speed=1.0):
        if not text.strip():
            raise ValueError("Text is empty")

        if engine_type == "online":
            return self._speak_online(text, lang, output_file)
        else:
            return self._speak_offline(text, lang, output_file, speed)

    def _speak_online(self, text, lang, output_file):
        if not HAS_GTTS:
            raise ImportError("gTTS is not installed.")
        save_path = output_file if output_file else self._get_temp_path()
        tts = gTTS(text=text, lang=lang)
        tts.save(save_path)
        return save_path

    def _speak_offline(self, text, lang, output_file, speed):
        if not self.offline_engine:
            raise ImportError("pyttsx3 is not working.")

        # Adjust voice and rate for offline engine
        self._set_offline_voice(lang)
        try:
            base_rate = int(self.offline_engine.getProperty('rate') or 200)
        except Exception:
            base_rate = 200
        try:
            new_rate = int(base_rate * float(speed))
            self.offline_engine.setProperty('rate', new_rate)
        except Exception:
            pass

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
        try:
            voices = self.offline_engine.getProperty('voices')
            for voice in voices:
                if lang in voice.id or (hasattr(voice, 'languages') and lang in getattr(voice, 'languages', [])):
                    self.offline_engine.setProperty('voice', voice.id)
                    return
        except Exception:
            pass

    def _get_temp_path(self):
        return os.path.join(tempfile.gettempdir(), f"tts_{uuid.uuid4().hex[:8]}.mp3")

    @staticmethod
    def _which(program):
        try:
            return subprocess.call(["which", program], stdout=subprocess.DEVNULL) == 0
        except Exception:
            return False

    @staticmethod
    def play_audio(filename, speed=1.0):
        """Cross-platform audio player with optional speed control (best with mpv)."""
        system = platform.system()
        # Prefer mpv for speed support
        if TTSManager._which('mpv'):
            cmd = ["mpv", filename]
            if float(speed) != 1.0:
                cmd = ["mpv", f"--speed={float(speed)}", filename]
            try:
                subprocess.Popen(cmd)
                return
            except Exception:
                pass

        if system == "Windows":
            # Windows built-in start doesn't support speed; fallback to start and warn
            try:
                os.startfile(filename)
                if float(speed) != 1.0:
                    messagebox.showwarning("Notice", "Playback speed requires 'mpv' to work. Playing at normal speed.")
                return
            except Exception:
                pass
        elif system == "Darwin":
            # afplay doesn't support speed
            try:
                subprocess.call(["afplay", filename])
                if float(speed) != 1.0:
                    messagebox.showwarning("Notice", "Playback speed requires 'mpv' to work. Playing at normal speed.")
                return
            except Exception:
                pass
        else:
            # Linux fallback players
            players = ["mpg123", "aplay", "paplay", "xdg-open"]
            for player in players:
                if TTSManager._which(player):
                    try:
                        subprocess.Popen([player, filename])
                        if float(speed) != 1.0:
                            messagebox.showwarning("Notice", "Playback speed requires 'mpv' to work. Playing at normal speed.")
                        return
                    except Exception:
                        continue

        # Last resort: try xdg-open or os.startfile
        try:
            if hasattr(os, 'startfile'):
                os.startfile(filename)
            else:
                subprocess.call(["xdg-open", filename])
            if float(speed) != 1.0:
                messagebox.showwarning("Notice", "Playback speed requires 'mpv' to work. Playing at normal speed.")
        except Exception as e:
            messagebox.showerror("Playback Error", str(e))

class TTSApp:
    def __init__(self, root):
        self.manager = TTSManager()
        self.root = root
        self.root.title("Universal Text-to-Speech")
        self.root.geometry("760x560")
        self.root.configure(bg="#1b1b1f")

        self.style = ttk.Style()
        try:
            self.style.theme_use('clam')
        except Exception:
            pass

        self._configure_dark_style()
        self.setup_ui()

    def _configure_dark_style(self):
        bg = '#1b1b1f'
        panel = '#232329'
        fg = '#e7e7e7'
        accent = '#3b82f6'

        self.style.configure('TFrame', background=bg)
        self.style.configure('TLabel', background=bg, foreground=fg)
        self.style.configure('TButton', background=panel, foreground=fg, relief='flat')
        self.style.map('TButton', background=[('active', '!disabled', '#2b2b30')])
        self.style.configure('TCombobox', fieldbackground=panel, background=panel, foreground=fg)
        self.style.configure('Horizontal.TProgressbar', troughcolor='#2a2a2a', background=accent)

    def setup_ui(self):
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.pack(fill=tk.X)

        ttk.Label(control_frame, text="Engine:").pack(side=tk.LEFT, padx=6)
        self.engine_var = tk.StringVar(value="online")
        engine_combo = ttk.Combobox(control_frame, textvariable=self.engine_var,
                                    values=["online", "offline"], state="readonly", width=10)
        engine_combo.pack(side=tk.LEFT, padx=6)

        ttk.Label(control_frame, text="Lang:").pack(side=tk.LEFT, padx=6)
        self.lang_var = tk.StringVar(value="en")
        self.lang_combo = ttk.Combobox(control_frame, textvariable=self.lang_var,
                                       values=["en", "es", "fr", "de", "it", "pt", "ru", "ja", "ko"],
                                       width=6)
        self.lang_combo.pack(side=tk.LEFT, padx=6)

        # Speed control (0.5x, 1.0x, 2.0x)
        ttk.Label(control_frame, text="Speed:").pack(side=tk.LEFT, padx=6)
        self.speed_var = tk.StringVar(value="1.0x")
        speed_combo = ttk.Combobox(control_frame, textvariable=self.speed_var,
                                   values=["0.5x", "1.0x", "2.0x"], state="readonly", width=6)
        speed_combo.pack(side=tk.LEFT, padx=6)

        ttk.Button(control_frame, text="Load Text", command=self.load_text_file).pack(side=tk.RIGHT, padx=6)

        text_frame = ttk.Frame(self.root, padding="10")
        text_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(text_frame, text="Enter text below:").pack(anchor=tk.W)
        self.text_area = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, height=18, font=("Consolas", 12),
                                                   bg='#0f0f13', fg='#e6e6e6', insertbackground='#ffffff', bd=0, relief='flat')
        self.text_area.pack(fill=tk.BOTH, expand=True, pady=8)

        action_frame = ttk.Frame(self.root, padding="16")
        action_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.progress = ttk.Progressbar(action_frame, mode='indeterminate', style='Horizontal.TProgressbar')
        self.progress.pack(fill=tk.X, pady=(0, 10))

        self.btn_play = ttk.Button(action_frame, text="▶ Play Audio", command=self.on_play)
        self.btn_play.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        self.btn_save = ttk.Button(action_frame, text="💾 Save to File", command=self.on_save)
        self.btn_save.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        status_bar.configure(background='#151518', foreground='#bdbdbd')

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

    def _parse_speed(self):
        val = self.speed_var.get().strip().lower().rstrip('x')
        try:
            return float(val)
        except Exception:
            return 1.0

    def on_play(self):
        text = self.text_area.get("1.0", tk.END).strip()
        if not text:
            return
        speed = self._parse_speed()
        self.toggle_controls(False)
        self.status_var.set("Synthesizing...")
        threading.Thread(target=self._run_play, args=(text, speed), daemon=True).start()

    def _run_play(self, text, speed):
        try:
            path = self.manager.speak(text, self.engine_var.get(), self.lang_var.get(), None, speed)
            self.status_var.set("Playing...")
            self.manager.play_audio(path, speed)
            self.status_var.set("Done")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.status_var.set("Error")
        finally:
            self.root.after(0, self.toggle_controls, True)

    def on_save(self):
        text = self.text_area.get("1.0", tk.END).strip()
        if not text:
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".mp3",
                                                 filetypes=[("MP3", "*.mp3"), ("WAV", "*.wav")])
        if not file_path:
            return

        speed = self._parse_speed()
        self.toggle_controls(False)
        self.status_var.set("Saving...")
        threading.Thread(target=self._run_save, args=(text, file_path, speed), daemon=True).start()

    def _run_save(self, text, filepath, speed):
        try:
            # Note: online engine (gTTS) will save normal audio; speed applied only at playback.
            self.manager.speak(text, self.engine_var.get(), self.lang_var.get(), filepath, speed)
            messagebox.showinfo("Success", f"Saved to {filepath}")
            if self.engine_var.get() == 'online' and float(speed) != 1.0:
                messagebox.showinfo("Note", "Saved file was generated with normal speed. To play back at a different speed use the UI 'Play' button which requires 'mpv' for variable-speed playback.")
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
    parser.add_argument("--speed", type=float, default=1.0, help="Playback/synthesis speed multiplier (e.g., 0.5, 1.0, 2.0)")

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
        print(f"[*] Engine: {args.engine} | Lang: {args.lang} | Speed: {args.speed}")
        path = manager.speak(text, args.engine, args.lang, args.file, args.speed)

        if args.file:
            print(f"[*] Saved to: {path}")

        if args.play:
            print("[*] Playing...")
            manager.play_audio(path, args.speed)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_cli()
    else:
        root = tk.Tk()
        app = TTSApp(root)
        root.mainloop()

