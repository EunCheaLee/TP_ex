import requests

proxies = {
    "http": None,
    "https": None
}

response = requests.get("https://stdict.korean.go.kr/api/search.do",
                        params={"key": "API_KEY", "q": "인사", "req_type": "json"},
                        proxies=proxies, timeout=5)
print(response.status_code)
print(response.text)