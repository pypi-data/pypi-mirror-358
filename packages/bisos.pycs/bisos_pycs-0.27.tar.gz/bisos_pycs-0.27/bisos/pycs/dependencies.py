import subprocess
import sys
import venv
from pathlib import Path
import re
import  packaging


def pipxPkgInstall(package: str) -> None:
    """Installs a package using pipx."""
    print(f"Installing {package} using pipx...")
    subprocess.run(["pipx", "upgrade", package], check=True)


def pipxVenvPathGet(package: str) -> str:
    """Gets the virtual environment path of a pipx-installed package."""
    return f"/bisos/pipx/venvs/{package}"
    result = subprocess.run(["pipx", "list"], capture_output=True, text=True, check=True)

    # Find the installation path using regex
    pattern = rf"{package}.*?installed at (.+)"
    match = re.search(pattern, result.stdout, re.DOTALL)

    if match:
        return match.group(1).strip()
    else:
        print(f"Failed to find the virtual environment for {package}.")
        sys.exit(1)


def pipxDependenciesStr(package: str) -> str:
    """Lists dependencies for a pipx-installed package and returns as a string."""
    print(f"Listing dependencies for {package}...")
    result = subprocess.run(["pipx", "runpip", package, "freeze"], capture_output=True, text=True, check=True)
    return result.stdout.strip()


def pipxDependenciesToFile(package: str, deps: str) -> None:
    """Saves dependencies to a requirements.txt file."""
    canonical_name = packaging.utils.canonicalize_name(package)
    filename = f"{canonical_name}_requirements.pipx"
    with open(filename, "w") as f:
        f.write(deps + "\n")

    print(f"Dependencies saved to {filename}")


def pipVenvCreate(venv_path: Path) -> None:
    """Creates a virtual environment in the given path."""
    print(f"Creating virtual environment at {venv_path}...")
    venv.create(venv_path, with_pip=True)


def pipPkgInstall(venv_path: Path, package: str) -> None:
    """Installs the given package inside the virtual environment."""
    print(f"Installing {package} inside the virtual environment...")
    subprocess.run([venv_path / "bin" / "pip", "install", package], check=True)


def pipDependenciesStr(venv_path: Path) -> str:
    """Lists dependencies using pip freeze inside the virtual environment."""
    print("Extracting dependencies...")
    result = subprocess.run(
        [venv_path / "bin" / "pip", "freeze"], capture_output=True, text=True, check=True
    )
    return result.stdout.strip()


def pipDependenciesToFile(package: str, deps: str) -> None:
    """Saves dependencies to a requirements.txt file."""
    canonical_name = packaging.utils.canonicalize_name(package)
    filename = f"{canonical_name}_requirements.pip"
    with open(filename, "w") as f:
        f.write(deps + "\n")

    print(f"Dependencies saved to {filename}")


# def main(package_name: str) -> None:
#     """Automates package installation and requirements file generation."""
#     venv_path = Path(f"./{package_name}_venv")

#     create_virtualenv(venv_path)
#     install_package(venv_path, package_name)

#     dependencies = list_dependencies(venv_path)
#     print(dependencies)

#     save_dependencies_to_file(package_name, dependencies)

#     print("Done.")


# if __name__ == "__main__":
#     if len(sys.argv) < 2:
#         print("Usage: python generate_requirements.py <package-name>")
#         sys.exit(1)

#     package_name: str = sys.argv[1]
#     main(package_name)



# if __name__ == "__main__":
#     if len(sys.argv) < 2:
#         print("Usage: python pipx_deps.py <package-name>")
#         sys.exit(1)

#     package_name: str = sys.argv[1]

#     install_package(package_name)
#     venv_path: str = get_venv_path(package_name)
#     print(f"{package_name} is installed at: {venv_path}")

#     dependencies: str = list_dependencies(package_name)
#     print(dependencies)

#     save_dependencies_to_file(package_name, dependencies)

#     print("Done.")
