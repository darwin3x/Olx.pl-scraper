import requests
from bs4 import BeautifulSoup
import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
from io import BytesIO
import subprocess
import threading
import time
import platform
import winsound

# Konfiguracja
print("\033[35m" + r"""
   ________  .__             _________                                      
   \_____  \ |  | ___  ___  /   _____/ ________________  ______   ___________ 
    /   |   \|  | \  \/  /  \_____  \_/ ___\_  __ \__  \ \____ \_/ __ \_  __ \
   /    |    \  |__>    <   /        \  \___|  | \// __ \|  |_> >  ___/|  | \/
   \_______  /____/__/\_ \ /_______  /\___  >__|  (____  /   __/ \___  >__|   
           \/           \/         \/     \/           \/|__|        \/        
""" + "\033[0m")

# Pobranie linku OLX
URL = input("\033[35mPodaj link do strony OLX: \033[0m")
ODSWIEZ_CO_SEKUND = 10
wyswietlone_linki = set()

def placeholder_image(size=(120, 120)):
    img = Image.new("RGB", size, color="#2e2e2e")
    draw = ImageDraw.Draw(img)
    text = "Brak zdjęcia"
    w, h = draw.textsize(text)
    draw.text(((size[0]-w)/2, (size[1]-h)/2), text, fill="white")
    return ImageTk.PhotoImage(img)

def pobierz_obraz(url):
    if not url:
        return placeholder_image()
    if url.startswith("//"):
        url = "https:" + url
    try:
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        img = Image.open(BytesIO(r.content))
        img.thumbnail((120, 120))
        return ImageTk.PhotoImage(img)
    except:
        return placeholder_image()

def otworz_link(link):
    if not link.startswith("http"):
        link = "https://www.olx.pl" + link
    subprocess.run(f'start "" "{link}"', shell=True)

def dodaj_ogloszenie_gui(parent, ogloszenie):
    frame_bg = "#1e1e1e"
    container = tk.Frame(parent, bg=parent['bg'])
    container.pack(anchor="n", pady=5)

    prostokat_width = 700
    prostokat_height = 160
    frame = tk.Frame(container, bg=frame_bg, width=prostokat_width, height=prostokat_height, bd=0)
    frame.pack()
    frame.pack_propagate(False)
    frame.grid_propagate(False)
    frame.columnconfigure(1, weight=1)

    # Obraz oferty
    img_label = tk.Label(frame, bg=frame_bg, width=120, height=120)
    if ogloszenie['image']:
        img_label.config(image=ogloszenie['image'])
        img_label.image = ogloszenie['image']
    img_label.grid(row=0, column=0, rowspan=4, padx=5, pady=5)

    # Tekst oferty
    tk.Label(frame, text=f"Tytuł: {ogloszenie.get('title', 'Brak tytułu')}", font=("Arial", 11, "bold"),
             wraplength=400, justify="left", bg=frame_bg, fg="white").grid(row=0, column=1, sticky="w")
    tk.Label(frame, text=f"Cena: {ogloszenie.get('price', 'Brak ceny')}", fg="#b366ff",
             wraplength=400, justify="left", bg=frame_bg).grid(row=1, column=1, sticky="w")
    tk.Label(frame, text=f"Lokalizacja: {ogloszenie.get('location', 'Brak lokalizacji')}", fg="#b366ff",
             wraplength=400, justify="left", bg=frame_bg).grid(row=2, column=1, sticky="w")
    tk.Label(frame, text=f"Link: {ogloszenie.get('link', '')}", fg="#b366ff",
             wraplength=400, justify="left", bg=frame_bg).grid(row=3, column=1, sticky="w")

    # Przycisk otwórz oferte
    button_width = 160
    button_height = 40
    button_bg = "#4b0082"
    button_hover = "#6a0dad"
    button_fg = "white"
    corner_radius = 15

    canvas_btn = tk.Canvas(frame, width=button_width, height=button_height, highlightthickness=0, bg=frame_bg)
    canvas_btn.grid(row=0, column=2, rowspan=4, sticky="e", padx=5, pady=5)

    def create_rounded_rect(canvas, x1, y1, x2, y2, r, **kwargs):
        points = [
            x1+r, y1, x2-r, y1, x2, y1+r, x2, y2-r,
            x2-r, y2, x1+r, y2, x1, y2-r, x1, y1+r
        ]
        return canvas.create_polygon(points, smooth=True, **kwargs)

    rect = create_rounded_rect(canvas_btn, 2, 2, button_width-2, button_height-2, corner_radius,
                               fill=button_bg, outline="")
    txt = canvas_btn.create_text(button_width//2, button_height//2, text="Otwórz w przeglądarce",
                                 fill=button_fg, font=("Arial", 10, "bold"), width=button_width-20)

    def on_enter(e):
        canvas_btn.itemconfig(rect, fill=button_hover)
        canvas_btn.config(cursor="hand2")
    def on_leave(e):
        canvas_btn.itemconfig(rect, fill=button_bg)
        canvas_btn.config(cursor="")

    for tag in [rect, txt]:
        canvas_btn.tag_bind(tag, "<Enter>", on_enter)
        canvas_btn.tag_bind(tag, "<Leave>", on_leave)
        canvas_btn.tag_bind(tag, "<Button-1>", lambda e: otworz_link(ogloszenie['link']))

def monitoruj_ogloszenia(parent):
    global wyswietlone_linki

    # Zapis linków
    try:
        response = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            ads = soup.select('[data-cy="l-card"]')
            for ad in ads:
                link_el = ad.select_one('a.css-1tqlkj0')
                link = link_el['href'] if link_el else None
                if link:
                    wyswietlone_linki.add(link)
    except:
        pass

    while True:
        try:
            response = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"})
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                ads = soup.select('[data-cy="l-card"]')
                for ad in ads:
                    link_el = ad.select_one('a.css-1tqlkj0')
                    link = link_el['href'] if link_el else None
                    if not link or link in wyswietlone_linki:
                        continue

                    title_el = ad.select_one('[data-cy="ad-card-title"] h4')
                    price_el = ad.select_one('[data-testid="ad-price"]')
                    location_el = ad.select_one('[data-testid="location-date"]')
                    img_el = ad.find('img')
                    img_url = None
                    if img_el:
                        img_url = img_el.get('src') or img_el.get('data-src') or img_el.get('data-lazy')

                    ogloszenie = {
                        'title': title_el.get_text(strip=True) if title_el else "Brak tytułu",
                        'price': price_el.get_text(strip=True) if price_el else "Brak ceny",
                        'location': location_el.get_text(strip=True) if location_el else "Brak lokalizacji",
                        'link': link,
                        'image': pobierz_obraz(img_url)
                    }

                    wyswietlone_linki.add(link)
                    parent.after(0, dodaj_ogloszenie_gui, parent, ogloszenie)

                    # Dźwięk
                    try:
                        winsound.Beep(1000, 1000)
                    except:
                        pass
        
        except Exception as e:
           print("Błąd:", e)

        time.sleep(ODSWIEZ_CO_SEKUND)

# GUI
root = tk.Tk()
root.title("Monitor OLX - nowe ogłoszenia")
root.geometry("700x650")
root.resizable(False, False)
root.configure(bg="#121212")

main_frame = tk.Frame(root, bg="#121212")
main_frame.pack(fill="both", expand=True)

canvas = tk.Canvas(main_frame, bg="#121212", bd=0, highlightthickness=0)
scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview,
                         bg="#6a0dad", troughcolor="#1e1e1e", activebackground="#8b00ff",
                         bd=0, highlightthickness=0)
scrollable_frame = tk.Frame(canvas, bg="#121212")

canvas.configure(yscrollcommand=scrollbar.set)
canvas.create_window((0,0), window=scrollable_frame, anchor="n")

def on_frame_configure(event):
    canvas.configure(scrollregion=canvas.bbox("all"))
scrollable_frame.bind("<Configure>", on_frame_configure)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Scroll myszką – obsługa platformowa
def _on_mousewheel(event):
    system = platform.system()
    if system == "Windows":
        canvas.yview_scroll(-1 * int(event.delta / 120), "units")

canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))
canvas.bind("<Button-4>", _on_mousewheel)
canvas.bind("<Button-5>", _on_mousewheel)

# Monitoruj w tle
threading.Thread(target=monitoruj_ogloszenia, args=(scrollable_frame,), daemon=True).start()

root.mainloop()
