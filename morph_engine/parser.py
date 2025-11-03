# morph_engine/parser.py
from .token_morph import TipeToken
from .ast_nodes import (
    ProgramNode, DeklarasiVariabelNode, PanggilFungsiNode,
    IdentifierNode, StringNode
)

class Parser:
    def __init__(self, token_list):
        self.token_list = token_list
        self.posisi = 0
        self.token_sekarang = self.token_list[self.posisi]

    def maju(self):
        """Memajukan posisi baca token."""
        self.posisi += 1
        if self.posisi < len(self.token_list):
            self.token_sekarang = self.token_list[self.posisi]
        else:
            self.token_sekarang = None # Sinyal akhir

    def parse_statement(self):
        """Menganalisis satu pernyataan (statement)."""
        if self.token_sekarang.tipe in (TipeToken.BIAR, TipeToken.TETAP):
            return self.parse_deklarasi_variabel()

        if self.token_sekarang.tipe == TipeToken.TULIS:
             return self.parse_panggil_fungsi()

        # Jika token tidak dikenali sebagai awal statement, kembalikan None
        return None


    def parse_deklarasi_variabel(self):
        """Menganalisis 'biar nama = nilai' atau 'tetap nama = nilai'."""
        jenis_deklarasi = self.token_sekarang
        self.maju()

        nama_variabel = IdentifierNode(self.token_sekarang)
        self.maju() # Lewati identifier

        if self.token_sekarang.tipe != TipeToken.SAMA_DENGAN:
            raise SyntaxError("Error Sintaks: Diharapkan ada '=' setelah nama variabel.")
        self.maju() # Lewati '='

        # Nilai bisa berupa string atau identifier
        if self.token_sekarang.tipe == TipeToken.STRING:
            nilai = StringNode(self.token_sekarang)
            self.maju()
            return DeklarasiVariabelNode(jenis_deklarasi, nama_variabel, nilai)
        else:
             raise SyntaxError("Error Sintaks: Diharapkan ada nilai (string) setelah '='.")


    def parse_panggil_fungsi(self):
        """Menganalisis 'tulis("halo")' atau 'tulis(variabel)'."""
        nama_fungsi = self.token_sekarang # Token TULIS itu sendiri
        self.maju()

        if self.token_sekarang.tipe != TipeToken.BUKA_KURUNG:
            raise SyntaxError("Error Sintaks: Diharapkan ada '(' setelah nama fungsi.")
        self.maju()

        # Argumen bisa berupa string atau identifier (nama variabel)
        if self.token_sekarang.tipe == TipeToken.STRING:
            argumen = StringNode(self.token_sekarang)
            self.maju()
        elif self.token_sekarang.tipe == TipeToken.IDENTIFIER:
            argumen = IdentifierNode(self.token_sekarang)
            self.maju()
        else:
            raise SyntaxError("Error Sintaks: Diharapkan ada argumen (string atau variabel) di dalam fungsi.")

        if self.token_sekarang.tipe != TipeToken.TUTUP_KURUNG:
            raise SyntaxError("Error Sintaks: Diharapkan ada ')' setelah argumen fungsi.")
        self.maju()

        # Menggunakan nilai dari token TULIS ('tulis') sebagai nama fungsi
        return PanggilFungsiNode(IdentifierNode(nama_fungsi), argumen)


    def parse(self):
        """Membangun AST dari daftar token."""
        statements = []
        while self.token_sekarang is not None and self.token_sekarang.tipe != TipeToken.ADS:
            statement = self.parse_statement()
            if statement:
                statements.append(statement)
            else:
                self.maju()

        return ProgramNode(statements)
