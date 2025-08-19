from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
import webbrowser, requests, json, os, time
def fmt_time(iso_str: str) -> str:
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00")).astimezone(ZoneInfo("Europe/Berlin"))
        return dt.strftime("%d.%m.%Y %H:%M")
    except Exception as e:
        
        return iso_str or ""

def _favorites_path():
    try:
        home = Path.home()
        path = home / ".news_app" / "favorites.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        return path
    except Exception:
        return Path(__file__).with_name("favorites.json")

def ensure_favorites_file():
    path = _favorites_path()
    if not path.exists():
        path.write_text("[]", encoding="UTF-8")

def load_favorites():
    ensure_favorites_file()
    path = _favorites_path()
    try:
        return json.loads(path.read_text(encoding="UTF-8"))
    except json.JSONDecodeError:
        path.write_text("[]", encoding="UTF-8")
        return []

def save_favs(items: list):
    path = _favorites_path()
    path.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="UTF-8")

def add_fav(item: dict):
    favs = load_favorites()
    favs.append(item)
    save_favs(favs)

def remove_favs(index: int) -> bool:
    favs= load_favorites()
    if 0 <= index < len(favs):
        favs.pop(index)
        save_favs(favs)
        return True
    return False

def list_favs() -> list:
    return load_favorites()

def main():
    print(fmt_time("2023-10-01T12:00:00Z"))  # Example usage

if __name__ == "__main__":
    main()