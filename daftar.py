from __future__ import print_function #untuk mencetak tulisan
from PIL import Image # library Pillow untuk mengolah citra
from PIL import ImageTk
from imutils.video import VideoStream # untuk video stream
import Tkinter as tki # untuk tampilan GUI 
from Tkinter import Frame # untuk frame pada GUI
import tkMessageBox # message box
import threading # untuk multi-threading
import datetime # library untuk tanggal dan waktu
import time # library untuk penggunaan waktu
import imutils # library untuk video
import cv2 # library OpenCV
import os # library OS linux
import sys # library untuk perintah system pada linux
import sqlite3 # untuk database sqlite3

# fungsi untuk memasukkan data pendaftar ke database
def InsertOrUpdate(Id, nama):
	# menghubungkan ke database facebase
	conn=sqlite3.connect("facebase")
	cmd=""" CREATE TABLE IF NOT EXISTS pegawai (
                                        id integer(10) PRIMARY KEY NOT NULL,
                                        nama text(50) NOT NULL,
                                        jenis_kelamin varchar(8),
                                        jabatan varchar(50),
										no_telp varchar(15),
										foto_pegawai varchar(50)
                                    ); """
	# eksekusi perintah sql
	conn.execute(cmd)
	cmd="SELECT * FROM pegawai WHERE id="+str(Id)
	cursor=conn.execute(cmd)
	isRecordExist=0
	for row in cursor:
		isRecordExist=1
	if(isRecordExist==1):
		cmd='UPDATE pegawai SET nama="'+str(nama)+'",jenis_kelamin="'+str(jenis_kelamin)+'",jabatan="'+str(jabatan)+'",no_telp="'+str(no_telp)+'"WHERE id='+str(Id)
	else:
		cmd='Insert INTO pegawai(id,nama,jenis_kelamin,jabatan,no_telp,foto_pegawai) Values("'+str(Id)+'","'+str(nama)+'","'+str(jenis_kelamin)+'","'+str(jabatan)+'","'+str(no_telp)+'","'+str(foto_pegawai)+'")'
	conn.execute(cmd)
	# mengcommit perintah
	conn.commit()
	# memutuskan koneksi ke database
	conn.close()

# raw input untuk memasukkan data inputan ke variabel
global Id
Id=raw_input('Masukkan ID: ')
nama=raw_input('Masukkan nama anda: ')
jenis_kelamin=raw_input('Masukkan jenis kelamin anda: ')
jabatan=raw_input('Masukkan posisi/jabatan anda: ')
no_telp=raw_input('Masukkan No. Telp anda: ')
foto_pegawai="pegawai_"+str(Id)
# memanggil fungsi untuk memasukkan data ke database
InsertOrUpdate(Id, nama)

# menginisialisasi fungsi cascadeclassifier dari OpenCV
# ke variabel faceCascade
cascadePath = "faceclassifier.xml"
faceCascade = cv2.CascadeClassifier(cascadePath)

cond = False

class DaftarGUI:
	def __init__(self, vs):
		# menyimpan objek video stream dan output path,
		# lalu menginisialisasi frame yg terakhir dibaca, 
		# threading untuk membaca setiap frame, dan 
		# event untuk memberhentikan thread
		self.vs = vs
		self.frame = None
		self.thread = None
		self.stopEvent = None
		
		# inisialisasi root window dan panel untuk gambar
		self.root = tki.Tk()
		self.panel = None

		# membuat fungsi untuk tombol daftar dan train
		def daftar():
			global cond
			cond = True			
		def train():
			os.system("python trainer.py")
			tkMessageBox.showinfo("Info Training", "Training data berhasil.")

		# membuat tombol daftar dan train
		f=Frame(self.root)
		f.pack(side="right",fill="both",expand="yes")
		btn = tki.Button(f, text="Daftar",
			command=daftar)
		btn2 = tki.Button(f, text="Train",
			command=train)
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
		# membuat callback untuk menangani saat aplikasi ditutup
		self.root.wm_title("Daftar")
		self.root.wm_protocol("WM_DELETE_WINDOW", self.onClose)

	# funsi untuk videoLoop
	def videoLoop(self):
		# memanggil variabel global cond, dan Id
		global cond, Id
		# inisialisasi variabel untuk jumlah sampel
		sampleNum=0
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
					if cond==True:
						# menambahkan variabel sampel wajah 
						sampleNum=sampleNum+1
        				# menyimpan gambar ke folder dataset dengan penamaan berdasarkan Id
						cv2.imwrite("dataset/User."+Id +'.'+ str(sampleNum) + ".jpg", gray[y:y+h,x:x+w])
						# kondisi untuk pengambilan maksimal 20 sampel
						if sampleNum>20:							
							cond=False
							# menyimpan foto untuk data identitas pegawai
							cv2.imwrite("foto/pegawai_"+Id+".jpg", self.frame) 
							# info untuk memberitahukan bahwa pendaftaran berhasil
							tkMessageBox.showinfo("Info Daftar", "Daftar berhasil.")
				
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

	# fungsi yang dijalankan saat window aplikasi ditutup
	def onClose(self):
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
	pba = DaftarGUI(vs)
	pba.root.mainloop()

#menjalankan fungsi start
start()
