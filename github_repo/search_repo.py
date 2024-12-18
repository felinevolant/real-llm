import requests
import pandas as pd
import os

# GitHub API 搜索代码的基本 URL
base_url = "https://api.github.com/search/code"

# 定义要搜索的编程语言列表
languages = ["python", "java", "javascript", "go", "php", "c#", "kotlin"]

# 搜索的关键词
search_query = "api.openai.com"

# GitHub API 请求头，可以使用个人访问令牌（token）来提高请求限制
headers = {
    "Accept": "application/vnd.github.v3+json",
    # "Authorization": "token "  # 如果有 GitHub token
}

output_dir = "api_repo"
os.makedirs(output_dir, exist_ok=True)

# 搜索不同语言的代码
for language in languages:
    query = f"{search_query}+language:{language}"
    url = f"{base_url}?q={query}"

    # 请求 API 获取结果
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        search_results = response.json()
        items = search_results.get("items", [])

        # 存储当前语言的项目数据
        repo_data = []
        for item in items:
            repo = item["repository"]
            repo_data.append({
                "language": language,
                "repo_name": repo["name"],
                "repo_owner": repo["owner"]["login"],
                "repo_url": repo["html_url"],
                "repo_description": repo.get("description", "No description"),
            })
        # 如果该语言有结果，保存为对应的 CSV 文件
        if repo_data:
            df = pd.DataFrame(repo_data)
            file_path = os.path.join(output_dir, f"openapi_{language}_repos.csv")
            df.to_csv(file_path, index=False, encoding="utf-8")
            print(f"Results for {language} saved to {file_path}")
        else:
            print(f"No results found for {language}.")
    else:
        print(f"Error fetching data for {language}: {response.status_code}")
