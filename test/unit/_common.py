import boto3


def create_instances(region_name, ami_id, count):
    client = boto3.client("ec2", region_name=region_name)
    client.run_instances(ImageId=ami_id, MinCount=count, MaxCount=count)
