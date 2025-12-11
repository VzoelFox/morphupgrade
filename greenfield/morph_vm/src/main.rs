use std::fs::File;
use std::io::{self, Read};
use std::env;

// Constants
const MAGIC: &[u8] = b"VZOEL FOXS";

// Helper for reading
struct Reader {
    buffer: Vec<u8>,
    pos: usize,
}

impl Reader {
    fn new(buffer: Vec<u8>) -> Self {
        Reader { buffer, pos: 0 }
    }

    fn read_byte(&mut self) -> Option<u8> {
        if self.pos < self.buffer.len() {
            let b = self.buffer[self.pos];
            self.pos += 1;
            Some(b)
        } else {
            None
        }
    }

    fn read_bytes(&mut self, n: usize) -> Option<Vec<u8>> {
        if self.pos + n <= self.buffer.len() {
            let slice = &self.buffer[self.pos..self.pos + n];
            self.pos += n;
            Some(slice.to_vec())
        } else {
            None
        }
    }

    fn read_int(&mut self) -> Option<i32> {
        let bytes = self.read_bytes(4)?;
        Some(i32::from_le_bytes(bytes.try_into().ok()?))
    }
}

fn main() -> io::Result<()> {
    // CLI Args
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        println!("Usage: morph_vm <file.mvm>");
        return Ok(());
    }
    let filename = &args[1];

    println!("[Rust VM] Membaca file: {}", filename);

    // Read File
    let mut file = File::open(filename)?;
    let mut buffer = Vec::new();
    file.read_to_end(&mut buffer)?;

    let mut reader = Reader::new(buffer);

    // Verify Header
    let magic = reader.read_bytes(10).expect("Gagal membaca Magic Bytes (File terlalu pendek)");
    if magic != MAGIC {
        panic!("Invalid Magic Bytes: {:?}", String::from_utf8_lossy(&magic));
    }
    println!("Header OK: VZOEL FOXS valid.");

    let ver = reader.read_byte().expect("Gagal membaca Versi");
    println!("Versi Bytecode: {}", ver);

    let flags = reader.read_byte().expect("Gagal membaca Flags");
    println!("Flags: {}", flags);

    let ts = reader.read_int().expect("Gagal membaca Timestamp");
    println!("Timestamp: {}", ts);

    // Try to read the first tag (should be 7 for CodeObject)
    if let Some(tag) = reader.read_byte() {
        println!("Root Tag: {} (Harus 7 untuk CodeObject)", tag);

        if tag == 7 {
             // Read Name String
             if let Some(name_len) = reader.read_int() {
                 if let Some(name_bytes) = reader.read_bytes(name_len as usize) {
                     println!("Nama Modul: {}", String::from_utf8_lossy(&name_bytes));
                 } else {
                     println!("Gagal membaca bytes nama modul");
                 }
             } else {
                 println!("Gagal membaca panjang nama modul");
             }
        }
    } else {
        println!("File berakhir setelah header.");
    }

    Ok(())
}
