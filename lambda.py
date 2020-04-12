import os
import boto3
import email
import re
from botocore.exceptions import ClientError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

region = os.environ['Region']

def fetchMessage(messageId):

    bucketName = os.environ['IncomingBucket']
    pathPrefix = os.environ['IncomingBucketPrefix']

    if pathPrefix:
        path = (pathPrefix + "/" + messageId)
    else:
        path = messageId

    url = (f"http://s3.console.aws.amazon.com/s3/object/{bucketName}/{path}?region={region}")

    client = boto3.client("s3")
    item = client.get_object(Bucket=bucketName, Key=path)
    data = item['Body'].read()

    result = {
        "id": messageId,
        "file": data,
        "path": url
    }

    return result

def createMessage(msgFile):

    DELIMETER = ";"

    sender = os.environ['ForwardingEmail']
    recipient = os.environ['RecipentEmail']
    subjectPrefix = os.environ['SubjectPrefix']

    inMessage = email.message_from_string(msgFile['file'].decode('utf-8'))
    inSubject = inMessage['Subject']

    outSubject = subjectPrefix + inSubject
    outBody = ("Forwarded from "
              + DELIMETER.join(inMessage.get_all('From'))
              + ". Original Message: " + msgFile['path'])
    outBodyText = MIMEText(outBody, _subtype="html")

    outMessage = MIMEMultipart()
    outMessage.attach(outBodyText)
    outMessage['Subject'] = outSubject
    outMessage['From'] = sender
    outMessage['To'] = recipient

    # Save & attach the original message
    fileName = re.sub('[^0-9a-zA-Z]+', '_', inSubject) + ".eml"
    attachment = MIMEApplication(msgFile["file"], fileName)
    attachment.add_header("Content-Disposition", 'attachment', filename=fileName)
    outMessage.attach(attachment)

    result = {
        "Source": sender,
        "Destinations": recipient,
        "Data": outMessage.as_string()
    }

    return result

def sendMesage(message):
    regionName = os.environ['Region']

    client = boto3.client('ses', regionName)

    try:
        response = client.send_raw_email(
            Source=message['Source'],
            Destinations=[
                message['Destinations']
            ],
            RawMessage={
                'Data':message['Data']
            }
        )

    except ClientError as e:
        result = e.response['Error']['Message']
    else:
        result = "Email sent! Message ID: " + response['MessageId']

    return result

def lambda_handler(event, context):

    messageId = event['Records'][0]['ses']['mail']['messageId']
    print(f"Received message ID {messageId}")

    msgFile = fetchMessage(messageId)
    message = createMessage(msgFile)
    result = sendMesage(message)
    print(result)