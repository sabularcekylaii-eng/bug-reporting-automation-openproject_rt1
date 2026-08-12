import datetime
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox

from sheets_client import SheetsClient
from openproject_client import OpenProjectClient
from rt1_client import RT1Client


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Bug Reporting Automation")
        self.root.geometry("640x520")

        self.is_running = False

        tk.Label(
            root, text="Bug Reporting Automation", font=("Arial", 14, "bold")
        ).pack(anchor="w", padx=15, pady=(15, 0))
        tk.Label(
            root,
            text="Reads pending bug rows, creates an OpenProject ticket, then a linked RT1 ticket.",
            font=("Arial", 9), fg="#555"
        ).pack(anchor="w", padx=15, pady=(0, 10))

        self.run_button = tk.Button(
            root, text="Run Now", command=self.run_now_clicked,
            bg="#4CAF50", fg="white", font=("Arial", 11, "bold"), height=2
        )
        self.run_button.pack(fill="x", padx=15, pady=(0, 15))

        tk.Label(root, text="Log:", font=("Arial", 9, "bold")).pack(anchor="w", padx=15)
        self.log_box = scrolledtext.ScrolledText(root, height=22, font=("Consolas", 9), state="disabled")
        self.log_box.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    def log(self, message):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        line = f"[{timestamp}] {message}\n"

        def append():
            self.log_box.configure(state="normal")
            self.log_box.insert(tk.END, line)
            self.log_box.see(tk.END)
            self.log_box.configure(state="disabled")

        self.root.after(0, append)

    def run_now_clicked(self):
        if self.is_running:
            self.log("A run is already in progress, please wait...")
            return
        threading.Thread(target=self.run_job, daemon=True).start()

    def run_job(self):
        self.is_running = True
        self.root.after(0, lambda: self.run_button.configure(state="disabled", text="Running..."))

        rt1 = None
        try:
            self.log("Connecting to Google Sheet...")
            sheet = SheetsClient()
            pending = sheet.get_pending_rows()

            if not pending:
                self.log("No pending bug rows found. Nothing to do.")
                return

            self.log(f"Found {len(pending)} pending bug(s).")

            op = OpenProjectClient()

            rt1 = RT1Client(log_callback=self.log)
            rt1.login()

            for i, row in enumerate(pending, start=1):
                self.log(f"--- Processing row {row['row_number']} ({i}/{len(pending)}) ---")
                try:
                    self.log(f"Creating OpenProject ticket: {row['title']}")
                    wp_id, op_link = op.create_bug(
                        title=row["title"],
                        steps=row["steps"],
                        expected=row["expected"],
                        actual=row["actual"],
                        environment=row["environment"],
                    )
                    self.log(f"OpenProject #{wp_id} created -> {op_link}")

                    rt1_ticket = rt1.create_and_resolve_ticket(row["title"], row["actual"], op_link)

                    sheet.mark_row_complete(row["row_number"], op_link, rt1_ticket)
                    self.log(f"Row {row['row_number']} done -> OP #{wp_id}, RT1 #{rt1_ticket}")
                except Exception as row_err:
                    self.log(f"FAILED row {row['row_number']}: {row_err}")
                    try:
                        sheet.mark_row_failed(row["row_number"], str(row_err))
                    except Exception:
                        pass

            self.log("Run complete.")

        except Exception as e:
            self.log(f"ERROR: {e}")
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
        finally:
            if rt1:
                rt1.close()
            self.is_running = False
            self.root.after(0, lambda: self.run_button.configure(state="normal", text="Run Now"))


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
