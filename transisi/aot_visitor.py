# transisi/aot_visitor.py
from . import absolute_sntx_morph as ast

class AotVisitor:
    """
    Visitor AST ringan yang tugasnya hanya memeriksa keberadaan
    nama-nama tertentu (alias FFI) di dalam pohon AST.
    """
    def __init__(self, target_names: set[str]):
        self.target_names = target_names
        self.ditemukan = False

    def periksa(self, node: ast.MRPH):
        """Mulai proses pemeriksaan dari node yang diberikan."""
        self.ditemukan = False
        self._kunjungi(node)
        return self.ditemukan

    def _kunjungi(self, node):
        """Mendelegasikan ke metode '_kunjungi_*' yang sesuai."""
        if self.ditemukan or node is None:
            return

        nama_metode = f"_kunjungi_{type(node).__name__}"
        visitor = getattr(self, nama_metode, self._kunjungi_default)
        visitor(node)

    def _kunjungi_default(self, node):
        """Default visitor, mengiterasi semua atribut node."""
        for attr in vars(node).values():
            if isinstance(attr, ast.MRPH):
                self._kunjungi(attr)
            elif isinstance(attr, list):
                for item in attr:
                    if isinstance(item, ast.MRPH):
                        self._kunjungi(item)

    def _kunjungi_Identitas(self, node: ast.Identitas):
        if node.nama in self.target_names:
            self.ditemukan = True
