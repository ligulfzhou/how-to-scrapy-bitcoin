

class APIError(Exception):
    """All custom API Exceptions"""
    pass


class APIParamError(APIError):
    code = 400
    description = "Parameter Invalid"
