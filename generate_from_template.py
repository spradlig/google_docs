"""
Module:
    generate_from_template.py

Description:
    This file contains a convenience function for generating a new file from a
    template.

Usage:
    import generate_from_template

    new_doc = generate_from_template.execute(
        template=<TEMPLATE_ID>,
        new_file_name=<new file name>,
        replacements=<replacements>,
        folder=<folder where the new file lives>
    )

Notes:


References:
    https://developers.google.com/docs/api/quickstart/python
    https://developers.google.com/docs/api/how-tos/documents

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
    1)
"""

# Standard library imports


# Tool imports
from auth import get_service
from constants import SCOPES
from files import copy_file


# https://developers.google.com/docs/api/how-tos/merge
def execute(template: str, new_file_name: str, replacements: list[dict], folder: [str, None] = None):
    """
    Convenience function for generating a new file from a template and executing the replacements.

    Args:
        template:           ID string for the template file.
        new_file_name:      The full name of the file (not a file ID since the file
                            doesn't exist yet).
        replacements:       List of dicts where each dict contains the
                            following information:
                            {
                                'replaceAllText':
                                {
                                    'containsText':
                                    {
                                        'text': '<some token>',
                                        'matchCase':  'true'
                                    },
                                    'replaceText': <text to replace token>,
                                }
                            }
        folder:             Full path of the folder where you want the new file
                            to live.

    Returns:
        The result from the Google API. It should includes details about the new
        file.
    """

    if folder is None:
        # Make the folder the root folder for the user's drive.
        folder = '/'

    # Copy the template to a new file name.
    new_doc_id = copy_file(template=template, new_file_name=new_file_name, folder=folder)

    # Use batchUpdate to finish the document.
    service = get_service(scopes=SCOPES['google_docs']['batchUpdate'])

    result = service.documents().batchUpdate(
        documentId=new_doc_id,
        body={'requests': replacements}
    ).execute()

    return result
