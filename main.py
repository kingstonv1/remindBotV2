import imaplib
import email
import Secret

secret = Secret()

user = secret.username
passwd = secret.password
imap_url = "imap.gmail.com"

def getBody(msg):
    if msg.is_multipart():
        return getBody(msg.get_payload(0))
    else:
        return msg.get_payload(None, True)

def getEmails(messageBytes, content):
    messages = []
    for num in messageBytes[0].split():
        typ, data = content.fetch(num, '(RFC822)')
        messages.append(data)

    return messages


con = imaplib.IMAP4_SSL(imap_url)
con.login(user, passwd)