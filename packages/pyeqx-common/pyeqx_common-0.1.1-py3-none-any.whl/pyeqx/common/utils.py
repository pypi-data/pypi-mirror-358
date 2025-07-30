from importlib.metadata import version, PackageNotFoundError
from packaging.requirements import Requirement
from packaging.version import parse

from pyeqx.common.result import FunctionExecuteResult


class PackageVersionNotMatchException(Exception):
    def __init__(self, name: str, installed_version: str, desired_version: str):
        self.name = name

        super().__init__(
            f"Package {name} found, version {installed_version}, but it is higher than desired version {desired_version}. Please check the package version."
        )


class PackageNotFoundException(Exception):
    def __init__(self, name: str, version: str, path: str):
        self.name = name
        self.version = version
        self.path = path

        super().__init__(
            f"Package {name} ({version}) not found. Please install via pip. (pip3 install --upgrade {path})"
        )


def check_dependencies(packages: list[str]) -> FunctionExecuteResult:
    for package in packages:
        # check_result = __check_package(
        #     name=package, package_version=package["version"], package_path=package
        # )
        check_result = __check_package(package=package)

        if not check_result.is_success:
            return FunctionExecuteResult(error=check_result.error)

    return FunctionExecuteResult(data=True)


def __check_package(package: str) -> FunctionExecuteResult:
    try:
        req = Requirement(package)
        installed_version = version(req.name)

        if not req.specifier.contains(installed_version, prereleases=True):
            return FunctionExecuteResult(
                error=PackageVersionNotMatchException(
                    name=req.name,
                    installed_version=installed_version,
                    desired_version=req.specifier,
                )
            )

        return FunctionExecuteResult(data=True)
    except PackageNotFoundError:
        return FunctionExecuteResult(
            error=PackageNotFoundException(
                name=req.name, version=req.specifier, path=package
            )
        )
    except Exception as e:
        return FunctionExecuteResult(error=e)
