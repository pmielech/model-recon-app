import tkinter.messagebox
from tkinter import *
# from PyQt5.QtWidgets import *
import cv2
from PIL import Image, ImageTk
import mediapipe as mp
import sys

width, height = 800, 600
vid = None
label_widget = None
userInput = sys.argv


def init_interface():
    global width, height, label_widget

    app = Tk()
    app.bind('<Escape>', lambda e: app.quit())
    app.grid_rowconfigure(0, weight=1)
    app.grid_rowconfigure(1, weight=1)
    app.grid_columnconfigure(0, weight=1)
    app.grid_columnconfigure(1, weight=1)

    label_widget = Label(app)
    label_widget.grid(row=0, column=0, sticky=NW)
    app.geometry(f"{width + 100}x{height + 100}")

    button1 = Button(app, text="Open Camera", command=get_frame)
    button1.grid(column=0, row=1)

    button2 = Button(app, text="test_button")
    button2.grid(column=1, row=1)

    return app


def init_camera():
    global width, height
    video = cv2.VideoCapture(0)
    video.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    video.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    return video


def get_frame():
    global vid, label_widget
    _, frame = vid.read()
    frame = cv2.resize(frame, (width, height), interpolation=cv2.INTER_NEAREST)

    opencv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)

    captured_image = Image.fromarray(opencv_image)
    photo_image = ImageTk.PhotoImage(image=captured_image)

    label_widget.photo_image = photo_image
    label_widget.configure(image=photo_image)

    label_widget.after(10, get_frame)


if __name__ == '__main__':
    vid = init_camera()
    app = init_interface()
    try:
        app.mainloop()
    except Exception as ex:
        print(ex)
