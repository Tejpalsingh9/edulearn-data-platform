import boto3
import json
import csv
import random
import time
from datetime import datetime
from botocore.exceptions import ClientError


class EnrollmentEventProducer:
    """
    Reads EduLearn enrollment records from CSV and streams them to
    an Amazon Kinesis Data Stream one event at a time.
    Simulates real-time enrollment ingestion for the EduLearn platform.
    """

    CONFIG = {
        'stream_name'   : 'team2-edulearn-events-stream',
        'region'        : 'ap-south-1',
        'batch_size'    : 50,
        'delay_seconds' : 0.1
    }

    def __init__(self):
        """
        Initialises the boto3 Kinesis client and tracking counters.
        """
        self.kinesis_client = boto3.client(
            'kinesis',
            region_name=self.CONFIG['region']
        )
        self.sent   = 0
        self.failed = 0

    def build_event(self, row):
        """
        Takes a CSV row dict, enriches it with event_timestamp,
        and returns the JSON-encoded string ready to send to Kinesis.

        Args:
            row (dict): A row from csv.DictReader on enrollments.csv.

        Returns:
            str: JSON string representing the enrollment event.
        """
        event = dict(row)
        event['event_timestamp'] = datetime.utcnow().isoformat()
        event['ingest_date']     = datetime.utcnow().strftime("%Y-%m-%d")
        return json.dumps(event)

    def send_event(self, event_json):
        """
        Sends a single event to the configured Kinesis stream.
        On ClientError, increments self.failed and prints the error.
        On success, increments self.sent.

        Args:
            event_json (str): JSON string of the enrollment event.
        """
        try:
            event_data = json.loads(event_json)
            partition_key = event_data.get('enrollment_id', str(random.randint(1000, 9999)))
            self.kinesis_client.put_record(
                StreamName  = self.CONFIG['stream_name'],
                Data        = event_json,
                PartitionKey= partition_key
            )
            self.sent += 1
            print(f"[EduLearn] Sent: {partition_key} | city: {event_data.get('city')} "
                  f"| fees: ₹{event_data.get('total_fees')}")
        except ClientError as e:
            self.failed += 1
            print(f"[EduLearn] Failed: {str(e)}")

    def run(self, csv_path):
        """
        Reads enrollments.csv row by row using csv.DictReader,
        calls build_event + send_event up to CONFIG batch_size rows,
        sleeps CONFIG delay_seconds between sends, and prints final summary.

        Args:
            csv_path (str): Path to the enrollments CSV file.
        """
        try:
            with open(csv_path, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for i, row in enumerate(reader):
                    if i >= self.CONFIG['batch_size']:
                        break
                    event_json = self.build_event(row)
                    self.send_event(event_json)
                    time.sleep(self.CONFIG['delay_seconds'])
        except FileNotFoundError:
            print(f"[EduLearn] ERROR: File not found → {csv_path}")

        print(f"\n[EduLearn] Summary: Sent={self.sent} | Failed={self.failed}")


if __name__ == '__main__':
    producer = EnrollmentEventProducer()
    producer.run('data/enrollments.csv')
