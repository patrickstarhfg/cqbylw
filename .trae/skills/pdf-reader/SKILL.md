---
name: "pdf-reader"
description: "Reads and extracts text from PDF files. Invoke when the user wants to read, summarize, or analyze PDF content. Uses Python (PyMuPDF) to extract text."
---

# PDF Reader Skill

This skill allows you to read and extract text from PDF files using Python. It is the preferred method for handling PDF content over generic file reading tools.

## How to Use

1.  **Check for PyMuPDF**: Ensure `PyMuPDF` (module name `fitz`) is installed.
    ```bash
    pip install pymupdf
    ```
2.  **Write a Python Script**: Create a temporary script to open the PDF and extract text.
    
    Example script:
    ```python
    import fitz  # PyMuPDF
    import sys

    def read_pdf(file_path, start_page=0, num_pages=5):
        try:
            doc = fitz.open(file_path)
            total_pages = len(doc)
            print(f"Total pages: {total_pages}")
            
            end_page = min(start_page + num_pages, total_pages)
            
            for i in range(start_page, end_page):
                page = doc.load_page(i)
                text = page.get_text()
                print(f"--- Page {i+1} ---")
                print(text)
                print("\n")
                
        except Exception as e:
            print(f"Error reading PDF: {e}")

    if __name__ == "__main__":
        if len(sys.argv) > 1:
            read_pdf(sys.argv[1])
        else:
            print("Please provide a PDF file path.")
    ```
3.  **Run the Script**: Execute the script and capture the output.
4.  **Clean Up**: Delete the temporary script after use.

## Capabilities

-   Extract text from specific pages (e.g., Abstract, Introduction, Conclusion).
-   Get metadata (page count, author, etc.).
-   Search for keywords within the PDF.

## Notes

-   Always use absolute paths for PDF files.
-   Be mindful of output length; extract only relevant pages or use keyword searching if the document is large.
