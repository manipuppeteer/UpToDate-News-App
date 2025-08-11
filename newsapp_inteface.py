import customtkinter as ctk
import tkinter as tk
from PIL import Image
import webbrowser, requests, threading, json, os
from io import BytesIO
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path

placeholder_pic = "photo.jpg"

def fmt_time(iso_str: str) -> str:
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00")).astimezone(ZoneInfo("Europe/Berlin"))
        return dt.strftime("%d.%m.%Y %H:%M")
    except Exception:
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


class NewsFrame(ctk.CTkFrame):
    def __init__(self, master, headline, url, imgurl, time_iso, source=""):
        super().__init__(master)
        self.url = url
        self.article_dict = {
            "title" : headline,
            "url" : url,
            "urlToImage" : imgurl,
            "publishedAt" : time_iso,
            "source" : source,

        }

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

        self.label= ctk.CTkLabel(self, text=headline, font=("Arial", 16, "bold"),
                                 wraplength=420, justify = "left")
        self.label.grid(row=0, column=0, columnspan=2, padx=10, pady=(10,2), sticky="w")

        meta = f"Published: {fmt_time(time_iso)}"
        if source: meta += f"   -   {source}"
        self.age = ctk.CTkLabel(self, text=meta, font=("Arial", 10))
        self.age.grid(row=1, column=0, columnspan=2, padx=10, pady=(0,8), sticky="w")

        self.img = ctk.CTkImage(light_image=Image.open(placeholder_pic), size=(225, 150))
        self.img_label = ctk.CTkLabel(self, image=self.img, text="")
        self.img_label.grid(row=0, column=2, rowspan=3, padx=10, pady=10, sticky="n")

        self.read_button = ctk.CTkButton(self, text="Read more", command=self.read_more)
        self.read_button.grid(row=2, column=0, padx=(10,5), pady=(0,10), sticky="ew")

        self.fav_button= ctk.CTkButton(self, text="Add to Favorites", command=self.add_to_favorites)
        self.fav_button.grid(row=2, column=1, padx=(10,5), pady=(0,10), sticky="ew" )

        if imgurl and imgurl.strip():
            threading.Thread(target=self._load_image_async, args=(imgurl,), daemon=True).start()

    def _load_image_async(self, imgurl: str):
        try:
            r = requests.get(imgurl, timeout=6)
            r.raise_for_status()
            im = Image.open(BytesIO(r.content))
            new_img = ctk.CTkImage(light_image=im, size=(225, 150))
            self.img_label.after(0, lambda: self._set_img(new_img))
        except Exception:
            pass
    def _set_img(self, new_img):
        self.img = new_img
        self.img_label.configure(image=self.img)

    def read_more(self):
        if self.url:
            webbrowser.open(self.url)

    def add_to_favorites(self):
        try:
            add_fav(self.article_dict)
            self.fav_button.configure(text="Saved ✓", state="disabled")
            try:
                self.after(0, render_favorites)
            except NameError:
                pass
        except Exception as e:
            print(f"Favorit speichern fehlgeschlagen: {e}")

app = ctk.CTk()
app.title("News Application")
app.geometry("800x600")
tabs = ctk.CTkTabview(app)
tabs.pack(fill="both", expand=True)
tab_frames = {}
for name in [
    "Latest News", "Favorites", "National News", "International News",
    "Sports News", "Entertainment News", "Technology News", "Health News"
]:
    tab = tabs.add(name)
    sf = ctk.CTkScrollableFrame(tab)
    sf.pack(fill="both", expand=True, padx=6, pady=6)
    tab_frames[name] = sf

def render_favorites():
    # erst leeren
    frame = tab_frames["Favorites"]
    for w in frame.winfo_children():
        w.destroy()

    favs = list_favs()
    if not favs:
        ctk.CTkLabel(frame, text="Keine Favoriten gespeichert.").pack(pady=10)
        return

    for idx, art in enumerate(favs):
        row = ctk.CTkFrame(frame)
        row.pack(fill="x", padx=6, pady=6)

        title = art.get("title", "(ohne Titel)")
        src = (art.get("source") or "")
        ts = fmt_time(art.get("publishedAt", ""))

        ctk.CTkLabel(row, text=f"{title}\n{ts}   –   {src}", justify="left", wraplength=520)\
            .grid(row=0, column=0, sticky="w", padx=8, pady=6)

        def open_url(u=art.get("url", "")):
            if u: webbrowser.open(u)

        ctk.CTkButton(row, text="Öffnen", command=open_url).grid(row=0, column=1, padx=6)
        ctk.CTkButton(row, text="Löschen", fg_color="#aa3333",
                      command=lambda i=idx: (remove_favs(i), render_favorites()))\
            .grid(row=0, column=2, padx=6)

# Beim Start einmal laden:
render_favorites()



from newsapi import get_news
articles = get_news()
for article in articles:
    frame = NewsFrame(
        tab_frames["Latest News"],
        article.get("title", "(ohne Titel)"),
        article.get("url", ""),
        article.get("urlToImage", ""),
        article.get("publishedAt", ""),
        source=(article.get("source") or {}).get("name", "")
    )
    frame.pack(fill="both", expand=True)
app.mainloop()