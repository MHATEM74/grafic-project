# core/save_system.py
import json
import os
from characters.character_data import CHARACTERS

class SaveSystem:
    PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "savegame.json")

    @staticmethod
    def load():
        data = {}
        if os.path.exists(SaveSystem.PATH):
            try:
                with open(SaveSystem.PATH, "r") as f:
                    data = json.load(f)
                for ch in CHARACTERS:
                    cid = str(ch["id"])
                    if cid in data.get("owned", {}):
                        ch["owned"] = data["owned"][cid]
            except Exception as e:
                print(f"Error loading save: {e}")
                
        return {
            "coins": data.get("coins", 0),
            "selected_char": data.get("selected_char", 0),
            "achievements": data.get("achievements", {}),
            "stats": data.get("stats", {}),
            "daily_streak": data.get("daily_streak", 0),
            "last_login": data.get("last_login", "")
        }

    @staticmethod
    def save(game_state):
        owned = {str(ch["id"]): ch["owned"] for ch in CHARACTERS}
        data = {
            "coins": game_state.coins,
            "selected_char": game_state.selected_char,
            "owned": owned,
            "achievements": game_state.achievements,
            "stats": game_state.stats,
            "daily_streak": game_state.daily_streak,
            "last_login": game_state.last_login
        }
        try:
            with open(SaveSystem.PATH, "w") as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Error saving game: {e}")
