import os
import boto3


class BotoClientFactory:

    def get_boto_client(self, client_type: str, region_name: str):
        session = boto3.session.Session(region_name=region_name)
        client = session.client(
            service_name=client_type,
            region_name=region_name
        )

        if 'USE_AIRFLOW' in os.environ and (os.environ['USE_AIRFLOW'] == 'true' or os.environ['USE_AIRFLOW'] == 'True' or os.environ['USE_AIRFLOW'] == True):
            sts_client = boto3.client('sts')
            
            if 'AWS_ROLE_ARN' not in os.environ:
                raise Exception('Must have AWS_ROLE_ARN set')
            
            assumed_role_object=sts_client.assume_role(
                RoleArn=os.environ['AWS_ROLE_ARN'],
                RoleSessionName="airflow_session"
            )
            credentials=assumed_role_object['Credentials']
            session = boto3.Session(
                aws_access_key_id=credentials['AccessKeyId'],
                aws_secret_access_key=credentials['SecretAccessKey'],
                aws_session_token=credentials['SessionToken']
            )
            client = session.client(
                service_name=client_type,
                region_name=region_name
            )

        return client
