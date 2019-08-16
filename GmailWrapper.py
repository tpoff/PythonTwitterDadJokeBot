'''
Wrapper class to connect and use gmail to send and recieve emails,
'''
import smtplib
import imaplib
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# added to avoid errors in pulling too much information at one time.
imaplib._MAXLINE = 10000000

class GmailWrapper:
    def __init__(self, user_email, password):
        self.user_email = user_email
        self.password = password
        self.send_email_server = None
        self.receive_email_server = None
        self.error_message = ""
        self.connect_to_gmail_server()

    def __del__(self):
        # make sure to disconnect from the server
        self.disconnect_from_gmail_server()

    def connect_to_gmail_server(self):
        """
        attempst to connect to the send and recieve email servers using the stored credentials.
        :return:
        """
        if self.send_email_server is None:
            try:
                self.send_email_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                self.send_email_server.ehlo()
                self.send_email_server.login(self.user_email, self.password)
            except Exception as e:
                self.send_email_server = None
                self.error_message = "Could not connect"
        if self.receive_email_server is None:
            try:
                self.receive_email_server = imaplib.IMAP4_SSL('imap.gmail.com')
                self.receive_email_server.login(self.user_email, self.password)
            except Exception as e:
                self.receive_email_server = None
                self.error_message = "Could not connect"

    def disconnect_from_gmail_server(self):
        """
        disconnect the send_email_server and none the send and receive server connections
        :return:
        """
        if self.send_email_server is not None:
            self.send_email_server.close()
        self.send_email_server = None
        self.receive_email_server = None

    def format_email_text(self, recepients, subject, body):
        """
        function to format the email so we can send it,
        converts the recepients, subject and body into a formatted string

        uses MIMEMultipart to format the string

        :param recepients: list of email addresses to send the email to
        :param subject: subject line of the email
        :param body: body o the email
        :return: str formatted email
        """
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = self.user_email
        msg['To'] = ", ".join(recepients)
        message_html = MIMEText("<div>%s</div>" % body, 'html')
        msg.attach(message_html)
        return msg.as_string()

    def send_email(self, recepients, subject, body):
        """
        tries to send an email using the send_email_server
        :param recepients:
        :param subject:
        :param body:
        :return:
        """

        # if we're not connected return false
        if self.send_email_server is None:
            return False

        # format the email message into a single string
        message = self.format_email_text(recepients, subject, body)
        try:  # try to send the email
            self.send_email_server.sendmail(self.user_email, recepients, message, subject)
        except Exception as e:
            # if we fail, store the error and return false
            self.error_message = str(e)
            return False

    def get_email_from_id(self, email_id):
        """
        takes in an email id and returns information relevant to the email in a dict
        :param email_id:
        :return: dict of relevant information on the email including the raw payload
        """
        if self.receive_email_server is not None:
            typ, data = self.receive_email_server.fetch(str(email_id), '(RFC822)')

            for response_part in data:
                if isinstance(response_part, tuple):
                    body = response_part[1].decode("utf-8")
                    msg = email.message_from_string(body)
                    msg['Payload'] = str(body)
                    return msg
        return None

    def get_emails(self, folder="inbox", start_at=0, num_emails=5):
        """
        gets the latest n emails using the receive email server
        :param folder:
        :param start_at:
        :param num_emails:
        :return:
        """
        recieved_emails = []
        if self.receive_email_server is not None:
            self.receive_email_server.select(folder)
            data_type, data = self.receive_email_server.search(None, 'ALL')
            mail_ids = data[0]

            id_list = mail_ids.split()
            latest_email_id = int(id_list[-1])
            start_at = latest_email_id-start_at
            end_at = start_at - num_emails
            if start_at <= 0:
                return []
            if end_at < 0:
                end_at = 0

            for i in range(start_at, end_at, -1):
                recieved_email = self.get_email_from_id(i)
                recieved_emails.append(recieved_email)

        return recieved_emails
