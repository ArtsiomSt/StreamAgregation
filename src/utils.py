def get_available_params(params: dict, available_params: list[str]) -> dict:
    result = {}
    for param_key, param_value in params.items():
        if param_key in available_params and param_value is not None:
            result[param_key] = param_value
    return result
