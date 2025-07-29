from pathlib import Path
from typing import Optional
import os

# Setup the jpype import system, to allow python style imports for java modules
import jpype.imports
import opentrafficsim

import commonroad_ots


OTS_MODULES = [
    "animation",
    "base",
    "core",
    "demo",
    "draw",
    "editor",
    "kpi",
    "parser-xml",
    "road",
    "sim0mq-kpi",
    "sim0mq-swing",
    "swing",
    "trafficcontrol",
    "web",
    "sim0mq",
]


def try_to_autodetect_latest_installed_ots_version(ots_home: Path) -> Optional[str]:
    """
    Searchs for all compilied OTS modules in `ots_home` and tries to find the latest version.
    Requires that OTS has been compiled.

    Returns
    -------
    Optional[str]
        Either the version string, or None if no version could be autodetected

    Parameters
    ----------
    ots_home : Path
        Path to the root of the opentrafficsim installation
    """
    # Use an over-approximating glob, which will match all jars that have a version string inside.
    # It would be optimal to only match jars which end with the version strings
    # (because those are the module jars, that need to be loaded later).
    # But globs cannot match regular languages, therefore this approach must suffice.
    available_jars = ots_home.glob("ots-*/target/ots-*-[0-9]*.[0-9]*.[0-9]*.jar")
    available_versions = set()
    for jar_path in available_jars:
        jar_path_parts = jar_path.stem.split("-")
        if len(jar_path_parts) == 0:
            continue

        version_str = jar_path_parts[-1]
        version_parts = tuple(version_str.split("."))
        if len(version_parts) != 3:
            continue

        # Store the versions in their parts as a tuple, so we can do a simple comparison to find the max version
        available_versions.add(version_parts)

    if len(available_versions) == 0:
        return None
    else:
        latest_version_parts = max(available_versions)
        latest_version = ".".join(latest_version_parts)
        return latest_version


def _build_ots_module_jar_path(ots_module: str, ots_home: Path, ots_version: str) -> Path:
    return ots_home / f"ots-{ots_module}" / "target" / f"ots-{ots_module}-{ots_version}.jar"


def configure_lookup_paths_for_ots_modules(ots_home: Path, ots_version: str):
    """
    Load all modules for OTS version `ots_version` from `ots_home`.

    Parameters
    ----------
    ots_home : Path
        Path to the root of the opentrafficsim installation
    ots_version: str
        Version of the opentrafficsim installation

    Raises
    ----------
    RuntimeError
        when one of the modules cannot be loaded
    """
    # The module 'ots-distribution' is special, because it acts as a meta module for all OTS modules.
    # Therefore, we can either load the ots-distribution or all other modules individually.
    # This all-in-one OTS distribution is preferred, but in case it is not available we can also
    # safely fallback to loading the individual modules for compatability reasons.
    ots_distribution_module_jar_path = _build_ots_module_jar_path("distribution", ots_home, ots_version)
    if ots_distribution_module_jar_path.exists():
        jpype.addClassPath(str(ots_distribution_module_jar_path))
        return

    for ots_module in OTS_MODULES:
        ots_module_jar_path = _build_ots_module_jar_path(ots_module, ots_home, ots_version)
        if not ots_module_jar_path.exists():
            raise RuntimeError(
                f"Cannot load OTS because JAR for module {ots_module} at {ots_module_jar_path} does not exist!"
                " Have you built OTS for version {ots_version}?"
            )

        jpype.addClassPath(str(ots_module_jar_path))


def setup_ots():
    """Auto-load all OTS modules and start OTS

    Raises
    ----------
    RuntimeError
        When the opentrafficsim installation could not be found or no valid version could be loaded
    """
    # Set the OTS_HOME fallback to the OTS submodule in the cr-ots-interface repo
    ots_home = Path(commonroad_ots.__file__).parent.parent / "opentrafficsim"
    ots_home_raw = os.getenv("OTS_HOME")
    if ots_home_raw is not None:
        ots_home = Path(ots_home_raw)

    if not ots_home.exists():
        raise RuntimeError(
            f"OTS installation could not be found at {ots_home}: path does not exist!"
            " Make sure that OTS is installed and that you have set the 'OTS_HOME' environment variable."
        )

    # Prefer the OTS_VERSION environment variable. If OTS_VERSION is not set, fallback to autodetection
    ots_version = None
    if "OTS_VERSION" in os.environ:
        ots_version = os.environ["OTS_VERSION"]
    else:
        ots_version = try_to_autodetect_latest_installed_ots_version(ots_home)
        if ots_version is None:
            raise RuntimeError(
                f"Failed to autodetect the installed OTS version at {ots_home}!"
                " Make sure that you have built OTS or, if the version autodetection is not working,"
                " Try to set the 'OTS_VERSION' environment variable!"
            )

    configure_lookup_paths_for_ots_modules(ots_home, ots_version)

    if not jpype.isJVMStarted():
        jpype.startJVM()
