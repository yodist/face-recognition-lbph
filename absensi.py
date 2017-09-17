from __future__ import print_function #untuk mencetak tulisan
from PIL import Image # library Pillow untuk mengolah citra
from PIL import ImageTk
from imutils.video import VideoStream # untuk video stream
from imutils.video import FPS
import Tkinter as tki # untuk tampilan GUI 
from Tkinter import Frame # untuk frame pada GUI
import tkMessageBox # message box
import threading # untuk multi-threading
import datetime # library untuk tanggal dan waktu
import time # libary untuk penggunaan waktu
import imutils # library untuk video
import cv2 # library OpenCV
import os # library OS linux
import sys # library untuk perintah system pada linux
import sqlite3 # untuk database sqlite3
import numpy as np # numerical processing dengan python

# membuat recognizer LBPH dengan fungsi yang sudah disediakan
# oleh OpenCV dan memasukkan ke variabel recognizer
recognizer = cv2.face.createLBPHFaceRecognizer()
# memuat recognizer yang sudah di training oleh
# program trainer
recognizer.load('recognizer/trainner.yml')

# menginisialisasi fungsi cascadeclassifier dari OpenCV
# ke variabel faceCascade
cascadePath = "faceclassifier.xml"
faceCascade = cv2.CascadeClassifier(cascadePath)
# inisialisasi variabel counter untuk meyakinkan 
# wajah yang dideteksi
counter = 0
# variabe untuk menyimpan data checkin dan checkout
status = statusOut = False
# variabel untuk menyimpan foto checkin dan checkout
fotoIn = fotoOut = False
# inisialisasi variabel confidence dan filename
conf = 120
filename = " "

# fungsi untuk memasukkan data check-in ke database tabel dataabsensi
def insertCheckIn(Id, nama):
	global filename
	# menyimpan data tanggal pada datenow
	datenow = datetime.datetime.now()
	# menyimpan data waktu (jam: menit: detik) pada variabel timenow
	timenow = datenow.strftime("%H:%M:%S")
	# menyambungkan ke database facebase
	conn=sqlite3.connect("facebase")
	cmd=""" CREATE TABLE IF NOT EXISTS dataabsensi (
                                        LogId INTEGER PRIMARY KEY AUTOINCREMENT,
										id integer(10) NOT NULL,
                                        nama text(50) NOT NULL,
										tanggal varchar(20) NOT NULL,
                                        waktu_masuk date NOT NULL,
										foto_masuk varchar(100),
										waktu_keluar date,
										foto_keluar varchar(100)
                                    ); """
	conn.execute(cmd)
	cmd='SELECT * FROM dataabsensi WHERE id='+str(Id)+' AND tanggal="'+str(datenow.date())+'" AND waktu_keluar IS NULL' 
	cursor = conn.execute(cmd)
	isRecordExist=0
	for row in cursor:
		isRecordExist=1
	if (isRecordExist==1):
		# info pada terminal bahwa check-in gagal
		print("[INFO] gagal check-in, harap check-out terlebih dahulu")
	else:
		conn.execute("INSERT INTO dataabsensi(id, nama, tanggal, waktu_masuk, foto_masuk) values(?, ?, ?, ?, ?)", (Id, nama, datenow.date(), timenow, filename))
		conn.commit()
		global fotoIn
		fotoIn = True
		print("[INFO] Check-in berhasil")
	# memutuskan koneksi dengan database
	conn.close()

# fungsi untuk memasukkan data check-out
def insertCheckOut(Id, nama):
	global filename
	datenow = datetime.datetime.now()
	timenow = datenow.strftime("%H:%M:%S")
	conn=sqlite3.connect("facebase")
	cmd=""" CREATE TABLE IF NOT EXISTS dataabsensi (
                                        LogId INTEGER PRIMARY KEY AUTOINCREMENT,
										id integer(10) NOT NULL,
                                        nama text(50) NOT NULL,
										tanggal varchar(20) NOT NULL,
                                        waktu_masuk date NOT NULL,
										foto_masuk varchar(100),
										waktu_keluar date,
										foto_keluar varchar(100)
                                    ); """
	conn.execute(cmd)
	cmd='SELECT * FROM dataabsensi WHERE id='+str(Id)+' AND tanggal="'+str(datenow.date())+'" AND waktu_keluar IS NULL' 
	cursor = conn.execute(cmd)
	isRecordExist=0
	for row in cursor:
		isRecordExist=1
	if (isRecordExist==1):
		conn.execute('UPDATE dataabsensi SET waktu_keluar="'+str(timenow)+'", foto_keluar="'+ filename +'" WHERE id='+str(Id)+' AND tanggal="'+str(datenow.date())+'" AND waktu_keluar IS NULL' )
		conn.commit()
		global fotoOut
		fotoOut = True
		print("[INFO] Check-out berhasil")
	else:
		print("[INFO] gagal check-out, harap check-in terlebih dahulu")
	conn.close()

# mengambil data profile berdasarkan Id dari 
# database tabel pegawai
def getProfile(Id):
	conn=sqlite3.connect("facebase")
	cmd="SELECT * FROM pegawai WHERE id="+str(Id)
	cursor=conn.execute(cmd)
	profile=None
	for row in cursor:
		profile=row
	conn.close()
	return profile

# membuat class detector
class Detector:
	def __init__(self, vs, outputPath):
		
		# menyimpan objek video stream dan output path,
		# lalu menginisialisasi frame yg terakhir dibaca, 
		# threading untuk membaca setiap frame, dan 
		# event untuk memberhentikan thread
		self.vs = vs
		self.fps = FPS().start()
		self.outputPath = outputPath
		self.frame = None
		self.thread = None
		self.stopEvent = None
 
		# inisialisasi root window dan panel untuk gambar
		self.root = tki.Tk()
		self.root.attributes("-fullscreen",True)
		self.panel = None

		# membuat tombol check-in dan check-out
		f=Frame(self.root)
		f.pack(side="right",fill="both",expand="yes")
		btn = tki.Button(f, text="Check in",
			command=self.checkIn)
		btn2 = tki.Button(f, text="Check out",
			command=self.checkOut)
		btn.pack(side="top", fill="both", expand="yes", padx=10,
			pady=10)
		btn2.pack(side="bottom", fill="both", expand="yes", padx=10,
			pady=10)
		
		# memulai thread untuk secara konstan membaca setiap frame
		# video yang diambil kamera
		self.stopEvent = threading.Event()
		self.thread = threading.Thread(target=self.videoLoop, args=())
		self.thread.start()
 
		# memberi judul aplikasi
		self.root.wm_title("Aplikasi Absensi Pegawai")
		# membuat callback untuk menangani saat aplikasi ditutup
		self.root.wm_protocol("WM_DELETE_WINDOW", self.onClose)
	

	def videoLoop(self):
		# mengimport variabel-variabel global ke
		# dalam fungsi videoLoop
		global status, statusOut
		global fotoIn, fotoOut
		global conf
		global counter
		global filename
		try:
			
			while not self.stopEvent.is_set():
				x=y=h=w=2
				# deklarasi frame untuk tangkapan kamera
				self.frame = self.vs.read()
				#resize frame ke ukuran 300px width
				self.frame = imutils.resize(self.frame, width=300)		
				# mengubah gambar dari warna BGR ke GRAY 
				gray = cv2.cvtColor(self.frame,cv2.COLOR_BGR2GRAY)
				# mendeteksi wajah dengan menggunakan faceCascade
				faces = faceCascade.detectMultiScale(gray, 1.3, 5)
				# looping menggunakan variabel dari hasil pendeteksian wajah
				for(x,y,w,h) in faces:
					# mengkotakkan bagian wajah pada gambar berdasarkan 
					# titik koordinat yang disimpan oleh classifier
					# berupa x, y, w, dan h dimana x untuk koordinat x,
					# y untuk titik koordinat y, w dan h untuk lebar dan 
					# panjang dari bagian yang terdeteksi wajah 
					cv2.rectangle(self.frame,(x,y),(x+w,y+h),(225,0,0),2)

				# menyimpan fungsi predict collector untuk jarak minimum
				# dari wajah yang sudah disediakan oleh library OpenCV
				# ke variabel result
				result=cv2.face.MinDistancePredictCollector()
				# memprediksi wajah pegawai dari gambar yang ditangkap
				# menggunakan recognizer LBPH
				recognizer.predict(gray[y:y+h,x:x+w],result)
				# predict collector akan mengembalikan Id dan nilai
				# confidence dari hasil perhitungan pada variabel result
				Id,conf=result.getLabel(),result.getDist()
				# mencetak nilai confidence pada terminal
				print(conf)

				# memngambil data pegawai pegawai dari tabel pegawai
				# pada database dan disimpan ke variabel profile
				profile=getProfile(Id)

				if (profile!=None):
					# jika nilai confidence yang dihasilkan lebih kecil daripada nilai threshold confidence
					# maka perintah yang ada di dalam if ini akan dijalankan
					if(conf<=50):
						counter += 1
						# menaruh text ID dan nama dari pegawai yang dikenali identitasnya
						# di bagia bawah kotak deteksi
						cv2.putText(self.frame,str(profile[0]), (x,y+h+30),cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
						cv2.putText(self.frame,str(profile[1]), (x,y+h+60),cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
						if(status == True):
							# jika setelah pengecekkan 5 kali berturut-turut hasil dari pengenalan
							# wajah ini menghasilkan data prediksi yang sama maka kode pada
							# if ini akan dijalankan
							if(counter >= 5):
								ts = datetime.datetime.now()
								filename = "check-in_{}.jpg".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))
								insertCheckIn(profile[0], profile[1])
								if(fotoIn==True):
									
									p = os.path.sep.join((self.outputPath, filename))
									# menyimpan foto hasil pengenalan wajah untuk check-in ke folder foto
									cv2.imwrite(p, self.frame.copy())
									print("[INFO] berhasil melakukan check-in, {}".format(filename))
									# info message box bahwa check-in telah berhasil
									tkMessageBox.showinfo("Info Absensi", "Berhasil melakukan check-in")
									fotoIn = False
								else:
									# info message box bahwa check-in gagal dan harus check-out terlebih dahulu
									tkMessageBox.showinfo("Info Absensi", "Gagal check-in, harap check-out terlebih dahulu")

								status = False
							else:
								# mereset nilai counter
								counter = 0
						if(statusOut == True):
							if(counter >= 5):
								ts = datetime.datetime.now()
								filename = "check-out_{}.jpg".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))
								insertCheckOut(profile[0], profile[1])
								if(fotoOut==True):
									p = os.path.sep.join((self.outputPath, filename))
									# save the file
									cv2.imwrite(p, self.frame.copy())
									print("[INFO] berhasil melakukan check-out, {}".format(filename))
									# menyimpan foto hasil pengenalan wajah untuk check-in ke folder foto
									tkMessageBox.showinfo("Info Absensi", "Berhasil melakukan check-out")
									fotoOut = False
								else:
									# info message box bahwa check-out gagal dan harus check-in terlebih dahulu
									tkMessageBox.showinfo("Info Absensi", "Gagal check-out, harap check-in terlebih dahulu")
								statusOut = False
							else:
								counter = 0

					else:
						# menaruh text di bagian bawah kotak deteksi bahwa wajah yang terdeteksi tidak diketahui identitasnya
						cv2.putText(self.frame,str("Tidak Dikenal"), (x,y+h+30),cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
						counter = 0
				
				self.fps.update()
				# merubah format gambar ke bentuk warna RGB ke
				# variabel image yang digunakan untuk menampilkan 
				# gambar ke panel GUI
				image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
				image = Image.fromarray(image)
				image = ImageTk.PhotoImage(image)				
				if self.panel is None:
					self.panel = tki.Label(image=image)
					self.panel.image = image
					self.panel.pack(side="left", padx=10, pady=10)				
				else:
					self.panel.configure(image=image)
					self.panel.image = image
 		
		# menambahkan pengecualian untuk bug dari library
		# TkInter saat digabungkan 
		except RuntimeError, e:
			print("[INFO] caught a RuntimeError")

	# check-in digunakan mengkonfirmasi agar program loop
	# dapat memasukkan data check-in ke database
	def checkIn(self):
		global conf
		if(conf<=50):			
			global status
			status = True
		else:
			print("[INFO] gagal check-in, wajah tidak dikenali")
			tkMessageBox.showinfo("Info Absensi", "Gagal check-in, wajah tidak dikenali")
	
	# check-in digunakan mengkonfirmasi agar program loop
	# dapat memasukkan data check-in ke database
	def checkOut(self):
		global conf
		if(conf<=50):
			global statusOut
			statusOut = True
		else:
			print("[INFO] gagal check-out, wajah tidak dikenali")
			tkMessageBox.showinfo("Info Absensi", "Gagal check-out, wajah tidak dikenali")

	def onClose(self):
		# set the stop event, cleanup the camera, and allow the rest of
		# the quit process to continue
		self.fps.stop()
		print("[INFO] approx. FPS: {:.2f}".format(self.fps.fps()))
		print("[INFO] closing...")
		
		self.stopEvent.set()
		self.vs.stop()
		self.root.quit()

def start(): 
	# inisialisasi video stream dan warm up camera
	print("[INFO] warming up camera...")
	vs = VideoStream(-1).start()
	time.sleep(2.0)
	 
	# menjalankan program looping utama
	pba = Detector(vs, "foto")
	pba.root.mainloop()

# memanggil fungsi start
start()
