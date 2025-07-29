# Copyright © 2020 Amazon Web Services
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os
import base64
import boto3
import requests
import json
from botocore.exceptions import ClientError
from configparser import ConfigParser
from osdu_api.providers.aws.boto_client_factory import BotoClientFactory

def _get_secret(region_name, secret_name, secret_dict_key):
    boto_client_factory = BotoClientFactory()
    client = boto_client_factory.get_boto_client('secretsmanager', region_name)

    # In this sample we only handle the specific exceptions for the 'GetSecretValue' API.
    # See https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
    # We rethrow the exception by default.

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        print("Could not get client secret from secrets manager")
        raise e
    else:
        # Decrypts secret using the associated KMS CMK.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
        else:
            decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])

    return_secret_serialized = secret
    if return_secret_serialized == None:
        return_secret_serialized = decoded_binary_secret

    return_secret = json.loads(return_secret_serialized)[secret_dict_key]

    return return_secret


def get_service_principal_token():
    config_parser = ConfigParser(os.environ)
    config_file_name = 'osdu_api.ini'

    found_names = config_parser.read(config_file_name)
    if config_file_name not in found_names:
        raise Exception('Could not find osdu_api.ini config file')

    param_mount = os.getenv('PARAMETER_MOUNT_PATH')

    client_id = get_mount_parameter(param_mount, config_parser.get('provider', 'client_id_ssm_path'))
    client_secret = get_mount_secret(param_mount, config_parser.get('provider', 'client_secret_name'), config_parser.get('provider', 'client_secret_dict_key'))
    token_url = get_mount_parameter(param_mount, config_parser.get('provider', 'token_url_ssm_path'))
    aws_oauth_custom_scope = get_mount_parameter(param_mount, config_parser.get('provider', 'aws_oauth_custom_scope_ssm_path'))

    auth = '{}:{}'.format(client_id, client_secret)
    encoded_auth = base64.b64encode(str.encode(auth))

    headers = {}
    headers['Authorization'] = 'Basic ' + encoded_auth.decode()
    headers['Content-Type'] = 'application/x-www-form-urlencoded'

    data = {
        "grant_type": "client_credentials",
        "scope": aws_oauth_custom_scope
    }
    response = requests.post(url=token_url, headers=headers, data=data)
    return json.loads(response.content.decode())['access_token']

def get_mount_parameter(param_mount_path, parameter):
    with open(os.path.join(param_mount_path, parameter)) as file:
        param_value = file.read()
    return param_value

def get_mount_secret(param_mount_path, parameter, secret_key):
    with open(os.path.join(param_mount_path, parameter)) as file:
        secret_string = file.read()
    return_secret = json.loads(secret_string)[secret_key]
    return return_secret

