import boto3
from datetime import datetime, timedelta
import time

cw = boto3.client('cloudwatch')

# https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/viewing_metrics_with_cloudwatch.html

INSTANCE_CREDITS = dict (
    nano = 72, micro = 144, small = 288, medium = 576, large = 864, xlarge = 1296
)
INSTANCE_CREDITS ["2xlarge"] = 1958

units = {
    'CPUCreditBalance': 'Count',
    'FreeableMemory': 'Bytes',
    'FreeStorageSpace': 'Bytes',
    'CPUUtilization': 'Percent'
}

def get_metric (kind, name, id, hours = 24, period = 3600):
    response = cw.get_metric_statistics (
        Namespace='AWS/EC2' if kind == 'ec2' else 'AWS/RDS',
        MetricName=name,
        Dimensions=[
            {
                'Name': 'InstanceId' if kind == "ec2" else 'DBInstanceIdentifier',
                'Value': id
            },
        ],
        StartTime=datetime.utcnow () - timedelta (hours = hours),
        EndTime=datetime.utcnow () - timedelta (hours = 0),
        Period=period,
        Statistics=['Average', 'Minimum', 'Maximum'],
        Unit=units [name]
    )
    return response ["Datapoints"]

def get_credit_balance (instance):
    if not instance.instance_type.startswith ("t"):
        return
    response = get_metric ('ec2', 'CPUCreditBalance', instance.id, 1, 300)
    lastest = response [-1]
    t, c = instance.instance_type.split (".")
    max_credits = INSTANCE_CREDITS [c]
    if t != 't2' and c in ('nano', 'micro', 'small'):
        max_credits *= 2
    return int (lastest ["Average"]), max_credits
