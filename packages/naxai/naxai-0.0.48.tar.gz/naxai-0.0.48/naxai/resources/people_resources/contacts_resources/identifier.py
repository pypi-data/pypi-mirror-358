"""
Contact identifier resource for the Naxai People SDK.

This module provides methods for managing the primary identifier type for contacts
in the Naxai platform. It allows users to retrieve and update which identifier
(email, phone, or externalId) is used as the unique key for contact records,
which affects how contacts are referenced throughout the API.

Available Functions:
    get()
        Retrieves the current primary identifier type for contacts.
        Returns a GetContactIdentifierResponse containing the identifier type
        (email, phone, or externalId).

    update(identifier)
        Updates the primary identifier type used for contacts.
        Takes an identifier parameter specifying the new type to use
        (email, phone, or externalId).
        Returns an UpdateContactIdentifierResponse confirming the change.

"""

import json
from typing import Literal
from naxai.models.people.responses.contacts_responses import (GetContactIdentifierResponse,
                                                              UpdateContactIdentifierResponse)

class IdentifierResource:
    """identifier resource for people.contacts resource"""

    def __init__(self, client, root_path):
        self._client = client
        self.root_path = root_path + "/keyIdentifier"
        self.headers = {"Content-Type": "application/json"}

    def get(self):
        """
        Retrieve the current primary identifier type for contacts in the Naxai People API.
        
        This method fetches information about which identifier type (email, phone, or externalId)
        is currently being used as the primary identifier for contacts in your account.
        The primary identifier determines how contacts are uniquely identified in the system.
        
        Returns:
            GetContactIdentifierResponse: A response object containing the current primary
                identifier type. The identifier field will be one of:
                "email", "phone", or "externalId".
        
        Raises:
            NaxaiAPIRequestError: If there is an error response from the API.
            NaxaiAuthenticationError: If authentication fails.
            NaxaiAuthorizationError: If the account lacks permission to access this information.
        
        Example:
            ```python
            with NaxaiClient(api_client_id="your_id", api_client_secret="your_secret") as client:
                # Get the current primary identifier type
                response = client.people.contacts.identifier.get()
                
                # Display the current identifier type
                print(f"Current primary identifier type: {response.identifier}")
                
                # Use the identifier in conditional logic
                if response.identifier == "email":
                    print("Contacts are identified by email address")
                elif response.identifier == "phone":
                    print("Contacts are identified by phone number")
                elif response.identifier == "externalId":
                    print("Contacts are identified by external ID")
            ```
        
        Note:
            - The primary identifier affects how contacts are identified across the entire API
            - This setting applies to all contacts in your account
            - Understanding the current identifier type is important when creating or
              updating contacts
        """
        # pylint: disable=protected-access
        return GetContactIdentifierResponse.model_validate_json(
            json.dumps(self._client._request("GET",
                                             self.root_path,
                                             headers=self.headers)))

    def update(self, identifier: Literal["email", "phone", "externalId"]):
        """
        Update the primary identifier type for contacts in the Naxai People API.
        
        This method changes which identifier type (email, phone, or externalId) is used
        as the primary identifier for contacts in your account. The primary identifier
        determines how contacts are uniquely identified in the system.

        For this method to work, you'll first have to delete all or your contacts.
        
        Returns:
            UpdateContactIdentifierResponse: A response object containing the new primary
                identifier type. The identifier field will be one of:
                "email", "phone", or "externalId".
        
        Raises:
            NaxaiAPIRequestError: If there is an error response from the API.
            NaxaiAuthenticationError: If authentication fails.
            NaxaiAuthorizationError: If the account lacks permission to modify this setting.
        
        Example:
            ```python
            with NaxaiClient(api_client_id="your_id", api_client_secret="your_secret") as client:
                # Update the primary identifier type
                response = client.people.contacts.identifier.update(identifier="email")
                
                # Confirm the change
                print(f"Primary identifier type updated to: {response.identifier}")
                
                # Verify the change by getting the current setting
                current = client.people.contacts.identifier.get()
                assert current.identifier == response.identifier, "Update failed"
                print("Update confirmed")
            ```
        
        Note:
            - This is a significant change that affects how contacts are identified across
              the entire API
            - Before changing the identifier type, ensure that all contacts are removed
            - This operation may take some time to propagate through the system
            - Consider the impact on any integrations or automations that rely on the
              current identifier type
        """
        request_json = {"identifier": identifier}
        # pylint: disable=protected-access
        return UpdateContactIdentifierResponse.model_validate_json(
            json.dumps(self._client._request("PUT",
                                             self.root_path,
                                             json=request_json,
                                             headers=self.headers)))
