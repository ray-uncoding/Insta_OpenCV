import json
import requests
import datetime

class InstaAPI:
    def __init__(self, config_path, command_url, state_url):
        self.command_url = command_url
        self.state_url = state_url

        # 載入配置
        with open(config_path, "r") as file:
            self.api_config = json.load(file)

    def send_command(self, command_name, dynamic_params=None, headers=None):
        try:
            if command_name not in self.api_config:
                raise ValueError(f"未知的指令名稱: {command_name}")

            # 構建請求 payload
            payload = self.api_config[command_name]
            if dynamic_params:
                payload["parameters"].update(dynamic_params)

            # 發送請求
            response = requests.post(self.command_url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API 請求失敗: {e}")
            return {"error": str(e)}

    def poll_state(self, headers=None):
        response = requests.post(self.state_url, json={}, headers=headers, timeout=5)
        response.raise_for_status()
        return response.json()