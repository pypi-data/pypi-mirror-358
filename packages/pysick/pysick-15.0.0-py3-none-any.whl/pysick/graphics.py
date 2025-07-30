
def __element__():
    global SickError
    from pysick import pysick_core
    from pysick_core import SickError as err
    SickError = err
__element__()
##########################################################
def draw_rect(master, x, y, width, height, fill):
    try:
        x2 = x + width
        y2 = y + height
        master.canvas.create_rectangle(x, y, x2, y2, fill=fill)
    except Exception as ex:
        raise SickError(str(ex))

def fill_screen(master, fill):
    try:
        master.canvas.delete("all")
        master.canvas.create_rectangle(0, 0, master.width, master.height, fill=fill)
    except Exception as ex:
        raise SickError(str(ex))

def draw_oval(master, x, y, width, height, fill):
    try:
        x2 = x + width
        y2 = y + height
        master.canvas.create_oval(x, y, x2, y2, fill=fill)
    except Exception as ex:
        raise SickError(str(ex))

def draw_circle(master, x, y, radius, fill):
    try:
        master.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill=fill)
    except Exception as ex:
        raise SickError(str(ex))
def draw_line(master, x1, y1, x2, y2, fill):
    try:
        master.canvas.create_line(x1, y1, x2, y2, fill=fill)
    except Exception as ex:
        raise SickError(str(ex))
