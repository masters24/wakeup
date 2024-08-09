from tkinter import *
import tkinter.messagebox as tkMessageBox
import sqlite3
from scipy.spatial import distance
from imutils import face_utils
import imutils
import dlib
import cv2
from pygame import mixer
from datetime import datetime, timedelta
global eror
eror=""


def eye_aspect_ratio(eye):
	A = distance.euclidean(eye[1], eye[5])
	B = distance.euclidean(eye[2], eye[4])
	C = distance.euclidean(eye[0], eye[3])
	ear = (A + B) / (2.0 * C)
	return ear

def detect_drowsi(thresh):
	frame_check = 10
	detect = dlib.get_frontal_face_detector()
	predict = dlib.shape_predictor('shape_predictor.dat') 

	(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_68_IDXS["left_eye"]
	(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_68_IDXS["right_eye"]
	cap=cv2.VideoCapture(0)
	flag=0
	while True:
		ret, frame=cap.read()
		frame = imutils.resize(frame, width=600)
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		subjects = detect(gray, 0)
		for subject in subjects:
			shape = predict(gray, subject)
			shape = face_utils.shape_to_np(shape)
			leftEye = shape[lStart:lEnd]
			rightEye = shape[rStart:rEnd]
			leftEAR = eye_aspect_ratio(leftEye)
			rightEAR = eye_aspect_ratio(rightEye)
			ear = (leftEAR + rightEAR) / 2.0
			leftEyeHull = cv2.convexHull(leftEye)
			rightEyeHull = cv2.convexHull(rightEye)
			cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
			cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)
			if ear < thresh:
			
				if flag >= frame_check:
					cv2.putText(frame, "********************ALERT!********************", (30, 30),
						cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
					cv2.putText(frame, "********************ALERT!********************", (30,425),
						cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
					print ("Drowsy")
					mixer.init()
					mixer.music.load('alert.mp3')
					mixer.music.play()
				flag += 1
			else:
				flag = 0
		cv2.imshow("Wake-up watcher", frame)
		key = cv2.waitKey(1) & 0xFF
		if key == ord("q"):
			break
        
	cv2.destroyAllWindows()


root = Tk()
root.title("Wake-up watcher")
width = 500
height = 300
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width/2) - (width/2)
y = (screen_height/2) - (height/2)
root.geometry("%dx%d+%d+%d" % (width, height, x, y))
root.resizable(0, 0)

#==============================METHODS========================================
def Exit():
        root.destroy()
        exit()
def Database():
    global conn, cursor
    conn = sqlite3.connect("pythontut.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS `member` (mem_id INTEGER NOT NULL PRIMARY KEY  AUTOINCREMENT, username TEXT, password TEXT)")       
    cursor.execute("SELECT * FROM `member` WHERE `username` = 'admin' AND `password` = 'admin'")
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO `member` (username, password) VALUES('admin', 'admin')")
        conn.commit()
    
def Login(event=None):
    Database()
    if USERNAME.get() == "" or PASSWORD.get() == "":
        lbl_text.config(text="Please complete the required field!", fg="red")
    else:
        cursor.execute("SELECT * FROM `member` WHERE `username` = ? AND `password` = ?", (USERNAME.get(), PASSWORD.get()))
        if cursor.fetchone() is not None:
            HomeWindow()
            USERNAME.set("")
            PASSWORD.set("")
            lbl_text.config(text="")
        else:
            lbl_text.config(text="Invalid username or password", fg="red")
            USERNAME.set("")
            PASSWORD.set("")   
    cursor.close()
    conn.close()

def Register(event=None):
    Database()
    if USERNAME.get() == "" or PASSWORD.get() == "":
        lbl_text.config(text="Please complete the required field!", fg="red")
    else:
        cursor.execute("SELECT * FROM `member` WHERE `username` = ?", (USERNAME.get(),))
        if cursor.fetchone() is not None:
            lbl_text.config(text="Username already taken", fg="red")
        else:
            cursor.execute("INSERT INTO `member` (username, password) VALUES(?, ?)", (USERNAME.get(), PASSWORD.get()))
            conn.commit()
            lbl_text.config(text="Registration successful", fg="green")
            USERNAME.set("")
            PASSWORD.set("")
    cursor.close()
    conn.close()
def update_time():
    current_time = datetime.now().strftime("%I:%M:%S %p")
    current_date = (datetime.now() - timedelta(days=5)).strftime("%d-%m-%Y")
    weekday = datetime.now().strftime("%A")
    time_label.config(text=f"{current_date} ({weekday})\n{current_time}\n")
    Home.after(1000, update_time) 
def HomeWindow():
    global Home
    root.withdraw()
    Home = Toplevel()
    Home.title("Wake-up watcher")
    width = 600
    height = 500
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width/2) - (width/2)
    y = (screen_height/2) - (height/2)
    root.resizable(0, 0)
    Home.geometry("%dx%d+%d+%d" % (width, height, x, y))
    lbl_home = Label(Home, text="!! Welcome The System has Started !!", font=('Gabriola', 25)).pack()
    btn_back = Button(Home, text='Back', command=Back).pack(pady=20, fill=X)
    global time_label
    time_label =Label(Home, text="", fg="green", anchor="center",font=("Times new roman", 20))
    time_label.pack()
    update_time()  
    Button(Home,text="Start Scan",width=15, font=("Times new roman", 20),  fg="Black", bd=5, command=startscan).pack()
    Label(Home, text="").pack()
    Button(Home,text='EXIT',width=15,fg='Black',font=("Times new roman",20), bd=5, command=function1).pack()

def startscan():
    thresh=0.3
    detect_drowsi(thresh)
        
def function1():
    Exit()

def Back():
    Home.destroy()
    root.deiconify()
    
#==============================VARIABLES======================================
USERNAME = StringVar()
PASSWORD = StringVar()

#==============================FRAMES=========================================
Top = Frame(root, bd=2,  relief=RIDGE)
Top.pack(side=TOP, fill=X)
Form = Frame(root)
Form.pack(side=TOP, pady=20)

#==============================LABELS=========================================
lbl_title = Label(Top, text = "Login to Start the System", font=('Gabriola', 19))
lbl_title.pack(fill=X)
lbl_username = Label(Form, text = "Username:", font=('Times new roman', 20), bd=15)
lbl_username.grid(row=0, sticky="e")
lbl_password = Label(Form, text = "Password:", font=('Times new roman', 20), bd=15)
lbl_password.grid(row=1, sticky="e")
lbl_text = Label(Form)
lbl_text.grid(row=2, columnspan=2)

#==============================ENTRY WIDGETS==================================
username = Entry(Form, textvariable=USERNAME, font=(14))
username.grid(row=0, column=1)
password = Entry(Form, textvariable=PASSWORD, show="*", font=(14))
password.grid(row=1, column=1)

#==============================BUTTON WIDGETS=================================
btn_login = Button(Form, text="Login", width=12,font=('Times new roman', 14), bd=8,command=Login)
btn_login.grid(pady=15,padx=5, row=3, column=0)
btn_login.bind('<Return>', Login)

btn_register = Button(Form, text="Register", width=12,font=('Times new roman', 14), bd=8,command=Register)
btn_register.grid(pady=15, row=3, column=1)
btn_register.bind('<Return>', Register)

root.mainloop()
