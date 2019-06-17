from tkinter import *

from tkinter import messagebox
turn=0

def chooseturn():
    top = Tk()
    top.title("Choose")
    top.geometry("200x200")

    def yes():
        global turn
        turn = "black"
        return

        #print ("black")

    def no():
        global turn
        turn = "white"
        return
        #print ("white")

    B1 = Button(top, text = "First", command = yes)
    B2 = Button(top, text = "Second", command = no)
    B1.place(x = 35,y = 100)
    B2.place(x = 95,y = 100)
    mainloop()
    return turn
