# tests/fixtures/ffi_test_module.py

def proses_list_bersarang(data):
    """Menerima list of lists dan meratakannya."""
    if not isinstance(data, list):
        raise TypeError("Input harus berupa list")
    hasil_rata = []
    for sublist in data:
        if isinstance(sublist, list):
            hasil_rata.extend(sublist)
        else:
            hasil_rata.append(sublist)
    return hasil_rata

def modifikasi_kamus(data):
    """Menerima dictionary, menambahkan item, dan mengembalikannya."""
    if not isinstance(data, dict):
        raise TypeError("Input harus berupa dictionary")
    data["status_py"] = "diproses"
    return data

def picu_error():
    """Sengaja menimbulkan ValueError."""
    raise ValueError("Ini adalah kesalahan yang disengaja dari FFI")

def tambah_item_ke_daftar(daftar, item):
    """Menambahkan item ke list dan mengembalikan list baru (pola fungsional)."""
    if not isinstance(daftar, list):
        raise TypeError("Input pertama harus berupa list")
    return daftar + [item]
