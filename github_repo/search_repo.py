import requests
import pandas as pd

# GitHub API 搜索代码的基本 URL
base_url = "https://api.github.com/search/code"

# 定义要搜索的编程语言列表
languages = ["python", "java", "javascript", "go", "php", "c#", "kotlin"]

# 搜索的关键词
search_query = "api.openai.com"

# GitHub API 请求头，可以使用个人访问令牌（token）来提高请求限制
headers = {
    "Accept": "application/vnd.github.v3+json",
    # "Authorization": "token YOUR_GITHUB_TOKEN"  # 如果有 GitHub token
}

# 存储结果的列表
repo_data = []

# 搜索不同语言的代码
for language in languages:
    query = f"{search_query}+language:{language}"
    url = f"{base_url}?q={query}"

    # 请求 API 获取结果
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        search_results = response.json()
        items = search_results.get("items", [])

        for item in items:
            repo = item["repository"]
            repo_data.append({
                "language": language,
                "repo_name": repo["name"],
                "repo_owner": repo["owner"]["login"],
                "repo_url": repo["html_url"],
                "repo_description": repo.get("description", "No description"),
            })
    else:
        print(f"Error fetching data for {language}: {response.status_code}")

# 使用 pandas 创建 DataFrame
df = pd.DataFrame(repo_data)

# 输出结果到 CSV 文件
df.to_csv("api_repo/openai.csv", index=False, encoding="utf-8")

print("Results saved to api_repo/openai.csv")
