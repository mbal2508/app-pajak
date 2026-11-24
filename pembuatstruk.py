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

# Inisialisasi client Gemini (pastikan API Key sudah diset di environment variable)
client = genai.Client(api_key="AQ.Ab8RN6JIJKsxY1jMkPIfJOXH-glc97i40FnGloxxvtz9AqImfQ")

def deteksi_benda_dari_frame(frame):
    """
    Mengubah frame OpenCV (numpy array) menjadi gambar PIL,
    lalu mengirimkannya ke Gemini untuk dideteksi nama dan harganya.
    """
    try:
        # Konversi warna dari BGR (OpenCV) ke RGB (PIL)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb_frame)
        
        prompt = (
            "Analisis gambar benda yang dipegang ini. Tentukan nama barangnya secara singkat "
            "dan berikan estimasi harga pasaran wajar dalam bentuk angka bulat (integer) rupiah tanpa titik atau koma. "
            "Format jawaban HARUS persis seperti ini: [nama_barang]|[harga_angka]. "
            "Contoh: botol|15000"
        )

        print("🔍 AI sedang menganalisis benda...")
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[pil_image, prompt]
        )
        
        hasil_teks = response.text.strip()
        parts = hasil_teks.split("|")
        
        if len(parts) == 2:
            nama_barang = parts[0].strip().lower()
            harga_barang = int(parts[1].strip())
            return nama_barang, harga_barang
        else:
            return None, None
            
    except Exception as e:
        print(f"Error saat menghubungi AI: {e}")
        return None, None

def main():
    # Membuka kamera web (0 adalah default webcam laptop/PC)
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Error: Kamera tidak dapat diakses.")
        return

    list_pembelian = []
    
    print("=" * 50)
    print("  LIVE SCANNER KAMERA - APLIKASI KASIR AI")
    print("  Arahkan benda ke kamera, lalu TEKAN SPASI untuk scan.")
    print("  Tekan 'q' pada keyboard untuk keluar dan cetak struk.")
    print("=" * 50)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Gagal membaca frame dari kamera.")
            break

        # Tampilkan teks petunjuk di layar kamera
        cv2.putText(frame, "Tekan SPASI untuk Scan | 'q' untuk Selesai", 
                    (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # Tampilkan video live di jendela
        cv2.imshow("Live Scanner - App Pajak", frame)

        # Menangkap tombol keyboard yang ditekan user
        key = cv2.waitKey(1) & 0xFF
        
        # Jika user menekan tombol 'Spasi' (ASCII 32)
        if key == 32:
            print("\n📸 Memotret benda...")
            nama, harga = deteksi_benda_dari_frame(frame)
            
            if nama and harga:
                print(f"✨ Berhasil! Terdeteksi: {nama} | Harga: Rp{harga}")
                list_pembelian.append({"nama": nama, "harga": harga})
            else:
                print("❌ Gagal mendeteksi benda, coba posisikan lebih jelas di depan kamera.")
                
        # Jika user menekan tombol 'q' (keluar)
        elif key == ord('q'):
            break

    # Lepas kamera dan tutup jendela tampilan
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