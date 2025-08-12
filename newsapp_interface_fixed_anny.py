import customtkinter as ctk
import tkinter as tk
import tkinter.simpledialog as simpledialog
from PIL import Image
import webbrowser, requests, threading, json, os
from io import BytesIO
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from pathlib import Path

# ---------------------------------------------------------------------
# KONFIGURATION (hier könnt ihr alles WICHTIGE ändern)
# ---------------------------------------------------------------------
placeholder_pic = "photo.jpg"   # Pfad zu einem Platzhalterbild (oder eigenes Bild)
TITLE_FONT_FAMILY = "Arial"
TITLE_FONT_SIZE = 18         # <-- Hier Schriftgröße der Überschrift ändern
TITLE_FONT_STYLE = "bold"
META_FONT_SIZE = 16            # <-- Hier Schriftgröße der Metainfos ändern

TIME_ONLY = True           # <-- True = nur "HH:MM", False = komplettes Format
TIME_FORMAT = "%d.%m.%Y %H:%M"  # <-- Format, wenn TIME_ONLY = False
RECENT_HOURS = 8                # <-- für "General News": wie alt darf eine Nachricht sein?

# Liste der Tab-Namen (solltet ihr anpassen wollen)
CATEGORY_TABS = [
    "Latest News", "Business News", "General News",
    "Sports News", "Entertainment News", "Technology News", "Health News", "Science News",
    "Favorites",]

# Einfache Keyword-Map: Wörter -> Kategorie (kann erweitert werden)
CATEGORY_KEYWORDS = {
    "Business News": ["business", "economy", "market", "stock", "finance", "company"],
    "Sports News": ["sports", "football", "soccer", "basketball", "tennis", "match", "gamel", "goal", "liga"],
    "Entertainment News": ["movie", "film", "music", "celebrity", "tv", "stars", "concert", "festival", "hollywood"],
    "Technology News": ["tech", "technology", "ai", "software", "app", "iphone", "google", "microsoft", "chip"],
    "Health News": ["health", "medicine", "covid", "vaccine", "disease", "hospital", "doctor", "fitness"],
    "Science News": ["science", "research", "study", "nasa", "space", "discovery"]
}
# ---------------------------------------------------------------------

from newsapi import get_news    # bleibt wie in eurem Original (ihr müsst dieses Modul haben.


# --- Hilfsfunktionen für Zeit / Dateien / Favoriten (leicht verständlich) ---
def parse_iso(iso_str: str):
    """Versucht, einen ISO-Zeitstring in ein datetime-Objekt in Europe/Berlin zu verwandeln."""
    try:
        if not iso_str:
            return None
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return dt.astimezone(ZoneInfo("Europe/Berlin"))
    except Exception:
        return None

def fmt_time(iso_str: str) -> str:
    """Formatiert die Zeit nach euren Einstellungen (TIME_ONLY / TIME_FORMAT)."""
    dt = parse_iso(iso_str)
    if not dt:
        return iso_str or ""
    if TIME_ONLY:
        return dt.strftime("%H:%M")
    return dt.strftime(TIME_FORMAT)

def is_recent(iso_str: str, hours: int = RECENT_HOURS) -> bool:
    """Prüft, ob eine Nachricht nicht älter als 'hours' ist (Zeitzone: Europe/Berlin)."""
    dt = parse_iso(iso_str)
    if not dt:
        return False
    now = datetime.now(ZoneInfo("Europe/Berlin"))
    return (now - dt) <= timedelta(hours=hours)

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
    favs = load_favorites()
    if 0 <= index < len(favs):
        favs.pop(index)
        save_favs(favs)
        return True
    return False

def list_favs() -> list:
    return load_favorites()

# --- GUI-Komponente für eine Nachricht ---
class NewsFrame(ctk.CTkFrame):
    def __init__(self, master, headline, url, imgurl, time_iso, source=""):
        super().__init__(master)
        self.url = url
        self.article_dict = {
            "title": headline,
            "url": url,
            "urlToImage": imgurl,
            "publishedAt": time_iso,
            "source": source,
        }

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

        title_font = (TITLE_FONT_FAMILY, TITLE_FONT_SIZE, TITLE_FONT_STYLE)
        meta_font = (TITLE_FONT_FAMILY, META_FONT_SIZE)

        self.label = ctk.CTkLabel(self, text=headline, font=title_font,
                                 wraplength=420, justify="left")
        self.label.grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 2), sticky="w")

        meta = f"Published: {fmt_time(time_iso)}"
        if source:
            meta += f"   -   {source}"
        self.age = ctk.CTkLabel(self, text=meta, font=meta_font)
        self.age.grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 8), sticky="w")

        try:
            self.img = ctk.CTkImage(light_image=Image.open(placeholder_pic), size=(225, 150))
        except Exception:
            # falls Bild nicht existiert, ein leeres Bild verwenden
            self.img = None
        self.img_label = ctk.CTkLabel(self, image=self.img, text="")
        self.img_label.grid(row=0, column=2, rowspan=3, padx=10, pady=10, sticky="n")

        self.read_button = ctk.CTkButton(self, text="Read more", command=self.read_more)
        self.read_button.grid(row=2, column=0, padx=(10, 5), pady=(0, 10), sticky="ew")

        self.fav_button = ctk.CTkButton(self, text="Add to Favorites", command=self.add_to_favorites)
        self.fav_button.grid(row=2, column=1, padx=(10, 5), pady=(0, 10), sticky="ew")

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
            print(f"Failed to save favorite: {e}")

# --- Grund-UI aufbauen ---
app = ctk.CTk()
app.title("News Application")
app.geometry("900x700")

tabs = ctk.CTkTabview(app)
tabs.pack(fill="both", expand=True)
tab_frames = {}
for name in CATEGORY_TABS:
    tab = tabs.add(name)
    sf = ctk.CTkScrollableFrame(tab)
    sf.pack(fill="both", expand=True, padx=6, pady=6)
    tab_frames[name] = sf

# Favoriten rendern (wie bei eurem Original)
def render_favorites():
    frame = tab_frames["Favorites"]
    for w in frame.winfo_children():
        w.destroy()

    favs = list_favs()
    if not favs:
        ctk.CTkLabel(frame, text="No favorites saved.").pack(pady=10)
        return

    for idx, art in enumerate(favs):
        row = ctk.CTkFrame(frame)
        row.pack(fill="x", padx=6, pady=6)

        title = art.get("title", "(without Titel)")
        src = (art.get("source") or "")
        ts = fmt_time(art.get("publishedAt", ""))

        ctk.CTkLabel(row, text=f"{title}\n{ts}   –   {src}", justify="left", wraplength=520)\
            .grid(row=0, column=0, sticky="w", padx=8, pady=6)

        def open_url(u=art.get("url", "")):
            if u:
                webbrowser.open(u)

        ctk.CTkButton(row, text="Open", command=open_url).grid(row=0, column=1, padx=6)
        ctk.CTkButton(row, text="Delete", fg_color="#aa3333",
                      command=lambda i=idx: (remove_favs(i), render_favorites()))\
            .grid(row=0, column=2, padx=6)

render_favorites()

# kleine Hilfsfunktionen zum Klassifizieren / Darstellen
def change_titel(titel):
    teile = titel.split('-')
    new_titel = ''.join(teile[:-1])
    return new_titel.strip() if new_titel.strip() else titel

def classify_article(article: dict) -> str:
    """Gibt den passenden Tab-Namen zurück (z. B. 'Sports News')."""
    # 1) wenn das Feld 'category' vorhanden ist, versuchen zu matchen
    cat = (article.get("category") or "").lower()
    short_map = {
        "business": "Business News",
        "general": "General News",
        "sports": "Sports News",
        "sport": "Sports News",
        "entertainment": "Entertainment News",
        "technology": "Technology News",
        "tech": "Technology News",
        "health": "Health News",
        "science": "Science News"
    }
    if cat:
        if cat in short_map:
            return short_map[cat]
    # 2) aus Titel / Beschreibung Keywords prüfen
    text = (article.get("title") or "") + " " + (article.get("description") or "")
    text = text.lower()
    for cat_name, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                return cat_name
    # 3) Fallback
    return "General News"

def clear_frame(frame):
    for w in frame.winfo_children():
        w.destroy()

def populate_tabs(articles: list):
    """Füllt die Tabs mit passenden NewsFrames."""
    # erst alle Tabs (außer Favorites) leeren
    for name, frame in tab_frames.items():
        if name == "Favorites":
            continue
        clear_frame(frame)

    # Latest News: alle Artikel
    for article in articles:
        headline = change_titel(article.get("title", "(ohne Titel)"))
        frame = NewsFrame(
            tab_frames["Latest News"],
            headline,
            article.get("url", ""),
            article.get("urlToImage", ""),
            article.get("publishedAt", ""),
            source=(article.get("source") or {}).get("name", "")
        )
        frame.pack(fill="both", expand=True, padx=4, pady=4)

    # für jede Kategorie passende Artikel hinzufügen
    for article in articles:
        cat = classify_article(article)
        # General News: nur die letzten RECENT_HOURS Stunden
        if cat == "General News":
            if not is_recent(article.get("publishedAt", "")):
                continue  # überspringen, zu alt
        # Wenn Tab existiert, hinzufügen
        if cat in tab_frames:
            headline = change_titel(article.get("title", "(ohne Titel)"))
            frame = NewsFrame(
                tab_frames[cat],
                headline,
                article.get("url", ""),
                article.get("urlToImage", ""),
                article.get("publishedAt", ""),
                source=(article.get("source") or {}).get("name", "")
            )
            frame.pack(fill="both", expand=True, padx=4, pady=4)

# --- Nachrichten laden und Tabs befüllen ---
articles = get_news()  # eure vorhandene Funktion (muss eine Liste von dicts liefern)
if not isinstance(articles, list):
    articles = []
# Abfrage am Anfang, bevor News geladen werden
import tkinter.simpledialog as simpledialog

populate_tabs(articles)

# Fenster starten
app.mainloop()