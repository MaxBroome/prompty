# Import necessary libraries
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Define file paths and document ID
CREDENTIALS_FILE = 'creds.json'  # Google Cloud API credentials file
DOCUMENT_ID = '1eTTKXHAICFw65kOWhC1dkXbM2FBctEG_yf-Dp6FXc_Y'  # ID of the Google Docs document

# Authenticate and create the Google Docs API service using service account credentials
credentials = service_account.Credentials.from_service_account_file(
    CREDENTIALS_FILE, scopes=['https://www.googleapis.com/auth/documents.readonly']
)
docs_service = build('docs', 'v1', credentials=credentials)

# Define a function to extract text content from a Google Docs document
def get_text_from_document(document_id):
    document = docs_service.documents().get(documentId=document_id).execute()
    doc_content = document.get('body', {}).get('content', [])

    text = []
    for element in doc_content:
        if 'paragraph' in element:
            paragraph_elements = element.get('paragraph', {}).get('elements', [])
            for elem in paragraph_elements:
                text_run = elem.get('textRun')
                if text_run:
                    text.append(text_run.get('content', ''))
        elif 'table' in element:
            # Process tables
            table = element.get('table', {})
            for row in table.get('tableRows', []):
                for cell in row.get('tableCells', []):
                    for cell_content in cell.get('content', []):
                        for elem in cell_content.get('paragraph', {}).get('elements', []):
                            text_run = elem.get('textRun')
                            if text_run:
                                text.append(text_run.get('content', ''))

    return '\n'.join(text).strip()  # Strip to remove leading/trailing whitespace

# [Previous Python script code]

if __name__ == '__main__':
    # Get text content from the specified Google Docs document
    document_text = get_text_from_document(DOCUMENT_ID)

    # Split the text into blocks based on 2 or more consecutive line breaks
    text_blocks = [block.strip() for block in document_text.split('\n\n') if block.strip()]

    # Rejoin the text blocks with at least two line breaks in between
    formatted_text = '<br><br>'.join(text_blocks)

    # Now let's replace the content in the HTML file
    html_file_path = 'web-interface/index.html'  # Path to your HTML file
    with open(html_file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()

    # Replace the content within the <div class="teleprompter" id="teleprompter">...</div>
    import re
    new_html_content = re.sub(
        r'(<div class="teleprompter" id="teleprompter" role="none" aria-multiline="true" aria-label="TelePrompter Text" contenteditable="false">).*?(</div>)',
        r'\1' + formatted_text + r'\2',
        html_content,
        flags=re.DOTALL
    )

    # Write the modified HTML content back to the file
    with open(html_file_path, 'w', encoding='utf-8') as file:
        file.write(new_html_content)
