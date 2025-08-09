import customtkinter as ctk
import tkinter as tk
from PIL import Image
import webbrowser
import requests
from io import BytesIO
class NewsFrame(ctk.CTkFrame):
    def __init__(self, master, headline, url, imgurl, time):
        super().__init__(master)
        self.pack()
        # Configure grid weights for responsive layout
        self.columnconfigure(0, weight=1)  # Text column - flexible
        self.columnconfigure(1, weight=1)  # Button column - flexible  
        self.columnconfigure(2, weight=1)  # Image column - more space
        self.rowconfigure(0, weight=0)     # Headline row - no extra space
        self.rowconfigure(1, weight=0)     # Time row - no extra space
        self.rowconfigure(2, weight=0)     # Button row - no extra space
        self.create_widgets(headline, url, imgurl, time)

    def create_widgets(self, headline, url, imgurl, time):
        # Headline - top left, spans 2 columns for more width
        self.label = ctk.CTkLabel(self, text=headline, font=("Arial", 16, "bold"), 
                                 wraplength=400, justify="left")
        self.label.grid(row=0, column=0, columnspan=2, padx=10, pady=(10,2), sticky="w")

        # Published time - below headline
        self.age = ctk.CTkLabel(self, text=f"Published: {time}", font=("Arial", 10))
        self.age.grid(row=1, column=0, columnspan=2, padx=10, pady=(0,8), sticky="w")

        # Image - right side, spans all rows
        try:
            # Try to load image from URL
            if imgurl and imgurl.strip():
                response = requests.get(imgurl, timeout=5)
                img_data = Image.open(BytesIO(response.content))
                self.img = ctk.CTkImage(light_image=img_data, size=(225, 150))
            else:
                # Fallback to default image
                self.img = ctk.CTkImage(light_image=Image.open("photo.jpg"), size=(225, 150))
        except:
            # If URL fails, use default image
            self.img = ctk.CTkImage(light_image=Image.open("photo.jpg"), size=(225, 150))
        
        self.img_label = ctk.CTkLabel(self, image=self.img, text="")
        self.img_label.grid(row=0, column=2, rowspan=3, padx=10, pady=10, sticky="n")

        # Buttons - bottom row, side by side
        self.read_button = ctk.CTkButton(self, text="Read More", command=lambda: self.read_more(url))
        self.read_button.grid(row=2, column=0, padx=(10,5), pady=(0,10), sticky="ew")

        self.fav_button = ctk.CTkButton(self, text="Add to Favorites", command=self.add_to_favorites)
        self.fav_button.grid(row=2, column=1, padx=(5,10), pady=(0,10), sticky="ew")

    def read_more(self, url):
        webbrowser.open(url)

    def add_to_favorites(self):
        # Implement your logic to add the article to favorites
        pass

    def get_image(self):
        pass  # Placeholder for image retrieval logic if needed

app = ctk.CTk()
app.title("News Application")
app.geometry("800x600")
tabs = ctk.CTkTabview(app)
tabs.pack(fill="both", expand=True)
tab1 = tabs.add("Latest News")  
tab2 = tabs.add("Favorites")
tab3 = tabs.add("National News")
tab4 = tabs.add("International News")
tab5 = tabs.add("Sports News")
tab6 = tabs.add("Entertainment News")
tab7 = tabs.add("Technology News")
tab8 = tabs.add("Health News")

from newsapi import get_news
articles = get_news()
for article in articles:
    frame = NewsFrame(tab1, article['title'], article['url'], article.get('urlToImage', ''), article['publishedAt'])
    frame.pack(fill="both", expand=True)
app.mainloop()