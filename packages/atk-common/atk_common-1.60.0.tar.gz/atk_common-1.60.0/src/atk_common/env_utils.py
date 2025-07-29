import os
from atk_common.log_utils import add_log_item

def val_str(value):
    if value is None:
        return 'Empty'
    if isinstance(value, str):
        return value
    return str(value)

def get_env_value(key, abort_on_error=True):
    val = os.environ.get(key)
    if val is None and abort_on_error:
        err_msg = f"Environment variable '{key}' is not set."
        add_log_item(err_msg)
        raise ValueError(err_msg)
    add_log_item(key + ':' + val_str(val))
    return val
