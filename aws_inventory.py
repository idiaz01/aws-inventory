import os
import boto3
import sys
import logging
import pandas as pd
from pandas import ExcelWriter
from utils import load_yaml


# Set the logging level
logger = logging.getLogger("__name__")
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class AWSInventory:
    """
    This class is used to list AWS resources using Boto3.

    Attributes:
        aws_access_key_id (str): The
        aws_secret_access_key (str): The

    Methods:
        get_boto_client(service_name, region_name): Returns a Boto3 client for a given service and region.
        list_ec2_instances(aws_region): List EC2 instances in a given region.
        list_ec2_volumes(aws_region): List EC2 volumes in a given region.
        list_ec2_snapshots(aws_region): List EC2 snapshots in a given region.
        list_s3_buckets(): List S3 buckets.
        list_rds_instances(aws_region): List RDS instances in a given region.
        list_eks_clusters(aws_region): List EKS clusters in a given region.
        save_to_excel(dataframe_dict, filename): Save dataframes to an Excel file with different sheets.
    """
    def __init__(self, aws_config_file):
        """
        The constructor for the AWSInventory class.
        :param aws_config_file: The path to the AWS credentials file.
        """
        logging.info("Initializing AWSInventory")
        aws_credentials = load_yaml(aws_config_file)
        self.aws_access_key_id = aws_credentials['AWS_ACCESS_KEY_ID']
        self.aws_secret_access_key = aws_credentials['AWS_SECRET_ACCESS_KEY']

    def get_boto_client(self, service_name: str, region_name: str) -> boto3.client:
        """
        Returns a Boto3 client for a given service and region.
        :param service_name: The name of the AWS service.
        :param region_name: The name of the AWS region.
        :return: A Boto3 client.
        """
        logging.info(f'Getting Boto3 client for {service_name} in {region_name}')
        return boto3.client(
            service_name,
            region_name=region_name,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key
        )

    def list_ec2_instances(self, aws_region: str) -> pd.DataFrame:
        """
        List EC2 instances in a given region.
        :param aws_region: The AWS region to list the instances from.
        :return: A DataFrame with the instances' data.
        """
        logging.info(f'Listing EC2 instances in {aws_region}...')
        ec2 = self.get_boto_client('ec2', aws_region)
        instances = ec2.describe_instances()
        instances_data = []
        for reservation in instances['Reservations']:
            for instance in reservation['Instances']:
                instances_data.append({
                    'Name': next((tag['Value'] for tag in instance['Tags'] if tag['Key'] == 'Name'), ''),
                    'Instance ID': instance['InstanceId'],
                    'Type': instance['InstanceType'],
                    'OS': instance['PlatformDetails'],
                    'Region': aws_region,
                    'State': instance['State']['Name'],
                    # 'Price/hour (USD)': price_per_hour
                })
        logging.info(f'Found {len(instances_data)} instances in {aws_region}')
        return pd.DataFrame(instances_data)

    def list_ec2_volumes(self, aws_region: str) -> pd.DataFrame:
        """
        List EC2 volumes in a given region.
        :param aws_region: The AWS region to list the volumes from.
        :return: A DataFrame with the volumes' data.
        """
        logging.info(f'Listing EC2 volumes in {aws_region}...')
        ec2 = self.get_boto_client('ec2', aws_region)
        volumes = ec2.describe_volumes()
        volumes_data = []
        for volume in volumes['Volumes']:
            volumes_data.append({
                'Volume ID': volume['VolumeId'],
                'Size': volume['Size'],
                'State': volume['State'],
                'Region': aws_region,
            })
        logging.info(f'Found {len(volumes_data)} volumes in {aws_region}')
        return pd.DataFrame(volumes_data)

    def list_ec2_snapshots(self, aws_region: str) -> pd.DataFrame:
        """
        List EC2 snapshots in a given region.
        :param aws_region: The AWS region to list the snapshots from.
        :return: A DataFrame with the snapshots' data.
        """
        logging.info(f'Listing EC2 snapshots in {aws_region}...')
        ec2 = self.get_boto_client('ec2', aws_region)
        snapshots = ec2.describe_snapshots(OwnerIds=['self'])
        snapshots_data = []
        for snapshot in snapshots['Snapshots']:
            snapshots_data.append({
                'Snapshot ID': snapshot['SnapshotId'],
                'Volume Size': snapshot['VolumeSize'],
                'State': snapshot['State'],
                'Region': aws_region,
            })
        logging.info(f'Found {len(snapshots_data)} snapshots in {aws_region}')
        return pd.DataFrame(snapshots_data)

    def list_s3_buckets(self) -> pd.DataFrame:
        """
        List S3 buckets in all regions.
        :return: A DataFrame with the buckets' data.
        """
        logging.info('Listing S3 buckets...')
        s3 = self.get_boto_client('s3', 'us-east-1')
        buckets = s3.list_buckets()
        buckets_data = [{'Bucket Name': bucket['Name']} for bucket in buckets['Buckets']]
        logging.info(f'Found {len(buckets_data)} buckets')
        return pd.DataFrame(buckets_data)

    def list_rds_instances(self, aws_region: str) -> pd.DataFrame:
        """
        List RDS instances in a given region.
        :param aws_region: The AWS region to list the instances from.
        :return: A DataFrame with the instances' data.
        """
        logging.info(f'Listing RDS instances in {aws_region}...')
        rds = self.get_boto_client('rds', aws_region)
        instances = rds.describe_db_instances()
        instances_data = [{'DB Instance Identifier': instance['DBInstanceIdentifier'], 'DB Engine': instance['Engine']}
                          for instance in instances['DBInstances']]
        logging.info(f'Found {len(instances_data)} RDS instances in {aws_region}')
        return pd.DataFrame(instances_data)

    def list_eks_clusters(self, aws_region: str) -> pd.DataFrame:
        """
        List EKS clusters in a given region.
        :param aws_region: The AWS region to list the clusters from.
        :return: A DataFrame with the clusters' data.
        """
        logging.info(f'Listing EKS clusters in {aws_region}...')
        eks = self.get_boto_client('eks', aws_region)
        clusters = eks.list_clusters()
        clusters_data = [{'Cluster Name': name} for name in clusters['clusters']]
        logging.info(f'Found {len(clusters_data)} EKS clusters in {aws_region}')
        return pd.DataFrame(clusters_data)

    @staticmethod
    def save_to_excel(dataframe_dict: dict, filename: str):
        """
        Save dataframes to an Excel file with different sheets
        :param dataframe_dict: A dictionary where the key is the sheet name and the value is the dataframe
        :param filename: The name of the Excel file
        """
        logging.info(f'Saving data to {filename}...')
        with ExcelWriter(filename) as writer:
            for sheet_name, df in dataframe_dict.items():
                df.to_excel(writer, sheet_name=sheet_name)
        logging.info('Data saved successfully')


if __name__ == "__main__":
    # Get the output file from the arguments (e.g. python aws_inventory.py output.xlsx)
    output_file = sys.argv[1]

    # Get the current path
    current_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(current_path)
    inventory = AWSInventory('aws_credentials.yml')
    regions = ['us-east-1', 'eu-west-1', 'sa-east-1']

    all_ec2_data = pd.DataFrame()
    all_rds_data = pd.DataFrame()
    all_eks_data = pd.DataFrame()
    all_volumes_data = pd.DataFrame()
    all_snapshots_data = pd.DataFrame()
    all_s3_data = pd.DataFrame()

    for region in regions:
        df_ec2 = inventory.list_ec2_instances(region)
        all_ec2_data = pd.concat([all_ec2_data, df_ec2], ignore_index=True)

        df_rds = inventory.list_rds_instances(region)
        all_rds_data = pd.concat([all_rds_data, df_rds], ignore_index=True)

        # df_eks = inventory.list_eks_clusters(region)
        # all_eks_data = pd.concat([all_eks_data, df_eks], ignore_index=True)

        df_volumes = inventory.list_ec2_volumes(region)
        all_volumes_data = pd.concat([all_volumes_data, df_volumes], ignore_index=True)

        df_snapshots = inventory.list_ec2_snapshots(region)
        all_snapshots_data = pd.concat([all_snapshots_data, df_snapshots], ignore_index=True)

    # List S3 buckets
    df_s3 = inventory.list_s3_buckets()

    df_dict = {
        'EC2': all_ec2_data,
        'RDS': all_rds_data,
        # 'EKS': all_eks_data,
        'EC2-Volumes': all_volumes_data,
        'EC2-Snapshots': all_snapshots_data,
        'S3-Buckets': df_s3
    }

    inventory.save_to_excel(df_dict, output_file)
