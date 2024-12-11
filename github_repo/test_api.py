import requests

# GitHub API URL
url = "https://api.github.com/repos/microsoft/autogen/dependency-graph/compare/main...main"
token = "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"  # 替换为你的 GitHub 个人访问令牌

# 如果需要，提供 GitHub Token 进行认证
headers = {
    "Authorization": f"token {token}"
}

# 发送 GET 请求
response = requests.get(url, headers=headers)

# 如果请求成功，返回的数据
if response.status_code == 200:
    dependents_data = response.json()
    for dep in dependents_data:
        print(response)
else:
    print(f"请求失败: {response.status_code}, 错误信息: {response.json()}")
