Supplementary Materials
Remote Photoplethysmography
Martin C.T. Manullang
Institut Teknologi Sumatera
Website: mctm.web.id/course/if25-40305
2025

OUTLINE
1.The Magic Trick
2.The History of rPPG
3.Where to Look?
4.From Video to Signals
5.From Signal to Numbers
6.Real World Implementation
The Magic Trick
Demonstrasi: Pulse Oximeter
Perhatikan Alat Ini
Alat klip jari ini adalah pulse oximeter yang dapat mengukur detak jantung dan
kadar oksigen darah.
Cara Kerja:
1.Cahaya masuk ke dalam jari
2.Cahaya dipantulkan kembali
3.Sensor mendeteksi perubahan cahayaPertanyaan Kunci:
•Bagaimana alat ini bekerja?
•Apa yang dideteksi oleh sensor?
•Mengapa harus ditempelkan ke jari?
1.The Magic Trick 1.0. 4/65
Tantangan Baru
Bisakah kita melakukan hal yang sama
dengan webcam seharga Rp 300.000
dari jarak 1 meter?
Perbedaan Utama
Pulse oximeter memerlukan kontak langsung , sedangkan webcam bekerja dari jarak jauh
tanpa sentuhan.
1.The Magic Trick 1.0. 5/65
Apa itu Remote Photoplethysmography (rPPG)?
Deﬁnisi
rPPG adalah teknologi untuk mendeteksi perubahan volume darah menggunakan
sensor optik (kamera) secara jarak jauh .
Istilah Penting:
1.Remote = Jarak jauh, tanpa kontak ﬁsik
2.Photo = Menggunakan cahaya
3.Plethysmography = Pengukuran perubahan volume
Aplikasi:
•Monitoring kesehatan tanpa sentuhan
•Deteksi stres atau kelelahan
•Sistem keamanan berbasis biometrik
1.The Magic Trick 1.0. 6/65
Fisika Dasar: Hemoglobin dan Cahaya
Konsep Kunci
Darah mengandung hemoglobin yang berfungsi sebagai ﬁlter cahaya.
Sifat Hemoglobin:
1.Darah beroksigen berwarna merah
2.Menyerap cahaya hijau dengan sangat
baik
3.Memantulkan cahaya merahMengapa Penting?
•Perubahan volume darah = perubahan
penyerapan cahaya
•Kamera dapat mendeteksi perubahan
ini
•Terutama pada spektrum cahaya hijau
1.The Magic Trick 1.0. 7/65
Siklus Jantung: Fase Pompa
Apa yang Terjadi Saat Jantung Memompa?
Jantung memompa →Pembuluh darah mengembang →Lebih banyak darah di kulit.
Efek pada Kulit:
1.Volume darah di kulit meningkat
2.Kulit menyerap lebih banyak cahaya
3.Kulit terlihat sedikit lebih gelap
Analogi:
Bayangkan balon yang diisi air. Semakin banyak air, balon semakin besar dan warnanya
semakin pekat.
1.The Magic Trick 1.0. 8/65
Siklus Jantung: Fase Relaksasi
Apa yang Terjadi Saat Jantung Berelaksasi?
Jantung berelaksasi →Pembuluh darah mengecil →Lebih sedikit darah di kulit.
Efek pada Kulit:
1.Volume darah di kulit menurun
2.Kulit memantulkan lebih banyak cahaya
3.Kulit terlihat sedikit lebih terang
Fase Pompa:
Gelap (banyak darah)Fase Relaksasi:
Terang (sedikit darah)
1.The Magic Trick 1.0. 9/65
Kesimpulan: Apa yang Dilihat Kamera?
Kamera tidak melihat jantung,
tetapi melihat "kedipan warna"
di wajah yang terjadi 60-100 kali per menit!
Istilah Teknis
Fenomena ini disebut micro-blushing atau perubahan warna mikro pada kulit.
1.The Magic Trick 1.0. 10/65
Tantangan Teknis
Masalah Utama
Perubahan warna ini tidak terlihat oleh mata telanjang manusia.
Mengapa Tidak Terlihat?
1.Perubahan sangat kecil dan cepat
2.Mata manusia tidak cukup sensitif
3.Terjadi di seluruh permukaan wajah secara bersamaan
Fakta:
Perubahan terjadi setiap detik, tetapi terlalu
halus untuk mata kita.Solusi:
Gunakan kamera dan algoritma komputer!
1.The Magic Trick 1.0. 11/65
Seberapa Kecil Perubahan Ini?
Skala Perubahan
Perubahan warna hanya sekitar 1/10 dari satu nilai piksel dalam gambar 8-bit.
Apa Artinya?
1.Gambar 8-bit memiliki nilai piksel 0-255
2.Perubahan rPPG hanya sekitar 0.1 nilai piksel
3.Sangat kecil untuk dideteksi langsung
Analogi:
Seperti mencoba mendengar bisikan seseorang di tengah konser musik yang sangat keras.
1.The Magic Trick 1.0. 12/65
Masalah: Sinyal vs Noise
Perbandingan
Sinyal yang kita cari lebih kecil daripada noise (gangguan) dari sensor kamera.
Sumber Noise:
1.Kualitas sensor kamera
2.Pencahayaan ruangan
3.Gerakan subjek
4.Bayangan dan reﬂeksiTantangan:
•Sinyal rPPG sangat lemah
•Noise jauh lebih kuat
•Perlu teknik khusus untuk ekstraksi
1.The Magic Trick 1.0. 13/65
Pernyataan Masalah dalam Ilmu Komputer
Bagaimana cara menemukan sinyal
yang lebih kecil dari noise
sensor kamera?
Ini adalah Masalah Pemrosesan Sinyal
Kita perlu menggunakan algoritma dan matematika untuk memisahkan sinyal detak jantung
dari noise.
1.The Magic Trick 1.0. 14/65
Rangkuman: Memahami Masalah
Apa yang Sudah Kita Pelajari:
1.rPPG mendeteksi perubahan volume darah menggunakan kamera
2.Hemoglobin dalam darah menyerap cahaya hijau
3.Siklus jantung menyebabkan perubahan warna mikro pada kulit
4.Perubahan ini tidak terlihat mata telanjang
5.Sinyal sangat kecil, lebih kecil dari noise kamera
Pertanyaan Selanjutnya
Bagaimana cara kita mengekstrak sinyal detak jantung dari video wajah?
1.The Magic Trick 1.0. 15/65
The History of rPPG
Perjalanan Teknologi rPPG
Dari Eksperimen Sederhana
hingga Kecerdasan Buatan
(2008 - 2022)
Mengapa Sejarah Penting?
Memahami evolusi teknologi membantu kita mengerti mengapa danbagaimana algoritma
bekerja.
2.The History of rPPG 2.0. 17/65
GREEN (2008): Penemuan Awal
Penemuan Verkruysse
Peneliti menemukan bahwa cahaya hijau dapat mendeteksi detak jantung
menggunakan kamera biasa.
Prinsip Kerja:
1.Gunakan hanya kanal warna hijau dari kamera
2.Hitung rata-rata nilai piksel di area wajah
3.Perubahan nilai rata-rata = sinyal detak jantung
Kelebihan:
•Sangat sederhana
•Mudah dipahami
•Bekerja dengan baik di kondisi idealKekurangan:
•Sensitif terhadap gerakan
•Perlu pencahayaan bagus
•Mudah terganggu bayangan
2.The History of rPPG 2.0. 18/65
PCA (2011): Pemisahan Komponen
Ide Utama
Gunakan analisis komponen utama untuk memisahkan sinyal detak jantung dari
gangguan.
Bagaimana PCA Bekerja?
1.Ambil sinyal dari tiga kanal warna (Merah, Hijau, Biru)
2.Cari pola yang paling dominan dalam sinyal
3.Pilih komponen dengan frekuensi seperti detak jantung
Analogi:
Seperti mendengarkan tiga suara sekaligus, lalu memilih suara yang paling keras dan teratur.
2.The History of rPPG 2.0. 19/65
ICA (2010): Teknik Lebih Canggih
Independent Component Analysis
ICA dapat memisahkan sinyal yang tercampur menjadi sumber-sumber yang
independen.
Prinsip ICA:
1.Anggap sinyal warna adalah campuran
2.Pisahkan menjadi komponen
independen
3.Pilih komponen yang berhubungan
dengan detak jantungPerbedaan dengan PCA:
•ICA lebih baik untuk sinyal non-linear
•Dapat menangani berbagai sumber
gangguan
•Lebih kompleks secara komputasi
2.The History of rPPG 2.0. 20/65
CHROM (2013): Tahan Gerakan
Terobosan Penting
CHROM menggunakan rasio krominansi untuk mengurangi efek gerakan kepala.
Apa itu Krominansi?
1.Krominansi adalah informasi warna tanpa kecerahan
2.Gerakan kepala mengubah kecerahan, tapi tidak warna
3.Dengan fokus pada warna, gangguan gerakan berkurang
Mengapa Ini Penting?
Orang jarang duduk diam sempurna. CHROM membuat rPPG lebih praktis untuk
penggunaan sehari-hari.
2.The History of rPPG 2.0. 21/65
PBV (2014): Pola Khas Detak Jantung
Blood Volume Pulse Signature
Setiap detak jantung memiliki pola khas yang dapat dikenali.
Konsep PBV:
1.Detak jantung memiliki bentuk
gelombang tertentu
2.Cari pola ini dalam sinyal video
3.Gunakan pola untuk memperkuat sinyalKeuntungan:
•Lebih tahan terhadap gerakan
•Akurasi lebih tinggi
•Bekerja baik di berbagai kondisi
2.The History of rPPG 2.0. 22/65
SSR & POS (2015-2016): Pendekatan Ruang
Spatial Subspace Rotation
SSR dan POS menggunakan rotasi ruang warna untuk ekstraksi sinyal yang lebih
baik.
Ide Dasar:
1.Putar ruang warna RGB ke arah yang optimal
2.Proyeksikan sinyal ke arah detak jantung
3.Eliminasi arah yang mengandung noise
Analogi:
Seperti memutar kepala untuk mendengar suara dengan lebih jelas dari arah tertentu.
2.The History of rPPG 2.0. 23/65
LGI (2018): rPPG di Dunia Nyata
Local Group Invariance
LGI dirancang untuk bekerja di kondisi tidak terkontrol seperti di luar ruangan.
Tantangan Dunia Nyata:
1.Pencahayaan berubah-ubah
2.Gerakan kepala tidak teratur
3.Bayangan dan reﬂeksiSolusi LGI:
•Gunakan informasi lokal dari wajah
•Kombinasikan dengan invarian grup
•Lebih robust terhadap variasi
2.The History of rPPG 2.0. 24/65
HR-CNN & MTTS-CAN: Era Pembelajaran Mesin
Dari Aturan Manual
kePembelajaran Otomatis
HR-CNN (2018):
•Jaringan saraf untuk estimasi detak jantung
•Belajar pola dari data video wajah
MTTS-CAN (2020):
•Multi-task learning: ukur detak jantung dan pernapasan
•Temporal shift attention untuk menangkap perubahan waktu
•Dapat berjalan di perangkat mobile
2.The History of rPPG 2.0. 25/65
OMIT (2022): Pembelajaran Tanpa Supervisi
Face2PPG Pipeline
OMIT dapat belajar ekstraksi sinyal tanpa data label menggunakan pembelajaran
tanpa supervisi.
Apa Artinya?
1.Tidak perlu data detak jantung sebenarnya untuk pelatihan
2.Model belajar sendiri pola dari video wajah
3.Lebih ﬂeksibel dan dapat beradaptasi
Kelebihan:
•Tidak butuh data berlabel
•Lebih mudah diterapkanArah Masa Depan:
•Kombinasi dengan teknik lain
•Aplikasi real-time
2.The History of rPPG 2.0. 26/65
Where to Look?
Video adalah Matriks 3 Dimensi
Konsep Dasar
Video bukan ﬁlm, tetapi susunan angka dalam ruang 3 dimensi.
Tiga Dimensi Video:
1.Tinggi (Height): Jumlah baris piksel
2.Lebar (Width): Jumlah kolom piksel
3.Waktu (Time): Urutan frame video
Contoh:
•Video HD: 1920 x 1080 piksel
•30 frame per detik
•1 detik = 1920 x 1080 x 30 angkaImplikasi:
•Setiap piksel punya nilai warna
•Nilai berubah setiap frame
•Perubahan ini yang kita analisis
3.Where to Look? 3.0. 28/65
Tidak Semua Piksel Berguna
Fakta Penting
Kitatidak memerlukan seluruh gambar, hanya piksel yang mengandung sinyal
detak jantung.
Piksel yang Berguna:
1.Kulit wajah (dahi, pipi)
2.Area dengan pembuluh darah
3.Permukaan yang rataPiksel yang Tidak Berguna:
1.Latar belakang
2.Rambut
3.Mata dan gigi
4.Bayangan
Pertanyaan Kunci:
Bagaimana kita memilih piksel yang tepat?
3.Where to Look? 3.0. 29/65
Memilih Wilayah yang Tepat
Region of Interest (ROI)
Area dalam video yang mengandung
informasi detak jantung
Mengapa ROI Penting?
1.Mengurangi jumlah data yang diproses
2.Meningkatkan kualitas sinyal
3.Mempercepat komputasi
4.Mengurangi gangguan dari area tidak relevan
3.Where to Look? 3.0. 30/65
Langkah 1: Menemukan Wajah
Deteksi Wajah Otomatis
Gunakan pustaka standar seperti OpenCV atau MediaPipe untuk mendeteksi wajah
secara otomatis.
Cara Kerja Deteksi Wajah:
1.Algoritma mencari pola khas wajah manusia
2.Menandai lokasi wajah dengan kotak pembatas
3.Memberikan koordinat posisi wajah
OpenCV:
•Metode klasik (Haar Cascade)
•Cepat dan ringanMediaPipe:
•Berbasis deep learning
•Lebih akurat dan detail
3.Where to Look? 3.0. 31/65
Langkah 2: Memisahkan Kulit dari yang Lain
Segmentasi Kulit
Proses memilih hanya piksel kulit dan mengabaikan latar belakang, rambut, dan
mata.
Mengapa Perlu Segmentasi?
1.Rambut tidak memiliki pembuluh darah
2.Mata bergerak dan reﬂektif
3.Latar belakang tidak relevan
4.Hanya kulit yang menunjukkan perubahan warna
Metode Segmentasi:
•Rentang warna kulit dalam ruang warna tertentu
•Pembelajaran mesin untuk klasiﬁkasi piksel
•Kombinasi dengan deteksi tepi
3.Where to Look? 3.0. 32/65
Tantangan: Orang Bergerak!
Masalah Utama
Apa yang terjadi jika pengguna menggerakkan kepala saat video direkam?
Dampak Gerakan:
1.Posisi wajah berubah tiap frame
2.ROI tidak konsisten
3.Sinyal terdistorsi
4.Sulit membedakan gerakan dan detak
jantungContoh Gerakan:
•Kepala mengangguk
•Wajah berputar
•Tubuh bergeser
•Ekspresi wajah berubah
3.Where to Look? 3.0. 33/65
Solusi: Pelacakan, Bukan Hanya Deteksi
Perbedaan Penting
Deteksi menemukan wajah setiap frame, pelacakan mengikuti wajah yang sama
sepanjang video.
Mengapa Pelacakan Lebih Baik?
1.ROI tetap mengikuti wajah yang bergerak
2.Konsistensi piksel antar frame terjaga
3.Mengurangi kesalahan dari deteksi ulang
4.Lebih stabil untuk ekstraksi sinyal
Teknik Pelacakan:
•Optical ﬂow untuk mengikuti gerakan
•Landmark wajah untuk stabilisasi
•Kalman ﬁlter untuk prediksi posisi
3.Where to Look? 3.0. 34/65
Masalah: Piksel Tunggal Sangat Noisy
Sensor kamera tidak sempurna
Setiap piksel memiliki noise acak
Sumber Noise pada Piksel:
1.Noise sensor kamera (thermal noise)
2.Ketidakstabilan listrik
3.Kompresi video
4.Gangguan pencahayaan
Fakta
Jika kita hanya melihat satu piksel, noise lebih besar daripada sinyal detak jantung.
3.Where to Look? 3.0. 35/65
Solusi: Rata-rata Spasial
Konsep Kunci
Jika kita merata-ratakan semua piksel kulit , noise acak akan saling
menghilangkan, tetapi sinyal tetap bertahan.
Mengapa Ini Berhasil?
1.Noise pada setiap piksel adalah acak dan independen
2.Sinyal detak jantung tersinkronisasi di seluruh wajah
3.Rata-rata membatalkan noise, memperkuat sinyal
Analogi:
Seperti menanyakan waktu ke 100 orang dengan jam yang tidak akurat. Rata-rata jawaban
lebih akurat daripada satu orang saja.
3.Where to Look? 3.0. 36/65
Hasil: Dari Video 3D ke Sinyal 1D
Transformasi Data
Video 3D (Tinggi x Lebar x Waktu) menjadi tiga array 1D sepanjang waktu.
Tiga Sinyal:
1.Jejak Merah (Red trace)
2.Jejak Hijau (Green trace)
3.Jejak Biru (Blue trace)Setiap Jejak:
•Satu nilai per frame
•Rata-rata dari semua piksel ROI
•Berubah mengikuti waktu
Langkah Selanjutnya:
Bagaimana mengekstrak sinyal detak jantung dari tiga jejak warna ini?
3.Where to Look? 3.0. 37/65
From Video to Signals
Dari Sinyal Mentah ke Informasi Berguna
Kita punya tiga jejak warna,
tapi bagaimana mendapatkan
detak jantung dari angka-angka ini?
Tantangan
Sinyal mentah penuh dengan gangguan yang harus dibersihkan terlebih dahulu.
4.From Video to Signals 4.0. 39/65
Melihat Sinyal RGB Mentah
Bayangkan Graﬁk Tiga Garis:
1.Garis Merah: Nilai rata-rata kanal merah sepanjang waktu
2.Garis Hijau: Nilai rata-rata kanal hijau sepanjang waktu
3.Garis Biru: Nilai rata-rata kanal biru sepanjang waktu
Pengamatan Penting
Ketiga garis ini bergerak naik-turun, tetapi tidak semua gerakan adalah detak jantung.
Yang Kita Cari:
Gelombang kecil yang berulang 60-100 kali per menit, bukan perubahan besar yang lambat.
4.From Video to Signals 4.0. 40/65
Mengapa Kanal Hijau Paling Penting?
Fakta Fisika
Hemoglobin dalam darah menyerap cahaya hijau jauh lebih kuat daripada merah
atau biru.
Kanal Hijau:
•Sinyal detak jantung paling kuat
•Perubahan terlihat jelas
•Lebih sensitif terhadap volume darahKanal Merah & Biru:
•Lebih banyak dipengaruhi
pencahayaan
•Sinyal detak jantung lemah
•Lebih banyak noise
Kesimpulan:
Kanal hijau adalah "penyiar" sinyal detak jantung yang paling jelas.
4.From Video to Signals 4.0. 41/65
Analogi: Menyetel Radio
Tiga kanal warna seperti
tiga stasiun radio berbeda
Kanal Hijau:
Stasiun dengan siaran
musik jelas dan kuatKanal Merah:
Stasiun dengan banyak
statis dan gangguanKanal Biru:
Stasiun dengan sinyal
sangat lemah
Pilihan Logis
Kita akan fokus mendengarkan stasiun dengan siaran paling jelas (kanal hijau).
4.From Video to Signals 4.0. 42/65
Masalah: Sinyal yang Melayang
Apa itu Drift?
Perubahan lambat dan besar dalam nilai sinyal yang bukan disebabkan oleh detak
jantung.
Penyebab Drift:
1.Awan menutupi matahari (cahaya berkurang)
2.Orang bergeser di kursi (jarak ke kamera berubah)
3.Lampu berkedip atau meredup
4.Bayangan bergerak melintasi wajah
Dampak:
Sinyal detak jantung yang kecil "tertimbun" oleh perubahan besar yang lambat ini.
4.From Video to Signals 4.0. 43/65
Bayangkan: Gelombang di Atas Bukit
Detak jantung = riak air kecil
Drift = bukit besar yang naik-turun
Masalah
Kita ingin melihat riak airnya , bukan bukitnya.
Tanpa Detrending:
•Riak kecil tidak terlihat
•Bukit terlalu dominan
•Sulit mengukur frekuensiDengan Detrending:
•Bukit dihilangkan
•Riak menjadi jelas
•Frekuensi mudah dihitung
4.From Video to Signals 4.0. 44/65
Solusi: Detrending
Prinsip Detrending
Hitung rata-rata bergerak dari sinyal, lalu kurangkan dari sinyal asli.
Langkah-langkah:
1.Ambil 30 frame terakhir dari sinyal
2.Hitung nilai rata-rata dari 30 frame ini
3.Kurangkan nilai rata-rata dari sinyal saat ini
4.Ulangi untuk frame berikutnya
Hasil:
Kita mendapatkan sinyal yang hanya berisi perubahan cepat (detak jantung), tanpa
perubahan lambat (drift).
4.From Video to Signals 4.0. 45/65
Kita Tahu Batas Detak Jantung Manusia
Fakta Biologi
Jantung manusia tidak mungkin berdetak 3 kali per menit atau 500 kali per menit .
Batas Minimum:
•Detak jantung terendah: sekitar 40
BPM
•Setara dengan 0.67 Hz
•Lebih rendah = bukan detak jantungBatas Maksimum:
•Detak jantung tertinggi: sekitar 240
BPM
•Setara dengan 4.0 Hz
•Lebih tinggi = artefak atau noise
4.From Video to Signals 4.0. 46/65
Bandpass Filter: Penjaga Logis
Prinsip Kerja
Buang semua sinyal yang frekuensinya di luar rentang 0.67 Hz - 4.0 Hz .
Apa yang Dibuang?
1.Frekuensi rendah ( <0.67 Hz): Drift, perubahan cahaya lambat
2.Frekuensi tinggi ( >4.0 Hz): Noise sensor, bayangan berkedip
Apa yang Tersisa?
Hanya sinyal dengan frekuensi yang masuk akal untuk detak jantung manusia.
Analogi
Seperti penjaga pintu yang hanya membiarkan tamu berusia 40-240 masuk, menolak bayi
(terlalu muda) dan dinosaurus (terlalu tua).
4.From Video to Signals 4.0. 47/65
Ringkasan: Tiga Langkah Pembersihan
Dari Video ke Detak Jantung:
1.Pilih Kanal Hijau: Sinyal paling kuat dari perubahan volume darah
2.Detrending: Hilangkan perubahan lambat (drift) dengan mengurangi rata-rata bergerak
3.Bandpass Filter: Buang frekuensi yang tidak mungkin dari jantung manusia (0.67-4.0
Hz)
Hasil Akhir
Sinyal bersih yang hanya berisi informasi detak jantung.
Langkah Selanjutnya:
Bagaimana menghitung frekuensi dari sinyal yang sudah bersih ini?
4.From Video to Signals 4.0. 48/65
From Signal to Numbers
Tujuan Akhir: Menghitung Detak Jantung
Kita punya sinyal yang sudah bersih,
sekarang bagaimana menghitung
BPM (Beats Per Minute)?
Pertanyaan Kunci
Apakah kita hitung jumlah puncak gelombang dalam sinyal?
Jawaban: Tidak! Menghitung puncak rawan kesalahan karena noise kecil bisa terlihat
seperti puncak.
5.From Signal to Numbers 5.0. 50/65
Dua Cara Melihat Sinyal
Konsep Penting
Sinyal yang sama dapat dilihat dari dua sudut pandang berbeda: domain waktu dan
domain frekuensi .
Domain Waktu:
1.Melihat bagaimana nilai berubah
seiring waktu
2.Graﬁk nilai terhadap detik
3.Seperti membaca not balok satu per
satuDomain Frekuensi:
1.Melihat komponen frekuensi apa saja
yang ada
2.Graﬁk kekuatan terhadap frekuensi
3.Seperti melihat equalizer di stereo
5.From Signal to Numbers 5.0. 51/65
Analogi: Musik dan Equalizer
Domain Waktu = Membaca not balok
Domain Frekuensi = Melihat equalizer
Perbedaan Utama
Not balok menunjukkan kapan nada dimainkan, sedangkan equalizer menunjukkan
frekuensi mana yang paling kuat.
Untuk Detak Jantung:
•Domain waktu: Sulit membedakan puncak asli dari noise
•Domain frekuensi: Mudah melihat frekuensi dominan
5.From Signal to Numbers 5.0. 52/65
Mencari Frekuensi Dominan
Strategi Pintar
Cari frekuensi yang memiliki kekuatan terbesar dalam rentang 40-240 BPM. Itulah
detak jantung!
Mengapa Ini Lebih Baik?
1.Tidak perlu menghitung puncak satu per satu
2.Lebih tahan terhadap noise kecil
3.Otomatis menemukan pola yang paling kuat
4.Lebih akurat dan stabil
Analogi:
Seperti mencari suara orang yang paling keras berbicara di ruangan ramai, bukan
menghitung berapa kali dia menggerakkan bibir.
5.From Signal to Numbers 5.0. 53/65
Transformasi Fourier: Pengurai Ajaib
Analogi Smoothie
Bayangkan smoothie campuran buah. Transformasi Fourier seperti mesin yang bisa
memisahkan kembali pisang, stroberi, dan mangga dari smoothie!
Input:
•Sinyal kompleks (smoothie)
•Campuran berbagai frekuensi
•Sulit dianalisis langsungOutput:
•Daftar frekuensi (bahan)
•Kekuatan masing-masing frekuensi
•Mudah menemukan yang dominan
5.From Signal to Numbers 5.0. 54/65
Mencari "Bahan Terbanyak" dalam Sinyal
Langkah Sederhana
Setelah mengurai sinyal, cari frekuensi dengan nilai tertinggi dalam rentang
40-240 BPM.
Proses:
1.Transformasi Fourier mengurai sinyal menjadi frekuensi-frekuensi
2.Setiap frekuensi punya "tinggi" (kekuatan)
3.Kita hanya lihat frekuensi antara 0.67-4.0 Hz (40-240 BPM)
4.Frekuensi tertinggi = detak jantung
Hasil:
Misalnya frekuensi tertinggi ada di 1.2 Hz →Detak jantung = 1.2 x 60 = 72 BPM
5.From Signal to Numbers 5.0. 55/65
Masalah: Butuh Waktu untuk Menghitung
Fakta Penting
Kitatidak bisa menghitung detak jantung dari satu frame saja. Perlu beberapa detik
video!
Mengapa Perlu Waktu?
1.Satu frame terlalu singkat
2.Butuh beberapa siklus detak
3.Biasanya 5-10 detikKonsep Jendela:
•Ambil 10 detik terakhir video
•Hitung BPM dari segmen ini
•Ini disebut "jendela waktu"
Analogi:
Seperti menghitung kecepatan mobil, perlu melihat jarak yang ditempuh dalam waktu
tertentu, bukan posisi sesaat.
5.From Signal to Numbers 5.0. 56/65
Jendela Geser: Update Setiap Detik
Sliding Window
Hitung detak jantung setiap detik menggunakan 10 detik terakhir dari video.
Cara Kerja:
1.Detik ke-10: Hitung BPM dari detik 0-10
2.Detik ke-11: Hitung BPM dari detik 1-11
3.Detik ke-12: Hitung BPM dari detik 2-12
4.Dan seterusnya...
Keuntungan:
•Update hasil setiap detik
•Responsif terhadap perubahanPertimbangan:
•Hasil lebih halus
•Delay minimal (10 detik)
5.From Signal to Numbers 5.0. 57/65
Real World Implementation
Mengapa rPPG Belum Ada di Setiap Aplikasi?
Teknologi sudah ada sejak 2008,
tapi mengapa tidak semua aplikasi kesehatan
menggunakan rPPG ?
Tantangan Utama
Ada beberapa hambatan teknis yang membuat rPPG sulit diterapkan di kehidupan
sehari-hari.
6.Real World Implementation 6.0. 59/65
Musuh Terbesar: Artefak Gerakan
Pertanyaan Kunci
Apa yang terjadi jika saya menganggukkan kepala saat video direkam?
Dampak Gerakan Kepala:
1.Bayangan bergerak di wajah
2.Pencahayaan berubah drastis
3.Posisi wajah terhadap kamera berubah
4.Reﬂeksi cahaya berubah
Masalah Serius:
Perubahan cahaya akibat bayangan 100 kali
lebih kuat daripada perubahan akibat detak
jantung!Analogi:
Seperti mencoba mendengar bisikan di
tengah badai petir.
6.Real World Implementation 6.0. 60/65
Skala Perbandingan: Sinyal vs Artefak Gerakan
Sinyal Detak Jantung: 0.1 piksel
Artefak Gerakan: 10 piksel
(Perbandingan 1:100)
Mengapa Gerakan Begitu Kuat?
1.Bayangan mengubah kecerahan secara drastis
2.Gerakan kepala mengubah pantulan cahaya
3.Perubahan sudut pandang kamera
4.Efek ini jauh lebih besar dari perubahan darah
6.Real World Implementation 6.0. 61/65
Solusi: Blind Source Separation
Konsep Kunci
Gunakan ketiga kanal warna RGB untuk secara matematis memisahkan sinyal
gerakan dari sinyal darah.
Bagaimana Ini Bekerja?
1.Gerakan kepala memengaruhi ketiga kanal RGB secara bersamaan
2.Perubahan darah memengaruhi kanal hijau lebih kuat
3.Dengan membandingkan ketiga kanal, kita bisa memisahkan kedua efek ini
Metode BSS:
•ICA (Independent Component Analysis)
•CHROM (Chrominance-based method)
•POS (Plane-Orthogonal-to-Skin)Analogi:
Seperti memisahkan suara dua orang yang
bicara bersamaan dengan mendengar dari
dua mikrofon berbeda.
6.Real World Implementation 6.0. 62/65
Tantangan: Keragaman Warna Kulit
Masalah Inklusivitas
Teknologi rPPG bekerja lebih baik pada kulit terang daripada kulit gelap. Mengapa?
Peran Melanin:
1.Melanin adalah pigmen yang membuat kulit gelap
2.Melanin menyerap lebih banyak cahaya secara umum
3.Ini menurunkan rasio sinyal terhadap noise
4.Perubahan akibat darah lebih sulit dideteksi
Kulit Terang:
•Sinyal lebih kuat
•Noise relatif lebih kecil
•Lebih mudah dideteksiKulit Gelap:
•Sinyal lebih lemah
•Noise relatif lebih besar
•Butuh teknologi lebih baik
6.Real World Implementation 6.0. 63/65
Menuju Teknologi yang Lebih Inklusif
Dua Pendekatan Utama:
1.Kamera Lebih Baik: Sensor dengan sensitivitas tinggi dan noise rendah
2.Algoritma Lebih Cerdas: Pembelajaran mendalam (Deep Learning) yang dilatih
dengan beragam warna kulit
Pentingnya Keberagaman Data
Model pembelajaran mesin harus dilatih dengan data dari berbagai warna kulit untuk
menghindari bias.
Penelitian Terkini:
•Dataset beragam
•Algoritma adaptif
•Preprocessing khususHarapan Masa Depan:
•Akurasi setara untuk semua
•Teknologi yang adil
•Aplikasi universal
6.Real World Implementation 6.0. 64/65
Ringkasan: Perjalanan dari Video ke BPM
Pipeline Lengkap rPPG:
1.Video →Rekam wajah dengan kamera
2.Face Detection →Temukan dan lacak wajah
3.Spatial Average →Rata-rata piksel kulit untuk mengurangi noise
4.Detrending & Filter →Bersihkan sinyal dari drift dan frekuensi tidak relevan
5.FFT→Ubah ke domain frekuensi
6.Peak Detection →Temukan frekuensi dominan
7.BPM→Konversi frekuensi menjadi detak per menit
Pertanyaan?
Silakan ajukan pertanyaan tentang materi yang sudah kita bahas!
6.Real World Implementation 6.0. 65/65