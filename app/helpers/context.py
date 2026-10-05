from __future__ import annotations

from dataclasses import asdict, dataclass

PLATFORMS = {"both": "Scala & Dise", "scala": "Scala only", "dise": "Dise only"}
SCALA_ENGINES = {
    "unknown": "Unknown",
    "win32": "Windows 32-bit",
    "win64": "Windows 64-bit",
    "other": "Other / embedded",
}
DISE_VERSIONS = {
    "general": "General PC compatibility (One and Premium / Lite)",
    "unknown": "Unknown",
    "one": "Dise One / current",
    "legacy": "Premium & Lite",
}
DISE_PLAYERS = {
    "unknown": "Unknown",
    "pc": "External PC",
    "soc": "SoC (Generic)",
    "samsung": "Samsung SoC (Tizen)",
    "lg": "LG SoC (webOS)",
    "other": "Other",
}
PDF_WORKFLOWS = {
    "unknown": "Unknown / direct upload",
    "composer": "Composer PDF import",
}


@dataclass(frozen=True)
class PlaybackContext:
    platform: str = "both"
    scala_engine: str = "unknown"
    dise_version: str = "unknown"
    dise_player: str = "unknown"
    canvas_width: int | None = None
    canvas_height: int | None = None
    pdf_workflow: str = "unknown"
    simultaneous_videos: bool = False

    def __post_init__(self):
        for key, choices in (
            ("platform", PLATFORMS),
            ("scala_engine", SCALA_ENGINES),
            ("dise_version", DISE_VERSIONS),
            ("dise_player", DISE_PLAYERS),
            ("pdf_workflow", PDF_WORKFLOWS),
        ):
            if getattr(self, key) not in choices:
                raise ValueError(f"Choose a valid {key.replace('_', ' ')}.")
        if (self.canvas_width is None) != (self.canvas_height is None):
            raise ValueError("Enter both the content width and height.")
        for dimension in (self.canvas_width, self.canvas_height):
            if dimension is not None and (
                type(dimension) is not int or not 1 <= dimension <= 65535
            ):
                raise ValueError(
                    "Content dimensions must be whole numbers from 1 to 65535."
                )

    def includes(self, platform: str) -> bool:
        return self.platform in ("both", platform)

    def to_dict(self) -> dict:
        return asdict(self)

    def summary(self) -> str:
        parts = [PLATFORMS[self.platform]]
        if self.includes("scala"):
            parts.append("Scala: " + SCALA_ENGINES[self.scala_engine])
        if self.includes("dise"):
            parts.append(
                "Dise: "
                + DISE_VERSIONS[self.dise_version]
                + "; "
                + DISE_PLAYERS[self.dise_player]
            )
        if self.canvas_width is not None:
            parts.append(f"Content size: {self.canvas_width} x {self.canvas_height}")
        else:
            parts.append("Content size: unknown / mixed")
        if self.pdf_workflow == "composer":
            parts.append("PDF: Composer import")
        if self.simultaneous_videos:
            parts.append("Multiple videos playing together")
        return " | ".join(parts)
