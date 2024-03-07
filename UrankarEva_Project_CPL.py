# Imports
import ftplib
import threading
import os
import tkinter as tk
from tkinter import ttk, messagebox

# Defining the FTP server details
HOSTNAME = "ftp.bmrb.io"
USERNAME = None
PASSWORD = None
DIR = "pdb/holdings"

class FTPDownloader:
    # Defining the GUI
    def __init__(self, root):
        self.root = root
        self.root.title("FTP Downloader")

        # Configuring the application style
        app_bg_color = "#dbe1ff"
        label_font = ("Courier", 12, "bold")
        label_fg = "#4c599e"

        button_font = ("Courier", 10)
        button_bg = "#9ba4cc"
        button_fg = "white"

        self.root.configure(bg=app_bg_color)

        # Creating the widgets with the configured style
        self.url_label = tk.Label(root, text="FTP URL:")
        self.url_entry = tk.Entry(root, width=30)
        self.download_button = tk.Button(root, text="Download", command=self.start_download)

        self.download_button.configure(font=button_font, bg=button_bg, fg=button_fg)
        self.url_label.configure(font=label_font, bg=app_bg_color, fg=label_fg)

        self.url_label.grid(row=0, column=0, pady=10, padx=10, sticky="w")
        self.url_entry.grid(row=0, column=1, pady=10, padx=10, sticky="w")
        self.download_button.grid(row=0, column=2, pady=10, padx=10)

        self.progress_bars = {}
        self.current_row = 1

    # Defining the download function
    def start_download(self):
        # Get the URL from the entry box
        url = self.url_entry.get().strip()
        if not url.startswith("ftp://"):
            messagebox.showerror("Error", "Invalid FTP URL. It should start with 'ftp://'")
            return

        filename = os.path.basename(url)
        download_id = f"{len(self.progress_bars)}_{os.path.basename(url)}"
        # Create a progress bar for the file
        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(self.root, variable=progress_var, maximum=100, length=200)
        progress_bar.grid(row=self.current_row, column=0, columnspan=3, pady=5, padx=10, sticky="ew")

        self.progress_bars[download_id] = {"bar": progress_bar, "var": progress_var}
        # Start a new thread to download the file
        download_thread = threading.Thread(target=self.download_file, args=(url, HOSTNAME, DIR, filename, download_id))
        download_thread.start()

        self.current_row += 1

    # Defining the download file function
    def download_file(self, url, HOSTNAME, DIR, filename, download_id):
        try:
            # Connect to the FTP server
            ftp = ftplib.FTP(HOSTNAME)
            ftp.login()
            ftp.cwd(DIR)

            # Create the downloads directory if it doesn't exist
            download_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")
            if not os.path.exists(download_dir):
                os.makedirs(download_dir)

            local_filename = os.path.join(download_dir, filename)

            total_size = ftp.size(filename)
            bytes_downloaded = 0

            # Download the file in chunks
            blocksize = 8192
            with open(local_filename, 'wb') as local_file:
                def callback(data):
                    nonlocal bytes_downloaded
                    bytes_downloaded += len(data)
                    progress = (bytes_downloaded / total_size) * 100
                    self.root.after(100, lambda: self.update_progress(download_id, progress))
                    local_file.write(data)

                ftp.retrbinary(f"RETR {filename}", callback, blocksize)

            messagebox.showinfo("Success", f"Download of {filename} complete.")
        # Handle exceptions	
        except FileNotFoundError:
            messagebox.showerror("Error", f"File not found on the server: {filename}")
        except ftplib.error_perm as e:
            messagebox.showerror("Error", f"Permission error: {e}")
        except ftplib.error_temp as e:
            messagebox.showerror("Error", f"Temporary error: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Error downloading {filename}: {str(e)}")


    # Defining the update progress function (called on download completion)
    def update_progress(self, download_id, progress):
        # Update the progress bar
        if download_id in self.progress_bars:
            self.progress_bars[download_id]["var"].set(progress)
            self.root.update_idletasks()

if __name__ == "__main__":
    root = tk.Tk()
    downloader = FTPDownloader(root)
    root.mainloop()
