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

def clean_description(desc):
    if not desc:
        return "No description provided."
    # Truncate overly long descriptions for clean UI
    first_sentence = desc.split('.')[0].strip()
    if len(first_sentence) > 90:
        return first_sentence[:87] + "..."
    return first_sentence + "."

def generate_stats_summary(repos):
    total_repos = len(repos)
    public_repos = [r for r in repos if not r.get('fork') and r.get('name') not in EXCLUDE_REPOS]
    total_stars = sum(r.get('stargazers_count', 0) for r in public_repos)
    total_forks = sum(r.get('forks_count', 0) for r in public_repos)
    
    top_repo = max(public_repos, key=lambda x: (x.get('stargazers_count', 0), x.get('updated_at', ''))) if public_repos else None
    top_str = f"[{top_repo['name']}]({top_repo['html_url']}) ⭐ {top_repo['stargazers_count']}" if top_repo else "N/A"
    
    stats_md = f"⚙️ **{total_repos}** Repositories &nbsp;•&nbsp; ⭐ **{total_stars}** Total Stars &nbsp;•&nbsp; 🍴 **{total_forks}** Total Forks &nbsp;•&nbsp; 🔥 Top Project: {top_str}"
    return stats_md

def generate_repos_markdown(repos):
    public_repos = [r for r in repos if not r.get('fork') and r.get('name') not in EXCLUDE_REPOS]
    # Sort by stars descending, then by updated date
    public_repos.sort(key=lambda x: (x.get('stargazers_count', 0), x.get('updated_at', '')), reverse=True)
    top_repos = public_repos[:6]

    items = []
    for r in top_repos:
        name = r['name']
        url = r['html_url']
        stars_count = r.get('stargazers_count', 0)
        stars_badge = f" `⭐ {stars_count}`" if stars_count > 0 else ""
        desc = clean_description(r.get('description'))
        lang = f"`{r['language']}`" if r.get('language') else ""
        
        item = f"- **[{name}]({url})** {lang}{stars_badge}  \n  {desc}\n"
        items.append(item)
        
    return "\n".join(items)

def update_readme():
    repos = fetch_all_user_repos()
    if not repos:
        print("No repos fetched, skipping update.")
        return
    
    repos_md = generate_repos_markdown(repos)
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
        content = f"{before}<!-- REPOS-START -->\n{repos_md}\n<!-- REPOS-END -->{after}"

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(content)
    print("README.md updated with clean UI!")

if __name__ == "__main__":
    update_readme()
