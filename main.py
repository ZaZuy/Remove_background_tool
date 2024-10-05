import customtkinter as ctk
import tkinter
from tkinter import filedialog
from PIL import Image, ImageTk, ImageEnhance, ImageFilter
from rembg import remove
import os

crop_start_x, crop_start_y = None, None
crop_rect_id = None
cropped_img = None
save_img = None

def load_image():
    """Function to load an image file from the selected folder and display it on the canvas."""
    global tk_image, img, file_path
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png;*.bmp")])
    if file_path:
        img = Image.open(file_path)
        img = img.resize((512, 512), Image.LANCZOS)  
        tk_image = ImageTk.PhotoImage(img)

        canvas_load.delete("all") 
        canvas_load.create_image(0, 0, anchor="nw", image=tk_image)
        canvas_load.image = tk_image 

        generate_button.configure(state="normal")

def start_crop(event):
    global crop_start_x, crop_start_y, crop_rect_id
    crop_start_x, crop_start_y = event.x, event.y
    if crop_rect_id:
        canvas_load.delete(crop_rect_id)
    crop_rect_id = canvas_load.create_rectangle(crop_start_x, crop_start_y, crop_start_x, crop_start_y, outline='red')

def update_crop(event):
    if crop_rect_id:
        canvas_load.coords(crop_rect_id, crop_start_x, crop_start_y, event.x, event.y)

def end_crop(event):
    global img, cropped_img
    if crop_start_x is not None and crop_start_y is not None:
        end_x, end_y = event.x, event.y
        left, top, right, bottom = min(crop_start_x, end_x), min(crop_start_y, end_y), max(crop_start_x, end_x), max(crop_start_y, end_y)
        cropped_img = img.crop((left, top, right, bottom))
        cropped_img = cropped_img.resize((152, 152), Image.LANCZOS)
        cropped_img = cropped_img.filter(ImageFilter.SHARPEN)
        enhancer = ImageEnhance.Contrast(cropped_img)
        cropped_img = enhancer.enhance(1.2)

        enhancer = ImageEnhance.Brightness(cropped_img)
        cropped_img = enhancer.enhance(1.1)

        tk_cropped_image = ImageTk.PhotoImage(cropped_img)

        out_frame.delete("all") 
        out_frame.create_image(0, 0, anchor="nw", image=tk_cropped_image)
        out_frame.image = tk_cropped_image

def removebg():
    global cropped_img, save_img
    if cropped_img:
        image_without_bg = remove(cropped_img)
        save_img = image_without_bg.copy()
        tk_image_without_bg = ImageTk.PhotoImage(image_without_bg)

        out_frame.delete("all")
        out_frame.create_image(0, 0, anchor="nw", image=tk_image_without_bg)
        out_frame.image = tk_image_without_bg
        save_button.configure(state="normal")

def save():
    global save_img
    if save_img:
        save_directory = filedialog.askdirectory(title="Select Save Directory")
        if save_directory:
            outputPath = os.path.join(save_directory, os.path.basename(file_path).replace(os.path.splitext(file_path)[1], '') + '_nobg.png')
            save_img.save(outputPath)
            print(f"Background removed successfully. Image saved at: {outputPath}")
        else:
            print("Save operation was canceled.")
    else:
        print("No image to save.")

root = ctk.CTk()
root.title("Crop & Remove Background")

ctk.set_appearance_mode("dark")

# Input frame on the left side
input_frame = ctk.CTkFrame(root)
input_frame.pack(side="left", expand=True, padx=20, pady=20)

# Button to select an image
select_button = ctk.CTkButton(input_frame, text="Select Image", command=load_image)
select_button.grid(row=3, column=0, columnspan=2, sticky="news", padx=10, pady=10)

# Generate button to remove background (disabled initially)
generate_button = ctk.CTkButton(input_frame, text="Generate", command=removebg, state="disabled")
generate_button.grid(row=5, column=0, columnspan=2, sticky="news", padx=10, pady=10)

# Save button (disabled initially)
save_button = ctk.CTkButton(input_frame, text="Save", command=save, state="disabled")
save_button.grid(row=7, column=0, columnspan=2, sticky="news", padx=10, pady=10)

# Canvas to display the loaded image
canvas_load = tkinter.Canvas(root, width=512, height=512)
canvas_load.pack(side="left")

# Bind mouse events for cropping
canvas_load.bind("<ButtonPress-1>", start_crop)
canvas_load.bind("<B1-Motion>", update_crop)
canvas_load.bind("<ButtonRelease-1>", end_crop)

# Output frame (as a canvas) on the right side
out_frame = tkinter.Canvas(root, width=152, height=152) 
out_frame.pack(side="right", expand=True, padx=10, pady=10)

root.mainloop()