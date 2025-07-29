import requests
data={"topic":"service"}
a = 'https://ald-ym.llm-dev.try-mellerikat.com/alochat-0626-v5'
b = 'http://10.158.2.106:8080'
url=f"{b}/ask_chat?topic=test"
a = requests.post(url)
print(a.json()['response'])