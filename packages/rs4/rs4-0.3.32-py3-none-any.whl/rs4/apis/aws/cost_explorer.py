import boto3
import time
from datetime import datetime, timedelta
from calendar import monthrange

ce = boto3.client ('ce')

def get_cost ():
    def last_day_of_month(date_value):
        return monthrange(date_value.year, date_value.month)[1]

    '''
    {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Action": ["ce:*"],
            "Resource": ["*"]
        }]
    }
    '''
    now = datetime.now () - timedelta (days = 1)
    r = ce.get_cost_and_usage (
        TimePeriod = {
            'Start': time.strftime ('%Y-%m-%d', time.localtime (time.mktime ((now.year, now.month, 1, 0, 0, 0, 0, 0, 0)))),
            'End':   time.strftime ('%Y-%m-%d', time.localtime (time.mktime ((now.year, now.month, last_day_of_month (now), 0, 0, 0, 0, 0, 0))))
        },
        Granularity='MONTHLY',
        Metrics = ['BlendedCost']
    )
    return r ['ResultsByTime'][0]['Total']['BlendedCost']
