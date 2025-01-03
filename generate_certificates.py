import csv
import os
from pdfrw import PdfReader, PdfWriter

def replace_text_in_pdf(template_path, data, output_path):
    # Read the template PDF
    template_pdf = PdfReader(template_path)
    for page in template_pdf.pages:
        # Access the page's content stream
        if not page.Contents:
            continue

        # Handle multiple content streams (list) or single stream
        content_streams = page.Contents
        if isinstance(content_streams, list):
            content = ''.join(obj.stream for obj in content_streams if hasattr(obj, 'stream'))
        elif hasattr(content_streams, 'stream'):
            content = content_streams.stream
        else:
            continue

        # Ensure content is in string format for replacement
        if isinstance(content, bytes):
            content = content.decode("utf-8")

        # Replace placeholders with actual values
        for key, value in data.items():
            content = content.replace(key, value)

        # Encode the modified content back to binary
        if isinstance(page.Contents, list):
            for obj, updated_content in zip(content_streams, content.splitlines(True)):
                obj.stream = updated_content.encode("utf-8")
        elif hasattr(page.Contents, 'stream'):
            page.Contents.stream = content.encode("utf-8")

    # Save the updated PDF
    PdfWriter(output_path, trailer=template_pdf).write()

def process_csv(template_path, csv_file, output_dir):
    # Ensure the output directory exists
    output_dir = os.path.expanduser(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    with open(csv_file, mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Prepare data for replacement
            data = {
                "[PARTICIPANT]": row["PARTICIPANT"],
                "[WORKSHOP]": row["WORKSHOP"],
                "[AREA]": row["AREA"],
                "[DIRECTOR]": row["DIRECTOR"],
                "[PRESIDENT]": row["PRESIDENT"],
            }

            # Generate the output file path
            participant_name = row["PARTICIPANT"].replace(" ", "_")
            output_path = os.path.join(output_dir, f"{participant_name}.pdf")

            # Replace placeholders and create the certificate
            replace_text_in_pdf(template_path, data, output_path)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate certificates by replacing text in the template.")
    parser.add_argument(
        "template",
        type=str,
        help="Path to the certificate template PDF."
    )
    parser.add_argument(
        "csv",
        type=str,
        help="Path to the CSV file containing participant data."
    )
    parser.add_argument(
        "output_dir",
        type=str,
        help="Directory to save the generated certificates."
    )

    args = parser.parse_args()
    process_csv(args.template, args.csv, args.output_dir)



