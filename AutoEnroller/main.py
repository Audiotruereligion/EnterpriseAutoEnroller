import subprocess
import json
import tkinter as tk
import threading
import sys

new_array = []
path = "C:\\Users\\The Lab\\PycharmProjects\\AutoEnroller\\"
blank_ino = open(path + 'Blank.txt', 'r')
ae_ino = open(path + 'AE.txt', 'r')
auto_enroller_ino = open('AutoEnroller.ino', 'w')
sketch = path + 'AutoEnroller.ino'
file = 'C:\\Users\\The Lab\\PycharmProjects\\AutoEnroller\\arduino-cli.exe'
search = [path+'arduino-cli', 'core', 'search', 'Arduino Leonardo', '--format', 'json']
output = subprocess.Popen(search, stdout=subprocess.PIPE).communicate()[0]
board_son = json.loads(output)
board = board_son[0]['id'] + ':leonardo'
print(board)
install = ['arduino-cli', 'core', 'install', board]
list_boards = [file, 'board', 'list', '--format', 'json']
board_list = subprocess.Popen(list_boards, stdout=subprocess.PIPE).communicate()[0]
board_json = json.loads(board_list)
for key in board_json:
    new_array.append(key['address'])
old_array = new_array
count = 3
thread_looping = True
ready_to_load = False


class FlashThread(threading.Thread):
    def __init__(self, thread_id, name, counter):
        threading.Thread.__init__(self)
        self.threadID = thread_id
        self.name = name
        self.counter = counter

    def run(self):
        auto_enroller_ino.seek(1)
        auto_enroller_ino.write(blank_ino.read())
        auto_enroller_ino.truncate()
        compile_cmd = ['arduino-cli', 'compile', '-b', board, sketch]
        print(subprocess.Popen(compile_cmd, stdout=subprocess.PIPE).communicate()[0])
        for k in new_array:
            print("found device at: "+k['address'])
            com = k['address']
            flash_blank_cmd = ['arduino-cli', 'upload', '--port', com, '--fqbn', board, sketch]
            subprocess.call(flash_blank_cmd)


class ThreadLoop (threading.Thread):
    def __init__(self, thread_id, name, counter):
        threading.Thread.__init__(self)
        self.threadID = thread_id
        self.name = name
        self.counter = counter

    def run(self):
        global new_array
        global old_array
        global count
        while thread_looping:
            print('listening')
            loop_list = subprocess.Popen(list_boards, stdout=subprocess.PIPE).communicate()[0]
            loop_json = json.loads(loop_list)
            new_array = []
            for k in loop_json:
                print("found device")
                new_array.append(k['address'])
            for x in old_array:
                if x not in new_array:
                    print(x + ' changed')
                    flash_thread = FlashThread(count, "Flash-Thread", count)
                    flash_thread.start()
                    count = count + 1
            old_array = new_array


class InputThread (threading.Thread):
    def __init__(self, thread_id, name, counter):
        threading.Thread.__init__(self)
        self.threadID = thread_id
        self.name = name
        self.counter = counter

    def run(self):
        auto_enroller_ino.seek(1)
        auto_enroller_ino.write(ae_ino.read())
        auto_enroller_ino.truncate()
        auto_enroller_ino.close()
        compile_file = ['arduino-cli', 'compile', '-b', board, sketch]
        for b in new_array:
            print(subprocess.Popen(compile_file, stdout=subprocess.PIPE).communicate()[0])
            upload = ['arduino-cli', 'upload', '--port', b, '--fqbn', board, sketch]
            subprocess.call(upload)


loop_thread = ThreadLoop(1, "Loop-Thread", 1)
input_thread = InputThread(2, "Input-Thread", 2)
loop_thread.start()


def start_processing():
    global thread_looping
    thread_looping = False
    input_thread.start()


window = tk.Tk()
pixel = tk.PhotoImage(width=1, height=1)
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
width = int(screen_width*.8)
height = int(screen_height*.8)
offset_x = int(screen_width*.1)
offset_y = int(screen_height*.1)
window.geometry(str(width) + "x" + str(height) + "+" + str(offset_x) + "+" + str(offset_y))
button = tk.Button(window, text="Flash devices", bg="#082267", fg="white", command=start_processing, image=pixel,
                   width=100, height=60, compound="c")

window.configure(bg='#e8c7ae')
img = tk.PhotoImage(file="assets/AutoEnroller.png")

canvas = tk.Canvas(window, width=img.width(), height=img.height())
canvas.create_image(0, 0, anchor=tk.NW, image=img)
canvas.grid(column=4)
button.grid(column=4)


def on_closing():
    global thread_looping
    window.destroy()
    thread_looping = False
    sys.exit("done")


window.protocol("WM_DELETE_WINDOW", on_closing)
window.mainloop()