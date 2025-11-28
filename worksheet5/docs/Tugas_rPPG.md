Kerangka Acuan Kerja (T erm of Reference)
T ugas Implementasi: Real-time Remote Photoplethysmography
(rPPG)
Sistem T eknologi Multimedia
Institut T eknologi Sumatera
1 Deskripsi T ugas
T ugas ini bertujuan untuk memberikan pengalaman praktis kepada mahasiswa dalam meng-
implementasikan teknologi Remote Photoplethysmography (rPPG) yang telah dibahas di kelas.
Mahasiswa diminta untuk membangun sebuah sistem perangkat lunak yang mampu mendeteksi
detak jantung seseorang secara real-time menggunakan kamera (webcam) tanpa kontak fisik.
2 Lingkup Pekerjaan
Mahasiswa diharapkan untuk melakukan hal-hal berikut:
1. Rekreasi Pipeline rPPG: Mengimplementasikan kembali proses pemrosesan sinyal rP-
PG seperti yang didemonstrasikan di kelas, yang mencakup tahapan:
• Deteksi W ajah: Menggunakan pustaka seperti OpenCV atau MediaPipe untuk
mendeteksi dan melacak wajah (ROI).
• Ekstraksi Sinyal: Melakukan spatial averaging pada area kulit (khususnya kanal
Hijau/Green) untuk mendapatkan sinyal mentah.
• Pemrosesan Sinyal: Menerapkan teknik detrending (misalnya sliding average ) dan
Bandpass Filter (rentang 0.67 Hz - 4.0 Hz) untuk membersihkan noise.
• Estimasi BPM: Menggunakan T ransformasi F ourier (FFT) untuk mencari frekuensi
dominan dan mengonversinya menjadi Beats Per Minute (BPM) atau dapat juga
menggunakan fungsi findpeaks dari scipy .
2. Implementasi Real-time: Sistem harus dapat berjalan secara real-time menggunakan
input dari webcam, bukan hanya memproses video yang sudah direkam sebelumnya. Gu-
nakan konsep sliding window untuk pembaruan estimasi detak jantung secara kontinyu.
3. Peningkatan Kualitas (Improvement): Lakukan pemrosesan lebih lanjut untuk me-
ningkatkan akurasi dan ketahanan sistem. Contoh peningkatan yang dapat dilakukan
(pilih minimal satu atau gabungan):
• Implementasi metode ekstraksi sinyal yang lebih mutakhir dari POS untuk ketahanan
terhadap gerakan.
• Penanganan artefak gerakan atau perubahan pencahayaan yang lebih robust.
• Penggunaan skin segmentation atau RoI tertentu dari wajah
• Penggunaan filter adaptif atau teknik pemrosesan sinyal lanjutan lainnya.
• Visualisasi data yang informatif (grafik sinyal waktu nyata, plot spektrum frekuensi).
1
3 Kebijakan Pengerjaan
• Penggunaan T ugas Sebelumnya: Jika pada semester sebelumnya Anda telah meng-
ambil mata kuliah Pengolahan Sinyal dan pernah mengerjakan tugas dengan topik yang
sama, Anda diperbolehkan untuk menggunakan kembali kode tersebut. Namun, Anda
sangat disarankan untuk melakukan perbaikan, optimasi, atau penyesuaian agar sesuai
dengan konteks real-time pada mata kuliah ini.
• Bahasa Pemrograman: T ugas dikerjakan menggunakan bahasa Python.
4 F ormat Pengumpulan
• Hasil pengerjaan berupa kode sumber dalam format Jupyter Notebook ( .ipynb ) atau skrip
Python ( .py ).
• Buat penjelasan dan laporan singkat dalam format markdown, yang mencakup aspek
pembeda dengan demo yang dilakukan di kelas
• Kode harus diunggah ke repositori publik (misalnya GitHub).
• Jika Anda menggabungkan seluruh tugas hands-on dalam satu repositori, pastikan tautan
yang dikumpulkan mengarah spesifik ke folder tugas ini.
• T autan pengumpulan (submission link) dan tenggat waktu (deadline) dapat
dilihat pada halaman website perkuliahan.
5 Rubrik Penilaian
Penilaian akan didasarkan pada kriteria berikut:
No Kriteria Deskripsi Bobot
1 Implementasi Pipeline Dasar Keberhasilan mengimplementasikan tahap-
an dasar rPPG (Deteksi W ajah, ROI, Fil-
ter, FFT) sesuai materi kuliah.30%
2 Kapabilitas Real-time Sistem mampu berjalan lancar secara real-
time dengan input webcam (tidak lag ber-
lebihan, update BPM konsisten).25%
3 Peningkatan Kualitas ( Improve-
ment )Penerapan metode tambahan atau tek-
nik lanjutan untuk meningkatkan akura-
si atau stabilitas sinyal (misal: metode
POS/CHROM, filter adaptif, UI yang ba-
ik).25%
4 Kualitas Kode Kode tertulis dengan rapi, terstruktur, mu-
dah dibaca, dan disertai komentar atau do-
kumentasi yang jelas.20%
2