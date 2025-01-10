from datetime import datetime
import os
import pandas as pd
import requests
import time

def get_python_repos():
    headers = {
        'Authorization': f'token {os.environ.get("GITHUB_TOKEN")}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    repos = []
    page = 1
    while len(repos) < 100:  # Get top 100 repositories
        url = f'https://api.github.com/search/repositories?q=language:Python&sort=stars&order=desc&per_page=100&page={page}'
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            print(f"Error: API returned status code {response.status_code}")
            break
            
        data = response.json()
        if not data.get('items'):
            break
            
        repos.extend(data['items'])
        if page >= data['total_count'] // 100 + 1:
            break
            
        page += 1
        time.sleep(2)  # Be nice to the API
        
    return repos[:100]  # Return only top 100

def write_markdown(repos, output_file):
    # Create directories if they don't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('[Github Ranking](../README.md)\n')
        f.write('==========\n\n')
        f.write('## Top 100 Stars in Python\n\n')
        
        # Write table header
        f.write('| Ranking | Project Name | Stars | Forks | Language | Open Issues | Description | Last Commit |\n')
        f.write('| ------- | ------------ | ----- | ----- | -------- | ----------- | ----------- | ----------- |\n')
        
        # Write repository data
        for idx, repo in enumerate(repos, 1):
            description = repo['description'] or ''
            description = description.replace('|', '\|')  # Escape pipe characters
            
            f.write(f"| {idx} | [{repo['name']}]({repo['html_url']}) | {repo['stargazers_count']} | "
                   f"{repo['forks_count']} | {repo['language']} | {repo['open_issues_count']} | "
                   f"{description} | {repo['pushed_at']} |\n")

def save_to_csv(repos, output_file):
    # Create directories if they don't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Prepare data for DataFrame
    data = []
    for idx, repo in enumerate(repos, 1):
        data.append({
            'rank': idx,
            'item': 'Python',
            'repo_name': repo['name'],
            'stars': repo['stargazers_count'],
            'forks': repo['forks_count'],
            'language': repo['language'],
            'repo_url': repo['html_url'],
            'username': repo['owner']['login'],
            'issues': repo['open_issues_count'],
            'last_commit': repo['pushed_at'],
            'description': repo['description']
        })
    
    df = pd.DataFrame(data)
    df.to_csv(output_file, index=False)

def main():
    print("Fetching Python repositories...")
    repos = get_python_repos()
    
    if not repos:
        print("Error: No repositories found!")
        return
        
    print(f"Found {len(repos)} repositories")
    
    # Save markdown file
    md_file = '../Top100/Python.md'
    print(f"Writing markdown to {md_file}")
    write_markdown(repos, md_file)
    
    # Save CSV file
    save_date = datetime.now().strftime("%Y-%m-%d")
    csv_file = f'../Data/github-ranking-{save_date}.csv'
    print(f"Writing CSV to {csv_file}")
    save_to_csv(repos, csv_file)
    
    print("Done!")

if __name__ == "__main__":
    main()