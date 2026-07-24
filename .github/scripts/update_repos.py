import requests

USERNAME = "harindujayakody"
EXCLUDE_REPOS = [USERNAME]

def fetch_all_user_repos():
    url = f"https://api.github.com/users/{USERNAME}/repos?per_page=100"
    response = requests.get(url)
    if response.status_code != 200:
        print("Failed to fetch repos from GitHub API")
        return []
    return response.json()

def generate_stats_summary(repos):
    total_repos = len(repos)
    public_repos = [r for r in repos if not r.get('fork') and r.get('name') not in EXCLUDE_REPOS]
    total_stars = sum(r.get('stargazers_count', 0) for r in public_repos)
    total_forks = sum(r.get('forks_count', 0) for r in public_repos)
    
    top_repo = max(public_repos, key=lambda x: x.get('stargazers_count', 0)) if public_repos else None
    
    summary_md = f"| 📦 **Public Projects** | ⭐ **Total Stars** | 🍴 **Total Forks** | 🔥 **Top Highlight** |\n"
    summary_md += f"|:-------------------:|:-----------------:|:------------------:|:-------------------:|\n"
    top_repo_str = f"[{top_repo['name']}]({top_repo['html_url']}) ({top_repo['stargazers_count']} ⭐)" if top_repo else "N/A"
    summary_md += f"| {total_repos} | {total_stars} | {total_forks} | {top_repo_str} |\n"
    
    return summary_md

def generate_table_markdown(repos):
    public_repos = [r for r in repos if not r.get('fork') and r.get('name') not in EXCLUDE_REPOS]
    # Sort by stars descending, then by updated date
    public_repos.sort(key=lambda x: (x.get('stargazers_count', 0), x.get('updated_at', '')), reverse=True)
    top_repos = public_repos[:8]

    md = "| Project | Description | Tech | Stars |\n"
    md += "|:--------|:------------|:-----|:------|\n"
    for r in top_repos:
        name = r['name']
        url = r['html_url']
        stars_count = r.get('stargazers_count', 0)
        stars_str = f"⭐ {stars_count}" if stars_count > 0 else "-"
        desc = r.get('description') or "No description provided"
        lang = f"`{r['language']}`" if r.get('language') else "-"
        
        md += f"| [{name}]({url}) | {desc} | {lang} | {stars_str} |\n"
    return md

def update_readme():
    repos = fetch_all_user_repos()
    if not repos:
        print("No repos fetched, skipping update.")
        return
    
    table_md = generate_table_markdown(repos)
    stats_md = generate_stats_summary(repos)
    
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Update Stats section
    if "<!-- STATS-START -->" in content and "<!-- STATS-END -->" in content:
        before = content.split("<!-- STATS-START -->")[0]
        after = content.split("<!-- STATS-END -->")[1]
        content = f"{before}<!-- STATS-START -->\n{stats_md}\n<!-- STATS-END -->{after}"

    # Update Repos section
    if "<!-- REPOS-START -->" in content and "<!-- REPOS-END -->" in content:
        before = content.split("<!-- REPOS-START -->")[0]
        after = content.split("<!-- REPOS-END -->")[1]
        content = f"{before}<!-- REPOS-START -->\n{table_md}\n<!-- REPOS-END -->{after}"

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(content)
    print("README.md updated with latest stats & repos!")

if __name__ == "__main__":
    update_readme()
