import os
import requests
import pandas as pd
import time
import random
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.exceptions import SSLError, RequestException

# 定义要搜索的编程语言列表
languages = ["python"]

# 搜索的关键词
search_query = "api.openai.com"

# 输出目录
output_dir = "api_repo/code_file"
os.makedirs(output_dir, exist_ok=True)

# GitHub API 配置
GITHUB_API_URL = "https://api.github.com/search/code"

# 构建一个token列表, 代表多个Github用户的token凭证
API_KEYS = [

    # 添加更多的 API 密钥以应对速率限制
]

# 最大并发线程数
MAX_WORKERS = 10

# 每个请求的最大重试次数（在不使用retry的前提下，尽量避免）
MAX_RETRIES = 1


def get_headers():
    access_token = random.choice(API_KEYS)
    return {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {access_token}"
    }


def save_to_csv(language, items):
    csv_file = os.path.join(output_dir, f"openai_{language}.csv")
    data = []
    for item in items:
        repository = item.get('repository', {})
        data.append({
            "repo_name": repository.get('full_name', ''),
            "repo_url": repository.get('html_url', ''),
            "repo_des": repository.get('description', ''),
            "file_name": item.get('name', ''),
            "file_path": item.get('path', ''),
            "file_url": item.get('html_url', ''),
            "SHA": item.get('sha', ''),
            "git_url": item.get('git_url', '')
        })
    df_new = pd.DataFrame(data)
    if os.path.isfile(csv_file):
        df_new.to_csv(csv_file, mode='a', header=False, index=False, encoding='utf-8')
    else:
        df_new.to_csv(csv_file, mode='w', header=True, index=False, encoding='utf-8')
    print(f"保存 {len(df_new)} 条结果到 {csv_file}")


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


def search_github_code(query, language, date_str, page=1, per_page=100):
    full_query = f"{query} language:{language} created:{date_str}..{date_str}"
    params = {
        "q": full_query,
        "sort": "indexed",
        "order": "desc",
        "per_page": per_page,
        "page": page
    }
    try:
        headers = get_headers()
        response = requests.get(GITHUB_API_URL, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 403:
            print(f"达到速率限制或权限不足，状态码: {response.status_code}")
            return None
        else:
            print(f"请求失败: {response.status_code} - {response.text}")
            return None
    except SSLError as ssl_err:
        print(f"SSL 错误: {ssl_err}，跳过当前请求。")
        return None
    except RequestException as e:
        print(f"请求异常: {e}，跳过当前请求。")
        return None


def process_date(language, date_str):
    page = 1
    while True:
        result = search_github_code(search_query, language, date_str, page=page)
        if result and 'items' in result:
            items = result['items']
            if not items:
                print(f"日期 {date_str} 的第 {page} 页没有结果，跳过。")
                break
            save_to_csv(language, items)
            print(f"保存日期 {date_str} 的第 {page} 页，共 {len(items)} 条结果")
            if len(items) < 100:
                # 当前日期的数据已经取完
                break
            page += 1
            # 为避免速率限制，适当休眠
            time.sleep(2)
        else:
            # 如果返回 None，可能是由于速率限制或其他错误，跳过当前页
            print(f"跳过日期 {date_str} 的第 {page} 页。")
            break


def main():
    # 设置搜索的日期范围，从 2022-01-01 开始到今天
    end_date = datetime.utcnow().date()
    start_date = datetime(2022, 1, 1).date()

    for language in languages:
        print(f"开始搜索语言: {language}")
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = []
            for single_date in daterange(start_date, end_date):
                date_str = single_date.isoformat()
                print(f"提交搜索任务: {date_str}")
                futures.append(executor.submit(process_date, language, date_str))

            # 监控任务完成情况
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"任务执行异常: {e}")
        print(f"完成语言: {language}")


if __name__ == "__main__":
    main()
