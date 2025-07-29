"""
Asynchronous voice transfer reporting resource for the Naxai SDK.

This module provides asynchronous methods for retrieving and analyzing metrics related to
transferred voice calls, including transfer volumes, success rates, and duration statistics.
These reports help users understand how often calls are being transferred to other destinations
and the effectiveness of those transfers, supporting optimization of call routing and agent
handoff processes in a non-blocking manner suitable for high-performance asynchronous applications.

Available Functions:
    list(group, start_date, stop_date, number):
        Retrieves transferred call metrics grouped by specified time interval (hour/day/month).
        Allows filtering by date range and specific phone numbers.

"""

import json
from typing import Optional, Literal
from naxai.base.exceptions import NaxaiValueError
from naxai.models.voice.responses.reporting_responses import ListTransferredMetricsResponse

class TransferResource:
    """ Transfer resource for reporting resource """


    def __init__(self, client, root_path):
        self._client = client
        self.root_path = root_path + "/transfer"
        self.headers = {"Content-Type": "application/json"}

    async def list(self,
             group: Literal["day", "month"],
             start_date: str,
             stop_date: str,
             number: Optional[str] = None
             ):
        """
        Retrieve a list of transferred call metrics grouped by the specified time interval.
        
        This method fetches statistics for calls that were transferred from the API, allowing 
        filtering by date range and specific phone numbers. The results are grouped according 
        to the specified time interval.
        
        Args:
            group (Literal["day", "month"]): The time interval for grouping the metrics.
                - "day": Group metrics by day ( max 120 days between start and stop date)
                - "month": Group metrics by month ( max 24 months between start and stop date)
            start_date (str): The start date for the reporting period.
                - For "day"/"month" grouping: Format must be 'YYYY-MM-DD' or 'YY-MM-DD'
                - Required for all grouping types
            stop_date (str): The end date for the reporting period.
                - For "day"/"month" grouping: Format must be 'YYYY-MM-DD' or 'YY-MM-DD'
                - Required for all grouping types
            number (Optional[str]): Phone number to filter the metrics by. If provided,
                only metrics for this specific number will be returned.
        
        Returns:
            ListTransferredMetricsResponse: 
            A Pydantic model containing the transferred call metrics.
            The response includes:
                - start_date: Start timestamp of the reporting period
                - stop_date: End timestamp of the reporting period
                - direction: Call direction
                - number: The phone number associated with these metrics
                - group: The time interval grouping used
                - stats: List of BaseStats objects with detailed metrics for transferred calls
        
        Raises:
            NaxaiValueError: If required parameters are missing or in incorrect format:
                - When start_date is not provided
                - When stop_date is not provided
                - When date formats don't match the required format
        
        Example:
            >>> metrics = await client.voice.reporting.transfer.list(
            ...     group="day",
            ...     start_date="2023-01-01",
            ...     stop_date="2023-01-31",
            ...     number="1234567890"
            ... )
            >>> print(f"Found {len(metrics.stats)} daily records")
            >>> for stat in metrics.stats:
            ...     print(f"Date: {stat.date}, Calls: {stat.calls}")
            ...     print(f"Average duration: "
            ...     f"{stat.duration/stat.calls:.1f} seconds" if stat.calls > 0 else "No calls")
        """

        if start_date is None:
            raise NaxaiValueError("startDate must be provided when group is 'day' or 'month'")

        if len(start_date) < 8 or len(start_date) > 10:
            raise NaxaiValueError("startDate must be in the format 'YYYY-MM-DD' or 'YY-MM-DD'")

        if stop_date is None:
            raise NaxaiValueError("stopDate must be provided when group is 'day' or 'month'")

        if len(stop_date) < 8 or len(stop_date) > 10:
            raise NaxaiValueError("stopDate must be in the format 'YYYY-MM-DD' or 'YY-MM-DD'")

        params = {"group": group,
                  "startDate": start_date,
                  "stopDate": stop_date}
        if number:
            params["number"] = number
        # pylint: disable=protected-access
        return ListTransferredMetricsResponse.model_validate_json(
            json.dumps(await self._client._request("GET",
                                                   self.root_path,
                                                   params=params,
                                                   headers=self.headers)))
