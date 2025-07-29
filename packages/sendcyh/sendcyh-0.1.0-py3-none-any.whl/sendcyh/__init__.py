import requests

def send(title='代码执行完成',content='快来看看',device_key='4J4dARLgVuCC8UznJ5Hw7j'):
    try:
        url = f'https://api.day.app/{device_key}/{title}/{content}'
        response = requests.get(url)
        return response.status_code
    except requests.RequestException as e:
        print(f"发送失败: {e}")
        return None
