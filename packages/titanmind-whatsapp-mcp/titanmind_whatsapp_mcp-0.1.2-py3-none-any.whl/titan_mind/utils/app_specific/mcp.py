from titan_mind.utils.app_specific.utils import is_the_mcp_to_run_in_server_mode_or_std_dio
from titan_mind.utils.general.mcp import get_the_headers_from_the_current_mcp_request
import os


def get_the_api_key() -> str:
    if is_the_mcp_to_run_in_server_mode_or_std_dio():
        api_key = get_the_headers_from_the_current_mcp_request().get("api-key")
    else:
        api_key = os.environ.get("api-key")

    return api_key


def get_the_business_code() -> str:
    if is_the_mcp_to_run_in_server_mode_or_std_dio():
        business_code = get_the_headers_from_the_current_mcp_request().get("bus-code")
    else:
        business_code = os.environ.get("bus-code")

    return business_code
