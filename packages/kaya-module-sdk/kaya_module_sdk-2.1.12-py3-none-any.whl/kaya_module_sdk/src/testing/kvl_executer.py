# External dependencies
import logging
import importlib.util
import mypy.api as mypy_api

# import pysnooper

from typing import Any
from flake8.api import legacy as flake8

# Internal dependencies
from kaya_module_sdk.src.exceptions.module_not_found import ModuleNotFoundException
from kaya_module_sdk.src.utils.metadata.equal import EQ
from kaya_module_sdk.src.utils.metadata.greater import GT
from kaya_module_sdk.src.utils.metadata.greater_or_equal import GTE
from kaya_module_sdk.src.utils.metadata.less import LT
from kaya_module_sdk.src.utils.metadata.less_or_equal import LTE
from kaya_module_sdk.src.utils.metadata.max_len import MaxLen
from kaya_module_sdk.src.utils.metadata.maximum import Max
from kaya_module_sdk.src.utils.metadata.min_len import MinLen
from kaya_module_sdk.src.utils.metadata.minimum import Min
from kaya_module_sdk.src.utils.metadata.value_range import ValueRange
from kaya_module_sdk.src.utils.metadata.eq_len import EQLen
from kaya_module_sdk.src.utils.metadata.const import Const
from kaya_module_sdk.src.utils.metadata.not_const import NotConst
from kaya_module_sdk.src.utils.metadata.order import Order

log = logging.getLogger(__name__)

type Check = dict[str, list[dict[str, Any]]]
type Report = dict[str, Check]


class KVLE:
    """
    [ KVL(E) ]: Kaya Validation Framework (Executor)

    Responsibilities:
      - Run linters (flake8), type checkers (mypy) and module validations.
      - Load and apply metadata constraint rules.
      - Aggregate validation results for rules, metadata, and source.
    """

    def __init__(self, **context: Any) -> None:
        self.context = context
        self.check: Report = {
            "rules": {"ok": [], "nok": []},
            "meta": {"ok": [], "nok": []},
            "source": {"ok": [], "nok": []},
        }

    # @pysnooper.snoop()
    def check_package_installed(self, test: dict) -> bool:
        try:
            importlib.util.find_spec(test["package"])
        except ModuleNotFoundError as e:
            raise ModuleNotFoundException(f'Package {test["package"]} is not installed!') from e
        return True

    # @pysnooper.snoop()
    def load_constraint_rules(self, *rules: str) -> dict:
        matches = []
        metadata_classes = [
            EQ,
            GT,
            GTE,
            LT,
            LTE,
            MaxLen,
            Max,
            MinLen,
            Min,
            ValueRange,
            EQLen,
            Const,
            NotConst,
            Order,
        ]
        for rule in rules:
            for mcls in metadata_classes:
                try:
                    instance = mcls(None, None) if ";" in rule else mcls(None)
                    instance.load(rule)
                except Exception:
                    continue
                matches.append(instance)
        # NOTE: Only include those with complete data.
        formatted = {item.__class__.__name__: item for item in matches if None not in item._data.values()}
        return formatted if rules and formatted else {}

    # @pysnooper.snoop()
    def check_rules(self) -> dict:
        """Runs constraint rules checks on module inputs/outputs and aggregates results."""
        package_instance = self.context.get("module_package", {}).get("instance")
        package_name = package_instance.config.name
        submodules = package_instance.modules
        rules_report: dict = {"ok": [], "nok": []}
        for module_name, module_obj in submodules.items():
            error_flag = False
            module_record = {
                "package": package_name,
                "module": module_name,
                "functions": {"main": []},
            }
            # NOTE: Process manifest validations
            manifest = module_obj.manifest
            if not manifest:
                error_flag = True
                module_record["manifest"] = {"required": True, "set": False}
                module_record["error"] = error_flag
                rules_report["nok"].append(module_record)
                continue
            if not isinstance(manifest, dict) or not manifest.get("inputs"):
                error_flag = True
                module_record["manifest"] = {
                    "required": True,
                    "set": True,
                    "valid": False,
                    "value": manifest,
                }
                module_record["error"] = error_flag
                rules_report["nok"].append(module_record)
                continue
            # NOTE: Process input validations.
            for arg in manifest["inputs"]:
                if not arg.get("validations"):
                    continue
                loaded = self.load_constraint_rules(*arg["validations"])
                if arg["validations"] and not loaded:
                    error_flag = True
                for cname in loaded:
                    values = list(loaded[cname]._data.values())
                    if len(values) == 1:
                        values = values[0]
                    module_record["functions"]["main"].append(
                        {
                            "name": cname,
                            "target": "inputs",
                            "verb": cname.lower(),
                            "field": arg["label"],
                            "rule": [cname, values],
                            "error": error_flag,
                        }
                    )
            # NOTE: Process output validations.
            for ret in manifest["outputs"]:
                if not ret.get("validations"):
                    continue
                loaded = self.load_constraint_rules(*ret["validations"])
                if ret["validations"] and not loaded:
                    error_flag = True
                for cname in loaded:
                    values = list(loaded[cname]._data.values())
                    if len(values) == 1:
                        values = values[0]
                    module_record["functions"]["main"].append(
                        {
                            "name": cname,
                            "target": "outputs",
                            "verb": cname.lower(),
                            "field": ret["label"],
                            "rule": [cname, values],
                            "error": error_flag,
                        }
                    )
            module_record["error"] = error_flag
            if error_flag:
                rules_report["nok"].append(module_record)
            else:
                rules_report["ok"].append(module_record)
        self.check["rules"] = rules_report
        return self.check["rules"]

    # @pysnooper.snoop()
    def check_meta(self, module_data: dict, report: bool = True, **kwargs: Any) -> dict:
        """Runs metadata validations and aggregates results."""
        package_instance = self.context.get("module_package", {}).get("instance")
        package_name = package_instance.config.name
        package_version = package_instance.config.version
        submodules = package_instance.modules
        meta_report: Check = {"ok": [], "nok": []}
        for module_name, module_obj in submodules.items():
            error_flag = False
            module_record = {
                "package": package_name,
                "package_version": package_version,
                "module": module_name,
            }
            if not module_obj.config:
                error_flag = True
                module_record["config"] = {"required": True, "set": False}
            for key in module_obj.config._mandatory:
                value = module_obj.config.__dict__.get(key)
                if not value:
                    error_flag = True
                    module_record[key] = {"required": True, "set": False}
                    continue
                valid = (type(value) in (str,)) if key != "version" else (type(value) in (str, float))
                module_record[key] = {
                    "required": True,
                    "set": True,
                    "valid": valid,
                    "value": value,
                }
            manifest = module_obj.manifest
            if not manifest:
                error_flag = True
                module_record["manifest"] = {
                    "required": True,
                    "set": False,
                    "valid": False,
                    "value": manifest,
                }
            elif not isinstance(manifest, dict):
                error_flag = True
                module_record["manifest"] = {
                    "required": True,
                    "set": True,
                    "valid": False,
                    "value": manifest,
                }
            if error_flag:
                meta_report["nok"].append(module_record)
            else:
                meta_report["ok"].append(module_record)
        self.check["meta"] = meta_report
        return self.check["meta"]

    # @pysnooper.snoop()
    def check_source(self, loaded_files: dict) -> dict:
        """Runs source code validations (flake8, mypy) and aggregates results."""
        source_report: dict = {"ok": [], "nok": []}
        for file_path, _ in loaded_files.items():
            errors: list = []
            style_guide = flake8.get_style_guide()
            flake8_report = style_guide.check_files([file_path])
            if flake8_report.total_errors > 0:
                flake8_output = [
                    {
                        error[0]: [error[1], error[2]]
                        for error in flake8_report._application.file_checker_manager.results
                    }
                ]
                errors.append({"tool": "flake8", "output": flake8_output})
            mypy_result = mypy_api.run([file_path])
            mypy_stdout, mypy_stderr, mypy_exit_status = mypy_result
            if mypy_stderr or mypy_exit_status:
                errors.append(
                    {
                        "tool": "mypy",
                        "output": mypy_stdout + mypy_stderr,
                        "exit": mypy_exit_status,
                    }
                )
            if errors:
                source_report["nok"].append({"path": file_path, "errors": errors, "result": "NOK"})
            else:
                source_report["ok"].append({"path": file_path, "errors": [], "result": "OK"})
        self.check["source"] = source_report
        return self.check["source"]
