from requests import Session, RequestException
from typing import Literal, Dict, Any, Optional


class FailedCaptcha(Exception): pass
class InvalidKey(Exception): pass
class InvalidMethod(Exception): pass
class FailedBalance(Exception): pass


MethodTypes = Literal[
    "outlook", "twitter", "twitter_unlock", "roblox_signup", "roblox_login",
    "roblox_join", "ea", "github-signup", "demo", "roblox_wall", "airbnb-register"
]

BrowserTypes = Literal[
    "chrome", "opera", "edge", "firefox", "chrome mac", "firefox mac",
    "chrome linux", "firefox linux", "safari"
]

OperatingSystemTypes = Literal["windows", "mac", "linux"]


class CaptchaSolver:
    _session = Session()
    _base_url = "https://api.captchasolver.ai/"

    def __init__(self, method: MethodTypes, key: str):
        if not key or not isinstance(key, str):
            raise InvalidKey("CaptchaSolver key must be a non-null string")
        if method not in MethodTypes.__args__:
            raise InvalidMethod(f"{method} is not a valid method. Valid options: {MethodTypes.__args__}")

        self.key = key
        self.method = method

    def solve(
        self,
        proxy: str,
        blob: Optional[str] = None,
        method: Optional[MethodTypes] = None,
        browser: BrowserTypes = "firefox",
        operating_system: OperatingSystemTypes = "windows",
        version: int = 139,
    ) -> str:

        method = method or self.method

        if method not in MethodTypes.__args__:
            raise InvalidMethod(f"{method} is not a valid method. Valid options: {MethodTypes.__args__}")

        payload = {
            "key": self.key,
            "method": method,
            "proxy": proxy,
            "browser": browser,
            "os": operating_system,
            "version": version,
        }

        if blob:
            payload["blob"] = blob

        try:
            response = self._session.post(f"{self._base_url}api/solve", json=payload)
            response.raise_for_status()

            result: Dict[str, Any] = response.json()
            if "Failed:" in result.get("msg", ""):
                raise FailedCaptcha(result["msg"])

            token = result.get("token")
            if not token:
                raise FailedCaptcha("No token received from CaptchaSolver")

            return token

        except RequestException as e:
            raise FailedCaptcha(f"Network error while solving captcha: {e}") from e
        except (ValueError, KeyError) as e:
            raise FailedCaptcha(f"Invalid response format: {e}") from e

    def balance(self) -> int:
        try:
            response = self._session.get(
                f"{self._base_url}api/getBalance", params={"key": self.key}
            )
            response.raise_for_status()

            result: Dict[str, Any] = response.json()
            balance = result.get("balance")
            if balance is None:
                raise FailedCaptcha("No balance received from CaptchaSolver")

            return int(balance)

        except RequestException as e:
            raise FailedBalance(f"Network error while fetching balance: {e}") from e
        except (ValueError, KeyError) as e:
            raise FailedBalance(f"Invalid response format: {e}") from e
