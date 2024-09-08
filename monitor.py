import os
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Access credentials from environment variables
gmail_user = os.getenv('GMAIL_USERNAME')
gmail_password = os.getenv('GMAIL_APP_PASSWORD')

# URL to monitor
url = "https://museum-tickets.nintendo.com/en/calendar"
# File to store the last fetched content of the webpage
content_file = "webpage_content.txt"

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

    # Check if the content file exists, indicating a previous run
    if os.path.exists(content_file):
        # Read the last saved content
        with open(content_file, 'r') as file:
            old_content = file.read()

        # Compare the old and new content
        if new_content != old_content:
            print("Change detected on the webpage.")
            send_email_alert("Webpage Change Detected", f"The webpage at {url} has changed.")
    else:
        print("No previous content found. Saving initial content.")

    # Save the new content, whether it's the first run or after detecting a change
    with open(content_file, 'w') as file:
        file.write(new_content)

# Run the check
check_for_changes()
