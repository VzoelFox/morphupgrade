# tests/unit/test_performance.py
# -*- coding: utf-8 -*-

# PATCH-TEST-001: Menambahkan test suite untuk regresi kinerja.
# TODO: Tambahkan skenario kinerja lainnya (misalnya, loop, alokasi memori).

import pytest
import time

RECURSION_CODE = """
fungsi hitung_mundur(n) maka
    jika n <= 0 maka
        kembalikan 0
    akhir
    kembalikan hitung_mundur(n - 1)
akhir

# Angka ini mungkin perlu disesuaikan agar berjalan cukup lama
# tapi tidak terlalu lama. Batas rekursi di penerjemah.py adalah 450.
# Kita menggunakan angka yang lebih rendah (100) untuk memastikan
# program berjalan tanpa mencapai batas rekursi interpreter (150).
tulis(hitung_mundur(100))
"""

@pytest.mark.performance
def test_recursion_performance(capture_output):
    """
    Memastikan bahwa rekursi yang dalam tidak mengalami penurunan kinerja yang signifikan.
    Tes ini mencoba beberapa kali dengan ambang batas waktu yang semakin longgar
    untuk mengakomodasi variabilitas lingkungan eksekusi.
    """
    time_thresholds = [0.5, 1.0, 5.0]  # Batas waktu dalam detik
    last_duration = -1

    for attempt, threshold in enumerate(time_thresholds, 1):
        try:
            start_time = time.time()
            result = capture_output(RECURSION_CODE)
            duration = time.time() - start_time

            print(f"Percobaan Kinerja {attempt}: Eksekusi selesai dalam {duration:.4f} detik (Batas: {threshold}s). Hasil: {result}")

            if duration <= threshold:
                # Lulus jika waktu eksekusi di bawah ambang batas saat ini
                assert result.strip() == "0"
                return

            last_duration = duration

        except Exception as e:
            pytest.fail(f"Tes kinerja gagal karena kesalahan runtime yang tidak terduga pada percobaan {attempt}: {e}")

    # Jika loop selesai, berarti semua percobaan gagal memenuhi batas waktu.
    pytest.fail(
        f"Kinerja rekursi melampaui semua ambang batas yang ditetapkan. "
        f"Waktu eksekusi terakhir adalah {last_duration:.4f}s, melebihi batas terakhir {time_thresholds[-1]}s."
    )
