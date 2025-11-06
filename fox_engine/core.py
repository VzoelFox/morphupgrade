# fox_engine/core.py
# PATCH-014A: Refactor arsitektur TugasFox untuk io_handler eksplisit.
# PATCH-014B: Tambahkan metrik I/O dan kegagalan untuk MiniFox.
# PATCH-017D: Perkuat docstring dan type hinting untuk kejelasan maksimal.
# TODO: Integrasikan metrik bytes_dibaca/ditulis di ManajerFox. (SELESAI)
# FASE-2.5: Perjelas IOType untuk pelacakan metrik yang lebih akurat.
from typing import Callable, Optional, Any
import time

from .internal.aliansi_nilai_tetap import AliansiNilaiTetap, auto
from .internal.kelas_data import kelasdata

class FoxMode(AliansiNilaiTetap):
    """
    Menentukan mode eksekusi yang diinginkan untuk sebuah `TugasFox`.
    Setiap mode sesuai dengan strategi eksekusi yang berbeda di `ManajerFox`.
    """
    THUNDERFOX = "tfox"  #: Mode kompilasi Ahead-of-Time (AOT) untuk tugas berat CPU.
    WATERFOX = "wfox"    #: Mode Just-in-Time (JIT) adaptif untuk beban kerja campuran.
    SIMPLEFOX = "sfox"   #: Mode async murni untuk tugas ringan dengan latensi rendah.
    MINIFOX = "mfox"     #: Mode spesialis I/O untuk operasi file dan jaringan.
    AUTO = "auto"        #: Memungkinkan ManajerFox memilih mode terbaik secara otomatis.

class IOType(AliansiNilaiTetap):
    """
    Mendefinisikan tipe spesifik dari operasi I/O, digunakan oleh `MiniFoxStrategy`.
    Ini memungkinkan `MiniFoxStrategy` untuk menerapkan optimisasi di masa depan
    berdasarkan jenis I/O dan untuk pelacakan metrik yang akurat.
    """
    # Operasi File
    FILE_BACA = "file:baca"      #: Membaca data dari sistem file.
    FILE_TULIS = "file:tulis"    #: Menulis data ke sistem file.

    # Operasi Jaringan
    NETWORK_KIRIM = "net:kirim"  #: Mengirim data melalui jaringan.
    NETWORK_TERIMA = "net:terima"#: Menerima data dari jaringan.

    # Operasi Streaming
    STREAM_BACA = "stream:baca"  #: Membaca dari sumber data streaming.
    STREAM_TULIS = "stream:tulis"#: Menulis ke tujuan data streaming.

    # Generik (digunakan jika arah tidak relevan)
    FILE_GENERIC = "file"
    NETWORK_GENERIC = "network"
    STREAM_GENERIC = "stream"

class StatusTugas(AliansiNilaiTetap):
    """
    Mewakili status siklus hidup dari sebuah `TugasFox` di dalam `PencatatTugas`.
    """
    MENUNGGU = auto      #: Tugas telah didaftarkan tetapi belum dieksekusi.
    BERJALAN = auto      #: Tugas sedang dalam proses eksekusi.
    SELESAI = auto       #: Tugas berhasil diselesaikan.
    GAGAL = auto         #: Tugas gagal selama eksekusi.
    DIBATALKAN = auto    #: Tugas dibatalkan sebelum atau selama eksekusi.

@kelasdata
class TugasFox:
    """
    Mewakili satu unit pekerjaan yang dapat dieksekusi oleh `ManajerFox`.
    Objek ini adalah struktur data inti yang membawa semua informasi
    yang diperlukan untuk eksekusi, penjadwalan, dan pemantauan.

    Attributes:
        nama (str): Nama unik untuk identifikasi dan logging tugas.
        coroutine (Callable): Coroutine utama yang berisi logika tugas.
        mode (FoxMode): Mode eksekusi yang diminta.
        prioritas (int): Prioritas tugas (belum diimplementasikan sepenuhnya).
        batas_waktu (Optional[float]): Batas waktu eksekusi dalam detik.
        jenis_operasi (Optional[IOType]): Jenis I/O spesifik untuk `MiniFoxStrategy`.
        io_handler (Optional[Callable]): Fungsi synchronous blocking untuk tugas I/O.
        bytes_processed (int): Jumlah byte yang diproses oleh `io_handler`.
        dibuat_pada (float): Timestamp pembuatan tugas.
        estimasi_durasi (Optional[float]): Estimasi durasi tugas untuk mode AUTO.
    """
    nama: str
    coroutine: Callable
    mode: FoxMode
    prioritas: int = 1
    batas_waktu: Optional[float] = None
    jenis_operasi: Optional[IOType] = None
    io_handler: Optional[Callable] = None
    bytes_processed: int = 0
    dibuat_pada: float = None
    estimasi_durasi: Optional[float] = None

    def __post_init__(self):
        """Menginisialisasi nilai default setelah konstruktor utama."""
        if self.dibuat_pada is None:
            self.dibuat_pada = time.time()

@kelasdata
class MetrikFox:
    """
    Menyimpan metrik operasional agregat dari `ManajerFox` untuk pemantauan.
    Objek ini berfungsi sebagai pusat data untuk observabilitas sistem.

    Attributes:
        tugas_tfox_selesai (int): Jumlah tugas ThunderFox yang berhasil.
        tugas_wfox_selesai (int): Jumlah tugas WaterFox yang berhasil.
        tugas_sfox_selesai (int): Jumlah tugas SimpleFox yang berhasil.
        tugas_mfox_selesai (int): Jumlah tugas MiniFox yang berhasil.
        tugas_mfox_gagal (int): Jumlah tugas MiniFox yang gagal.
        tugas_gagal (int): Total tugas yang gagal di semua mode.
        avg_durasi_tfox (float): Rata-rata durasi eksekusi tugas ThunderFox.
        avg_durasi_wfox (float): Rata-rata durasi eksekusi tugas WaterFox.
        avg_durasi_sfox (float): Rata-rata durasi eksekusi tugas SimpleFox.
        avg_durasi_mfox (float): Rata-rata durasi eksekusi tugas MiniFox.
        bytes_dibaca (int): Total byte yang dibaca oleh `MiniFoxStrategy`.
        bytes_ditulis (int): Total byte yang ditulis oleh `MiniFoxStrategy`.
    """
    tugas_tfox_selesai: int = 0
    tugas_wfox_selesai: int = 0
    tugas_sfox_selesai: int = 0
    tugas_mfox_selesai: int = 0
    tugas_mfox_gagal: int = 0
    kompilasi_aot: int = 0  # Dipertahankan untuk kompatibilitas masa depan
    kompilasi_jit: int = 0  # Dipertahankan untuk kompatibilitas masa depan
    tugas_gagal: int = 0
    avg_durasi_tfox: float = 0.0
    avg_durasi_wfox: float = 0.0
    avg_durasi_sfox: float = 0.0
    avg_durasi_mfox: float = 0.0
    bytes_dibaca: int = 0
    bytes_ditulis: int = 0
