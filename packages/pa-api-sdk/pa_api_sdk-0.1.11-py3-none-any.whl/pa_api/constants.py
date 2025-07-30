# https://docs.paloaltonetworks.com/pan-os/9-1/pan-os-panorama-api/get-started-with-the-pan-os-rest-api/pan-os-rest-api-error-codes
PANORAMA_ERRORS = {
    1: "The operation was canceled, typically by the caller.",
    2: "Unknown internal server error.",
    3: "Bad request. The caller specified an invalid parameter.",
    4: (
        "Gateway timeout. A firewall or Panorama module timed out "
        "before a backend operation completed."
    ),
    5: "Not found. The requested entity was not found.",
    6: "Conflict. The entity that the caller attempted to create already exists.",
    7: (
        "Forbidden. The caller does not have permission "
        "to execute the specified operation."
    ),
    8: "Resource exhausted. Some resource has been exhausted.",
    9: (
        "Failed precondition. The operation was rejected because the system"
        " is not in a state required for the execution of the operation."
    ),
    10: "Aborted because of conflict. A typical cause is a concurrency issue.",
    11: (
        "Out of range. The operation was attempted past a valid range."
        " And example is reaching an end-of-file."
    ),
    12: (
        "Not implemented. The operation is disabled,"
        " not implemented, or not supported."
    ),
    13: (
        "Internal server error. An unexpected and potentially"
        "serious internal error occurred."
    ),
    14: "Service unavailable. The service is temporarily unavailable.",
    15: ("Internal server error. Unrecoverable data loss or data corruption occurred."),
    16: (
        "Unauthorized. The request does not have valid authentication"
        "credentials to perform the operation."
    ),
}
SUCCESS_CODE = 19
