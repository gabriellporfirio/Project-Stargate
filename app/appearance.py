from pathlib import Path
from tkinter import font as tkfont, ttk

COLORS = {
    "ink": "#F2F2F2",
    "secondary": "#BBBBBB",
    "muted": "#9A9A9A",
    "paper": "#232323",
    "card": "#2B2B2B",
    "inner": "#383838",
    "hover": "#454545",
    "line": "#494949",
    "highlight": "#5A5A5A",
    "selected": "#505050",
    "accent": "#C0394B",
    "accent_active": "#A8303F",
    "accent_bright": "#DD5A6E",
    "pass": "#6EE7A0",
    "review": "#F5C26B",
    "fail": "#FF9C9C",
    "info": "#EC8F9C",
}


def _fonts(root):
    available = {name.casefold(): name for name in tkfont.families(root)}
    body = next(
        (available[name.casefold()] for name in ("Figtree", "Segoe UI", "Roboto", "Arial")
         if name.casefold() in available),
        tkfont.nametofont("TkDefaultFont", root).actual("family"),
    )
    heading = available.get("cal sans", body)
    return {
        "body": (body, 10),
        "small": (body, 9),
        "caption": (body, 9, "bold"),
        "button": (body, 10, "bold"),
        "title": (heading, 16),
        "result": (body, 15, "bold"),
        "heading": (heading, 12),
        "summary": (body, 11),
        "lead": (heading, 14),
    }


def _rounded_image(root, fill, border, radius, gradient=None):
    from PIL import Image, ImageColor, ImageDraw, ImageTk

    scale = 4
    size = (radius * 2 + (4 if gradient else 128)) * scale
    image = Image.new("RGBA", (size, size), fill)
    if gradient:
        top, bottom = (ImageColor.getrgb(colour) for colour in gradient)
        drawing = ImageDraw.Draw(image)
        for y in range(size):
            colour = tuple(round(a + (b - a) * y / (size - 1)) for a, b in zip(top, bottom))
            drawing.line((0, y, size, y), fill=colour)
    mask = Image.new("L", (size, size))
    ImageDraw.Draw(mask).rounded_rectangle(
        (0, 0, size - 1, size - 1), radius=radius * scale, fill=255
    )
    image.putalpha(mask)
    ImageDraw.Draw(image).rounded_rectangle(
        (scale // 2, scale // 2, size - scale // 2 - 1, size - scale // 2 - 1),
        radius=radius * scale, outline=border, width=scale,
    )
    image = image.resize((size // scale, size // scale), Image.Resampling.LANCZOS)
    photo = ImageTk.PhotoImage(image, master=root)
    root._pixel_theme_images.append(photo)
    return photo


def _button_style(style, root, name, primary, fonts):
    fill = COLORS["accent" if primary else "inner"]
    border = COLORS["accent_bright" if primary else "highlight"]
    hover = COLORS["accent_active" if primary else "hover"]
    gradient = ("#CC4659", "#B8364A") if primary else None
    normal = _rounded_image(root, fill, border, 18, gradient)
    active = _rounded_image(root, hover, border, 18)
    focused = _rounded_image(root, fill, COLORS["ink"], 18, gradient)
    pressed = _rounded_image(root, hover, COLORS["ink"], 18)
    disabled = _rounded_image(root, COLORS["card"], COLORS["line"], 18)
    element = f"Pixel.{name}.button"
    style.element_create(
        element, "image", normal, ("disabled", disabled), ("pressed", pressed),
        ("focus", focused), ("active", active), border=18, padding=0, sticky="nsew",
        width=40, height=40,
    )
    style.layout(f"{name}.TButton", [(element, {"sticky": "nsew", "children": [
        ("Button.padding", {"sticky": "nsew", "children": [
            ("Button.label", {"sticky": "nsew"})
        ]})
    ]})])
    style.configure(
        f"{name}.TButton", font=fonts["button"], foreground=COLORS["ink"],
        background=COLORS["card" if primary else "paper"],
        padding=(18, 9), borderwidth=0, anchor="center",
    )
    background = COLORS["card" if primary else "paper"]
    style.map(
        f"{name}.TButton", foreground=[("disabled", COLORS["muted"])],
        background=[("disabled", background), ("active", background), ("pressed", background)],
    )


def _arrow_image(root):
    from PIL import Image, ImageDraw, ImageTk

    arrow = Image.new("RGBA", (48, 32))
    ImageDraw.Draw(arrow).polygon(((4, 8), (44, 8), (24, 28)), fill=COLORS["secondary"])
    photo = ImageTk.PhotoImage(arrow.resize((12, 8), Image.Resampling.LANCZOS), master=root)
    root._pixel_theme_images.append(photo)
    return photo


def apply_theme(root):
    fonts = _fonts(root)
    root.configure(background=COLORS["paper"])
    style = ttk.Style(root)
    if "clam" in style.theme_names():
        style.theme_use("clam")
    style.configure(".", font=fonts["body"], background=COLORS["paper"], foreground=COLORS["ink"])
    for name, colour in [("App", "paper"), ("Card", "paper"), ("Surface", "card")]:
        style.configure(f"{name}.TFrame", background=COLORS[colour])
    if not hasattr(root, "_pixel_theme_images"):
        root._pixel_theme_images = []
        card = _rounded_image(root, COLORS["card"], COLORS["line"], 22)
        style.element_create(
            "Pixel.card", "image", card, border=22, padding=0, sticky="nsew",
            width=48, height=48,
        )
        style.layout("Card.TFrame", [("Pixel.card", {"sticky": "nsew"})])
        _button_style(style, root, "Primary", True, fonts)
        _button_style(style, root, "Secondary", False, fonts)
        field = _rounded_image(root, COLORS["inner"], COLORS["line"], 12)
        focused = _rounded_image(root, COLORS["inner"], COLORS["accent_bright"], 12)
        style.element_create(
            "Pixel.field", "image", field, ("focus", focused), border=12, padding=0, sticky="nsew",
            width=28, height=28,
        )
        style.element_create("Pixel.downarrow", "image", _arrow_image(root))
        style.layout("Setup.TCombobox", [("Pixel.field", {"sticky": "nsew", "children": [
            ("Combobox.padding", {"sticky": "nsew", "children": [
                ("Pixel.downarrow", {"side": "right", "sticky": ""}),
                ("Combobox.textarea", {"sticky": "nsew"})
            ]})
        ]})])
    for name, background, foreground, font in [
        ("Title", "card", "ink", fonts["title"]),
        ("Body", "card", "secondary", fonts["body"]),
        ("Muted", "paper", "muted", fonts["small"]),
        ("CardCaption", "card", "muted", fonts["caption"]),
        ("Result", "card", "ink", fonts["result"]),
        ("PanelTitle", "card", "ink", fonts["heading"]),
    ]:
        style.configure(
            f"{name}.TLabel",
            background=COLORS[background],
            foreground=COLORS[foreground],
            font=font,
        )
    style.configure(
        "Setup.TCombobox", font=fonts["body"], padding=(12, 9), arrowsize=16,
        fieldbackground=COLORS["inner"], background=COLORS["paper"],
        foreground=COLORS["ink"], arrowcolor=COLORS["secondary"],
        bordercolor=COLORS["line"], lightcolor=COLORS["inner"],
        darkcolor=COLORS["inner"], borderwidth=0,
    )
    style.configure("Card.Setup.TCombobox", background=COLORS["card"])
    style.map(
        "Setup.TCombobox",
        foreground=[("disabled", COLORS["muted"]), ("readonly", COLORS["ink"])],
        background=[("readonly", COLORS["paper"]), ("disabled", COLORS["paper"])],
        fieldbackground=[("readonly", COLORS["inner"]), ("disabled", COLORS["inner"])],
        selectbackground=[("readonly", COLORS["inner"])],
        selectforeground=[("readonly", COLORS["ink"])],
        arrowcolor=[("active", COLORS["ink"])],
    )
    style.map(
        "Card.Setup.TCombobox",
        background=[("readonly", COLORS["card"]), ("disabled", COLORS["card"])],
    )
    style.configure(
        "Vertical.TScrollbar", background=COLORS["highlight"],
        troughcolor=COLORS["card"], bordercolor=COLORS["card"],
        lightcolor=COLORS["highlight"], darkcolor=COLORS["highlight"],
        arrowcolor=COLORS["secondary"], borderwidth=0, arrowsize=12,
    )
    style.map("Vertical.TScrollbar", background=[("active", COLORS["muted"])])
    style.configure(
        "Horizontal.TProgressbar",
        background=COLORS["accent_bright"],
        troughcolor=COLORS["paper"],
        borderwidth=0,
        thickness=3,
    )
    for option, value in {
        "font": fonts["body"], "background": COLORS["card"],
        "foreground": COLORS["ink"], "selectBackground": COLORS["selected"],
        "selectForeground": "white", "selectBorderWidth": 0,
    }.items():
        root.option_add(f"*TCombobox*Listbox.{option}", value)
    return fonts


def load_logo(root):
    try:
        from PIL import Image, ImageTk

        with Image.open(Path(__file__).parent / "assets" / "pixel.ico") as source:
            logo = source.convert("RGBA")
            logo.thumbnail((48, 48), Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(logo, master=root)
    except (OSError, ImportError):
        return None


def compact_filename(name, limit=54):
    if len(name) <= limit:
        return name
    return name[: limit - 19] + "…" + name[-18:]
