"""
Module:
    auth.py

Description:
    This file contains the code for acquiring a service object which
    is authorized to perform tasks in your docs and drive service with
    Google.

Usage:
    from auth import get_service

    service = get_service(scopes=SCOPES['google_docs']['batchUpdate'])

Notes:


References:


License:
    GNU General Public License v3.0
    See LICENSE.MD

"""

"""
Version History:
    Original:
        GS | 23-Feb-23
"""

"""
TODOs:
    1)  Create service objects for docs and drive so that they don't need to be
        re-instantiated for every function.
"""

# Standard library imports
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Tool imports
import constants


def get_service(scopes: [list[str], None] = None, service_type: str = 'docs'):
    """
    Modified version of what appears in Google's quickstart.py. This function
    outputs an instance of the service/resource object. The object can be given
    access to docs or drive and can be accorded various privileges.

    Args:
        scopes:         Defines the privileges the service should have. See
                        constants.py for valid scopes and their descriptions.
        service_type:   What type of service should be returned?
                        Valid types are docs or drive.

    Returns:
        Instance of the service/resource object
    """

    if scopes is None:
        scopes = [constants.SCOPES['read_all_google_docs']]

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(constants.TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(constants.TOKEN_FILE, scopes)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                constants.CREDENTIALS_FILE,
                scopes
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(constants.TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    try:
        if service_type == 'docs':
            return build('docs', 'v1', credentials=creds)
        elif service_type == 'drive':
            return build('drive', 'v3', credentials=creds)
    except HttpError as err:
        print(err)
