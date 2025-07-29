import logging
import os
from typing import Optional
import boto3
from mypy_boto3_ssm import SSMClient

logging.basicConfig(level=logging.INFO)

# Mandatory environment variable, representing the referent region of AWS location
AWS_REGION_KEY = 'AWS_REGION'

class PropertiesManager:
    """
    A client for retrieving parameters from _AWS Systems Manager Parameter Store_

    *PropertiesManager* provide a tool for easily retrieve the value of a specified parameters
    from the AWS data storage *Systems Manager Parameter Store*.

    When used in non AWS environment it is mandatory to provide short time credentials in order
    to be authorized to access the service. When an application run in AWS environment, an authorization
    process must be applied in order to skip the credentials providing process.

    No matter of the runtime environment, the variable ·`AWS_REGION` must always been set.
    """

    def __init__(self, endpoint_url: Optional[str] = None) -> None:
        """
        The function initializes an SSM client using the AWS region specified in an environment variable or
        raises an exception if the variable is not found.
        """
        
        MESSAGE_AWS_REGION_NOT_FOUND: str = f'Unable to find environment variable {AWS_REGION_KEY}'

        region: Optional[str] = os.environ.get(AWS_REGION_KEY)

        if endpoint_url:
            self.ssm_client: SSMClient = boto3.client(
                service_name="ssm", endpoint_url=endpoint_url)
        elif region:
            self.ssm_client: SSMClient = boto3.client(
                service_name="ssm", region_name=region)
        else:
            logging.error(MESSAGE_AWS_REGION_NOT_FOUND)
            
            raise Exception(MESSAGE_AWS_REGION_NOT_FOUND)

    def fetch_parameter_value(self, param_key: str, encryption: bool = True) -> Optional[str]:
        """
        The `fetch_parameter_value` function retrieves a parameter value from AWS Systems Manager Parameter
        Store, with an option to decrypt it if it's encrypted.

        Args:
          param_key (str): The `fetch_parameter_value` method is designed to retrieve a parameter value from
                           AWS Systems Manager Parameter Store using the `param_key` provided. The `encryption` parameter is a
                           boolean flag that indicates whether the parameter value should be decrypted or not.
          encryption (bool): The `encryption` parameter in the `fetch_parameter_value` method is a boolean
                            flag that indicates whether the parameter value should be retrieved in its decrypted form. When
                            `encryption` is set to `True`, the parameter value will be fetched with decryption. If `encryption`
                            is set to `False`,. Defaults to True

        Returns:
          The `fetch_parameter_value` method returns the value of the parameter with the specified key if it
        is successfully fetched from the SSM parameter store. If an error occurs during the fetching
        process, it returns `None`.
        """

        try:
            parameter = self.ssm_client.get_parameter(
                Name=param_key, WithDecryption=encryption)

            return parameter['Parameter']['Value']
        except Exception as e:
            logging.error(
                f"Error trying to fetch parameter {param_key}. Exception stacktrace: {e}", stack_info=True)

            return None
