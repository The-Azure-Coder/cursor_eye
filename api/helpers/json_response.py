from flask import jsonify

def success(status_code=200, message="", data=None):
    """
    Generates a standardized success JSON response for Flask routes.

    Args:
        status_code (int): HTTP status code to return. Default is 200.
        message (str): A human-readable message.
        data (dict | list | None): Optional data payload.

    Returns:
        Response: Flask JSON response object.
    """
    response = {
        "status": status_code,
        "message": message,
        "data": data or {} or []
    }
    return jsonify(response), status_code


def error(status_code=400, message="An error occurred", errors=None):
    """
    Generates a standardized error JSON response for Flask routes.

    Args:
        status_code (int): HTTP status code to return. Default is 400.
        message (str): Error message description.
        errors (dict | list | None): Additional error details if available.

    Returns:
        Response: Flask JSON response object.
    """
    response = {
        "status": status_code,
        "message": message,
        "errors": errors or {}
    }
    return jsonify(response), status_code
