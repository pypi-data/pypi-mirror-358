"""
Email transactional resource for the Naxai SDK.

This module provides methods for sending transactional emails through the Naxai platform,
including personalized, event-triggered communications such as account notifications,
password resets, order confirmations, and receipts. It supports both direct HTML content
and template-based emails with variable substitution.

Available Functions:
    send(data: SendTransactionalEmailRequest)
        Send a transactional email to one or more recipients.
        Supports personalized emails with HTML content or template-based emails with
        variable substitution.
        Returns a unique identifier for tracking the email's status.

"""

import json
from naxai.models.email.requests.transactional_requests import SendTransactionalEmailRequest
from naxai.models.email.responses.transactional_responses import SendTransactionalEmailResponse

class TransactionalResource:
    """ transactional resource for email resource """

    def __init__(self, client, root_path):
        self._client = client
        self.root_path = root_path
        self.headers = {"Content-Type": "application/json"}

    def send(self, data: SendTransactionalEmailRequest):
        """
        Send a transactional email to one or more recipients.
        
        This method allows sending personalized transactional emails such as account notifications,
        password resets, order confirmations, and other event-triggered communications. The email
        content can be specified using either HTML or plain text.
        
        Args:
            data (SendTransactionalEmailRequest): A model containing all the information
            needed to send the transactional email, including:
                - sender (SenderObject): The sender's information (email and name)
                - to (list[DestinationObject]): List of primary recipients
                - cc (Optional[list[CCObject]]): List of CC recipient email addresses
                - bcc (Optional[list[BCCObject]]): List of BCC recipient email addresses
                - reply_to (Optional[str]): Reply-to email address
                - subject (str): Email subject line
                - text (Optional[str]): Plain text version of the email
                - html (Optional[str]): HTML version of the email
                - attachments (Optional[list[Attachment]]): Files to attach to the email
                - enable_tracking (Optional[bool]): Whether to enable open and click tracking
        
        Returns:
            SendTransactionalEmailResponse: A response object containing the unique identifier
            for the sent email.
                This ID can be used for tracking and querying the email's status.
        
        Raises:
            NaxaiAPIRequestError: 
                If the API request fails due to invalid parameters or server issues
            NaxaiAuthenticationError: If authentication fails
            NaxaiAuthorizationError: If the account lacks permission to send emails
            NaxaiRateLimitExceeded: If the rate limit for sending emails is exceeded
        
        Example:
            >>> # Basic email with HTML content
            >>> response = client.email.transactional.send(
            ...     SendTransactionalEmailRequest(
            ...         sender=SenderObject(email="sender@example.com", name="Sender Name"),
            ...         to=[DestinationObject(email="recipient@example.com", name="Recipient Name")],
            ...         subject="Your Account Verification",
            ...         html="<html><body><h1>Verify Your Account</h1>\
            ...               <p>Click the link to verify your account.</p></body></html>",
            ...         text="Verify Your Account\n\nClick the link to verify your account.",
            ...         enable_tracking=True
            ...     )
            ... )
            >>> print(f"Email sent with ID: {response.id}")
            
            >>> # Email with multiple recipients and attachments
            >>> response = client.email.transactional.send(
            ...     SendTransactionalEmailRequest(
            ...         sender=SenderObject(email="orders@example.com", name="Example Store"),
            ...         to=[
            ...             DestinationObject(email="customer@example.com", name="John Doe"),
            ...             DestinationObject(email="manager@example.com", name="Jane Manager")
            ...         ],
            ...         cc=[CCObject(email="support@example.com", name="Support Team")],
            ...         bcc=[BCCObject(email="records@example.com", name="Records")],
            ...         reply_to="no-reply@example.com",
            ...         subject="Your Order #12345 Has Shipped",
            ...         html="<html><body><p>Your order has been shipped!</p></body></html>",
            ...         attachments=[
            ...             Attachment(
            ...                 id="att_123",
            ...                 name="invoice.pdf",
            ...                 content_type="application/pdf",
            ...                 data="base64_encoded_pdf_data"
            ...             )
            ...         ],
            ...         enable_tracking=True
            ...     )
            ... )
            >>> print(f"Order notification sent with ID: {response.id}")
        
        Note:
            - At least one of text or html must be provided
            - The sender email must be a verified sender in your Naxai account
            - For high deliverability, ensure your sender domain is properly configured
              with SPF and DKIM
            - Tracking options require proper configuration of tracking domains
            - Attachments should be kept reasonably sized to avoid delivery issues
        
        See Also:
            SendTransactionalEmailRequest: For the complete structure of the request data
            SendTransactionalEmailResponse: For the structure of the response
        """
        # pylint: disable=protected-access
        return SendTransactionalEmailResponse.model_validate_json(
            json.dumps(self._client._request("POST",
                                             self.root_path + "/send",
                                             json=data.model_dump(by_alias=True,
                                                                  exclude_none=True),
                                             headers=self.headers,
                                             timeout=30.0)))
