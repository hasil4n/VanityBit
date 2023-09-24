import tkinter as tk
from tkinter import Menu, messagebox
from bitcoin import *
import threading
import time
import os

class VanityAddressGenerator:

    def __init__(self, root):
        self.root = root
        self.root.title("Vanity Bitcoin Address Generator")

        self.label = tk.Label(root, text="Vanity Bitcoin Address Generator", font=("Arial", 16, "bold"))
        self.label.pack(pady=20)

        self.input_label = tk.Label(root, text="希望のアドレスの先頭文字列を入力:")
        self.input_label.pack(padx=10, pady=10)

        self.entry = tk.Entry(root)
        self.entry.pack(padx=10, pady=10)

        self.thread_label = tk.Label(root, text="使用するスレッド数を入力:")
        self.thread_label.pack(padx=10, pady=5)

        self.thread_entry = tk.Entry(root)
        self.thread_entry.pack(padx=10, pady=5)

        self.generate_button = tk.Button(root, text="生成開始", command=self.start_generation)
        self.generate_button.pack(padx=10, pady=5)

        self.address_label = tk.Label(root, text="生成されたバニティアドレス:")
        self.address_label.pack(padx=10, pady=10)

        self.address_display = tk.Text(root, height=1, width=40)
        self.address_display.pack(padx=10, pady=10)

        self.private_key_label = tk.Label(root, text="秘密鍵 (WIF):")
        self.private_key_label.pack(padx=10, pady=10)

        self.private_key_display = tk.Text(root, height=1, width=60)
        self.private_key_display.pack(padx=10, pady=10)

        self.hashrate_label = tk.Label(root, text="ハッシュレート (試行/秒):")
        self.hashrate_label.pack(padx=10, pady=10)

        self.hashrate_display = tk.Label(root, text="0")
        self.hashrate_display.pack(padx=10, pady=10)

        self.create_context_menu()

        self.found = threading.Event()
        self.attempts = 0

    def create_context_menu(self):
        self.context_menu = Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Copy", command=self.copy_to_clipboard)
        self.address_display.bind("<Button-3>", self.show_context_menu)
        self.private_key_display.bind("<Button-3>", self.show_context_menu)

    def show_context_menu(self, event):
        self.context_menu.post(event.x_root, event.y_root)

    def copy_to_clipboard(self):
        widget = self.root.focus_get()
        selected_text = widget.get("sel.first", "sel.last")
        self.root.clipboard_clear()
        self.root.clipboard_append(selected_text)

    def generate_vanity_address(self):
        desired_prefix = self.entry.get()
        while not self.found.is_set():
            private_key = random_key()
            wif_key = encode_privkey(private_key, 'wif')
            public_key = privtopub(private_key)
            address = pubtoaddr(public_key)
            self.attempts += 1

            if address.startswith("1" + desired_prefix):
                self.found.set()
                self.address_display.delete(1.0, tk.END)
                self.address_display.insert(tk.END, address)
                self.private_key_display.delete(1.0, tk.END)
                self.private_key_display.insert(tk.END, wif_key)
                self.generate_button.config(state=tk.NORMAL)

    def monitor_hashrate(self):
        while not self.found.is_set():
            start_attempts = self.attempts
            time.sleep(1)
            current_rate = self.attempts - start_attempts
            self.hashrate_display.config(text=str(current_rate))

    def start_generation(self):
        try:
            thread_count = int(self.thread_entry.get())
            max_threads = os.cpu_count()

            if thread_count > max_threads:
                tk.messagebox.showerror("エラー", f"PCの最大スレッド数は {max_threads} です。これ以下の数を入力してください。")
                return

            self.found.clear()
            self.attempts = 0

            self.generate_button.config(state=tk.DISABLED)

            t = threading.Thread(target=self.monitor_hashrate)
            t.start()

            for _ in range(thread_count):
                t = threading.Thread(target=self.generate_vanity_address)
                t.start()
        except ValueError:
            tk.messagebox.showerror("エラー", "無効なスレッド数です。正しい数値を入力してください。")
            self.generate_button.config(state=tk.NORMAL)

if __name__ == "__main__":
    root = tk.Tk()
    app = VanityAddressGenerator(root)
    root.mainloop()
