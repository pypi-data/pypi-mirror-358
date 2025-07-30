import boto3
import time
from datetime import datetime, timedelta
from calendar import monthrange
from rs4 import attrdict
from . import cloudwatch
import numpy as np

ec2 = boto3.client ('ec2')

def get_instnace_info (type):
    if type.startswith ("db."):
        type = type [3:]
    r = ec2.describe_instance_types(
        InstanceTypes = [type]
    )
    return r ["InstanceTypes"][0]


def get_instance_ids (id):
    instances = boto3.resource ('ec2').instances.filter (Filters=[{'Name': 'tag:Name', 'Values': [id]}])
    return [inst.id for inst in instances ]

def get_instance (id):
    r = ec2.describe_instances (InstanceIds=[id])
    return r ["Reservations"][0]["Instances"][0]

def get_metric (id):
    inst = get_instance (id)
    m = attrdict.AttrDict ()
    m.instance_type = inst ['InstanceType']
    type_info = get_instnace_info (m.instance_type)
    m.memory = int (type_info ['MemoryInfo']['SizeInMiB'] * 1024 * 1024)

    if m.instance_type.startswith ("t"):
        credits = cloudwatch.get_metric ('ec2', 'CPUCreditBalance', id, hours = 1, period = 300)
        lastest = credits [-1]
        t, c = m.instance_type.split (".")
        m.max_credits = cloudwatch.INSTANCE_CREDITS [c]
        if t != 't2' and c in ('nano', 'micro', 'small'):
            m.max_credits *= 2
        m.credit_balance = int (lastest ["Average"])

    cpu = cloudwatch.get_metric ('ec2', 'CPUUtilization', id, hours = 24, period = 3600)
    m.cpu_usages = [int (x ['Average']) for x in cpu]
    return m


if __name__ == "__main__":
    from pprint import pprint

    ids = get_instance_ids ('dangolchain-api-qa')
    pprint (get_metric (ids [0]))
