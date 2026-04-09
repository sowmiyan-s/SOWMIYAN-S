import requests
import re
import os

def get_top_repos(username, limit=5):
    # Fetch all repositories
    url = f"https://api.github.com/users/{username}/repos?sort=updated&per_page=100"
    headers = {}
    
    # Use GITHUB_TOKEN if available to avoid rate limiting
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"
        
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error fetching repos: {response.status_code}")
        return []
    
    repos = response.json()
    # Filter out the profile README repo itself and any forks (optional)
    repos = [r for r in repos if r['name'].lower() != username.lower() and not r['fork']]
    
    # Sort by stars, then by update time
    repos.sort(key=lambda x: (x['stargazers_count'], x['updated_at']), reverse=True)
    
    return repos[:limit]

def generate_project_markdown(repo, username):
    name = repo['name']
    description = repo['description'] or "No description provided."
    url = repo['html_url']
    language = repo['language'] or "Misc"
    
    # Clean description to avoid breaking markdown
    description = description.replace("\n", " ")
    
    return f"""
### 🚀 [{name}]({url})
> {description}
<p>
  <img src="https://img.shields.io/github/stars/{username}/{name}?style=flat-square&logo=github&color=FFD700" alt="Stars">
  <img src="https://img.shields.io/badge/language-{language}-blue?style=flat-square" alt="Language">
</p>"""

def update_readme(username):
    repos = get_top_repos(username)
    if not repos:
        print("No repos found.")
        return

    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()
    
    project_list = "\n".join([generate_project_markdown(r, username) for r in repos])

    # Search for the markers
    pattern = r"<!-- PROJECTS_START -->.*?<!-- PROJECTS_END -->"
    replacement = f"<!-- PROJECTS_START -->\n{project_list}\n<!-- PROJECTS_END -->"
    
    if re.search(pattern, content, flags=re.DOTALL):
        new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(new_content)
        print("README.md updated successfully.")
    else:
        print("Markers not found in README.md")

if __name__ == "__main__":
    GITHUB_USERNAME = "sowmiyan-s"
    update_readme(GITHUB_USERNAME)
