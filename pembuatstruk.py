"""
APP PEMBUAT STRUK KASIR

Workflow:
1. user menginput produk yang dibeli dengan menampilkan ke camera.
2. produk yang discan masuk ke daftar produk dengan menampilkan nama dan harganya.
3. user menginput uang yang diterima.
4. jika tombol buat struk diklik, struk keluar dengan menampilkan total harga ditambah pajak,
   jumlah uang yang diterima dan kembalian.
5. user diberikan opsi untuk ulang dari awal atau selesai.

Cara kerja:
1. benda diperlihatkan ke camera, CV dan ML mendeteksi itu benda apa.
2. google gen ai mencari harga pasaran benda tersebut dan memberikan 
   output satu integer(contoh: 17000).
3. nama produk dan harganya disimpan ke dictionary dan ditampilkan di daftar produk
4. jika tombol buat struk diklik, struk keluar dengan menampilkan header, total harga ditambah pajak,
   jumlah uang yang diterima, kembalian, dan footer.
5. user diberikan opsi break atau melanjutkan loop.

"""
# def greeting():
#    print("\n========== PILIH PRODUK ==========")

# produk = {"kaos":20000, "botol":30000}

# while True:
#    list_pembelian = []

#    greeting()
#    for nama, harga in produk.items():
#       print(f"{nama}:{harga}")

#    while True:
#       input_produk_yang_dibeli = input("Masukan nama produk yang dibeli! (ketik 'cukup' jika produk sudah cukup) ").lower()
#       if input_produk_yang_dibeli == "cukup":
#          break

#       produk_yang_dibeli = produk[input_produk_yang_dibeli]
#       list_pembelian.append({"nama":input_produk_yang_dibeli, "harga":produk_yang_dibeli})

#       print("\nProduk yang dipilih:")
#       for item in list_pembelian:
#          print(f"- {item['nama']}:{item['harga']}")

#    total_pembelian = 0
#    for item in list_pembelian:
#       total_pembelian += item["harga"]

#    while True:
#       uang_cust = int(input("\nMasukan jumlah uang yang diberikan! "))

#       if uang_cust >= total_pembelian:
#          kembalian = uang_cust - total_pembelian
#          break
#       else:
#          print("Uang kurang!!! Masukan ulang jumlah uang")

#    buat_struk = input("Buat struk? ya/tidak ").lower()
#    if buat_struk == "ya":
#       print("\n========== STRUK PEMBELIAN ==========")
#       print("Produk yang dibeli:")
#       for item in list_pembelian:
#          print(f"- {item['nama']}:{item['harga']}")
#       print(f"\nUang diterima: Rp.{uang_cust}\nKembalian: Rp.{kembalian}")
#       print("=====================================")

#    ulang = input("ulang? ya/tidak ").lower()
#    if ulang != "ya":
#       break

import cv2
from google import genai
from PIL import Image
import os
import threading
import time

# Inisialisasi client Gemini (pastikan API Key sudah diset di environment variable)
client = genai.Client(api_key="AQ.Ab8RN6JIJKsxY1jMkPIfJOXH-glc97i40FnGloxxvtz9AqImfQ")

is_processing = False
list_pembelian = []

def proses_ai_background(frame):
    global is_processing
    max_retries = 3
    delay = 2

    for attempt in range(max_retries):
        try:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_frame)
            
            prompt = (
                "Analisis gambar benda yang dipegang ini. Tentukan nama barangnya secara singkat "
                "dan berikan estimasi harga pasaran wajar dalam bentuk angka bulat (integer) rupiah tanpa titik atau koma. "
                "Format jawaban HARUS persis seperti ini: [nama_barang]|[harga_angka]. "
                "Contoh: botol|15000"
            )

            print(f"\n🔍 AI sedang menganalisis benda (Percobaan {attempt + 1}/{max_retries})...")
            response = client.models.generate_content(
                model='gemini-3.5-flash-lite',
                contents=[pil_image, prompt]
            )
            
            hasil_teks = response.text.strip()
            parts = hasil_teks.split("|")
            
            if len(parts) == 2:
                nama_barang = parts[0].strip().lower()
                harga_barang = int(parts[1].strip())
                print(f"✨ Berhasil! Terdeteksi: {nama_barang} | Harga: Rp{harga_barang}")
                list_pembelian.append({"nama": nama_barang, "harga": harga_barang})
                break  # Berhenti mengulang jika berhasil
            else:
                print("❌ Gagal mendeteksi format benda dari AI.")
                break
                
        except Exception as e:
            print(f"⚠️ Gagal pada percobaan {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                print(f"⏳ Menunggu {delay} detik sebelum mencoba ulang...")
                time.sleep(delay)
                delay *= 2  # Waktu tunggu bertambah secara berkala (exponential backoff)
            else:
                print("❌ Gagal total menghubungi AI setelah beberapa kali percobaan. Silakan coba tekan spasi lagi nanti.")
    
    is_processing = False

def main():
    global is_processing
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Error: Kamera tidak dapat diakses.")
        return

    print("=" * 50)
    print("  LIVE SCANNER KAMERA (WITH THREADING)")
    print("  Arahkan benda ke kamera, lalu TEKAN SPASI untuk scan.")
    print("  Tekan 'q' pada keyboard untuk keluar dan cetak struk.")
    print("=" * 50)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Gagal membaca frame dari kamera.")
            break

        # Tampilkan status di layar video
        status_text = "Status: Memproses AI..." if is_processing else "Tekan SPASI untuk Scan | 'q' untuk Selesai"
        color = (0, 0, 255) if is_processing else (0, 255, 0)
        
        cv2.putText(frame, status_text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        cv2.imshow("Live Scanner - App Pajak", frame)

        key = cv2.waitKey(1) & 0xFF
        
        # Jika tombol Spasi ditekan dan AI sedang tidak sibuk
        if key == 32:
            if not is_processing:
                is_processing = True
                print("\n📸 Memotret benda, mengirim ke background thread...")
                
                # Jalankan fungsi AI di dalam thread terpisah
                t = threading.Thread(target=proses_ai_background, args=(frame.copy(),))
                t.start()
            else:
                print("⏳ AI masih memproses foto sebelumnya, mohon tunggu sebentar...")
                
        # Jika tombol 'q' ditekan (keluar)
        elif key == ord('q'):
            # Tunggu sebentar jika thread masih berjalan sebelum keluar
            if is_processing:
                print("Menunggu proses AI terakhir selesai...")
            break

    cap.release()
    cv2.destroyAllWindows()

    # Cetak ringkasan hasil belanja
    if list_pembelian:
        print("\n" + "=" * 35)
        print("          STRUK BELANJA AKHIR        ")
        print("=" * 35)
        subtotal = 0
        for item in list_pembelian:
            print(f"- {item['nama']} : Rp{item['harga']}")
            subtotal += item['harga']
        print("-" * 35)
        print(f"Total Keseluruhan: Rp{subtotal}")
        print("=" * 35)
    else:
        print("\nTidak ada produk yang di-scan.")

if __name__ == "__main__":
    main()