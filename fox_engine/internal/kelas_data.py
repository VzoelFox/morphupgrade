# fox_engine/internal/kelas_data.py

import inspect

def kelasdata(cls):
    """
    Dekorator yang secara otomatis menambahkan metode __init__, __repr__,
    dan __eq__ ke sebuah kelas, mirip dengan @dataclass.

    Ini mengambil anotasi tipe dari kelas untuk membangun metode-metode tersebut.
    Juga mendukung metode __post_init__ untuk logika inisialisasi tambahan.
    """

    fields = list(inspect.get_annotations(cls, eval_str=True).keys())
    original_init = getattr(cls, '__init__', None)
    post_init = getattr(cls, '__post_init__', None)

    def __init__(self, *args, **kwargs):
        """
        Konstruktor yang dihasilkan secara dinamis.
        """
        all_args = kwargs.copy()
        for i, arg in enumerate(args):
            if i < len(fields):
                all_args[fields[i]] = arg

        for field_name in fields:
            # Periksa apakah nilai diberikan dalam panggilan
            if field_name in all_args:
                setattr(self, field_name, all_args[field_name])
            # Jika tidak, periksa apakah ada nilai default di kelas
            elif hasattr(cls, field_name):
                setattr(self, field_name, getattr(cls, field_name))
            # Jika tidak ada nilai yang diberikan dan tidak ada default,
            # biarkan (akan menyebabkan AttributeError jika diakses,
            # yang merupakan perilaku yang wajar untuk field yang wajib).

        # Panggil __post_init__ jika ada
        if post_init:
            post_init(self)

    def __repr__(self):
        """
        Representasi string yang dihasilkan secara dinamis.
        """
        field_reprs = []
        for name in fields:
            # Hanya tampilkan di repr jika field benar-benar ada di instance
            if hasattr(self, name):
                field_reprs.append(f"{name}={getattr(self, name)!r}")
        return f"{cls.__name__}({', '.join(field_reprs)})"

    def __eq__(self, other):
        """
        Perbandingan kesetaraan yang dihasilkan secara dinamis.
        """
        if not isinstance(other, cls):
            return NotImplemented
        for field_name in fields:
            if getattr(self, field_name) != getattr(other, field_name):
                return False
        return True

    # Hanya ganti __init__ jika belum didefinisikan secara manual oleh pengguna
    if original_init is None or original_init is object.__init__:
        setattr(cls, '__init__', __init__)

    setattr(cls, '__repr__', __repr__)
    setattr(cls, '__eq__', __eq__)

    return cls
