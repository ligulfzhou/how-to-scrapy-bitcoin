from flask import Blueprint, jsonify
from exception import APIError

eh_bp = Blueprint('errorhandler', __name__)


@eh_bp.app_errorhandler(APIError)
def handle_exception(err):
    """Return custom JSON when APIError or its children are raised"""
    response = {"error": err.description, "message": ""}
    if len(err.args) > 0:
        response["message"] = err.args[0]

    # Add some logging so that we can monitor different types of errors
    # app.logger.error(f"{err.description}: {response["message"]}")
    return jsonify(response), err.code


@eh_bp.app_errorhandler(500)
def handle_exception(err):
    """Return JSON instead of HTML for any other server error"""
    # app.logger.error(f"Unknown Exception: {str(err)}")
    # app.logger.debug(''.join(traceback.format_exception(etype=type(err), value=err, tb=err.__traceback__)))
    response = {"error": "Internal Server Error"}
    return jsonify(response), 500
