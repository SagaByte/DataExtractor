# DataExtractor

A simple Termux tool to extract **email addresses, phone numbers, and URLs** from `.txt` and `.pdf` files.

This tool helps you pull and display:

-   **Email addresses**
-   **Phone numbers**
-   **Links (URLs)**

You can choose to save the results to a `results.txt` file.

## Features

-   Extracts emails, phone numbers, and URLs using robust regular expressions.
-   Supports both `.txt` and `.pdf` file formats.
-   Option to save extracted data to a local `results.txt` file.

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
    git clone https://github.com/T6ARB/DataExtractor
    ```

4.  **Navigate to the Tool Directory:**
    ```bash
    cd DataExtractor
    ```

5.  **Install Required Python Libraries:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

With -s/-- save you can save the file if it was Pdf/txt

### Example:
```bash
python extractor.py example.txt -s
```
```bash
python extractor.py example.pdf --save
