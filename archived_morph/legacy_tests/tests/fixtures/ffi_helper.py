# tests/fixtures/ffi_helper.py

def cause_type_error(data):
    """
    Fungsi ini dirancang untuk menyebabkan TypeError dengan mencoba
    mengakses atribut pada tipe data yang tidak mendukungnya.
    """
    # kamus (dict) tidak punya atribut 'append'
    return data.append("seharusnya gagal")

def another_error_function(x, y):
    """
    Fungsi yang akan melempar ZeroDivisionError.
    """
    return x / y
