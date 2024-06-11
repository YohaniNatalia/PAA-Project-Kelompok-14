import numpy as np
from PIL import Image, ImageTk
import random
import tkinter as tk

# Konfigurasi ukuran peta dan sel
map_width, map_height = 150, 150
cell_size = 80  # Ukuran setiap sel dalam piksel

# Menginisialisasi peta
city_map = np.zeros((map_height * cell_size, map_width * cell_size, 3), dtype=np.uint8)
occupied_map = np.zeros((map_height, map_width), dtype=bool)  # Matriks status peta

# Fungsi untuk memeriksa apakah area bangunan bersebelahan dengan jalan
def is_next_to_road(x, y, size):
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    for dy in range(size[1]):
        for dx in range(size[0]):
            nx, ny = x + dx, y + dy
            for ddx, ddy in directions:
                nnx, nny = nx + ddx, ny + ddy
                if 0 <= nnx < map_width and 0 <= nny < map_height and occupied_map[nny, nnx]:
                    return True
    return False

# Fungsi untuk menggambar jalan dengan garis putus-putus
def draw_road(color, start, end, dashed=False):
    dash_length = 20 # Panjang dash dan gap dalam piksel (disesuaikan dengan skala)
    if start[0] == end[0]:  # Jalan vertikal
        for y in range(start[1], end[1] + 1):
            if 0 <= y < map_height and 0 <= start[0] < map_width:
                city_map[y * cell_size:(y + 1) * cell_size, start[0] * cell_size:(start[0] + 1) * cell_size] = color
                occupied_map[y, start[0]] = True
                if dashed and y % dash_length < dash_length // 1:
                    for i in range(cell_size // 4, cell_size * 3 // 4):  # Garis putus-putus di tengah
                        city_map[y * cell_size + i, start[0] * cell_size + cell_size // 2 - 1:start[0] * cell_size + cell_size // 2 + 1] = [255, 255, 255]
    else:  # Jalan horizontal
        for x in range(start[0], end[0] + 1):
            if 0 <= start[1] < map_height and 0 <= x < map_width:
                city_map[start[1] * cell_size:(start[1] + 1) * cell_size, x * cell_size:(x + 1) * cell_size] = color
                occupied_map[start[1], x] = True
                if dashed and x % dash_length < dash_length // 1:
                    for i in range(cell_size // 4, cell_size * 3 // 4):  # Garis putus-putus di tengah
                        city_map[start[1] * cell_size + cell_size // 2 - 1:start[1] * cell_size + cell_size // 2 + 1, x * cell_size + i] = [255, 255, 255]

# Fungsi untuk menempatkan bangunan secara berulang sampai berhasil
def place_building_until_success(image_path, size, max_attempts=1000):
    for _ in range(max_attempts):
        top_left = (random.randint(0, map_width - size[0]), random.randint(0, map_height - size[1]))
        if is_next_to_road(top_left[0], top_left[1], size) and not occupied_map[top_left[1]:top_left[1] + size[1], top_left[0]:top_left[0] + size[0]].any():
            try:
                building = Image.open(image_path).convert('RGB')
                building = building.resize((size[0] * cell_size, size[1] * cell_size), Image.LANCZOS)
                y_start = top_left[1] * cell_size
                y_end = y_start + size[1] * cell_size
                x_start = top_left[0] * cell_size
                x_end = x_start + size[0] * cell_size
                city_map[y_start:y_end, x_start:x_end] = np.array(building)
                occupied_map[top_left[1]:top_left[1] + size[1], top_left[0]:top_left[0] + size[0]] = True
                return True
            except FileNotFoundError:
                print(f"File not found: {image_path}")
                return False
    return False

# Fungsi untuk membagi area menggunakan Binary Space Partitioning dan membuat jalan dengan pola
def binary_space_partition(x, y, width, height, min_size, roads):
    if width <= min_size * 2 or height <= min_size * 2:
        return

    vertical_split = width > height
    if vertical_split:
        if width > min_size * 2:
            split = random.randint(min_size, width - min_size)
            draw_road([148, 148, 148], (x + split, y), (x + split, y + height - 1), True)
            roads.append((x + split, y, x + split, y + height - 1))
            binary_space_partition(x, y, split, height, min_size, roads)
            binary_space_partition(x + split, y, width - split, height, min_size, roads)
    else:
        if height > min_size * 2:
            split = random.randint(min_size, height - min_size)
            draw_road([148, 148, 148], (x, y + split), (x + width - 1, y + split), True)
            roads.append((x, y + split, x + width - 1, y + split))
            binary_space_partition(x, y, width, split, min_size, roads)
            binary_space_partition(x, y + split, width, height - split, min_size, roads)

# Fungsi untuk menghubungkan semua jalan ke tepi kanvas atau ke jalan lain
def extend_road_to_edge_or_road():
    for y in range(map_height):
        for x in range(map_width):
            if occupied_map[y, x]:
                if x == 0 or not occupied_map[y, x - 1]:
                    extend_road([148, 148, 148], (x, y), (-1, 0))  # Kiri
                if x == map_width - 1 or not occupied_map[y, x + 1]:
                    extend_road([148, 148, 148], (x, y), (1, 0))  # Kanan
                if y == 0 or not occupied_map[y - 1, x]:
                    extend_road([148, 148, 148], (x, y), (0, -1))  # Atas
                if y == map_height - 1 or not occupied_map[y + 1, x]:
                    extend_road([148, 148, 148], (x, y), (0, 1))  # Bawah

def extend_road(color, start, direction):
    x, y = start
    dx, dy = direction
    while 0 <= x < map_width and 0 <= y < map_height and not occupied_map[y, x]:
        city_map[y * cell_size:(y + 1) * cell_size, x * cell_size:(x + 1) * cell_size] = color
        occupied_map[y, x] = True
        x += dx
        y += dy

# Fungsi untuk desain ulang kota dengan berbagai tata letak
def redesign_city(layout):
    global city_map, occupied_map
    city_map.fill(0)  # Membersihkan peta
    occupied_map.fill(False)  # Membersihkan status peta

    grass_color = [34, 139, 34]  # Warna hijau tua untuk area kosong

    roads = []
    if layout == "BSP":
        # Buat jalan dengan algoritma BSP
        binary_space_partition(0, 0, map_width, map_height, 20, roads)
    elif layout == "Grid":
        # Buat jalan dengan tata letak grid
        for i in range(0, map_width, 10):
            draw_road([148, 148, 148], (i, 0), (i, map_height - 1), True)
            roads.append((i, 0, i, map_height - 1))
        for j in range(0, map_height, 10):
            draw_road([148, 148, 148], (0, j), (map_width - 1, j), True)
            roads.append((0, j, map_width - 1, j))

    # Perluas jalan buntu ke tepi kanvas atau jalan lain
    extend_road_to_edge_or_road()

    # Tempatkan bangunan dengan memastikan jumlah yang diinginkan
    place_building_until_success(r"C:\CBM PAA\Kelompok 14 PAA\Kelompok 14\Map Assets\roof2.png", (10, 5))
    for _ in range(4):
        place_building_until_success(r"C:\CBM PAA\Kelompok 14 PAA\Kelompok 14\Map Assets\roof1.png", (5, 3))
    for _ in range(10):
        place_building_until_success(r"C:\CBM PAA\Kelompok 14 PAA\Kelompok 14\Map Assets\rumah_lebar.png", (2, 2))
    for _ in range(10):
        place_building_until_success(r"C:\CBM PAA\Kelompok 14 PAA\Kelompok 14\Map Assets\rumah_kecil.png", (1, 2))
    for _ in range(5):
        place_building_until_success(r"C:\CBM PAA\Kelompok 14 PAA\Kelompok 14\Map Assets\air-mancur.png", (9, 7))
    for _ in range(10):
        place_building_until_success(r"C:\CBM PAA\Kelompok 14 PAA\Kelompok 14\Map Assets\rumah_besar.png", (4, 3))

    # Tempatkan pohon di area yang kosong
    tree_image = Image.open(r"C:\CBM PAA\Kelompok 14 PAA\Kelompok 14\Map Assets\pohon.png").convert('RGB')
    tree_image = tree_image.resize((2 * cell_size, 2* cell_size), Image.LANCZOS)
    tree_array = np.array(tree_image)

    for y in range(map_height - 1):  # -1 to avoid index error for 2x2 trees
        for x in range(map_width - 1):  # -1 to avoid index error for 2x2 trees
            if not occupied_map[y, x] and not occupied_map[y, x + 1] and not occupied_map[y + 1, x] and not occupied_map[y + 1, x + 1]:
                if random.random() < 0.1:  # Adjust probability as needed
                    city_map[y * cell_size:(y + 2) * cell_size, x * cell_size:(x + 2) * cell_size] = tree_array
                    occupied_map[y:y + 2, x:x + 2] = True

    # Warna hijau untuk area kosong
    for y in range(map_height):
        for x in range(map_width):
            if not occupied_map[y, x]:
                city_map[y * cell_size:(y + 1) * cell_size, x * cell_size:(x + 1) * cell_size] = grass_color

# Fungsi untuk memperbarui tampilan peta
def update_map(layout, zoom_level=2):
    redesign_city(layout)
    final_map = Image.fromarray(city_map)
    final_map_resized = final_map.resize((map_width * cell_size // zoom_level, map_height * cell_size // zoom_level), Image.LANCZOS)  # Sesuaikan zoom
    img_tk = ImageTk.PhotoImage(final_map_resized)

    canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)
    canvas.image = img_tk  # Simpan referensi gambar untuk mencegah garbage collection
    canvas.config(scrollregion=canvas.bbox(tk.ALL))  # Set scrollregion after image is created

# Fungsi untuk zoom in
def zoom_in():
    global zoom_level
    zoom_level = max(1, zoom_level - 1)  # Kurangi level zoom, dengan batas minimum 1
    update_map(layout_var.get(), zoom_level)

# Fungsi untuk zoom out
def zoom_out():
    global zoom_level
    zoom_level += 1  # Tambah level zoom
    update_map(layout_var.get(), zoom_level)

# GUI setup
root = tk.Tk()
root.title("IKN Design City")

# Frame utama untuk canvas dan scrollbars
frame = tk.Frame(root)
frame.pack(fill=tk.BOTH, expand=True)

# Frame untuk tombol dan scrollbar horizontal
bottom_frame = tk.Frame(root)
bottom_frame.pack(fill=tk.X, side=tk.BOTTOM)

# Setup canvas untuk menampilkan gambar
canvas = tk.Canvas(frame, width=750, height=550)
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Scrollbars
hbar = tk.Scrollbar(bottom_frame, orient=tk.HORIZONTAL, command=canvas.xview)
hbar.pack(side=tk.BOTTOM, fill=tk.X)
vbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
vbar.pack(side=tk.RIGHT, fill=tk.Y)
canvas.config(xscrollcommand=hbar.set, yscrollcommand=vbar.set)

# Dropdown untuk memilih tata letak
layout_var = tk.StringVar(root)
layout_var.set("BSP")  # Default value

layout_menu = tk.OptionMenu(bottom_frame, layout_var, "BSP", "Grid")
layout_menu.pack(side=tk.BOTTOM)

# Button to redesign map
button = tk.Button(bottom_frame, text="Redesign Map", command=lambda: update_map(layout_var.get(), zoom_level))
button.pack(side=tk.BOTTOM)

# Zoom in and zoom out buttons
zoom_in_button = tk.Button(bottom_frame, text="Zoom In", command=zoom_in)
zoom_in_button.pack(side=tk.LEFT)

zoom_out_button = tk.Button(bottom_frame, text="Zoom Out", command=zoom_out)
zoom_out_button.pack(side=tk.RIGHT)

# Menampilkan peta awal
zoom_level = 2  # Level zoom awal
update_map(layout_var.get(), zoom_level)

root.mainloop()
