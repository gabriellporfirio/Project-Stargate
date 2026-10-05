import logging
import os
from pathlib import Path
import queue
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk

from appearance import COLORS, apply_theme, compact_filename, load_logo
from helpers.models import Status
from helpers.probe import SUPPORTED_EXTENSIONS
from helpers.reporting import human_size
from presets import DEFAULT_LAYOUT, DEFAULT_PLAYER, LAYOUTS, PLAYERS, make_context
from workflow import Action, check_files, details


class MediaChecker:
    def __init__(self, root, initial_path=None):
        self.root = root
        root.title("Pixel Media Checker")
        root.geometry("1080x700")
        root.minsize(860, 580)
        root.report_callback_exception = self.callback_error
        if os.name == "nt":
            try:
                root.iconbitmap(str(Path(__file__).parent / "assets" / "pixel.ico"))
            except tk.TclError:
                pass
        self.paths = [Path(initial_path)] if initial_path else []
        self.results = []
        self.events = queue.Queue()
        self.busy = False
        self.custom_size = None
        self.details_open = False
        self.player = tk.StringVar(value=DEFAULT_PLAYER)
        self.layout = tk.StringVar(value=DEFAULT_LAYOUT)
        self.previous_layout = DEFAULT_LAYOUT
        self.status = tk.StringVar(value="Choose the player and files to check.")
        self.batch_setup = ""
        self.file_title = tk.StringVar(value="No files selected")
        self.file_meta = tk.StringVar(value="Choose one or more files to begin.")
        self.build_window()
        self.show_selected()
        root.after(80, self.poll)
        if self.paths:
            root.after(150, self.run_check)

    def build_window(self):
        fonts = apply_theme(self.root)
        body = ttk.Frame(self.root, style="App.TFrame", padding=16)
        body.pack(fill="both", expand=True)
        body.columnconfigure(0, weight=1)
        body.rowconfigure(4, weight=1)

        file_card = ttk.Frame(body, style="Card.TFrame", padding=(20, 18))
        file_card.grid(row=0, column=0, sticky="ew")
        file_card.columnconfigure(1, weight=1)
        self.logo = load_logo(self.root)
        if self.logo:
            ttk.Label(file_card, image=self.logo, style="Body.TLabel").grid(
                row=0, column=0, rowspan=2, padx=(0, 16)
            )
        # A bounded text column reserves the action button's space for long names.
        ttk.Label(
            file_card, textvariable=self.file_title, style="Title.TLabel", width=1
        ).grid(row=0, column=1, sticky="ew")
        ttk.Label(
            file_card, textvariable=self.file_meta, style="Body.TLabel", width=1
        ).grid(row=1, column=1, sticky="ew", pady=(5, 0))
        self.choose_button = ttk.Button(
            file_card,
            text="Choose files",
            style="Primary.TButton",
            command=self.choose_files,
        )
        self.choose_button.grid(row=0, column=2, rowspan=2, padx=(18, 0))
        self.batch_selector = ttk.Combobox(
            file_card, style="Card.Setup.TCombobox", state="readonly", width=20,
            font=fonts["body"],
        )
        self.batch_selector.grid(
            row=2, column=1, columnspan=2, sticky="ew", pady=(12, 0)
        )
        self.batch_selector.grid_remove()
        self.batch_selector.bind(
            "<<ComboboxSelected>>", lambda event: self.show_selected()
        )

        setup = ttk.Frame(body, style="App.TFrame")
        setup.grid(row=1, column=0, sticky="ew", pady=(12, 0))
        setup.columnconfigure((1, 3), weight=1, uniform="setup")
        ttk.Label(setup, text="Player", style="Muted.TLabel").grid(
            row=0, column=0, padx=(0, 8)
        )
        self.player_box = ttk.Combobox(
            setup,
            textvariable=self.player,
            values=list(PLAYERS),
            state="readonly",
            style="Setup.TCombobox",
            font=fonts["body"],
            width=18,
        )
        self.player_box.grid(row=0, column=1, sticky="ew", padx=(0, 20))
        ttk.Label(setup, text="Layout", style="Muted.TLabel").grid(
            row=0, column=2, padx=(0, 8)
        )
        self.layout_box = ttk.Combobox(
            setup,
            textvariable=self.layout,
            values=list(LAYOUTS),
            state="readonly",
            style="Setup.TCombobox",
            font=fonts["body"],
            width=18,
        )
        self.layout_box.grid(row=0, column=3, sticky="ew")
        self.player_box.bind("<<ComboboxSelected>>", lambda event: self.setup_changed())
        self.layout_box.bind(
            "<<ComboboxSelected>>", lambda event: self.setup_changed(edit_size=True)
        )
        self.progress = ttk.Progressbar(
            body, mode="indeterminate", style="Horizontal.TProgressbar"
        )
        self.progress.grid(row=2, column=0, sticky="ew", pady=(8, 0))
        self.progress.grid_remove()

        cards = ttk.Frame(body, style="App.TFrame")
        cards.grid(row=3, column=0, sticky="ew", pady=14)
        cards.columnconfigure((0, 1, 2), weight=1, uniform="result")
        self.cards = {}
        for column, name in enumerate(("Overall", "Scala", "Dise")):
            card = ttk.Frame(cards, style="Card.TFrame", padding=(18, 14))
            card.grid(
                row=0,
                column=column,
                sticky="nsew",
                padx=(0 if column == 0 else 6, 0 if column == 2 else 6),
            )
            card.columnconfigure(0, weight=1)
            ttk.Label(card, text=name.upper(), style="CardCaption.TLabel").grid(
                row=0, column=0, sticky="w"
            )
            value = ttk.Label(
                card,
                text="—",
                style="Result.TLabel",
                width=1,
                wraplength=240,
                justify="left",
                anchor="w",
            )
            # Keep the longer action wording readable at smaller window sizes.
            value.bind(
                "<Configure>",
                lambda event, label=value: label.configure(
                    wraplength=max(1, event.width)
                ),
            )
            value.grid(row=1, column=0, sticky="ew", pady=(7, 0))
            self.cards[name] = value

        panel = ttk.Frame(body, style="Card.TFrame", padding=(20, 16))
        panel.grid(row=4, column=0, sticky="nsew")
        panel.columnconfigure(0, weight=1)
        panel.rowconfigure(1, weight=1)
        self.panel_title = ttk.Label(panel, text="Summary", style="PanelTitle.TLabel")
        self.panel_title.grid(row=0, column=0, sticky="w", pady=(0, 12))
        text_area = ttk.Frame(panel, style="Surface.TFrame")
        text_area.grid(row=1, column=0, sticky="nsew")
        text_area.columnconfigure(0, weight=1)
        text_area.rowconfigure(0, weight=1)
        self.detail_text = tk.Text(
            text_area,
            height=7,
            wrap="word",
            font=fonts["summary"],
            spacing1=4,
            spacing3=10,
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
            background=COLORS["card"],
            foreground=COLORS["ink"],
            selectbackground=COLORS["selected"],
            selectforeground=COLORS["ink"],
            insertbackground=COLORS["accent_bright"],
            padx=0,
            pady=0,
            state="disabled",
        )
        self.detail_text.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(
            text_area, orient="vertical", command=self.detail_text.yview,
            style="Vertical.TScrollbar",
        )
        scrollbar.grid(row=0, column=1, sticky="ns", padx=(8, 0))
        self.detail_text.configure(yscrollcommand=scrollbar.set)
        self.detail_text.tag_configure("lead", font=fonts["lead"])

        footer = ttk.Frame(body, style="App.TFrame")
        footer.grid(row=5, column=0, sticky="ew", pady=(12, 0))
        footer.columnconfigure(0, weight=1)
        self.status_label = ttk.Label(
            footer, textvariable=self.status, style="Muted.TLabel", wraplength=400
        )
        self.status_label.grid(row=0, column=0, sticky="w", padx=(0, 10))
        footer.bind(
            "<Configure>",
            lambda event: self.status_label.configure(
                wraplength=max(140, event.width - 290)
            ),
        )
        self.details_button = ttk.Button(
            footer,
            text="Show details",
            style="Secondary.TButton",
            command=self.toggle_details,
            state="disabled",
        )
        self.details_button.grid(row=0, column=1, padx=(0, 8))

    def choose_files(self):
        chosen = filedialog.askopenfilenames(
            parent=self.root,
            title="Choose files to check",
            filetypes=[
                (
                    "Media files",
                    " ".join("*" + ext for ext in sorted(SUPPORTED_EXTENSIONS)),
                ),
                ("All files", "*.*"),
            ],
        )
        if chosen:
            self.paths = [Path(path) for path in chosen]
            self.run_check()

    def setup_changed(self, edit_size=False):
        if edit_size and self.layout.get() == "Custom size…":
            initial = (
                "x".join(map(str, self.custom_size))
                if self.custom_size
                else "1920x1080"
            )
            value = simpledialog.askstring(
                "Content size",
                "Width × height in pixels (for example 5760x1080)",
                initialvalue=initial,
                parent=self.root,
            )
            if value is None:
                self.layout.set(self.previous_layout)
                return
            try:
                width, height = (
                    int(part.strip())
                    for part in value.lower().replace("×", "x").split("x")
                )
                make_context(self.player.get(), self.layout.get(), (width, height))
                self.custom_size = (width, height)
            except ValueError:
                self.layout.set(self.previous_layout)
                messagebox.showerror(
                    "Check the size",
                    "Enter a whole-number width and height between 1 and 65535.",
                    parent=self.root,
                )
                return
        self.previous_layout = self.layout.get()
        if self.paths:
            self.run_check()

    def run_check(self):
        if self.busy or not self.paths:
            return
        context = make_context(self.player.get(), self.layout.get(), self.custom_size)
        self.batch_setup = f"{self.player.get()} · {self.layout.get()}"
        if self.layout.get() == "Custom size…":
            self.batch_setup += f" ({context.canvas_width}×{context.canvas_height})"
        self.results = []
        self.refresh_batch(reset=True)
        self.show_selected()
        self.details_button.configure(state="disabled")
        self.set_busy(True)
        self.status.set(f"Checking 0 of {len(self.paths)}…")
        paths = list(self.paths)

        def worker():
            try:
                for result in check_files(paths, context):
                    self.events.put(result)
            finally:
                self.events.put(None)

        threading.Thread(target=worker, daemon=True).start()

    def set_busy(self, busy):
        self.busy = busy
        if busy:
            self.progress.grid()
            self.progress.start(15)
        else:
            self.progress.stop()
            self.progress.grid_remove()
        self.choose_button.configure(state="disabled" if busy else "normal")
        for box in (self.player_box, self.layout_box):
            box.configure(state="disabled" if busy else "readonly")

    def poll(self):
        try:
            while True:
                result = self.events.get_nowait()
                if result is None:
                    self.set_busy(False)
                    counts = {
                        action: sum(r.action == action for r in self.results)
                        for action in Action
                    }
                    self.status.set(
                        " · ".join(
                            f"{action.value}: {count}"
                            for action, count in counts.items()
                            if count
                        )
                        or "No files checked."
                    )
                    state = "normal" if self.results else "disabled"
                    self.details_button.configure(state=state)
                    continue
                self.results.append(result)
                self.refresh_batch()
                self.show_selected()
                self.status.set(f"Checking {len(self.results)} of {len(self.paths)}…")
        except queue.Empty:
            pass
        finally:
            self.root.after(80, self.poll)

    def refresh_batch(self, reset=False):
        selected = 0 if reset else max(0, self.batch_selector.current())
        values = []
        for index, path in enumerate(self.paths):
            state = (
                self.results[index].action.value
                if index < len(self.results)
                else "Waiting"
            )
            values.append(f"{state}  ·  {compact_filename(path.name, 64)}")
        self.batch_selector.configure(values=values)
        if values:
            self.batch_selector.current(min(selected, len(values) - 1))
        if len(values) > 1:
            self.batch_selector.grid()
        else:
            self.batch_selector.grid_remove()

    def set_details(self, text):
        self.detail_text.configure(state="normal")
        self.detail_text.delete("1.0", "end")
        self.detail_text.insert("1.0", text)
        self.detail_text.tag_add("lead", "1.0", "1.end")
        self.detail_text.configure(state="disabled")
        self.detail_text.yview_moveto(0)

    def show_selected(self):
        index = max(0, self.batch_selector.current())
        result = self.results[index] if index < len(self.results) else None
        path = self.paths[index] if index < len(self.paths) else None
        self.file_title.set(
            compact_filename(path.name) if path else "No files selected"
        )
        self.file_meta.set(
            f"File {index + 1} of {len(self.paths)}"
            if path
            else "Choose one or more files to begin."
        )
        for card in self.cards.values():
            card.configure(text="—", foreground=COLORS["muted"])
        self.panel_title.configure(text="Details" if self.details_open else "Summary")
        if not result:
            self.set_details(
                "Checking your files…\nResults will appear here."
                if path
                else "Your results appear here.\nChoose files to get started."
            )
            return
        color = {
            Action.PASS: "pass",
            Action.REVIEW: "review",
            Action.RETURN: "fail",
            Action.ERROR: "fail",
        }[result.action]
        self.cards["Overall"].configure(
            text=result.action.value, foreground=COLORS[color]
        )
        if result.report:
            meta = result.report.metadata
            properties = [
                f"File {index + 1} of {len(self.paths)}",
                meta.media_type.title(),
                human_size(meta.size_bytes),
            ]
            if meta.width and meta.height:
                properties.append(f"{meta.width} × {meta.height}")
            self.file_meta.set("  ·  ".join(properties))
            for platform in (result.report.scala, result.report.dise):
                label, color = {
                    Status.PASS: (Action.PASS.value, "pass"),
                    Status.REVIEW: (Action.REVIEW.value, "review"),
                    Status.FAIL: (Action.RETURN.value, "fail"),
                }.get(platform.status, (Action.REVIEW.value, "review"))
                self.cards[platform.platform].configure(
                    text=label if platform.selected else "Not selected",
                    foreground=COLORS[color if platform.selected else "muted"],
                )
        if self.details_open:
            self.set_details(details(result))
            return
        headline = {
            Action.PASS: "No changes needed.",
            Action.REVIEW: "Check before scheduling.",
            Action.RETURN: "Check with the client before scheduling.",
            Action.ERROR: "This file could not be checked.",
        }[result.action]
        self.set_details(headline + "\n\n" + result.reason)

    def toggle_details(self, force_open=False):
        if not self.results:
            return
        self.details_open = force_open or not self.details_open
        self.show_selected()
        self.details_button.configure(
            text="Hide details" if self.details_open else "Show details"
        )

    def callback_error(self, exc_type, value, traceback):
        logging.error("Desktop callback failed", exc_info=(exc_type, value, traceback))
        messagebox.showerror(
            "Could not complete that action",
            "Please try again. If it continues, close and reopen the app.",
            parent=self.root,
        )


def launch(initial_path=None):
    if os.name == "nt":
        try:
            import ctypes

            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except (AttributeError, OSError):
            pass
    root = tk.Tk()
    MediaChecker(root, initial_path)
    root.mainloop()
