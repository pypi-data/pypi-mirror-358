from . import _tkinter_pysick as tk
from . import _messagebox_pysick as messagebox
SickVersion = '15.0.0'
class SickError(Exception):
    """Custom error for PySick module."""
    def __init__(self, message="A SickError occurred!"):
        super().__init__(message)
class InGine:
    def __init__(self, width, height):
        global icon_path_red,icon_path_yellow,icon_path_blue
        print(f'[pysick] Window Initialized with {width}x{height}')
        self.root = tk.Tk()
        self.root.title('pysick graphics')
        self.width = width
        self.height = height
        self.root.geometry(str(self.width) + 'x' + str(self.height))
        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height)
        self.canvas.delete('all')
        self.canvas.pack()
        try:
            import os
            icon_path_blue = os.path.join(os.path.dirname(__file__), "assets/blue_icon_2k.png")
            icon_path_red = os.path.join(os.path.dirname(__file__), "assets/red_icon_2k.png")
            icon_path_yellow = os.path.join(os.path.dirname(__file__), "assets/yellow_icon_2k.png")
            icon_image = tk.PhotoImage(file=icon_path_blue)
            self.root.iconphoto(True, icon_image)
        except Exception as ex:
            raise SickError(str(ex))
    def sickloop(self):
        try:
            icon_image_yellow = tk.PhotoImage(file=icon_path_yellow)
            self.root.iconphoto(True, icon_image_yellow)
        except Exception as ex:
            raise SickError(str(ex))

        self.root.mainloop()
    def set_title(self, title):
        self.root.title(title)
    def lock(self, key, func):
        self.root.bind(key, lambda event: func())
    def unlock(self, key):
        self.root.unbind(key)
    def add_label(self, text, x, y, font=("Arial", 14), color="black"):
        label = tk.Label(self.root, text=text, font=font, fg=color)
        label.place(x=x, y=y)
    def add_button(self, text, x, y, func, width=10, height=2):
        button = tk.Button(self.root, text=text, command=func, width=width, height=height)
        button.place(x=x, y=y)
    def time_in(self, ms, func):
        self.root.after(ms, lambda: func())
    def quit(self):
        self.root.destroy()
class message_box:
    @staticmethod
    def ask_question(title, text):
        messagebox.askquestion(title, text)
    @staticmethod
    def show_info(title, text):
        messagebox.showinfo(title, text)
    @staticmethod
    def show_warning(title, text):
        messagebox.showwarning(title, text)
    @staticmethod
    def show_error(title, text):
        messagebox.showerror(title, text)
    @staticmethod
    def about(title, text):
        messagebox.showinfo(title, text)
class graphics:
    @staticmethod
    def draw_rect(master, x, y, width, height, fill):
        try:
            x2 = x + width
            y2 = y + height
            master.canvas.create_rectangle(x, y, x2, y2, fill=fill)
        except Exception as ex:
            raise SickError(str(ex))
    @staticmethod
    def fill_screen(master, fill):
        try:
            master.canvas.delete("all")
            master.canvas.create_rectangle(0, 0, master.width, master.height, fill=fill)
        except Exception as ex:
            raise SickError(str(ex))
    @staticmethod
    def draw_oval(master, x, y, width, height, fill):
        try:
            x2 = x + width
            y2 = y + height
            master.canvas.create_oval(x, y, x2, y2, fill=fill)
        except Exception as ex:
            raise SickError(str(ex))
    @staticmethod
    def draw_circle(master, x, y, radius, fill):
        try:
            master.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill=fill)
        except Exception as ex:
            raise SickError(str(ex))
    @staticmethod
    def draw_line(master, x1, y1, x2, y2, fill):
        try:
            master.canvas.create_line(x1, y1, x2, y2, fill=fill)
        except Exception as ex:
            raise SickError(str(ex))
def about():
    messagebox.showinfo('pysick shows', f'Hello, this is pysick(v.{SickVersion},2.1.2026),tk(-v{str(tk.TkVersion)}),Tcl(v-3.10)')

if __name__ != '__main__':
    print('\033[36m Hello. This is to say that the module is imported correctly.')
    print(f'pysick(v.{SickVersion},2.1.2026),tk(-v{str(tk.TkVersion)}),Tcl(v-3.10)LicenseRelease')
    print('Hi from CowZik Singles\033 [0m')

