import os
import requests
import difflib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re

# Access credentials from environment variables
gmail_user = os.getenv('GMAIL_USERNAME')
gmail_password = os.getenv('GMAIL_APP_PASSWORD')

# URL to monitor
url = "https://museum-tickets.nintendo.com/en/calendar"
# File to store the last fetched content of the webpage
content_file = "webpage_content.txt"

# Patterns to ignore in the content
IGNORE_PATTERNS = [r'<meta name="csrf-token" content="[^"]*">']

# Function to filter out unwanted patterns from content
def filter_content(content, patterns):
    for pattern in patterns:
        content = re.sub(pattern, '<ignored>', content)
    return content

# Function to send email alert
def send_email_alert(subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = gmail_user
        msg['To'] = "punchyycovet@gmail.com"
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(gmail_user, gmail_password)
            server.sendmail(gmail_user, msg['To'], msg.as_string())

        print("Email sent successfully")

    except Exception as e:
        print(f"Failed to send email: {e}")

# Function to fetch webpage content
def fetch_webpage_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error if the request failed
        return response.text
    except Exception as e:
        print(f"Failed to fetch webpage: {e}")
        return None

# Function to check if the webpage has changed
def check_for_changes():
    new_content = fetch_webpage_content(url)
    if new_content is None:
        return

    # Filter out unwanted patterns
    new_content_filtered = filter_content(new_content, IGNORE_PATTERNS)

    # Check if the content file exists, indicating a previous run
    if os.path.exists(content_file):
        # Read the last saved content
        with open(content_file, 'r') as file:
            old_content = file.read()

        # Filter out unwanted patterns from old content
        old_content_filtered = filter_content(old_content, IGNORE_PATTERNS)

        # Compare the filtered old and new content
        if new_content_filtered != old_content_filtered:
            print("Change detected on the webpage.")
            
            # Find differences between filtered old and new content
            diff = difflib.unified_diff(old_content_filtered.splitlines(), new_content_filtered.splitlines(), lineterm='')
            diff_text = '\n'.join(diff)

            # Send an email with the specific changes
            send_email_alert("Webpage Change Detected", f"The webpage at {url} has changed.\n\nChanges:\n{diff_text}")
    else:
        print("No previous content found. Saving initial content.")

    # Save the new content, whether it's the first run or after detecting a change
    with open(content_file, 'w') as file:
        file.write(new_content)

# Run the check
check_for_changes()
