import os

from dotenv import load_dotenv

load_dotenv()

def is_the_mcp_to_run_in_server_mode_or_std_dio():
    run_in_remote_server_mode = os.getenv("RUN_REMOTE_SERVER_MODE", "False")
    return run_in_remote_server_mode.lower() == "true"