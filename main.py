import imaplib
import Secret
import re

secret = Secret()

user = secret.username
passwd = secret.password
imap_url = "imap.gmail.com"

# Credit for these 3 functions goes to GeeksForGeeks.
# https://www.geeksforgeeks.org/python-fetch-your-gmail-emails-from-a-particular-user/.
def getBody(msg):
    if msg.is_multipart():
        return getBody(msg.get_payload(0))
    else:
        return msg.get_payload(None, True)


def search(key, value, connection):
    result, data = connection.search(None, key, '"{}"'.format(value))
    return data

def getEmails(messageBytes):
    msgs = []
    for num in messageBytes[0].split():
        typ, data = con.fetch(num, '(RFC822)')
        msgs.append(data)

    return msgs

def parseMail(message):
    # body = str()
    # date = str()
    # time = str()
    # teacher = str()

    # A regex to find the flags which will precede the body of our message,
    startRE = re.compile(r'Content-Type: text\/plain;.*\sMime-Version: \d\.\d\s\s')
    endRE = re.compile(r'--.*\n')

    # Get the text between the end of the first match and the start of the second.
    pos1 = startRE.search(message).end()
    # We must search for the next occurrence of the end pattern AFTER position1, or else it will match too early.
    pos2 = endRE.search(message[pos1:]).start()
    # Since the second match works on a smaller substring, we need to offset the position value.
    pos2 += pos1

    print(message[pos1:pos2].strip())


con = imaplib.IMAP4_SSL(imap_url)
con.login(user, passwd)
con.select("Inbox")

messages = getEmails(search('FROM', 'chat+1ac362f0-7ba9-4dfb-9b15-27630bf5eb76@mail.remind.com', con))

for msg in messages[::-1]:
    for sent in msg:
        if type(sent) is tuple:

            # encoding set as utf-8
            content = str(sent[1], 'utf-8')
            data = str(content)

            # Handling errors related to unidecode
            try:
                indexstart = data.find("ltr")
                data2 = data[indexstart + 5: len(data)]
                indexend = data2.find("</div>")

                # printing the required content which we need
                # to extract from our email i.e. our body
                parseMail(data2[0: indexend])

            except UnicodeEncodeError as e:
                pass
