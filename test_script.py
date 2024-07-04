import argparse
import re
import requests
import subprocess
import sys

def validate_version(version):
    # A simple regex for semantic versioning
    pattern = r'^\d+\.\d+\.\d+$'
    return re.match(pattern, version) is not None

def fetch_release_info(repo, tag=None):
    url = f"https://api.github.com/repos/{repo}/releases"
    if tag:
        url = f"{url}/tags/v{tag}"
    else:
        url = f"{url}/latest"
    
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch release information from {url}")
        return None
    
    return response.json()

def install_package(version=None):
    repo = "ssaurabh9/py_package"
    
    if version:
        if not validate_version(version):
            print(f"Invalid version format: {version}. Expected format: x.y.z")
            return
        release = fetch_release_info(repo, tag=version)
    else:
        release = fetch_release_info(repo)

    if not release:
        print("Release information could not be retrieved.")
        return

    # Find the wheel file in the assets
    wheel_asset = next((asset for asset in release['assets'] if asset['name'].endswith('.whl')), None)
    
    if not wheel_asset:
        print(f"No wheel file found for {'latest' if not version else version} version.")
        return

    # Download the wheel file
    wheel_url = wheel_asset['browser_download_url']
    wheel_file = wheel_asset['name']

    response = requests.get(wheel_url)
    
    if response.status_code != 200:
        print(f"Failed to download the wheel file from {wheel_url}")
        return

    with open(wheel_file, 'wb') as f:
        f.write(response.content)

    # Install the wheel file
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", wheel_file])
        print(f"Package {'latest' if not version else version} installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install package {wheel_file}")
        raise e

def main():
    parser = argparse.ArgumentParser(description='Test script to install specific version of a package.')
    parser.add_argument('version', type=str, nargs='?', help='Version of the package to install')

    args = parser.parse_args()
    
    version = args.version

    if version:
        print(f"Installing package version: {version}")
        install_package(version)
    else:
        print("Installing the latest package version")
        install_package()

if __name__ == "__main__":
    main()
