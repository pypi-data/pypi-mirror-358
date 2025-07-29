import re
import sys
import logging
import getpass

from colorama import init, Fore, Style

init(autoreset=True)

TOKEN_PREFIXES = ["ghp_", "gho_", "ghu_", "ghs_", "github_pat_"]
TOKEN_RE = re.compile(rf"({'|'.join(map(re.escape, TOKEN_PREFIXES))})[a-zA-Z0-9_]+")

class FriendlyFormatter(logging.Formatter):
    def format(self, record):
        msg = record.getMessage()

        try:
            username = getpass.getuser()
            if username and username in msg:
                msg = msg.replace(username, "~")

            if "@" in msg:
                msg = TOKEN_RE.sub("[GITHUB_TOKEN_HIDDEN]", msg)

            if record.levelno == logging.INFO:
                return f"{Fore.RED} - {Style.RESET_ALL}{msg}{Style.RESET_ALL}"
            elif record.levelno == logging.WARNING:
                return f"{Fore.YELLOW}Warning:{Style.RESET_ALL} {msg}"
            elif record.levelno >= logging.ERROR:
                return f"{Fore.RED}Error:{Style.RESET_ALL} {msg}"
        except Exception as e:
            return f"{Fore.RED}Exception occurred in friendly formatter: {e}{Style.RESET_ALL}"

        return msg

def setup_logger():
    logger = logging.getLogger("secpack")
    logger.handlers.clear()
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(FriendlyFormatter())
    logger.addHandler(handler)
    return logger

logger = setup_logger()

# --- Utility for secure error logging ---
def log_error(msg: str, exc: Exception, verbose: bool):
    logger.error(f"{msg}: {exc}")