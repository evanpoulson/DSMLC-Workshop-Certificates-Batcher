import csv
import argparse
from pathlib import Path
from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader, PdfWriter

# Define positions for placeholders
placeholder_positions = {
    "[PARTICIPANT]": (150, 500),
    "[WORKSHOP]": (150, 450),
    "[AREA]": (150, 400),
    "[DIRECTOR]": (150, 200),
    "[PRESIDENT]": (350, 200)
}

def create_overlay(data):
    overlay_path = "overlay.pdf"
    c = canvas.Canvas(overlay_path)
    for key, value in data.items():
        if key in placeholder_positions:
            x, y = placeholder_positions[key]
            c.drawString(x, y, value)
    c.save()
    return overlay_path

def merge_pdfs(template_path, overlay_path, output_path):
    template_pdf = PdfReader(template_path)
    overlay_pdf = PdfReader(overlay_path)
    writer = PdfWriter()

    for page in template_pdf.pages:
        page.merge_page(overlay_pdf.pages[0])
        writer.add_page(page)

    with open(output_path, "wb") as output_file:
        writer.write(output_file)

def process_csv(template_path, csv_file, output_dir):
    Path(output_dir).mkdir(parents=True, exist_ok=True)  # Ensure the output directory exists
    with open(csv_file, mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            participant_name = row["Participant"]
            output_path = Path(output_dir) / f"{participant_name.replace(' ', '_')}_certificate.pdf"

            data = {
                "[PARTICIPANT]": row["Participant"],
                "[WORKSHOP]": row["Workshop"],
                "[AREA]": row["Area"],
                "[DIRECTOR]": row["Director"],
                "[PRESIDENT]": row["President"]
            }

            overlay_path = create_overlay(data)
            merge_pdfs(template_path, overlay_path, str(output_path))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate certificates with placeholders filled.")
    parser.add_argument(
        "template",
        type=str,
        help="Path to the certificate template (e.g., DSMLC_Workshop_Certificate_DARK.pdf)"
    )
    parser.add_argument(
        "csv",
        type=str,
        help="Path to the CSV file containing the participant data."
    )
    parser.add_argument(
        "output_dir",
        type=str,
        help="Directory to save the generated certificates."
    )

    args = parser.parse_args()

    process_csv(args.template, args.csv, args.output_dir)
