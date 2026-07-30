
import os
import sys
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
from pathlib import Path

from PIL import Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,
    Image as RLImage
)


APP_TITLE = "Marble Work Report Generator"
DEFAULT_LOGO = Path(__file__).with_name("marble_logo.png")


def safe_float(value: str) -> float:
    try:
        return float(value.strip())
    except (ValueError, AttributeError):
        raise ValueError(f"Invalid hours value: {value!r}")


def format_hours(value: float) -> str:
    if float(value).is_integer():
        return str(int(value))
    return f"{value:.2f}".rstrip("0").rstrip(".")


def fit_image(path: str, max_width: float, max_height: float) -> RLImage:
    with Image.open(path) as img:
        width, height = img.size
    scale = min(max_width / width, max_height / height)
    return RLImage(path, width=width * scale, height=height * scale)


def draw_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#667085"))
    canvas.drawRightString(
        landscape(A4)[0] - 15 * mm,
        8 * mm,
        f"Page {doc.page}"
    )
    canvas.restoreState()


def generate_report(output_path: str, month: str, rows: list[dict], logo_path: str):
    page_width, _ = landscape(A4)

    doc = SimpleDocTemplate(
        output_path,
        pagesize=landscape(A4),
        leftMargin=12 * mm,
        rightMargin=12 * mm,
        topMargin=12 * mm,
        bottomMargin=14 * mm,
        title=f"Yonatan Green report - {month}",
        author="Yonatan Green",
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=23,
        leading=27,
        textColor=colors.white,
        alignment=TA_LEFT,
        spaceAfter=0,
    )
    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#CFEAF3"),
        alignment=TA_LEFT,
    )
    header_style = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=11,
        textColor=colors.white,
        alignment=TA_CENTER,
    )
    product_style = ParagraphStyle(
        "Product",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#101828"),
        alignment=TA_LEFT,
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#344054"),
        alignment=TA_LEFT,
    )
    hours_style = ParagraphStyle(
        "Hours",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=13,
        textColor=colors.HexColor("#101828"),
        alignment=TA_CENTER,
    )
    total_style = ParagraphStyle(
        "Total",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=14,
        textColor=colors.white,
        alignment=TA_RIGHT,
    )

    story = []

    logo_cell = ""
    if logo_path and os.path.exists(logo_path):
        try:
            logo_cell = fit_image(logo_path, 46 * mm, 30 * mm)
        except Exception:
            logo_cell = ""

    header_text = [
        Paragraph(f"Yonatan Green report - {month}", title_style),
        Spacer(1, 2 * mm),
        Paragraph("Freelance development work for Marble", subtitle_style),
    ]
    header = Table(
        [[logo_cell, header_text]],
        colWidths=[55 * mm, page_width - 24 * mm - 55 * mm],
        rowHeights=[36 * mm],
    )
    header.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#102A36")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (0, 0), 4 * mm),
        ("RIGHTPADDING", (0, 0), (0, 0), 4 * mm),
        ("LEFTPADDING", (1, 0), (1, 0), 6 * mm),
        ("RIGHTPADDING", (1, 0), (1, 0), 6 * mm),
        ("TOPPADDING", (0, 0), (-1, -1), 3 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3 * mm),
        ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#4FB9D1")),
    ]))
    story.extend([header, Spacer(1, 7 * mm)])

    col_widths = [48 * mm, 43 * mm, 132 * mm, 26 * mm]
    table_data = [[
        Paragraph("Feature / Product", header_style),
        Paragraph("Image", header_style),
        Paragraph("Short description", header_style),
        Paragraph("Hours", header_style),
    ]]

    total_hours = 0.0
    for row in rows:
        hours = safe_float(str(row.get("hours", "0")))
        total_hours += hours

        image_cell = Paragraph("No image", body_style)
        image_path = row.get("image", "")
        if image_path and os.path.exists(image_path):
            try:
                image_cell = fit_image(image_path, 36 * mm, 24 * mm)
            except Exception:
                image_cell = Paragraph("Could not load image", body_style)

        table_data.append([
            Paragraph(str(row.get("title", "")).replace("\n", "<br/>"), product_style),
            image_cell,
            Paragraph(str(row.get("description", "")).replace("\n", "<br/>"), body_style),
            Paragraph(format_hours(hours), hours_style),
        ])

    report_table = Table(
        table_data,
        colWidths=col_widths,
        repeatRows=1,
        hAlign="LEFT",
    )

    style_commands = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#147D92")),
        ("BOX", (0, 0), (-1, -1), 0.7, colors.HexColor("#B8C9D0")),
        ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D0D5DD")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (1, 1), (1, -1), "CENTER"),
        ("ALIGN", (3, 1), (3, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, 0), 3.5 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 3.5 * mm),
        ("TOPPADDING", (0, 1), (-1, -1), 3 * mm),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 3 * mm),
        ("LEFTPADDING", (0, 0), (-1, -1), 3 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3 * mm),
    ]
    for i in range(1, len(table_data)):
        background = "#F8FAFC" if i % 2 == 1 else "#EEF6F8"
        style_commands.append(
            ("BACKGROUND", (0, i), (-1, i), colors.HexColor(background))
        )

    report_table.setStyle(TableStyle(style_commands))
    story.append(report_table)
    story.append(Spacer(1, 7 * mm))

    total_box = Table(
        [[Paragraph("TOTAL HOURS", total_style),
          Paragraph(format_hours(total_hours), total_style)]],
        colWidths=[page_width - 24 * mm - 38 * mm, 38 * mm],
        hAlign="RIGHT",
    )
    total_box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#102A36")),
        ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#4FB9D1")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
        ("TOPPADDING", (0, 0), (-1, -1), 4 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4 * mm),
        ("LEFTPADDING", (0, 0), (-1, -1), 4 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4 * mm),
    ]))
    story.append(total_box)

    doc.build(story, onFirstPage=draw_page_number, onLaterPages=draw_page_number)


class WorkRow:
    def __init__(self, parent, remove_callback, index: int):
        self.frame = ttk.LabelFrame(parent, text=f"Entry {index}", padding=8)
        self.remove_callback = remove_callback
        self.title_var = tk.StringVar()
        self.image_var = tk.StringVar()
        self.hours_var = tk.StringVar()

        ttk.Label(self.frame, text="Feature / product title").grid(row=0, column=0, sticky="w")
        ttk.Entry(self.frame, textvariable=self.title_var, width=35).grid(
            row=1, column=0, padx=(0, 8), sticky="ew"
        )

        ttk.Label(self.frame, text="Image").grid(row=0, column=1, sticky="w")
        image_frame = ttk.Frame(self.frame)
        image_frame.grid(row=1, column=1, padx=(0, 8), sticky="ew")
        ttk.Entry(image_frame, textvariable=self.image_var, width=42).pack(
            side="left", fill="x", expand=True
        )
        ttk.Button(image_frame, text="Browse", command=self.choose_image).pack(
            side="left", padx=(5, 0)
        )

        ttk.Label(self.frame, text="Hours worked").grid(row=0, column=2, sticky="w")
        ttk.Entry(self.frame, textvariable=self.hours_var, width=12).grid(
            row=1, column=2, padx=(0, 8), sticky="ew"
        )

        ttk.Button(
            self.frame, text="Remove", command=lambda: self.remove_callback(self)
        ).grid(row=1, column=3, sticky="e")

        ttk.Label(self.frame, text="Short description").grid(
            row=2, column=0, columnspan=4, sticky="w", pady=(8, 0)
        )
        self.description_text = tk.Text(self.frame, height=4, wrap="word")
        self.description_text.grid(row=3, column=0, columnspan=4, sticky="nsew")

        self.frame.columnconfigure(0, weight=2)
        self.frame.columnconfigure(1, weight=3)
        self.frame.columnconfigure(2, weight=1)

    def choose_image(self):
        path = filedialog.askopenfilename(
            title="Choose entry image",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.webp"),
                ("All files", "*.*"),
            ],
        )
        if path:
            self.image_var.set(path)

    def get_data(self):
        return {
            "title": self.title_var.get().strip(),
            "image": self.image_var.get().strip(),
            "description": self.description_text.get("1.0", "end").strip(),
            "hours": self.hours_var.get().strip(),
        }

    def set_data(self, data):
        self.title_var.set(data.get("title", ""))
        self.image_var.set(data.get("image", ""))
        self.hours_var.set(str(data.get("hours", "")))
        self.description_text.delete("1.0", "end")
        self.description_text.insert("1.0", data.get("description", ""))


class ReportApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1120x780")
        self.minsize(900, 600)

        self.month_var = tk.StringVar(value=datetime.now().strftime("%B %Y"))
        self.logo_var = tk.StringVar(
            value=str(DEFAULT_LOGO) if DEFAULT_LOGO.exists() else ""
        )
        self.rows = []

        self._build_ui()
        self.add_row()

    def _build_ui(self):
        top = ttk.Frame(self, padding=12)
        top.pack(fill="x")

        ttk.Label(top, text="Month").grid(row=0, column=0, sticky="w")
        ttk.Entry(top, textvariable=self.month_var, width=28).grid(
            row=1, column=0, padx=(0, 12), sticky="w"
        )

        ttk.Label(top, text="Marble logo").grid(row=0, column=1, sticky="w")
        ttk.Entry(top, textvariable=self.logo_var, width=60).grid(
            row=1, column=1, sticky="ew"
        )
        ttk.Button(top, text="Browse", command=self.choose_logo).grid(
            row=1, column=2, padx=(6, 0)
        )
        top.columnconfigure(1, weight=1)

        toolbar = ttk.Frame(self, padding=(12, 0, 12, 10))
        toolbar.pack(fill="x")
        ttk.Button(toolbar, text="+ Add entry", command=self.add_row).pack(side="left")
        ttk.Button(toolbar, text="Save project", command=self.save_project).pack(
            side="left", padx=6
        )
        ttk.Button(toolbar, text="Load project", command=self.load_project).pack(side="left")
        ttk.Button(toolbar, text="Generate PDF", command=self.generate_pdf).pack(side="right")

        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.scroll_frame = ttk.Frame(self.canvas, padding=(12, 0, 12, 12))

        self.scroll_frame.bind(
            "<Configure>",
            lambda event: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )
        self.canvas_window = self.canvas.create_window(
            (0, 0), window=self.scroll_frame, anchor="nw"
        )
        self.canvas.bind(
            "<Configure>",
            lambda event: self.canvas.itemconfigure(self.canvas_window, width=event.width),
        )
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def choose_logo(self):
        path = filedialog.askopenfilename(
            title="Choose Marble logo",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.webp"),
                ("All files", "*.*"),
            ],
        )
        if path:
            self.logo_var.set(path)

    def add_row(self, data=None):
        row = WorkRow(self.scroll_frame, self.remove_row, len(self.rows) + 1)
        row.frame.pack(fill="x", pady=(0, 10))
        self.rows.append(row)
        if data:
            row.set_data(data)

    def remove_row(self, row):
        if len(self.rows) == 1:
            messagebox.showinfo("Cannot remove", "The report needs at least one entry.")
            return
        row.frame.destroy()
        self.rows.remove(row)
        self.refresh_row_titles()

    def refresh_row_titles(self):
        for i, row in enumerate(self.rows, start=1):
            row.frame.configure(text=f"Entry {i}")

    def validate_rows(self):
        output = []
        for i, row in enumerate(self.rows, start=1):
            data = row.get_data()
            if not data["title"]:
                raise ValueError(f"Entry {i}: title is required.")
            if not data["description"]:
                raise ValueError(f"Entry {i}: description is required.")
            hours = safe_float(data["hours"])
            if hours < 0:
                raise ValueError(f"Entry {i}: hours cannot be negative.")
            data["hours"] = hours
            output.append(data)
        return output

    def generate_pdf(self):
        try:
            month = self.month_var.get().strip()
            if not month:
                raise ValueError("Month is required.")
            rows = self.validate_rows()
            default_name = f"Yonatan Green report - {month}.pdf"
            output_path = filedialog.asksaveasfilename(
                title="Save PDF report",
                initialfile=default_name,
                defaultextension=".pdf",
                filetypes=[("PDF file", "*.pdf")],
            )
            if not output_path:
                return

            generate_report(
                output_path=output_path,
                month=month,
                rows=rows,
                logo_path=self.logo_var.get().strip(),
            )
            messagebox.showinfo("Report created", f"PDF created successfully:\n{output_path}")
        except Exception as exc:
            messagebox.showerror("Could not create report", str(exc))

    def save_project(self):
        try:
            data = {
                "month": self.month_var.get().strip(),
                "logo": self.logo_var.get().strip(),
                "rows": [row.get_data() for row in self.rows],
            }
            path = filedialog.asksaveasfilename(
                title="Save report project",
                defaultextension=".json",
                filetypes=[("Report project", "*.json")],
            )
            if not path:
                return
            with open(path, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=2)
            messagebox.showinfo("Saved", "Project saved successfully.")
        except Exception as exc:
            messagebox.showerror("Could not save project", str(exc))

    def load_project(self):
        try:
            path = filedialog.askopenfilename(
                title="Load report project",
                filetypes=[("Report project", "*.json"), ("All files", "*.*")],
            )
            if not path:
                return
            with open(path, "r", encoding="utf-8") as file:
                data = json.load(file)

            for row in self.rows:
                row.frame.destroy()
            self.rows.clear()

            self.month_var.set(data.get("month", ""))
            self.logo_var.set(data.get("logo", ""))
            for row_data in data.get("rows", []):
                self.add_row(row_data)
            if not self.rows:
                self.add_row()
        except Exception as exc:
            messagebox.showerror("Could not load project", str(exc))


if __name__ == "__main__":
    ReportApp().mainloop()
