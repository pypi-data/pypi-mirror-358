from erioon.client import ErioonClient

def Auth(credential_string):
    """
    Authenticates a user using a colon-separated email:password string.

    Parameters:
    - credential_string (str): A string in the format "email:password"

    Returns:
    - ErioonClient instance: An instance representing the authenticated user.
      If authentication fails, the instance will contain the error message.

    Example usage:
    >>> from erioon.auth import Auth
    >>> client = Auth("<API_KEY>:<EMAIL>:<PASSWORD>")
    >>> print(client)  # prints user_id if successful or error message if not
    """
    api, email, password = credential_string.split(":")
    return ErioonClient(api ,email, password)
