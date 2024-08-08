import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess
import os

class FFmpegGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("FFmpeg Command Generator")

        self.ffmpeg_path = None
        self.commands = []

        self.create_widgets()

    def create_widgets(self):
        self.add_command_frame()

        self.add_button = tk.Button(self.root, text="Добавить команду", command=self.add_command_frame)
        self.add_button.pack(pady=5)

        self.save_button = tk.Button(self.root, text="Создать BAT файл", command=self.save_commands)
        self.save_button.pack(pady=5)

        self.ffmpeg_button = tk.Button(self.root, text="Выбрать папку с ffmpeg", command=self.select_ffmpeg_path)
        self.ffmpeg_button.pack(pady=5)

        self.command_output = tk.Text(self.root, height=10)
        self.command_output.pack(pady=5, padx=5, fill='x')

    def add_command_frame(self):
        frame = tk.Frame(self.root)
        frame.pack(fill='x', pady=5)

        input_files = tk.Entry(frame, width=50)
        input_files.pack(side='left', padx=5)
        input_files.insert(0, "Выберите входные файлы")

        select_input_button = tk.Button(frame, text="Выбрать файлы", command=lambda: self.select_files(input_files, frame))
        select_input_button.pack(side='left')

        output_file = tk.Entry(frame, width=50)
        output_file.pack(side='left', padx=5)
        output_file.insert(0, "Выберите выходной файл")

        select_output_button = tk.Button(frame, text="Сохранить как", command=lambda: self.select_output_file(output_file))
        select_output_button.pack(side='left')

        delete_audio_var = tk.IntVar()
        save_audio_var = tk.IntVar()

        delete_audio_check = tk.Checkbutton(frame, text="Удалить звуковую дорожку", variable=delete_audio_var, command=self.update_command_output)
        delete_audio_check.pack(side='left', padx=5)

        save_audio_check = tk.Checkbutton(frame, text="Сохранить звуковую дорожку", variable=save_audio_var, command=self.update_command_output)
        save_audio_check.pack(side='left', padx=5)

        media_info_button = tk.Button(frame, text="Медиаинфо", state=tk.DISABLED, command=lambda: self.show_media_info(input_files.get()))
        media_info_button.pack(side='left', padx=5)

        self.commands.append((input_files, output_file, delete_audio_var, save_audio_var, media_info_button))

        video_codec_label = tk.Label(frame, text="Видео кодек:")
        video_codec_label.pack(side='left', padx=5)

        self.video_codec = ttk.Combobox(frame, values=["copy", "libx264", "libx265", "vp9", "mpeg4"])
        self.video_codec.set("copy")
        self.video_codec.pack(side='left', padx=5)

        audio_codec_label = tk.Label(frame, text="Аудио кодек:")
        audio_codec_label.pack(side='left', padx=5)

        self.audio_codec = ttk.Combobox(frame, values=["copy", "aac", "mp3", "vorbis", "opus"])
        self.audio_codec.set("copy")
        self.audio_codec.pack(side='left', padx=5)

    def select_files(self, entry, frame):
        file_paths = filedialog.askopenfilenames(filetypes=[("Video Files", "*.mp4;*.avi;*.mkv")])
        if file_paths:
            entry.delete(0, tk.END)
            entry.insert(0, ";".join(file_paths))
            self.update_output_file_name(entry)
            self.update_command_output()
            media_info_button = frame.children['!button3']
            media_info_button.config(state=tk.NORMAL)

    def select_output_file(self, entry):
        file_path = filedialog.asksaveasfilename(filetypes=[("Video Files", "*.mp4;*.avi;*.mkv")], defaultextension=".mp4")
        if file_path:
            entry.delete(0, tk.END)
            entry.insert(0, file_path)
        self.update_command_output()

    def select_ffmpeg_path(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.ffmpeg_path = folder_path
        self.update_command_output()

    def update_output_file_name(self, input_entry):
        input_files = input_entry.get().split(';')
        if input_files:
            input_file = input_files[0]
            base, ext = os.path.splitext(input_file)
            output_file = base + "_encoded" + ext
            for command in self.commands:
                command[1].delete(0, tk.END)
                command[1].insert(0, output_file)

    def update_command_output(self):
        self.command_output.delete(1.0, tk.END)
        commands_str = self.generate_commands_str()
        self.command_output.insert(tk.END, commands_str)

    def generate_commands_str(self):
        if not self.ffmpeg_path:
            ffmpeg_exec = "ffmpeg"
        else:
            ffmpeg_exec = f'"{self.ffmpeg_path}/ffmpeg"'
        
        commands_str = ""
        for command in self.commands:
            input_files = command[0].get().split(';')
            output_file = command[1].get()
            delete_audio = command[2].get()
            save_audio = command[3].get()

            for input_file in input_files:
                if not output_file:
                    base, ext = os.path.splitext(input_file)
                    output_file = base + "_encoded" + ext

                cmd = f'{ffmpeg_exec} -i "{input_file}" -c:v {self.video_codec.get()} -c:a {self.audio_codec.get()}'
                if delete_audio:
                    cmd += " -map 0:v? -map 0:s?"
                else:
                    cmd += " -map 0:v? -map 0:s? -map 0:a?"
                cmd += f' "{output_file}"'
                commands_str += cmd + "\n"

        return commands_str

    def save_commands(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".bat", filetypes=[("Batch File", "*.bat")])
        if not file_path:
            return

        with open(file_path, 'w', encoding='utf-8-sig') as f:
            f.write("chcp 65001\n")
            f.write(self.command_output.get(1.0, tk.END))
            f.write("pause\n")

        messagebox.showinfo("Успех", "BAT файл успешно создан!")

    def show_media_info(self, file_path):
        if not file_path:
            messagebox.showwarning("Ошибка", "Файл не выбран!")
            return

        if self.ffmpeg_path:
            ffprobe_exec = os.path.join(self.ffmpeg_path, "ffprobe")
        else:
            ffprobe_exec = "ffprobe"

        try:
            result = subprocess.run([ffprobe_exec, "-v", "error", "-show_entries", 
                                     "stream=index,codec_type,codec_name", "-of", "default=noprint_wrappers=1",
                                     file_path],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            messagebox.showinfo("Медиаинфо", result.stdout)
        except FileNotFoundError:
            messagebox.showerror("Ошибка", "Не удалось найти ffprobe. Проверьте путь к ffmpeg.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка при получении информации: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = FFmpegGUI(root)
    root.mainloop()
