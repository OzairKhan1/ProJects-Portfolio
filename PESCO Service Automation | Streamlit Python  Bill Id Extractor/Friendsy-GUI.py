import tkinter as tk
from tkinter import messagebox
import subprocess
import os

def run_setup():
    try:
        # Update button appearance
        btn.config(text="🔁 Already Running", bg="#cc0000", state="disabled")

        # Minimize the window
        root.iconify()

        # Folder for setup.bat
        folder_name = "Friendsy Setup"
        target_dir = os.path.join(os.getcwd(), folder_name)
        os.makedirs(target_dir, exist_ok=True)

        # Download setup.bat
        bat_url = "https://raw.githubusercontent.com/OzairKhan1/DataScrapper/main/setup.bat"
        bat_path = os.path.join(target_dir, "setup.bat")

        powershell_cmd = f'powershell -Command "Invoke-WebRequest -Uri \'{bat_url}\' -OutFile \'{bat_path}\'"'
        subprocess.run(powershell_cmd, shell=True, check=True)

        # Run setup.bat
        subprocess.run(['cmd.exe', '/c', bat_path], cwd=target_dir, check=True)

    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Something went wrong:\n{e}")
        btn.config(text="🚀 Launch Tool", bg="#90ee90", state="normal")  # Revert on error
        root.deiconify()  # Restore window
    except Exception as e:
        messagebox.showerror("Error", str(e))
        btn.config(text="🚀 Launch Tool", bg="#90ee90", state="normal")
        root.deiconify()  # Restore window

# GUI setup
root = tk.Tk()
root.title("PESCO Bill Id Extractor Launcher")
root.geometry("400x250")
root.configure(bg="#1e1e1e")

title = tk.Label(root, text="⚡ PESCO Bill Id Extractor", font=("Arial", 18, "bold"), fg="white", bg="#1e1e1e")
title.pack(pady=20)

# Button: Light Green, Bold, Large Font
btn = tk.Button(
    root,
    text="🚀 Launch Tool",
    command=run_setup,
    font=("Arial", 16, "bold"),
    fg="black",
    bg="#90ee90",
    activebackground="#5cb85c",
    activeforeground="white",
    bd=0,
    relief="flat",
    padx=30,
    pady=12
)
btn.pack(pady=20)

footer = tk.Label(root, text="Designed by Engr. Ozair Khan", font=("Arial", 10), fg="#888", bg="#1e1e1e")
footer.pack(side="bottom", pady=10)

root.mainloop()
