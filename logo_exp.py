import customtkinter as ctk
import tkinter as tk

app = ctk.CTk()
from PIL import Image

img = Image.open("logo.png")
img.save("logo.ico", format="ICO")
logo_img = tk.PhotoImage(file="logo.png")
app.iconphoto(False, logo_img)
app.iconbitmap("logo.ico")
app.logo_img = logo_img
app.mainloop()