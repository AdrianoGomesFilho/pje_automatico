import os
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog

def create_text_files_for_images(image_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    image_files = [f for f in os.listdir(image_dir) if f.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]
    current_index = 0

    def show_image(index):
        filename = image_files[index]
        image_path = os.path.join(image_dir, filename)
        text_filename = os.path.splitext(filename)[0] + '.txt'
        text_path = os.path.join(output_dir, text_filename)

        # Open the image
        img = Image.open(image_path)
        img = ImageTk.PhotoImage(img)
        panel.config(image=img)
        panel.image = img

        # Update the filename label
        filename_label.config(text=f"Filename: {filename}")

        # Adjust window size to fit the image
        root.geometry(f"{img.width()}x{img.height() + 150}")

    def show_next_image():
        nonlocal current_index
        if current_index < len(image_files):
            show_image(current_index)
        else:
            print("All images processed.")
            root.quit()

    def save_text(event=None):
        nonlocal current_index
        filename = image_files[current_index]
        text_filename = os.path.splitext(filename)[0] + '.txt'
        text_path = os.path.join(output_dir, text_filename)
        user_input = text_entry.get()
        with open(text_path, 'w') as text_file:
            text_file.write(user_input)
        print(f'Processed {filename} and created {text_filename}')
        current_index += 1
        text_entry.delete(0, tk.END)
        show_next_image()

    def return_to_previous(event=None):
        nonlocal current_index
        if current_index > 0:
            current_index -= 1
        while current_index > 0:
            prev_filename = image_files[current_index]
            prev_text_path = os.path.join(output_dir, os.path.splitext(prev_filename)[0] + '.txt')
            if os.path.exists(prev_text_path):
                os.remove(prev_text_path)
                print(f'Deleted {prev_text_path}')
                break
            current_index -= 1
        print(f'Returning to previous image: {image_files[current_index]}')
        text_entry.delete(0, tk.END)
        show_image(current_index)

    root = tk.Tk()
    root.title("CAPTCHA Box Creator")

    panel = tk.Label(root)
    panel.pack()

    filename_label = tk.Label(root, text="")
    filename_label.pack()

    text_entry = tk.Entry(root, width=50)
    text_entry.pack()

    save_button = tk.Button(root, text="Save and Next", command=save_text)
    save_button.pack()

    return_button = tk.Button(root, text="Return to Previous", command=return_to_previous)
    return_button.pack()

    root.bind('<Return>', save_text)  # Bind Enter key to save_text function
    root.bind('<BackSpace>', return_to_previous)  # Bind Backspace key to return_to_previous function

    show_next_image()
    root.mainloop()

# Example usage
image_directory = r'C:\Users\fish\script_pje\treinamento\imagens'
output_directory = r'C:\Users\fish\script_pje\treinamento\textos'
create_text_files_for_images(image_directory, output_directory)