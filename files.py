"""
Module:
    files.py

Description:
    This file holds a set of doc file related utilities.

Usage:
    from files import replacement_template, get_folders, create_folder, copy_file, share_file


Notes:


References:
    Replace tokens in a template doc: https://developers.google.com/docs/api/how-tos/merge
    Folders: https://developers.google.com/drive/api/guides/folder
    Sharing:
        https://developers.google.com/drive/api/guides/manage-sharing
        https://developers.google.com/drive/api/v3/reference/permissions
        https://stackoverflow.com/questions/11665215/is-it-possible-to-share-a-file-publicly-through-google-drive-api


License:
    GNU General Public License v3.0
    See LICENSE.MD

"""
import constants

"""
Version History:
    Original:
        GS | 23-Feb-23
"""

"""
TODOs:
    1)  
"""

# Standard library imports
import os
import copy
import json
from googleapiclient.errors import HttpError

# Tool imports
from auth import get_service
from constants import SCOPES


def replacement_template(token: str, new_value: str) -> dict:
    """
    The batchUpdate in Google's API requires a list of dict. The minimum
    dict required for text swapping is returned by this function.

    Args:
        token:          The token/string in the template doc to be
                        replaced.
        new_value:      The string to replace the token.

    Returns:
        (dict)          A dict in the correct format for batchUpdate.
    """

    return {
        'replaceAllText':
            {
                'containsText':
                    {
                        'text': token,
                        'matchCase': 'true'
                    },
                'replaceText': new_value,
            }
    }


def get_folders() -> [dict, None]:
    """
    Get all folders in the user's Google drive.

    Returns:
        (dict)          A dict with
                            key: full folder path from root
                            value: folder ID needed for all API operations
    """

    def build_directory_tree(res: dict) -> dict:

        tree = {'/': ''}
        parent_ids = []
        ids = []
        for file in res['files']:
            for parent_id in file['parents']:
                if parent_id not in parent_ids:
                    parent_ids.append(parent_id)

            ids.append(file['id'])

        for parent_id in parent_ids:
            if parent_id not in ids:
                # This is the Drive root level directory ID.
                if len(tree['/']) == 0:
                    tree['/'] = parent_id
                elif tree['/'] != parent_id:
                    raise ValueError(f'Current Root ID is {tree["/"]}. Another root, {parent_id}, is present.')

        # Remove the Root ID from the parent IDs list.
        parent_ids.remove(tree['/'])

        remainder = copy.copy(result['files'])
        removals = []
        for file in remainder:
            if file['parents'][0] == tree['/']:
                tree[file['id']] = f'/{file["name"]}'
                removals.append(file)

        for file in removals:
            remainder.remove(file)

        while len(remainder) > 0:
            removals = []
            for file in remainder:
                for parent_id in file['parents']:
                    if parent_id in tree:
                        tree[file['id']] = tree[parent_id] + f'/{file["name"]}'
                        removals.append(file)

            for file in removals:
                remainder.remove(file)

        return {v: k for k, v in tree.items()}

    try:
        service = get_service(scopes=SCOPES['google_docs']['share'], service_type='drive')

        resource = service.files()
        
        query = "mimeType='" + constants.MIME_TYPES["folder"] + "'"
        result = resource.list(
            q=query,
            fields="files(id, name, parents)"
        ).execute()      # The list function can also take a pageSize to limit the # of returns.

        tree = build_directory_tree(res=result)

        return tree

    except HttpError as error:
        print(f'An error occurred: {error}')
        return None


def create_folder(folder: str, parent_folder: str = '/') -> [str, None]:
    """
    Create a folder on the user's Google drive.

    Args:
        folder:             The name of a folder under the parent_folder.
        parent_folder:      The full folder path of the parent folder.
                            If the desired parent folder is the Google
                            drive root then pass in '/'. (Optional, this
                            arg defaults to the root folder.)

    Returns:
        (str)               If there weren't any errors, then the ID of the folder
                            after creation.
                            Otherwise, this function returns None.
    """

    try:
        service = get_service(scopes=SCOPES['google_docs']['share'], service_type='drive')

        folders = get_folders()

        if parent_folder in folders:
            parent_id = folders[parent_folder]
        else:
            raise ValueError(f'The parent folder does not exist in the available folders - \n{json.dumps(folders, indent=4)}')

        folder_metadata = {
            'name': folder,
            'mimeType': constants.MIME_TYPES['folder'],
            'parents': [parent_id]
        }
        folder = service.files().create(body=folder_metadata, fields='id').execute()

        return folder.get('id')

    except HttpError as error:
        print(f'An error occurred: {error}')
        return None


def copy_file(template: str, new_file_name: str, folder: [str, None] = None) -> [str, None]:
    """
    Copy a file to a new folder and file name. This works for any file but was built
    with the intention of copying a template to a new file name before executing the
    batchUpdate replacements.

    Args:
        template:           ID string for the template file.
        new_file_name:      The full name of the file (not a file ID since the file
                            doesn't exist yet).
        folder:             Full path of the folder where you want the new file
                            to live.

    Returns:
        (str)               If there weren't any errors, then the ID of the new file
                            after creation.
                            Otherwise, this function returns None.
    """

    try:
        service = get_service(scopes=SCOPES['google_docs']['copy'], service_type='drive')

        folders = get_folders()

        body = {
            'name': new_file_name
        }

        if folder is not None:
            if folder not in folders:
                parts = os.path.split(folder)
                create_folder(parts[1], parts[0])
                folders = get_folders()

            body['parents'] = [folders[folder]]

        drive_response = service.files().copy(
            fileId=template, body=body).execute()

        return drive_response.get('id')

    except HttpError as error:
        print(f'An error occurred: {error}')
        return None


def share_file(file: str, user: str) -> str:
    """
    This function provides the necessary functionality for sharing a file or folder
    with any email address provided.

    Args:
        file:       ID string for the file or folder to be shared.
        user:       Email address of the user to share the file/folder with.
                    Example: user@example.com

    Returns:
        (str)       If no error occurs, then the URL of the shared item is returned.
                    Otherwise, an error message is returned.
    """

    service = get_service(scopes=SCOPES['google_docs']['share'], service_type='drive')
    ids = []

    def callback(request_id, response, exception):
        # This comes directly from Google's sample code.
        if exception:
            # Handle error
            print(exception)
        else:
            print(f'Request_Id: {request_id}')
            print(F'Permission Id: {response.get("id")}')
            ids.append(response.get('id'))

    try:
        # pylint: disable=maybe-no-member
        batch = service.new_batch_http_request(callback=callback)
        user_permission = {
            'type': 'user',
            'role': 'reader',
            'emailAddress': user
        }
        batch.add(
            service.permissions().create(
                fileId=file,
                body=user_permission,
                fields='id',
            )
        )

        batch.execute()

        if len(ids) > 0:
            return f'https://drive.google.com/open?id={file}'
        else:
            return f'Error: No permissions were granted.'

    except HttpError as error:
        print(f'An error occurred: {error}')
        ids = None

        return f'Error: {error}'
