# Ringkasan Materi dan Tugas rPPG

## Pertemuan_12.pdf — Video Processing Fundamentals
- Transisi dari pengolahan gambar ke video: video menambah dimensi waktu (frame) di samping dimensi ruang dan kanal warna.
- Frame rate (FPS) sebagai sampling waktu; kompromi antara kualitas spasial (resolusi) dan temporal (FPS) tergantung kebutuhan.
- Sejarah singkat: evolusi ilusi gerak hingga era digital (zoetrope, film awal, standar TV NTSC/PAL/SECAM, VHS vs Betamax, digital/HD/streaming).
- Tantangan penyimpanan: perhitungan ukuran video tanpa kompresi; trade-off resolusi vs FPS.
- Inti: teknik pemrosesan gambar sebelumnya dapat diterapkan per-frame pada video, tetapi aspek temporal dan kapasitas data menjadi kunci.

## Pertemuan_13_rppg.pdf — Remote Photoplethysmography (rPPG)
- Konsep: deteksi perubahan volume darah secara jarak jauh menggunakan kamera (tanpa kontak) dengan memanfaatkan perubahan mikro warna kulit (micro-blushing) terutama pada kanal hijau.
- Fisika dasar: hemoglobin menyerap cahaya hijau; siklus jantung mengubah intensitas pantulan (gelap saat pompa, terang saat relaksasi).
- Tantangan: sinyal sangat kecil (~0.1 level piksel 8-bit) dan tertutup noise (sensor, pencahayaan, gerakan, bayangan); perlu algoritma pemrosesan sinyal.
- Sejarah algoritma: GREEN (2008) — rata-rata kanal hijau; ICA/PCA — pemisahan komponen; POS/CHROM dan metode modern untuk ketahanan terhadap gerakan/pencahayaan; evolusi hingga pendekatan berbasis deep learning.
- Pipeline umum: deteksi wajah/ROI, ekstraksi sinyal warna, detrending dan bandpass filter, transformasi ke domain frekuensi (FFT) untuk estimasi BPM; implementasi real-time memakai sliding window.
- Aplikasi: monitoring kesehatan tanpa kontak, deteksi stres/kelelahan, biometrik; kendala praktis pada pencahayaan, pergerakan, dan kualitas sensor.

## Tugas_rPPG.pdf — Kerangka Tugas Implementasi Real-time rPPG
- Tujuan: membangun sistem real-time rPPG dengan webcam untuk mengestimasi detak jantung tanpa kontak.
- Lingkup wajib: (1) deteksi & pelacakan wajah (ROI) via OpenCV/MediaPipe; (2) ekstraksi sinyal (spatial averaging kanal hijau); (3) pemrosesan sinyal — detrending + bandpass 0.67–4.0 Hz; (4) estimasi BPM via FFT atau findpeaks.
- Real-time: gunakan sliding window untuk pembaruan BPM kontinu (bukan hanya video statis).
- Improvement (pilih ≥1): metode ekstraksi sinyal lebih robust (mis. POS), mitigasi gerakan/pencahayaan, skin segmentation/ROI spesifik, filter adaptif, atau visualisasi real-time (time series & spektrum).
- Format: hasil dalam notebook .ipynb atau skrip .py plus laporan markdown singkat (bedakan dengan demo kelas); unggah ke repo publik, tautkan langsung ke folder tugas; bahasa Python.
- Rubrik: pipeline dasar 30%, performa real-time 25%, improvement 25%, kualitas kode/dokumentasi 20%; boleh reuse kode lama dengan perbaikan untuk konteks real-time.
