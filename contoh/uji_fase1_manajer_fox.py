# contoh/uji_fase1_manajer_fox.py
import asyncio
import time
import sys
import os

# Tambahkan root direktori ke sys.path agar bisa mengimpor fox_engine.
# Ini diperlukan karena skrip ini mungkin dijalankan langsung dari direktori 'contoh'.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fox_engine import tfox, wfox, fox, dapatkan_manajer_fox

async def simulasi_komputasi_berat():
    """Simulasi tugas yang membutuhkan waktu lama (mis: komputasi)."""
    print("... menjalankan komputasi berat (1.5 detik)")
    await asyncio.sleep(1.5)
    return "HASIL_DARI_TUGAS_BERAT"

async def simulasi_operasi_cepat():
    """Simulasi tugas yang berjalan cepat (mis: I/O)."""
    print("... menjalankan operasi cepat (0.1 detik)")
    await asyncio.sleep(0.1)
    return "HASIL_DARI_OPERASI_CEPAT"

async def uji_fungsionalitas_dasar():
    """Menguji fungsi-fungsi dasar dari ManajerFox."""
    print("🧪 Menguji Fungsionalitas Dasar ManajerFox Fase 1...")

    # 1. Uji mode eksplisit tfox
    print("\n--- Menguji mode ThunderFox (tfox) secara eksplisit ---")
    hasil1 = await tfox("tugas_berat_1", simulasi_komputasi_berat,
                        estimasi_durasi=1.5)
    print(f"✅ Hasil ThunderFox: {hasil1}")

    # 2. Uji mode eksplisit wfox
    print("\n--- Menguji mode WaterFox (wfox) secara eksplisit ---")
    hasil2 = await wfox("tugas_cepat_1", simulasi_operasi_cepat,
                        estimasi_durasi=0.1)
    print(f"✅ Hasil WaterFox: {hasil2}")

    # 3. Uji mode otomatis
    print("\n--- Menguji mode otomatis (fox) ---")
    # Tugas berat, ManajerFox harus memilih tfox
    hasil3 = await fox("otomatis_berat", simulasi_komputasi_berat,
                       estimasi_durasi=1.5)
    print(f"✅ Hasil mode Otomatis (berat): {hasil3}")
    # Tugas ringan, ManajerFox harus memilih wfox
    hasil4 = await fox("otomatis_cepat", simulasi_operasi_cepat,
                       estimasi_durasi=0.1)
    print(f"✅ Hasil mode Otomatis (cepat): {hasil4}")

    # 4. Uji metrik
    metrik = dapatkan_manajer_fox().dapatkan_metrik()
    print(f"\n📊 Metrik saat ini: {metrik}")

async def uji_mekanisme_keamanan():
    """Menguji mekanisme keamanan dasar seperti pencegahan duplikasi."""
    print("\n🧪 Menguji Mekanisme Keamanan...")

    # Uji pencegahan tugas duplikat
    print("\n--- Menguji pencegahan tugas dengan nama yang sama ---")
    try:
        # Coba jalankan dua tugas dengan nama identik secara bersamaan
        await asyncio.gather(
            tfox("tugas_duplikat", simulasi_operasi_cepat),
            wfox("tugas_duplikat", simulasi_operasi_cepat)
        )
    except ValueError as e:
        print(f"✅ Pencegahan duplikasi berhasil terpicu: {e}")

async def utama():
    """Fungsi utama untuk menjalankan semua skenario pengujian."""
    await uji_fungsionalitas_dasar()
    await uji_mekanisme_keamanan()

    # Lakukan shutdown manajer secara bersih setelah semua tes selesai
    await dapatkan_manajer_fox().shutdown()

if __name__ == "__main__":
    try:
        asyncio.run(utama())
    except KeyboardInterrupt:
        print("\n🛑 Pengujian dihentikan oleh pengguna.")
