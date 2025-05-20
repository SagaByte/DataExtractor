import re
import argparse
import os

# Try to import PyPDF2, provide error message if not installed
try:
    from PyPDF2 import PdfReader
except ImportError:
    print("PyPDF2 is not installed. Please install it using: pip install PyPDF2")
    exit(1) # Exit if essential library is missing

def extract_from_text(text):
    """
    Extracts emails, phone numbers, and URLs from a given text.
    """
    emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    # This regex attempts to catch various phone number formats
    phones = re.findall(r'(?:\+?\d{1,3}[-.●\s]?)?\(?\d{3}\)?[-.●\s]?\d{3}[-.●\s]?\d{4}(?:\s*x\d+)?', text)
    # This regex for URLs covers http/https and common domain characters
    urls = re.findall(r'https?://(?:www\.)?[a-zA-Z0-9./-]+(?:/[a-zA-Z0-9./-]+)*\b', text)
    return emails, phones, urls

def extract_from_pdf(pdf_path):
    """
    Extracts text from a PDF file and then calls extract_from_text to find data.
    """
    all_text = ""
    try:
        with open(pdf_path, 'rb') as f:
            reader = PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text: # Ensure text is not None
                    all_text += page_text + "\n" # Add newline for better separation between pages
    except Exception as e:
        print(f"Error reading PDF file {pdf_path}: {e}")
        return [], [], [] # Return empty lists on error
    return extract_from_text(all_text)

def save_results(filename, emails, phones, urls):
    """
    Saves the extracted emails, phone numbers, and URLs to a specified file.
    """
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("--- Extracted Emails ---\n")
        if emails:
            for email in sorted(list(set(emails))): # Use set for uniqueness, convert to list, sort for consistency
                f.write(f"- {email}\n")
        else:
            f.write("No emails found.\n")

        f.write("\n--- Extracted Phone Numbers ---\n")
        if phones:
            for phone in sorted(list(set(phones))):
                f.write(f"- {phone}\n")
        else:
            f.write("No phone numbers found.\n")

        f.write("\n--- Extracted URLs ---\n")
        if urls:
            for url in sorted(list(set(urls))):
                f.write(f"- {url}\n")
        else:
            f.write("No URLs found.\n")
    print(f"Results saved to {filename}")

def main():
    """
    Main function to parse arguments and run the extraction process.
    """
    parser = argparse.ArgumentParser(
        description="Extractor Tool: Extract emails, phone numbers, and URLs from text and PDF files.",
        formatter_class=argparse.RawTextHelpFormatter # Preserve newlines in help
    )
    parser.add_argument("file", help="Path to the .txt or .pdf file.")
    parser.add_argument(
        "-s", "--save", action="store_true",
        help="Save results to results.txt in the current directory."
    )

    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"Error: File not found at {args.file}")
        return

    emails, phones, urls = [], [], []

    if args.file.lower().endswith(".txt"):
        try:
            with open(args.file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                emails, phones, urls = extract_from_text(content)
        except Exception as e:
            print(f"Error reading text file {args.file}: {e}")
            return
    elif args.file.lower().endswith(".pdf"):
        emails, phones, urls = extract_from_pdf(args.file)
    else:
        print("Unsupported file type. Please provide a .txt or .pdf file.")
        return

    print("\n--- Extracted Emails ---")
    if emails:
        for email in sorted(list(set(emails))):
            print(f"- {email}")
    else:
        print("No emails found.")

    print("\n--- Extracted Phone Numbers ---")
    if phones:
        for phone in sorted(list(set(phones))):
            print(f"- {phone}")
    else:
        print("No phone numbers found.")

    print("\n--- Extracted URLs ---")
    if urls:
        for url in sorted(list(set(urls))):
            print(f"- {url}")
    else:
        print("No URLs found.")

    if args.save:
        save_results("results.txt", emails, phones, urls)

if __name__ == "__main__":
    main()
