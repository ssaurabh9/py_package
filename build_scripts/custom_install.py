import os
import requests
import subprocess
from setuptools.command.install import install

class CustomInstallCommand(install):
    def run(self):
        auth_token = self.get_auth_token()
        
        if not auth_token:
            raise ValueError("GITHUB_TOKEN environment variable not set")

        release_info = self.get_latest_release(auth_token)
        
        if not release_info:
            raise ValueError("No releases found or unable to fetch release info")

        wheel_url = self.get_wheel_url(release_info)
        if not wheel_url:
            raise ValueError("No .whl file found in the latest release")

        wheel_file = self.download_wheel(wheel_url, auth_token)

        subprocess.check_call(['pip', 'install', wheel_file])

        os.remove(wheel_file)

    def get_auth_token(self):
        return os.environ.get('GITHUB_TOKEN')

    def get_latest_release(self, auth_token):
        headers = {
            'Authorization': f'token {auth_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        response = requests.get(
            'https://api.github.com/repos/ssaurabh9/py_package/releases/latest',
            headers=headers
        )
        if response.status_code == 200:
            return response.json()
        return None

    def get_wheel_url(self, release_info):
        for asset in release_info['assets']:
            if asset['name'].endswith('.whl'):
                return asset['url']
        return None

    def download_wheel(self, url, auth_token):
        headers = {
            'Authorization': f'token {auth_token}',
            'Accept': 'application/octet-stream'
        }
        response = requests.get(url, headers=headers)
        filename = url.split('/')[-1]
        with open(filename, 'wb') as f:
            f.write(response.content)
        return filename