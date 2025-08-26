# based on https://github.com/aws-samples/cloudwatch-to-opensearch/blob/main/lambda/kdf-opensearch-transform-v2.py

"""
For processing data sent to Firehose by Cloudwatch Logs subscription filters.

Cloudwatch Logs sends to Firehose records that look like this where type is DATA_MESSAGE:

{
  "messageType": "DATA_MESSAGE",
  "owner": "123456789012",
  "logGroup": "log_group_name",
  "logStream": "log_stream_name",
  "subscriptionFilters": [
    "subscription_filter_name"
  ],
  "logEvents": [
    {
      "id": "01234567890123456789012345678901234567890123456789012345",
      "timestamp": 1510109208016,
      "message": "log message 1"
    },
    {
      "id": "01234567890123456789012345678901234567890123456789012345",
      "timestamp": 1510109208017,
      "message": "log message 2"
    }
    ...
  ]
}
The "message" value is compressed with GZIP and base64 encoded.

The code below will:

1) Iterate through all all records sent by CloudWatch and process the DATA_MESSAGE type.
2) Decode & Unzip the message payload
3) Look for JSON payloads and load objects if found. 
4) Package each log event message as a separate record, adding metadata and converting timestamp to utc date/time value
5) combine all log event records into JSON array 
6) Build KDF JSON response object with log events base64 encoded (NOTE: code will not GZIP output)

The output to S3 file will:

1) Be formatted as a JSON file that constitutes a JSON array with each log entry as a separate JSON object
2) Each log entry will include metadata that can be omitted by OSI 

Example output file:
[
    {
        "cloudwatch": {
            "logGroup": "/aws/lambda/my-lambda-function",
            "logStream": "2023/09/14/[$LATEST]9ae39e4917c04e7486a6cb81f892f33b",
            "owner": "12334567890"
        },
        "id": "37793152654191904442680491486618333209652445892414210048",
        "message": "[INFO] 2023-09-14T15:06:10.876Z 39b7ff85-5079-42bd-ae5e-39d102773384 example application message",
        "timestamp": "2023-09-14T14:59:36.842000Z"
    },...
]


Note: modify transformLogEvent() to change this output format to your desired output.

"""





import base64
import gzip
import json
import logging
import json
import jmespath
import requests
from datetime import datetime
from requests_auth_aws_sigv4 import AWSSigV4
import boto3


LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


def lambda_handler(event, context):
    """Extract the data from the event"""
    data = jmespath.search("awslogs.data", event)
    """Decompress the logs"""
    cwLogs = decompress_json_data(data)
    """Construct the payload"""
    payload = prepare_payload(cwLogs)
    print(payload)
    """Ingest the set of events to the pipeline"""    
    response = ingestData(payload)
    return {
        'statusCode': 200
    }

def decompress_json_data(data):
    compressed_data = base64.b64decode(data)
    uncompressed_data = gzip.decompress(compressed_data)
    return json.loads(uncompressed_data)

def prepare_payload(cwLogs):
    payload = []
    logEvents = cwLogs['logEvents']
    for logEvent in logEvents:
        request = {}
        request['id'] = logEvent['id']
        dt = datetime.fromtimestamp(logEvent['timestamp'] / 1000) 
        request['timestamp'] = dt.isoformat()
        request['message'] = logEvent['message'];
        request['owner'] = cwLogs['owner'];
        request['log_group'] = cwLogs['logGroup'];
        request['log_stream'] = cwLogs['logStream'];
        payload.append(request)
    return payload

def ingestData(payload):
    ingestionEndpoint = '{OpenSearch Pipeline Endpoint}'
    endpoint = 'https://' + ingestionEndpoint
    headers = {'Content-Type': 'application/json', 'Accept':'application/json'}
    r = requests.request('POST', f'{endpoint}/logs/ingest', json=payload, auth=AWSSigV4('osis'), headers=headers)
    LOGGER.info('Response received: ' + r.text)
    return r

