import imaplib
import re
import atexit
import time
import pickle  # come on, that's so funny
import Secret

secret = Secret()

user = secret.username
passwd = secret.password
imap_url = "imap.gmail.com"

parsed = []

def exitHandler():
    with open('./parsedMessages.txt', 'wb') as txt:
        txt.truncate(0)
        pickle.dump(parsed, txt)

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


def extractBody(message):
    # Regular Expressions to get the beginning and end positions of the email body.
    startRE = re.compile(r'Content-Type: text/plain;.*\sMime-Version: \d\.\d\s\s')
    endRE = re.compile(r'--.*\n')

    # Get the text between the end of the first match and the start of the second.
    pos1 = startRE.search(message).end()
    # We must search for the next occurrence of the end pattern AFTER position1, or else it will match too early.
    pos2 = endRE.search(message[pos1:]).start()
    # Since the second match works on a smaller substring, we need to offset the position value.
    pos2 += pos1

    return message[pos1:pos2].strip()


def extractTime(message):
    # A regular expression which matches Gmail's date/time formatting.
    timeRE = re.compile(r'\w{3}, \d\d \w{3} \d{4} \d\d:\d\d:\d\d')
    full = timeRE.search(message).group()

    # Convert the PST timestamp to EST by adding 3 hours
    timeEST = int(full[17:19]) + 3

    # Indexing hijinks to reformat from "Mon, 16 Jan 2023 13:55:15" to "Mon, Jan 16 1:55 PM"
    if timeEST > 12:
        return "On " + full[:4] + full[7:11] + full[4:8] + str(timeEST - 12) + full[19:22] + " PM"
    else:
        return "On " + full[:4] + full[7:11] + full[4:8] + str(timeEST) + full[19:22] + " AM"


def extractClass(message):
    # A regular expression to grab the subject line of the email, detailing the class & teacher.
    classRE = re.compile(r'(?<=Subject:) .*')
    # The "17" index is there to remove the "new message from" text which proceeds the subject.
    # The "-6" index is there to remove the "class" text which is ends the subject line.
    full = classRE.search(message).group().strip()[17:-6]
    return "From " + full


def parseMail(message):
    body = str()
    date = str()
    teacher = str()
    full = str()

    body = extractBody(message)
    date = extractTime(message)
    teacher = extractClass(message)

    full = teacher + "\n" + date + "\n" + body + "\n"

    # If the message hasn't already been read, read & store it.

    # If the array is empty
    if not parsed:
        print(full)
        parsed.append(full)
    else:
        # Check if the message string is in the parsed array
        if full not in parsed:
            print(full)
            parsed.append(full)


if __name__ == "__main__":
    atexit.register(exitHandler)

    with open('./parsedMessages.txt', 'rb') as txt:
        try:
            parsed = pickle.load(txt)
        except EOFError:
            pass

    con = imaplib.IMAP4_SSL(imap_url)
    con.login(user, passwd)
    con.select("Inbox")

    while True:
        # Search for every email with "New Message" in the subject.
        messages = getEmails(search('SUBJECT', 'New Message', con))

        for msg in messages[::-1]:
            for sent in msg:
                if type(sent) is tuple:

                    # encoding set as utf-8
                    content = str(sent[1], 'utf-8')
                    data = str(content)

                    # Handling errors related to unidecode
                    try:
                        indexStart = data.find("ltr")
                        data2 = data[indexStart + 5: len(data)]
                        indexEnd = data2.find("</div>")

                        # printing the required content which we need
                        # to extract from our email i.e. our body
                        parseMail(data2[0: indexEnd])

                    except UnicodeEncodeError as e:
                        pass
        time.sleep(15)
"""
    I'll BRB (again)
"""