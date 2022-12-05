from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env

from_email = os.getenv('FROM')
password = os.getenv('GMAIL_PASSWORD')


class Certificate:
    def __init__(self, name, title, date, instructor, template):
        self.name = name
        self.title = title
        self.date = date
        self.instructor = instructor
        self.template = template


width = 2000
height = 1545


def generate_certificate(cert):
    im = Image.open(cert.template)
    d = ImageDraw.Draw(im)
    text_color = (0, 0, 0)
    font = ImageFont.truetype('DejaVuSans.ttf', 100)
    # d.text(location, name, fill=text_color, font=font)
    d.text((width/2, (height/2-125)), cert.name,
           fill=text_color, font=font, anchor="mm")
    font = ImageFont.truetype('DejaVuSans.ttf', 60)
    d.text((width/2, (height/2+100)), cert.title,
           fill=text_color, font=font, anchor="mm")
    font = ImageFont.truetype('DejaVuSans.ttf', 50)
    d.text((width/2-385, (height/2+300)), cert.date,
           fill=text_color, font=font, anchor="mm")
    d.text((width/2+385, (height/2+300)), cert.instructor,
           fill=text_color, font=font, anchor="mm")
    filename = f'{cert.title}_{cert.name}.pdf'
    im.save(filename)
    return filename


def send_email(cert, email, cert_path, from_email, password):
    fromaddr = from_email
    toaddr = email
    # instance of MIMEMultipart
    msg = MIMEMultipart()
    # storing the senders email address
    msg['From'] = fromaddr
    # storing the receivers email address
    msg['To'] = toaddr
    # storing the subject
    msg['Subject'] = f"{cert.title} Certificate of Completion"
    # string to store the body of the mail
    body = f"Hey, {cert.name}, attached is your {cert.title} Certificate of Completion"
    # attach the body with the msg instance
    msg.attach(MIMEText(body, 'plain'))
    # open the file to be sent
    filename = cert_path
    attachment = open(filename, "rb")
    # instance of MIMEBase and named as p
    p = MIMEBase('application', 'octet-stream')
    # To change the payload into encoded form
    p.set_payload((attachment).read())
    # encode into base64
    encoders.encode_base64(p)
    p.add_header('Content-Disposition', "attachment; filename= %s" % filename)
    # attach the instance 'p' to instance 'msg'
    msg.attach(p)
    # creates SMTP session
    s = smtplib.SMTP('smtp.gmail.com', 587)
    # start TLS for security
    s.starttls()
    # Authentication
    s.login(fromaddr, password)
    # Converts the Multipart msg into a string
    text = msg.as_string()
    # sending the mail
    s.sendmail(fromaddr, toaddr, text)
    # terminating the session
    s.quit()


def main():

    title = 'API Hacking'
    name = 'Firstname Lastname'
    date = 'November 18, 2022'
    email = 'lazaro.fraga@gmail.com'
    instructor = 'Sunny Wear'
    template = 'cert.jpg'

    df = pd.read_csv('/home/laz/eventbrite-automation/cert_list.csv')

    for index, row in df.iterrows():
        if row['workshop'] != 'API Hacking':
            cert = Certificate(row['name'], row['workshop'],
                               date, row['instructor'], template)
            email = row['email']
            file = generate_certificate(cert)
            send_email(cert, email, file, from_email, password)


if __name__ == '__main__':
    main()
