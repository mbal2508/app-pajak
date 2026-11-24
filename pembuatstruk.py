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
def greeting():
   print("\n========== PILIH PRODUK ==========")

produk = {"kaos":20000, "botol":30000}

while True:
   list_pembelian = []

   greeting()
   for nama, harga in produk.items():
      print(f"{nama}:{harga}")

   while True:
      input_produk_yang_dibeli = input("Masukan nama produk yang dibeli! (ketik 'cukup' jika produk sudah cukup) ").lower()
      if input_produk_yang_dibeli == "cukup":
         break

      produk_yang_dibeli = produk[input_produk_yang_dibeli]
      list_pembelian.append({"nama":input_produk_yang_dibeli, "harga":produk_yang_dibeli})

      print("\nProduk yang dipilih:")
      for item in list_pembelian:
         print(f"- {item['nama']}:{item['harga']}")

   total_pembelian = 0
   for item in list_pembelian:
      total_pembelian += item["harga"]

   while True:
      uang_cust = int(input("\nMasukan jumlah uang yang diberikan! "))

      if uang_cust >= total_pembelian:
         kembalian = uang_cust - total_pembelian
         break
      else:
         print("Uang kurang!!! Masukan ulang jumlah uang")

   buat_struk = input("Buat struk? ya/tidak ").lower()
   if buat_struk == "ya":
      print("\n========== STRUK PEMBELIAN ==========")
      print("Produk yang dibeli:")
      for item in list_pembelian:
         print(f"- {item['nama']}:{item['harga']}")
      print(f"\nUang diterima: Rp.{uang_cust}\nKembalian: Rp.{kembalian}")
      print("=====================================")

   ulang = input("ulang? ya/tidak ").lower()
   if ulang != "ya":
      break