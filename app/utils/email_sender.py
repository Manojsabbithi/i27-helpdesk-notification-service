import os

import boto3


def send_email(
    to_email: str,
    subject: str,
    plain_body: str,
    html_body: str | None = None,
):
    """
    Send an email through Amazon SES.

    AWS credentials are not stored in the application.
    In EKS, boto3 receives temporary AWS credentials through IRSA.
    """

    aws_region = os.getenv("AWS_REGION", "ap-south-2")
    from_email = os.getenv("SES_FROM_EMAIL")

    if not from_email:
        raise RuntimeError("SES_FROM_EMAIL environment variable is not configured")

    ses = boto3.client(
        "sesv2",
        region_name=aws_region,
    )

    body = {
        "Text": {
            "Data": plain_body,
            "Charset": "UTF-8",
        }
    }

    if html_body:
        body["Html"] = {
            "Data": html_body,
            "Charset": "UTF-8",
        }

    response = ses.send_email(
        FromEmailAddress=from_email,
        Destination={
            "ToAddresses": [to_email],
        },
        Content={
            "Simple": {
                "Subject": {
                    "Data": subject,
                    "Charset": "UTF-8",
                },
                "Body": body,
            }
        },
    )

    return response["MessageId"]
