"""
Module:
    constants.py

Description:
    This file contains the constants that will be used by the tool.

Usage:
    import constants

Notes:
    This file is not intended to hold items such as local directory structures or
    API keys. It is intended to hold constants necessary manipulation of Google docs.

References:
    https://developers.google.com/docs/api/quickstart/python

License:
    https://creativecommons.org/licenses/by-nc-nd/4.0/
    Attribution-NonCommercial-NoDerivatives 4.0 International (CC BY-NC-ND 4.0)
    See LICENSE.txt

"""

"""
Version History:
    Original:
        GS | 23-Feb-23
"""

"""
TODOs:
    1)  Make service_type for the get_service function in auth.py an Enum, defined here,
        instead of a string.
"""

# Standard library imports


# Tool imports


TOKEN_FILE = 'token.json'
CREDENTIALS_FILE = 'credentials.json'

SCOPES = {
    'source_of_scopes_url': "https://docs.googleapis.com/$discovery/rest?version=v1",
    'all_access_to_everything_on_drive': "https://www.googleapis.com/auth/drive",
    'all_access_to_specific_file_on_drive': "https://www.googleapis.com/auth/drive.file",
    'read_all_google_docs': "https://www.googleapis.com/auth/documents.readonly",
    'all_access_to_all_google_docs': "https://www.googleapis.com/auth/documents",
    'see_and_download_all_files_in_drive': "https://www.googleapis.com/auth/drive.readonly",
    'google_docs': {
        'batchUpdate': ["https://www.googleapis.com/auth/documents"],
        'get': ["https://www.googleapis.com/auth/documents.readonly"],
        'create': ["https://www.googleapis.com/auth/documents"],
        'copy': ["https://www.googleapis.com/auth/drive"],
        'share': ["https://www.googleapis.com/auth/drive"]
    }
}

MIME_TYPES = {
    'folder': 'application/vnd.google-apps.folder',
}
