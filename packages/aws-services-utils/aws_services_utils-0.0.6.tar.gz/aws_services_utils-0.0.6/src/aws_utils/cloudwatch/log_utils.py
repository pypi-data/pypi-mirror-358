"""
The module provides some utilities for performing CloudWatch queries and boxing the results in simple
objects.

One of the coolest feature provided is the automatic check of query status and the subsequent results fetching
one the status is *ready*.
"""

from enum import Enum
import logging
from time import sleep

from typing import List, NamedTuple, Optional
import boto3

from datetime import datetime as dt

class DisplayField(NamedTuple):      
    name: str
    value: str

class CloudWatchLogsCollector:

    def __init__(self, log_group: str, endpoint_url: Optional[str] = None) -> None:
        """
        The function initializes a boto3 client for AWS CloudWatch Logs with optional
        credentials and endpoint URL.
        
        Args:
          log_group (str): The `log_group` parameter in the `__init__` method is a
        string that represents the name of the CloudWatch Logs log group that the
        instance of the class will interact with. This parameter is required when
        initializing an instance of the class.
          credentials (Optional[AwsCredentials]): The `credentials` parameter in the
        `__init__` method is used to provide AWS credentials for authentication when
        interacting with AWS services. It is an optional parameter, meaning it can be
        omitted when creating an instance of the class. If provided, it should be an
        object of type `AwsCredentials`
          endpoint_url (Optional[str]): The `endpoint_url` parameter in the `__init__`
        method is used to specify the endpoint URL for the AWS service client. This can
        be useful when you want to connect to a specific endpoint for the AWS service,
        for example, when using a local or custom endpoint for testing or development
        purposes
        """
        
        if endpoint_url:
            self.client = boto3.client(
                service_name='logs', endpoint_url=endpoint_url)
        else:
            self.client = boto3.client(
                service_name='logs')

        self.log_group = log_group

    def collect_raw_logs(self, query: str, start: dt, end: dt, wait_time: int = 5) -> Optional[List[List[DisplayField]]]:
        """
        Collect raw logs based on a query within a specified time range using a
        client, and returns the results as a list of display fields.

        Args:
          query (str): The `query` parameter in the `collect_raw_logs` method is a string that represents
                       the AWS CloudWatch Log Insight query to be executed on the logs. It specifies the conditions or filters
                       to be applied to the log data to retrieve specific information.
          start (dt): The `start` parameter in the `collect_raw_logs` function is of type `dt`, which likely
                      stands for `datetime`. This parameter represents the start time for querying logs. It is used to
                      specify the beginning of the time range for which logs should be queried.
          end (dt): The `end` parameter in the `collect_raw_logs` function is of type `dt`, which likely
                    stands for datetime. This parameter represents the end time for the log query.
          wait_time (int): The `wait_time` parameter in the `collect_raw_logs` function represents the time
                           interval (in seconds) that the function will wait before checking if the query results are complete.
                           This parameter allows you to control how frequently the function checks for the completion status of
                           the query results while waiting for them to. Defaults to 5

        Returns:
          The `collect_raw_logs` method returns an optional list of lists of `DisplayField` objects. The
            method collects raw logs based on the provided query, start and end timestamps, and optional wait
            time. If successful, it returns a list of lists of `DisplayField` objects representing the query
            results. If an error occurs during the process, it logs the error and returns `None`.
        """

        try:
            response = self.client.start_query(startTime=int(start.timestamp() * 1000),
                                               endTime=int(
                end.timestamp() * 1000),
                queryString=query,
                logGroupName=self.log_group)

            if response:

                while self.client.get_query_results(queryId=response['queryId'])['status'] != 'Complete':

                    sleep(wait_time)

                query_results = self.client.get_query_results(
                    queryId=response['queryId'])

                return [[DisplayField(name=field['field'], value=field['value']) for field in event] for event in query_results['results']]

        except Exception as e:
            logging.error(f"Error: {e}")

        return None

    def sort_events_fields(self, events_log_fields: List[List[DisplayField]], ordered_fields_list: List[str]) -> List[List[DisplayField]]:
        """
        The function `sort_events_fields` sorts the fields in a list of event logs based on a specified
        order of field names.

        Args:
          events_log_fields (List[List[DisplayField]]): The `events_log_fields` parameter is a list of lists
                                                        of `DisplayField` objects. Each inner list represents a single event log and contains `DisplayField`
                                                        objects related to that event.
          ordered_fields_list (List[str]): The `ordered_fields_list` parameter is a list of strings that
                                           specifies the desired order in which the fields should be sorted for each event log in the
                                           `events_log_fields` list. The function `sort_events_fields` takes a list of lists of `DisplayField`
                                           objects (`events_log_fields`)

        Returns:
          A list of lists of DisplayField objects, where each inner list is sorted based on the order
        specified in the ordered_fields_list.
        """

        return [self.__sort_event_fields(event_log, ordered_fields_list) for event_log in events_log_fields]

    def __sort_event_fields(self, log_event: List[DisplayField], ordered_fields_list: List[str]) -> List[DisplayField]:
        """
        The function sorts a list of DisplayField objects based on a provided list of field names.

        Args:
          log_event (List[DisplayField]): The `log_event` parameter is a list of `DisplayField` objects that
        you want to sort based on the order specified in the `ordered_fields_list`. The
        `ordered_fields_list` parameter is a list of strings that represent the desired order in which the
        `DisplayField` objects should be sorted
          ordered_fields_list (List[str]): The `ordered_fields_list` parameter is a list of strings that
        specifies the desired order of fields in the `log_event` list. The `__sort_event_fields` method
        sorts the `log_event` list based on the order specified in the `ordered_fields_list` parameter. If a
        field in

        Returns:
          a sorted list of DisplayField objects based on the order specified in the ordered_fields_list. If
        any item in the log_event list is not found in the ordered_fields_list, a warning message is logged
        and the original list is returned.
        """

        try:
            return sorted(log_event, key=lambda field: ordered_fields_list.index(field.name))
        except ValueError:
            logging.warning(
                'Some item not found inside the provided list. Returning original list')
            return log_event