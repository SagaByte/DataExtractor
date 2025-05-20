import re
import argparse
import os
import asyncio # Import asyncio for async functions

# Try to import PyPDF2, provide error message if not installed
try:
    from PyPDF2 import PdfReader
except ImportError:
    print("PyPDF2 is not installed. Please install it using: pip install PyPDF2")
    exit(1) # Exit if essential library is missing

# Try to import telegram, provide error message if not installed
try:
    from telegram import Bot
    from telegram.error import TelegramError
    # This is to handle 'RuntimeWarning: coroutine 'Bot.__init__' was never awaited'
    # if Bot is not properly awaited, though it's typically fine for simple usage here.
except ImportError:
    print("python-telegram-bot is not installed. Telegram functionality will be disabled.")
    Bot = None # Disable Telegram functionality if the library is not present

# This is a common workaround for running asyncio in environments where an event loop might already be running
# or for Jupyter notebooks. It makes `asyncio.run()` more robust.
try:
    import nest_asyncio
    nest_asyncio.apply()
except ImportError:
    # nest_asyncio is not strictly required but helps with certain environments.
    # If it's not installed, the tool will still work, but might hit RuntimeError in some cases.
    pass

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

async def send_to_telegram(token, chat_id, emails, phones, urls):
    """
    Sends the extracted data to a Telegram chat.
    """
    if not Bot:
        print("Telegram functionality is not available because 'python-telegram-bot' is not installed.")
        return

    # Ensure token and chat_id are valid
    if not token or not chat_id:
        print("Telegram token and chat ID must be provided to send results to Telegram.")
        return

    bot = Bot(token=token)
    message = "--- Extracted Data ---\n\n"

    message += "Emails:\n"
    if emails:
        for email in sorted(list(set(emails))):
            message += f"- {email}\n"
    else:
        message += "No emails found.\n"

    message += "\nPhone Numbers:\n"
    if phones:
        for phone in sorted(list(set(phones))):
            message += f"- {phone}\n"
    else:
        message += "No phone numbers found.\n"

    message += "\nURLs:\n"
    if urls:
        for url in sorted(list(set(urls))):
            message += f"- {url}\n"
    else:
        message += "No URLs found.\n"

    try:
        # Telegram messages have a character limit (4096 characters).
        # We should split the message if it's too long.
        if len(message) > 4096:
            print("Warning: Telegram message is too long. Splitting into multiple messages.")
            chunks = [message[i:i+4000] for i in range(0, len(message), 4000)] # Split into chunks
            for i, chunk in enumerate(chunks):
                await bot.send_message(chat_id=chat_id, text=f"Part {i+1}:\n{chunk}")
                await asyncio.sleep(0.5) # Small delay to avoid hitting rate limits
        else:
            await bot.send_message(chat_id=chat_id, text=message)
        print("Results sent to Telegram successfully!")
    except TelegramError as e:
        print(f"Error sending to Telegram: {e}")
        if "Bad Request: chat not found" in str(e) or "Forbidden: bot was blocked by the user" in str(e):
            print("Please ensure the chat ID is correct and you have started a conversation with the bot.")
        elif "Unauthorized" in str(e):
            print("Please check if your Telegram Bot API token is correct.")
    except Exception as e:
        print(f"An unexpected error occurred while sending to Telegram: {e}")

async def main():
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
    parser.add_argument(
        "-t", "--telegram", action="store_true",
        help="Send results to Telegram.\nRequires --telegram_token and --telegram_chat_id."
    )
    parser.add_argument(
        "--telegram_token",
        help="Your Telegram Bot API Token (e.g., from BotFather). Required with -t."
    )
    parser.add_argument(
        "--telegram_chat_id",
        help="Your Telegram Chat ID (the ID of the chat you want to send messages to). Required with -t."
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

    if args.telegram:
        if not args.telegram_token or not args.telegram_chat_id:
            print("Error: --telegram_token and --telegram_chat_id are required for Telegram functionality.")
        else:
            await send_to_telegram(args.telegram_token, args.telegram_chat_id, emails, phones, urls)

if __name__ == "__main__":
    asyncio.run(main())
