import json
import requests
import time
import threading

# 提供三个GitHub API tokens
tokens = []

target_records = []

def fetch_repos(token, start, end):
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
    }
    results = []
    gap = 50
    current_start = start
    current_end = current_start + gap - 1
    while current_end <= end:
        query = f"api.openai.com in:file language:JavaScript size:{current_start}..{current_end}"
        page = 1
        print(f"crawling file size between {current_start} to {current_end} with token index {tokens.index(token)}")
        while True:
            url = f'https://api.github.com/search/code?q={query}&per_page=100&page={page}'
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                results.extend(data.get('items'))
                target_records.extend(data.get('items'))
                if 'next' not in response.links:
                    break
                page += 1
            else:
                print('Failed to fetch data:', response.status_code)
                break
            time.sleep(10)  # 延迟以避免速率限制
        current_start += gap
        current_end += gap
        time.sleep(10)
    return results

# 创建线程
try:
    threads = []
    ranges = [(1, 70000), (70001, 140000), (140001, 210000)]
    for i in range(3):
        thread = threading.Thread(target=fetch_repos, args=(tokens[i], ranges[i][0], ranges[i][1]))
        threads.append(thread)
        thread.start()

    # 等待所有线程完成
    for thread in threads:
        thread.join()
finally:
# 将结果写入文件
    with open('api_repo/code_file/openai_javascript.json', 'w', encoding='utf-8') as f:
        json.dump(target_records, f, ensure_ascii=False, indent=4)
    print(f"Found {len(target_records)} items.")