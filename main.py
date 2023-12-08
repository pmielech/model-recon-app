import tkinter.messagebox
import tkinter as tk
#from tkinter import as tk
import cv2
import numpy as np

rt = tk.Tk()
vid = cv2.VideoCapture(0)

canvas = tk.Canvas()
img = None
height, width, channels = None, None, None


def get_frame():
    global img, rt
    ret, frame = vid.read()
    img = frame
    tk.Canvas.image = (img)
    canvas.create_image(480,600, anchor=tk.NW, image=img)

    # canvas.create_image(0,0, anchor=tk.NW, image=img)

def tk_interface_init():
    global rt, canvas
    #window
    width = 600
    height = 400

    rt.geometry(f"{width}x{height}")
    rt.grid()
    #Ui elements
    button_height = 50

    canvas = tk.Canvas(rt, width=width, height=height - button_height)

    # btn = Button(root, text="Select an image", command=get_frame())
    # btn.pack(side="bottom", fill="both", expand="yes", padx="10", pady="10")
    rt.grid_rowconfigure(0, weight=1)
    rt.grid_rowconfigure(1, weight=1)
    rt.grid_columnconfigure(0, weight=1)
    rt.grid_columnconfigure(1, weight=1)

    canvas.grid(row=0, column=0, sticky="nsew")

    # .create_image(canvas, )
    tk.Canvas.image = img
    canvas.create_image(480,600, anchor=tk.NW, image=img)
    tk.Label(rt, text="Etykieta 1").grid(row=0, column=0, sticky="nsew")
    tk.Button(rt, text="Get frame", command=get_frame()).grid(row=1, column=0, sticky="nsew")
    tk.Entry(rt).grid(row=1, column=1, sticky="nsew")


if __name__ == '__main__':
    tk_interface_init()

    rt.mainloop()
    #while True:
        # kick off the GUI

        #
        #
        # # frame_2 = cv2.cvtColor(frame, cv2.COLOR)
        # gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # cv2.imshow('img', img)
        #
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break

# After the loop release the cap object
vid.release()
# Destroy all the windows
cv2.destroyAllWindows()
