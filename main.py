import imaplib
import os
import librosa
import time
import ssl
import smtplib
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.mime.multipart import MIMEMultipart
from credentials import useName, passWord
from imap_tools import MailBox, AND
import whisper

while True:

    imap_url = 'imap.gmail.com'
    my_mail = imaplib.IMAP4_SSL(imap_url)
    my_mail.login(useName, passWord)
    directory = "C:/Users/admin/Documents/audios/"

    email_sender = useName
    email_receiver = useName

    my_mail.select('Inbox')

    with MailBox(imap_url).login(useName, passWord, 'INBOX') as mailbox:
        for msg in mailbox.fetch(criteria=AND(seen=False, from_="noreply@soho66.co.uk"), mark_seen=True):
            for att in msg.attachments:
                print(att.filename, att.content_type)
                if att.filename.lower().endswith('.wav'):
                    with open('C:/Users/admin/Documents/audios/{}'.format(att.filename), 'wb') as f:
                        f.write(att.payload)
                        f.close()

            for filename in os.listdir(directory):

                duration = librosa.get_duration(path=directory + filename)
                if duration < 300 and duration > 0.1:
                    if filename.endswith('.wav'):
                        audio_file = open(directory + filename, "rb")
                        model = whisper.load_model('small')
                        transcript = model.transcribe(audio=directory + filename, fp16=False)
                        text = transcript['text']
                        print(text)
                        print(filename)

                        # send the text with gmail
                        attach = MIMEBase("application", "octet-stream")
                        attach.set_payload(audio_file.read())
                        encoders.encode_base64(attach)
                        attach.add_header('Content-Disposition',f"attachment; filename = {filename}")
                        subject = msg.subject

                        em = MIMEMultipart()
                        em['From'] = email_sender
                        em['To'] = email_receiver
                        em['Subject'] = subject

                        html = """\
                                        <html>
                                          <head></head>
                                          <body>

                                            <p>Hello, there is a new transcription from the voice messages: <br>

                                            <p>{0}</p>

                                            <p>Transcription ended!.</p>
                                            </p>
                                          </body>
                                        </html>
                                        """.format(text)

                        part1 = MIMEText(html, 'html')
                        em.attach(part1)
                        em.attach(attach)

                        context = ssl.create_default_context()

                        server = smtplib.SMTP('smtp.gmail.com', 587)
                        server.ehlo()
                        server.starttls()
                        server.login(email_sender, passWord)
                        server.sendmail(email_sender, email_receiver, em.as_string())
                        server.quit()

                        audio_file.close()


                    else:
                        pass

            # Delele all files in directory
            for filename in os.listdir(directory):
                os.remove(os.path.join(directory, filename))

    mailbox.logout()

    time.sleep(600)