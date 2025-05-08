import json
import os

def load_config(config_name):
    """從 config 資料夾中載入指定的配置檔案"""
    config_path = os.path.join(os.path.dirname(__file__), "../config", config_name)
    with open(config_path, "r") as file:
        return json.load(file)