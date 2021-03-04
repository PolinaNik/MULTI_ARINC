"""Скрипт с вводом исходных данных для СИНТЕЗА"""

from tkinter import *
from tkinter.ttk import *

root=Tk()
root.title("PARSING ARINC")
Label1 = Label(root, text="Введите фамилию на латинице")
Label1.grid(row=0, column = 0)

Name = Entry(root)
Name.grid(row=0, column=1)

def func(event):
    a = Name.get()
    root.destroy()

    global params
    params = [a]

root.bind('<Return>', func)

def getInput():
    a = Name.get()
    root.destroy()

    global params
    params = [a]

btn = Button(root, text="Начать", command=getInput)
btn.grid(row=0, column=2)

root.mainloop()