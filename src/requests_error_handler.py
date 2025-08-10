
time_before_retry = 60
max_errors_allowed = 3
error_count = 0

def init_error_handler() -> tuple[int, int, int]:
    return(time_before_retry, max_errors_allowed, error_count)

def handle_response_not_ok(error_count: int) -> tuple[int, int]:
    error_count = error_count+1
    remaining_errors = max_errors_allowed-error_count

    return(error_count, remaining_errors)
    
def handle_request_exception(error_count: int) -> tuple[int, int]:
    error_count = error_count+1
    remaining_errors = max_errors_allowed-error_count

    return(error_count, remaining_errors)
    
def raise_no_more_tries_exception(max_errors_allowed: int):
    raise RuntimeError("Unable to complete request after trying %s times.", max_errors_allowed)