# fox_engine/internal/pecahan_kelas_abstrak.py

def metode_abstrak(func):
    """
    Dekorator untuk menandai sebuah metode sebagai metode abstrak yang harus
    diimplementasikan oleh kelas turunan.
    """
    func.__isabstractmethod__ = True
    return func

class MetaPecahanAbstrak(type):
    """
    Metaclass yang mengidentifikasi dan mendaftarkan metode abstrak.

    Saat sebuah kelas dibuat, metaclass ini akan memeriksa semua metode
    di kelas tersebut dan kelas induknya. Metode yang ditandai dengan
    `@metode_abstrak` akan dikumpulkan dalam sebuah set bernama `__metode_abstrak__`.
    """
    def __new__(cls, name, bases, namespace):
        new_class = super().__new__(cls, name, bases, namespace)

        # Kumpulkan metode abstrak dari kelas saat ini
        abstracts = {
            name for name, value in namespace.items()
            if getattr(value, "__isabstractmethod__", False)
        }

        # Kumpulkan juga metode abstrak yang belum terimplementasi dari kelas induk
        for base in bases:
            for name in getattr(base, "__metode_abstrak__", set()):
                # Jika kelas baru belum menyediakan implementasi konkret,
                # metode tersebut tetap dianggap abstrak.
                value = getattr(new_class, name, None)
                if getattr(value, "__isabstractmethod__", False):
                    abstracts.add(name)

        new_class.__metode_abstrak__ = frozenset(abstracts)
        return new_class

class PecahanKelasAbstrak(metaclass=MetaPecahanAbstrak):
    """
    Kelas dasar untuk membuat 'Pecahan Kelas Abstrak'.

    Kelas yang mewarisi dari ini berfungsi sebagai kontrak. Ia tidak dapat
    diinstansiasi secara langsung jika masih mengandung satu atau lebih
    metode abstrak yang belum diimplementasikan oleh kelas turunan konkret.
    """
    def __new__(cls, *args, **kwargs):  # type: ignore
        # Mencegah instansiasi jika kelas masih memiliki metode abstrak
        if cls.__metode_abstrak__:
            raise TypeError(
                f"Tidak dapat membuat instansi dari pecahan kelas abstrak '{cls.__name__}' "
                f"karena metode berikut belum diimplementasikan: "
                f"{', '.join(sorted(cls.__metode_abstrak__))}"
            )
        return super().__new__(cls)
