import tkinter as tk
from tkinter import Menu, messagebox
from bitcoin import *
import threading
import time
import os
import sys

class VanityAddressGenerator:

    def __init__(self, root):
        self.root = root
        self.root.title("VanityBit")

        font_large = ("Arial", 16, "bold")
        font_medium = ("Arial", 12)
        font_small = ("Arial", 10)

        self.label = tk.Label(root, text="Vanity Bitcoin Address Generator", font=font_large)
        self.label.pack(pady=20)

        self.input_label = tk.Label(root, text="希望のアドレスの先頭文字列を入力:", font=font_medium)
        self.input_label.pack(padx=20, pady=5)

        self.entry = tk.Entry(root, font=font_medium)
        self.entry.pack(padx=20, pady=5)

        self.thread_label = tk.Label(root, text="使用するスレッド数を入力:", font=font_medium)
        self.thread_label.pack(padx=20, pady=5)

        self.thread_entry = tk.Entry(root, font=font_medium)
        self.thread_entry.pack(padx=20, pady=5)

        self.generate_button = tk.Button(root, text="生成開始", command=self.start_generation, bg='#4CAF50', fg='white', font=font_medium)
        self.generate_button.pack(padx=20, pady=10)

        self.address_label = tk.Label(root, text="生成されたバニティアドレス:", font=font_medium)
        self.address_label.pack(padx=20, pady=5)

        self.address_display = tk.Text(root, height=1, width=40, font=font_small)
        self.address_display.pack(padx=20, pady=5)

        self.private_key_label = tk.Label(root, text="秘密鍵 (WIF):", font=font_medium)
        self.private_key_label.pack(padx=20, pady=5)

        self.private_key_display = tk.Text(root, height=1, width=60, font=font_small)
        self.private_key_display.pack(padx=20, pady=5)

        self.hashrate_label = tk.Label(root, text="ハッシュレート (試行/秒):", font=font_medium)
        self.hashrate_label.pack(padx=20, pady=5)

        self.hashrate_display = tk.Label(root, text="0", font=font_medium)
        self.hashrate_display.pack(padx=20, pady=5)

        self.create_context_menu()

        self.found = threading.Event()
        self.attempts = 0

    def create_context_menu(self):
        # Context menu for text boxes
        self.context_menu = Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Copy", command=self.copy_to_clipboard)
        self.address_display.bind("<Button-3>", self.show_context_menu)
        self.private_key_display.bind("<Button-3>", self.show_context_menu)

    def show_context_menu(self, event):
        self.context_menu.post(event.x_root, event.y_root)

    def copy_to_clipboard(self):
        # Get the widget that triggered the context menu
        widget = self.root.focus_get()
        # Get the selected text
        selected_text = widget.get("sel.first", "sel.last")
        self.root.clipboard_clear()
        self.root.clipboard_append(selected_text)

    def generate_vanity_address(self):
        desired_prefix = self.entry.get()
        while not self.found.is_set():
            private_key = random_key()
            wif_key = encode_privkey(private_key, 'wif')  # Convert to WIF format
            public_key = privtopub(private_key)
            address = pubtoaddr(public_key)
            self.attempts += 1
    
            if address.startswith("1" + desired_prefix):
                self.found.set()
                self.address_display.delete(1.0, tk.END)
                self.address_display.insert(tk.END, address)
                self.private_key_display.delete(1.0, tk.END)
                self.private_key_display.insert(tk.END, wif_key)  # Display the WIF private key
                self.generate_button.config(state=tk.NORMAL)  # Enable the button again
    
                # ANSI escape code for yellow text
                yellow = '\033[93m'
                # ANSI escape code to end the color setting
                end_color = '\033[0m'
                
                print(f"{yellow}[STOPPED]{end_color}\nAddress: {address}\nPrivate Key(WIF): {wif_key}\n")
                sys.stdout.flush()  # Forces the print output to be displayed immediately

    def monitor_hashrate(self):
        start_time = time.time()
        while not self.found.is_set():
            start_attempts = self.attempts
            time.sleep(1)
            elapsed_time = time.time() - start_time
            current_rate = self.attempts - start_attempts
            if self.found.is_set():
                break  # Stop if vanity address is found
            print(f"\033[91m[RUNNING]\033[0m \033[92mTotal:{self.attempts}h, Time:{int(elapsed_time)}s, Speed:{current_rate}h/s\033[0m")
            sys.stdout.flush()

    def start_generation(self):
        try:
            thread_count = int(self.thread_entry.get())
            max_threads = os.cpu_count()

            if thread_count > max_threads:
                tk.messagebox.showerror("エラー", f"PCの最大スレッド数は {max_threads} です。これ以下の数を入力してください。")
                return

            self.found.clear()
            self.attempts = 0

            # Disable the generate button
            self.generate_button.config(state=tk.DISABLED)

            # Start hashrate monitoring
            t = threading.Thread(target=self.monitor_hashrate)
            t.start()

            for _ in range(thread_count):
                t = threading.Thread(target=self.generate_vanity_address)
                t.start()
        except ValueError:
            tk.messagebox.showerror("エラー", "無効なスレッド数です。正しい数値を入力してください。")
            self.generate_button.config(state=tk.NORMAL)  # Enable the button in case of error

if __name__ == "__main__":
    root = tk.Tk()
    app = VanityAddressGenerator(root)
    root.mainloop()
