import boto3
from . import cloudwatch
from .ec2 import get_instnace_info
import numpy as np
from rs4 import attrdict

rds = boto3.client ('rds')

def get_instances ():
    return rds.describe_db_instances ()

def get_instance (id):
    for inst in get_instances ()["DBInstances"]:
        if inst ["DBInstanceIdentifier"] == id:
            return inst

def get_metric (id):
    inst = get_instance (id)

    m = attrdict.AttrDict ()
    m.instance_type = inst ['DBInstanceClass']
    m.disk = int (inst ['AllocatedStorage'] * 1024 * 1024 * 1024)
    type_info = get_instnace_info (m.instance_type)
    m.memory = int (type_info ['MemoryInfo']['SizeInMiB'] * 1024 * 1024)

    if m.instance_type.startswith ("db.t"):
        credits = cloudwatch.get_metric ('rds', 'CPUCreditBalance', id, hours = 1, period = 300)
        lastest = credits [-1]
        t, c = m.instance_type.split (".")[1:]
        m.max_credits = cloudwatch.INSTANCE_CREDITS [c]
        if t != 't2' and c in ('nano', 'micro', 'small'):
            m.max_credits *= 2
        m.credit_balance = int (lastest ["Average"])

    m.free_disk = int (cloudwatch.get_metric ('rds', 'FreeStorageSpace', id, hours = 1, period = 300)[-1]["Maximum"])
    m.free_memory = int (cloudwatch.get_metric ('rds', 'FreeableMemory', id, hours = 1, period = 300)[-1]["Maximum"])

    cpu = cloudwatch.get_metric ('rds', 'CPUUtilization', id, hours = 24, period = 3600)
    m.cpu_usages = [int (x ['Average']) for x in cpu]
    return m


if __name__ == "__main__":
    from pprint import pprint
    pprint (get_metric ('dangolchain'))

