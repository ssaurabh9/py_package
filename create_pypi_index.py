import os
import requests
from github import Github

def create_index_html(releases):
    html = '<!DOCTYPE html>\n<html>\n<body>\n'
    for release in releases:
        for asset in release.get_assets():
            if asset.name.endswith('.whl') or asset.name.endswith('.tar.gz'):
                html += f'<a href="{asset.browser_download_url}">{asset.name}</a><br>\n'
    html += '</body>\n</html>'
    return html

def main():
    token = os.environ.get('GITHUB_TOKEN')
    repo_name = os.environ.get('GITHUB_REPOSITORY')
    
    if not token or not repo_name:
        raise ValueError("GITHUB_TOKEN and GITHUB_REPOSITORY must be set")

    g = Github(token)
    repo = g.get_repo(repo_name)
    releases = repo.get_releases()

    index_html = create_index_html(releases)

    try:
        contents = repo.get_contents("index.html", ref="gh-pages")
        repo.update_file(contents.path, "Update PyPI index", index_html, contents.sha, branch="gh-pages")
    except:
        repo.create_file("index.html", "Create PyPI index", index_html, branch="gh-pages")

if __name__ == "__main__":
    main()