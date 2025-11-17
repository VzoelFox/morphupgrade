# transisi/stdlib/wajib/ffi_monitor.py
"""
Modul FFI untuk mengekspos fungsi pemantauan dan kontrol kualitas
dari Fox Engine ke dalam kode Morph.
"""

from fox_engine.api import dapatkan_manajer_fox

def cetak_laporan():
    """Mengambil manajer global dan mencetak laporan metriknya."""
    manajer = dapatkan_manajer_fox()
    if manajer:
        manajer.cetak_laporan_metrik()
    else:
        print("Peringatan: ManajerFox belum diinisialisasi.")
