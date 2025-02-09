import os
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog

def create_text_files_for_images(image_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    image_files = [f for f in os.listdir(image_dir) if f.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]
    current_index = 0

    def show_next_image():
        nonlocal current_index
        if current_index < len(image_files):
            filename = image_files[current_index]
            image_path = os.path.join(image_dir, filename)
            text_filename = os.path.splitext(filename)[0] + '.txt'
            text_path = os.path.join(output_dir, text_filename)

            # Open the image
            img = Image.open(image_path)
            img = ImageTk.PhotoImage(img)
            panel.config(image=img)
            panel.image = img

            # Adjust window size to fit the image
            root.geometry(f"{img.width()}x{img.height() + 100}")

            def save_text(event=None):
                nonlocal current_index
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
                text_entry.delete(0, tk.END)
                show_next_image()

            save_button.config(command=save_text)
            return_button.config(command=return_to_previous)
            root.bind('<Return>', save_text)  # Bind Enter key to save_text function
            root.bind('<BackSpace>', return_to_previous)  # Bind Backspace key to return_to_previous function
        else:
            print("All images processed.")
            root.quit()

    root = tk.Tk()
    root.title("CAPTCHA Box Creator")

    panel = tk.Label(root)
    panel.pack()

    text_entry = tk.Entry(root, width=50)
    text_entry.pack()

    save_button = tk.Button(root, text="Save and Next")
    save_button.pack()

    return_button = tk.Button(root, text="Return to Previous")
    return_button.pack()

    show_next_image()
    root.mainloop()

# Example usage
image_directory = r'C:\Users\fish\script_pje\treinamento\imagens'
output_directory = r'C:\Users\fish\script_pje\treinamento\textos'
create_text_files_for_images(image_directory, output_directory)