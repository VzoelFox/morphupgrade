# transisi/log_setup.py
import logging
import os
import sys

def setup_logging():
    """
    Mengkonfigurasi dan mengembalikan instance logger untuk proyek Morph.
    """
    logger = logging.getLogger("morph")

    # Hindari menambahkan handler duplikat jika fungsi ini dipanggil beberapa kali
    if logger.handlers:
        return logger

    # Tentukan level log dari environment variable, default ke INFO
    log_level_str = os.getenv("MORPH_LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_str, logging.INFO)
    logger.setLevel(log_level)

    # Format log yang informatif
    formatter = logging.Formatter(
        '%(asctime)s [%(name)s] %(levelname)s: %(message)s',
        datefmt='%H:%M:%S'
    )

    # Handler default ke stderr
    # Cek apakah ada handler yang sudah terpasang ke root logger
    # Ini untuk menghindari output duplikat di beberapa lingkungan (misalnya pytest)
    if not logging.getLogger().handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    # Handler opsional ke file jika environment variable diset
    log_file = os.getenv("MORPH_LOG_FILE")
    if log_file:
        try:
            file_handler = logging.FileHandler(log_file, mode='a')
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except (IOError, OSError) as e:
            logger.error(f"Gagal membuka file log '{log_file}': {e}", exc_info=False)

    logger.debug(f"Logger diinisialisasi: level={log_level_str}, file={log_file or 'hanya stderr'}")
    return logger

# Buat satu instance logger untuk diimpor oleh modul lain
logger = setup_logging()
