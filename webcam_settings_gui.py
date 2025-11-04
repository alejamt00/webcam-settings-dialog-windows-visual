#!/usr/bin/env python3
"""
Webcam Settings Dialog GUI - Automatic Version
Automatically detects webcams and launches the settings dialog
"""
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import re
import os
import sys


# Constants
CONTEXT_WINDOW_SIZE = 2  # Number of lines before/after to check for context
AUDIO_FILTER_TERMS = {'audio', 'microphone', 'sound'}  # Terms to filter out audio devices


class WebcamSettingsGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Webcam Settings Dialog")
        self.root.geometry("500x300")
        self.root.resizable(False, False)
        
        # Get the directory where the script is located
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            self.script_dir = os.path.dirname(sys.executable)
        else:
            # Running as script
            self.script_dir = os.path.dirname(os.path.abspath(__file__))
        
        self.ffmpeg_path = os.path.join(self.script_dir, "ffmpeg.exe")
        self.webcams = []
        
        self.setup_ui()
        self.detect_webcams()
    
    def setup_ui(self):
        """Setup the user interface"""
        # Title
        title_label = tk.Label(
            self.root,
            text="Webcam Settings Dialog Launcher",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=20)
        
        # Instructions
        instruction_label = tk.Label(
            self.root,
            text="Select your webcam from the list below:",
            font=("Arial", 10)
        )
        instruction_label.pack(pady=5)
        
        # Webcam selection frame
        selection_frame = tk.Frame(self.root)
        selection_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        # Listbox for webcams
        scrollbar = tk.Scrollbar(selection_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.webcam_listbox = tk.Listbox(
            selection_frame,
            yscrollcommand=scrollbar.set,
            font=("Arial", 10),
            height=6
        )
        self.webcam_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.webcam_listbox.yview)
        
        # Bind double-click to launch
        self.webcam_listbox.bind('<Double-Button-1>', lambda e: self.launch_settings())
        
        # Buttons frame
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=20)
        
        # Launch button
        self.launch_button = tk.Button(
            button_frame,
            text="Open Settings Dialog",
            command=self.launch_settings,
            font=("Arial", 11, "bold"),
            bg="#4CAF50",
            fg="white",
            padx=20,
            pady=10,
            state=tk.DISABLED
        )
        self.launch_button.pack(side=tk.LEFT, padx=10)
        
        # Refresh button
        refresh_button = tk.Button(
            button_frame,
            text="Refresh List",
            command=self.detect_webcams,
            font=("Arial", 11),
            padx=20,
            pady=10
        )
        refresh_button.pack(side=tk.LEFT, padx=10)
        
        # Status label
        self.status_label = tk.Label(
            self.root,
            text="Detecting webcams...",
            font=("Arial", 9),
            fg="gray"
        )
        self.status_label.pack(pady=5)
    
    def detect_webcams(self):
        """Detect available webcams using ffmpeg"""
        self.status_label.config(text="Detecting webcams...", fg="gray")
        self.webcam_listbox.delete(0, tk.END)
        self.webcams = []
        self.launch_button.config(state=tk.DISABLED)
        self.root.update()
        
        if not os.path.exists(self.ffmpeg_path):
            messagebox.showerror(
                "Error",
                f"ffmpeg.exe not found!\n\nPlease ensure ffmpeg.exe is in the same directory as this application:\n{self.script_dir}"
            )
            self.status_label.config(text="Error: ffmpeg.exe not found", fg="red")
            return
        
        try:
            # Run ffmpeg to list devices
            result = subprocess.run(
                [self.ffmpeg_path, "-list_devices", "true", "-f", "dshow", "-i", "dummy"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            # Parse the output to find video devices
            output = result.stderr  # ffmpeg outputs device list to stderr
            self.webcams = self._parse_ffmpeg_devices(output)
            
            # Update UI
            if self.webcams:
                for webcam in self.webcams:
                    self.webcam_listbox.insert(tk.END, webcam)
                self.webcam_listbox.selection_set(0)
                self.launch_button.config(state=tk.NORMAL)
                self.status_label.config(
                    text=f"Found {len(self.webcams)} webcam(s). Select one and click 'Open Settings Dialog'.",
                    fg="green"
                )
            else:
                self.status_label.config(text="No webcams found. Please connect a webcam and click 'Refresh List'.", fg="orange")
                messagebox.showwarning(
                    "No Webcams Found",
                    "No webcams were detected.\n\nPlease ensure:\n1. Your webcam is connected\n2. Your webcam drivers are installed\n3. Your webcam is not being used by another application"
                )
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to detect webcams:\n{str(e)}")
            self.status_label.config(text=f"Error: {str(e)}", fg="red")
    
    def _parse_ffmpeg_devices(self, output):
        """Parse ffmpeg output to extract video device names
        
        Args:
            output: String output from ffmpeg -list_devices
            
        Returns:
            List of video device names
        """
        devices = []
        lines = output.split('\n')
        
        for i, line in enumerate(lines):
            # Look for DirectShow video devices
            if '"' in line and 'video' in line.lower():
                # Extract device name from quotes
                match = re.search(r'"([^"]+)"', line)
                if match:
                    device_name = match.group(1)
                    device_name_lower = device_name.lower()
                    
                    # Avoid duplicates and filter out audio devices
                    if device_name not in devices and not any(term in device_name_lower for term in AUDIO_FILTER_TERMS):
                        # Additional check: look at context to confirm it's a video device
                        start_idx = max(0, i - CONTEXT_WINDOW_SIZE)
                        end_idx = min(len(lines), i + CONTEXT_WINDOW_SIZE + 1)
                        context = ' '.join(lines[start_idx:end_idx]).lower()
                        
                        if 'video' in context or (i > 0 and 'video' in lines[i-1].lower()):
                            devices.append(device_name)
        
        return devices
    
    def launch_settings(self):
        """Launch the webcam settings dialog for the selected webcam"""
        selection = self.webcam_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a webcam from the list.")
            return
        
        webcam_name = self.webcams[selection[0]]
        
        try:
            self.status_label.config(text=f"Launching settings dialog for '{webcam_name}'...", fg="blue")
            self.root.update()
            
            # Launch ffmpeg with the settings dialog
            # Use CREATE_NO_WINDOW to hide console, but the dialog will still show
            subprocess.Popen(
                [self.ffmpeg_path, "-f", "dshow", "-show_video_device_dialog", "true", "-i", f"video={webcam_name}"],
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            self.status_label.config(text=f"Settings dialog opened for '{webcam_name}'.", fg="green")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch settings dialog:\n{str(e)}")
            self.status_label.config(text=f"Error launching dialog", fg="red")


def main():
    root = tk.Tk()
    app = WebcamSettingsGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
