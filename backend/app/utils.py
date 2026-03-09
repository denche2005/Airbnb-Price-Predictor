import os
import json
import pickle


def save_object(file_path: str, obj) -> None:
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "wb") as f:
        pickle.dump(obj, f)


def load_object(file_path: str):
    with open(file_path, "rb") as f:
        return pickle.load(f)


def save_json(file_path: str, data: dict) -> None:
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)


def load_json(file_path: str) -> dict:
    with open(file_path, "r") as f:
        return json.load(f)
