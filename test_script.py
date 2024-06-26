import requests
import subprocess

def install_latest():
    # Fetch the latest release info
    repo = "ssaurabh9/py_package"
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    response = requests.get(url)
    release = response.json()

    # Find the wheel file in the assets
    wheel_asset = next((asset for asset in release['assets'] if asset['name'].endswith('.whl')), None)
    
    if wheel_asset:
        # Install the wheel
        subprocess.run(["pip", "install", wheel_asset['browser_download_url']])
    else:
        print("No wheel file found in the latest release.")

if __name__ == "__main__":
    install_latest()