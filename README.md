# Extractor Tool for Termux

An easy-to-use tool for Termux to extract important data from text (.txt) and PDF (.pdf) files. This tool helps you pull and display:

-   **Email addresses**
-   **Phone numbers**
-   **Links (URLs)**

You can choose to save the results to a `results.txt` file or send them directly to your Telegram account.

## Features

-   Extracts emails, phone numbers, and URLs using robust regular expressions.
-   Supports both `.txt` and `.pdf` file formats.
-   Option to save extracted data to a local `results.txt` file.
-   Option to send extracted data directly to a Telegram chat.
-   Handles large Telegram messages by splitting them into chunks.

## Installation on Termux

1.  **Update Termux:**
    ```bash
    pkg update && pkg upgrade -y
    ```

2.  **Install Python and Git:**
    ```bash
    pkg install python git -y
    ```

3.  **Clone the Repository:**
    ```bash
    git clone 
    https://github.com/SagaByte/DataExtractor
    ```
    **(Replace `YOUR_USERNAME` with your actual GitHub username where you uploaded the tool)**

4.  **Navigate to the Tool Directory:**
    ```bash
    cd ExtractorTool
    ```

5.  **Install Required Python Libraries:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

### Basic Usage

To extract data and display it in the terminal:

```bash
python extractor.py <file_path>
