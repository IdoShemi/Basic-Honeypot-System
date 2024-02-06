import boto3
from datetime import datetime
import time
from aws_cred import *

class aws_logger:

    def __init__(self, stream_name):
        aws_credentials_handler = AWSCredentialsHandler()

        self.aws_access_key = aws_credentials_handler.aws_access_key
        self.aws_secret_key = aws_credentials_handler.aws_secret_key
        self.region_name = "eu-north-1"  # e.g., "us-east-1"

        # Initialize the CloudWatch Logs client
        self.cloudwatch_logs = boto3.client('logs', region_name=self.region_name, aws_access_key_id=self.aws_access_key, aws_secret_access_key=self.aws_secret_key)

        # Define the log group and log stream names
        self.log_group_name = 'Honeypot'
        self.log_stream_name = stream_name
        
    def add_log(self, log_message):
        try:
            response = self.cloudwatch_logs.put_log_events(
                logGroupName=self.log_group_name,
                logStreamName=self.log_stream_name,
                logEvents=[
                    {
                        'timestamp': int(time.time() * 1000),
                        'message': log_message
                    }
                ]
            )
            return True, ("Log event sent successfully")
        except Exception as e:
            return False, (f"Error sending log event: {e}")
