from __future__ import print_function
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from email.mime.text import MIMEText
from googleapiclient.errors import HttpError
import base64
from main import get_listings

SCOPES = ['https://www.googleapis.com/auth/gmail.compose']
email_from = "rachelhadadcoding@gmail.com"
email_to = "rachelcmarsh@gmail.com"
# stockton.berry12@gmail.com
email_subject = "New Potentials"

listings_dict = get_listings()
if not listings_dict:
    email_message = "No new potential properties found today."
else:
    email_message = ""
    for n in range(len(listings_dict)):
        email_message += f"<img src={listings_dict[n]['img']} width=25% height=25%>" \
                         f"<br><b>{listings_dict[n]['street']}, {listings_dict[n]['city']}, {listings_dict[n]['state']} {listings_dict[n]['zip']}</b>" \
                         f"<br>{listings_dict[n]['url']}" \
                         f"<br><li> MLS Number: {listings_dict[n]['mls']}" \
                         f"<li>List Price: {listings_dict[n]['price']}" \
                         f"<li>Bedrooms: {listings_dict[n]['bedrooms']}" \
                         f"<li>Bathrooms: {listings_dict[n]['bathrooms']}" \
                         f"<li>Acres: {listings_dict[n]['acres']}" \
                         f"<li>Approx. Sq. Ft.: {listings_dict[n]['sqft']}" \
                         f"<li>Approx. Price per Sq. Ft.: ${listings_dict[n]['ppsqft']}" \
                         f"<li>Does it include any 'flagged phrases' in description?: {listings_dict[n]['flag_phrase']}<br><br><br>"


def main():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    service = build('gmail', 'v1', credentials=creds)
    return service


def create_message(sender, to, subject, message_text):
    message = MIMEText(message_text, 'html')
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    return {'raw': base64.urlsafe_b64encode(message.as_string().encode()).decode()}


def send_message(service, user_id, message):
    try:
        message = (service.users().messages().send(userId=user_id, body=message)
                   .execute())
        print('Message Id: %s' % message['id'])
        return message
    except HttpError as error:
        print(f'An error occurred: {error}')


created_message = create_message(sender=email_from, to=email_to, subject=email_subject, message_text=email_message)
service = main()
send_message(service=service, user_id="me", message=created_message)

if __name__ == '__main__':
    main()
