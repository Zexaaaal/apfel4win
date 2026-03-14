import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import os
import sys

# Import our logic
from font_converter import EmojiConverter
from system_installer import is_admin, run_as_admin, replace_font

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Apple Emoji to Windows Converter")
        self.geometry("600x550")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(1, weight=1)

        # Admin Badge
        admin_status = "Admin: YES" if is_admin() else "Admin: NO"
        admin_color = "green" if is_admin() else "red"
        self.admin_label = ctk.CTkLabel(self.main_frame, text=admin_status, text_color=admin_color, font=ctk.CTkFont(size=10, weight="bold"))
        self.admin_label.grid(row=0, column=2, padx=10, pady=10, sticky="ne")

        # Title
        self.label = ctk.CTkLabel(self.main_frame, text="Emoji Font Converter", font=ctk.CTkFont(size=24, weight="bold"))
        self.label.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10))

        # --- Section 1: Conversion ---
        self.conv_section = ctk.CTkLabel(self.main_frame, text="1. Conversion Settings", font=ctk.CTkFont(size=14, weight="bold"))
        self.conv_section.grid(row=1, column=0, columnspan=3, padx=20, pady=(10, 5), sticky="w")

        # Source File
        self.source_label = ctk.CTkLabel(self.main_frame, text="Source (Apple .ttc):")
        self.source_label.grid(row=2, column=0, padx=20, pady=5, sticky="e")
        self.source_entry = ctk.CTkEntry(self.main_frame)
        self.source_entry.grid(row=2, column=1, padx=(0, 10), pady=5, sticky="ew")
        self.source_entry.insert(0, os.path.abspath("AppleColorEmoji.ttc"))
        self.source_button = ctk.CTkButton(self.main_frame, text="Browse", width=80, command=self.browse_source)
        self.source_button.grid(row=2, column=2, padx=20, pady=5)

        # Target File
        self.target_label = ctk.CTkLabel(self.main_frame, text="Original (Segoe .ttf):")
        self.target_label.grid(row=3, column=0, padx=20, pady=5, sticky="e")
        self.target_entry = ctk.CTkEntry(self.main_frame)
        self.target_entry.grid(row=3, column=1, padx=(0, 10), pady=5, sticky="ew")
        self.target_entry.insert(0, os.path.abspath("seguiemj.ttf"))
        self.target_button = ctk.CTkButton(self.main_frame, text="Browse", width=80, command=self.browse_target)
        self.target_button.grid(row=3, column=2, padx=20, pady=5)

        self.convert_button = ctk.CTkButton(self.main_frame, text="Start Conversion", command=self.start_conversion)
        self.convert_button.grid(row=4, column=0, columnspan=3, padx=20, pady=15, sticky="ew")

        # --- Section 2: Installation ---
        self.inst_section = ctk.CTkLabel(self.main_frame, text="2. Installation", font=ctk.CTkFont(size=14, weight="bold"))
        self.inst_section.grid(row=5, column=0, columnspan=3, padx=20, pady=(10, 5), sticky="w")

        # Direct Install File
        self.direct_label = ctk.CTkLabel(self.main_frame, text="Custom Font (optional):")
        self.direct_label.grid(row=6, column=0, padx=20, pady=5, sticky="e")
        self.direct_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Use generated font by default")
        self.direct_entry.grid(row=6, column=1, padx=(0, 10), pady=5, sticky="ew")
        self.direct_button = ctk.CTkButton(self.main_frame, text="Browse", width=80, command=self.browse_direct)
        self.direct_button.grid(row=6, column=2, padx=20, pady=5)

        self.install_button = ctk.CTkButton(self.main_frame, text="Install to System (Requires Admin)", fg_color="green", hover_color="darkgreen", 
                                            command=self.start_installation)
        self.install_button.grid(row=7, column=0, columnspan=3, padx=20, pady=15, sticky="ew")

        # Progress & Status
        self.status_label = ctk.CTkLabel(self.main_frame, text="Status: Ready", font=ctk.CTkFont(size=12))
        self.status_label.grid(row=8, column=0, columnspan=3, padx=20, pady=5)

        self.progress_bar = ctk.CTkProgressBar(self.main_frame)
        self.progress_bar.grid(row=9, column=0, columnspan=3, padx=20, pady=(0, 20), sticky="ew")
        self.progress_bar.set(0)

        self.converted_font_path = "seguiemj_new.ttf"

    def browse_source(self):
        filename = filedialog.askopenfilename(filetypes=[("TrueType Collection", "*.ttc")])
        if filename:
            self.source_entry.delete(0, tk.END)
            self.source_entry.insert(0, filename)

    def browse_target(self):
        filename = filedialog.askopenfilename(filetypes=[("TrueType Font", "*.ttf")])
        if filename:
            self.target_entry.delete(0, tk.END)
            self.target_entry.insert(0, filename)

    def browse_direct(self):
        filename = filedialog.askopenfilename(filetypes=[("TrueType Font", "*.ttf")])
        if filename:
            self.direct_entry.delete(0, tk.END)
            self.direct_entry.insert(0, filename)

    def start_conversion(self):
        self.convert_button.configure(state="disabled")
        self.status_label.configure(text="Status: Converting... (Please wait)")
        self.progress_bar.set(0)
        self.progress_bar.start()
        
        thread = threading.Thread(target=self.run_conversion)
        thread.start()

    def run_conversion(self):
        apple_path = self.source_entry.get()
        segoe_path = self.target_entry.get()
        
        if not os.path.exists(apple_path) or not os.path.exists(segoe_path):
            self.after(0, lambda: self.on_conversion_complete(False))
            return

        converter = EmojiConverter(apple_path, segoe_path)
        success = converter.convert(self.converted_font_path)
        self.after(0, lambda: self.on_conversion_complete(success))

    def on_conversion_complete(self, success):
        self.progress_bar.stop()
        self.convert_button.configure(state="normal")
        if success:
            self.status_label.configure(text="Status: Conversion successful!")
            self.progress_bar.set(1)
        else:
            self.status_label.configure(text="Status: Conversion failed (Files missing?)")
            self.progress_bar.set(0)

    def start_installation(self):
        # We are now guaranteed to be admin at startup, so we can skip the manual check here
        font_to_install = self.direct_entry.get()
        if not font_to_install:
            font_to_install = self.converted_font_path
            
        if not os.path.exists(font_to_install):
            messagebox.showerror("Error", f"Font file not found: {font_to_install}\n\nPlease convert it first.")
            return

        self.install_button.configure(state="disabled")
        self.status_label.configure(text="Status: Installing to system...")
        
        thread = threading.Thread(target=lambda: self.run_installation(font_to_install))
        thread.start()

    def run_installation(self, font_path):
        success = replace_font(font_path)
        self.after(0, lambda: self.on_installation_complete(success))

    def on_installation_complete(self, success):
        self.install_button.configure(state="normal")
        if success:
            self.status_label.configure(text="Status: SUCCESS! Please restart Windows.")
            messagebox.showinfo("Success", "Font replaced successfully!\n\nPlease RESTART Windows for changes to take effect.")
        else:
            self.status_label.configure(text="Status: Installation failed.")
            messagebox.showerror("Error", "Failed to replace system font. Check console for errors.")

if __name__ == "__main__":
    if not is_admin():
        run_as_admin()
        sys.exit()
    
    app = App()
    app.mainloop()
