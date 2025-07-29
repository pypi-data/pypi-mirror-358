# External dependencies
# import pysnooper
import json
import subprocess
import pytest
import inspect
import socket

from functools import wraps
from logging import getLogger, Logger
from importlib.util import find_spec
from importlib import import_module
from typing import Callable, Optional, get_type_hints, get_args, Any

# Internal dependencies
from kaya_module_sdk.src.exceptions.kit_failure import KITFailureException
from kaya_module_sdk.src.exceptions.module_not_found import ModuleNotFoundException
from kaya_module_sdk.src.module.arguments import Args
from kaya_module_sdk.src.utils.check import is_matrix
from kaya_module_sdk.src.datatypes.classifier import KClassifier

# Global logger for this module
log: Logger = getLogger(__name__)


class KIT:
    """
    [ KIT ]: Kaya Integration Testing Framework

    This framework provides:
    - Extraction of test method parameters.
    - Dynamic determination of the web server endpoint based on the test class name.
    - Execution of HTTP requests via `curl` (using subprocess).
    - Injection of the HTTP response into test functions as a keyword argument.
    """

    # Configuration for the web server
    _webserver_protocol: str = "http"
    _webserver_host: str = "0.0.0.0"
    _webserver_port: str = "8080"
    _webserver_method: str = "GET"

    @classmethod
    def run(
        cls,
        inputs: Args,
        package: str = "",
        module: str = "",
        expected_error: Optional[int | type[Exception]] = None,
    ) -> Callable:
        """
        [ DESCRIPTION ]: Decorator to wrap a test function.
            - Extracts parameters from an Args object.
            - Checks necessary preconditions.
            - Constructs and sends an HTTP request.
            - Processes the response and instantiates a result using the test function's result constructor.
            - If an expected error is provided, verifies that the response meets that expectation.
            - Passes the processed result to the test function.
        """

        # @pysnooper.snoop()
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                # NOTE: Extract keyword parameters from the test function
                method_defaults = cls._get_method_kwargs(func)

                # NOTE: Determine module endpoint: if package and module are provided, use them;
                # otherwise, derive endpoint from the name of the inputs class.
                class_name = inputs.__class__.__name__
                module_endpoint = module if (module and package) else class_name.replace("Args", "")

                # NOTE: Ensure all preconditions are met before executing the request.
                if not cls.check_preconditions(package=package, module=module_endpoint):
                    raise KITFailureException("Failed to verify preconditions")

                # NOTE: Build the request payload from the inputs object's dictionary.
                request_payload = {
                    k.strip("_"): v for k, v in inputs.__dict__.items() if k.strip("_") not in ("errors")
                }

                # NOTE: Execute the HTTP request.
                response = cls.module_request(module_endpoint, request_payload)
                ret_type_hints = (
                    {}
                    if not list(method_defaults.items())
                    else {
                        key.strip("_"): val for key, val in get_type_hints(list(method_defaults.items())[0][1]).items()
                    }
                )
                if response["exit"] == 0:
                    for key, val in response.copy()["response"].items():
                        if key not in ret_type_hints:
                            response["response"][key] = val
                            continue
                        matrix_flag = is_matrix(ret_type_hints[key])
                        expected_key_type = (
                            (get_args(ret_type_hints[key])[0] if get_args(ret_type_hints[key]) else type(val))
                            if not matrix_flag
                            else get_args(get_args(ret_type_hints[key])[0])[0]
                        )
                        try:
                            if response["response"][key] and matrix_flag:
                                casted_return = [
                                    [cls._type_cast(item, expected_key_type) for item in row]
                                    for row in response["response"][key]
                                ]
                            elif response["response"][key] and isinstance(val, list):
                                casted_return = [
                                    cls._type_cast(item, expected_key_type) for item in response["response"][key]
                                ]
                            else:
                                casted_return = cls._type_cast(response["response"][key], expected_key_type)
                        except Exception as e:
                            response["response"]["errors"].append(str(e))
                            break
                        response["response"][key] = casted_return

                # NOTE: Instantiate the result using a "result" constructor provided in the test signature.
                rets_constructor = method_defaults.get("result")
                if rets_constructor is None:
                    raise KITFailureException("No result function specified in test method signature.")
                rets = rets_constructor(**response["response"])
                # NOTE: Handle expected errors if provided.
                if expected_error:
                    if isinstance(expected_error, int):
                        assert (
                            response["status_code"] == expected_error
                        ), f"Expected status {expected_error}, got {response['status_code']}"
                    elif issubclass(expected_error, Exception):
                        with pytest.raises(expected_error):
                            raise expected_error(f"Unexpected response: {response}")

                # NOTE: Call the original test function with the computed result for further user defined assertions
                return func(*args, result=rets)

            return wrapper

        return decorator

    @classmethod
    def check_preconditions(cls, package: str = "", module: str = "") -> bool:
        """
        Aggregates general and module-specific precondition checks.
        Returns True if all checks pass.
        """
        check_results: dict = {}
        preconditions: dict = {
            "general": {
                "webserver_running": cls.check_webserver_running,
            },
            "module_specific": {
                "package_installed": cls.check_package_installed,
                "module_exists": cls.check_module_exists,
            },
        }
        for name, check_func in preconditions["general"].items():
            check_results[name] = check_func()
        if package and module:
            for name, check_func in preconditions["module_specific"].items():
                check_results[name] = check_func(package, module)
        if not all(check_results.values()):
            log.error("KIT Preconditions not met:")
            for check, result in check_results.items():
                if not result:
                    log.error(" - %s", check)
        return all(check_results.values())

    @classmethod
    def check_webserver_running(cls) -> bool:
        """Verifies if the configured web server is running."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            result = sock.connect_ex((cls._webserver_host, int(cls._webserver_port)))
            return result == 0

    @classmethod
    def check_package_installed(cls, package: str, module: str) -> bool:
        """Checks whether a package is installed."""
        try:
            find_spec(package)
        except ModuleNotFoundError as e:
            raise ModuleNotFoundException(f"Package {package} is not installed!") from e
        except ValueError as e:
            raise ModuleNotFoundException(f"Package {package} does not have a spec!") from e
        return True

    @classmethod
    def check_module_exists(cls, package: str, module: str) -> bool:
        """Verifies that a specific module exists within the given package."""
        try:
            module_instance = import_module(f"{package}.module")
            return hasattr(module_instance, module)
        except ImportError:
            return False

    @classmethod
    def module_request(cls, module: str, request_body: dict) -> dict:
        """
        Executes an HTTP request to the given module endpoint using curl.
        Returns a dictionary containing:
            - 'response': Parsed JSON or raw output.
            - 'errors': Any errors extracted from the response.
            - 'exit': The curl exit code.
        """
        request_json = json.dumps(request_body)
        cmd = (
            f"curl -X {cls._webserver_method} -H \"Content-Type: application/json\" -d '{request_json}' "
            f"http://{cls._webserver_host}:{cls._webserver_port}/{module}"
        )
        run_stdout, run_stderr, run_exit = cls.shell_cmd(cmd)
        sanitized_out = run_stdout.replace("\\n", "").strip(" ")
        response_text = run_stdout + run_stderr if run_exit else sanitized_out
        errors = []
        try:
            json_out = json.loads(sanitized_out)
            if isinstance(json_out, dict):
                if "errors" in json_out:
                    errors += json_out["errors"]
                elif "error" in json_out:
                    errors.append(json_out["error"])
        except (TypeError, ValueError):
            pass
        if run_exit:
            errors.append(run_stderr)
        try:
            parsed_response = json.loads(response_text) if not run_exit else run_stdout
        except (TypeError, ValueError):
            parsed_response = response_text

        return {
            "response": parsed_response,
            "errors": errors,
            "exit": run_exit,
        }

    @classmethod
    def shell_cmd(cls, command: str, user: Optional[str] = None) -> tuple[str, str, int]:
        """
        Executes a shell command using subprocess.
        Returns a tuple: (stdout, stderr, exit code).
        """
        log.debug("Issuing system command: %s", command)
        if user:
            command = f"su {user} -c '{command}'"
        with subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
            output, errors = process.communicate()
            log.debug("Output: %s, Errors: %s", output, errors)
            return (
                output.decode("utf-8").rstrip("\n"),
                errors.decode("utf-8").rstrip("\n"),
                process.returncode,
            )

    @classmethod
    def _get_method_kwargs(cls, func: Callable) -> dict:
        """
        Returns a dictionary mapping keyword parameter names to their default values
        for the provided function. Only includes parameters that have default values.
        """
        sig = inspect.signature(func)
        return {
            k: v.default if v.default is not inspect.Parameter.empty else None
            for k, v in sig.parameters.items()
            if v.default is not inspect.Parameter.empty
        }

    @classmethod
    def _type_cast(cls, value: str, target_type: type | None) -> Any:
        if target_type not in {int, float, str, bool, None, Exception}:
            raise ValueError(f"Unsupported type: {target_type}")
        if target_type in (None, Exception):
            return value
        try:
            # Handle boolean separately as `bool("False")` evaluates to `True`
            if target_type is bool:
                return value.strip().lower() in {"true", "1", "yes"}
            # For other types (int, float, str)
            return value if target_type is None else target_type(value)
        except Exception as e:
            raise ValueError(f"Failed to cast '{value}' to {target_type}! Details: {e}") from e


# CODE DUMP
