use std::fs::File;
use std::io::{self, Read};
use std::env;

// Constants
const MAGIC: &[u8] = b"VZOEL FOXS";

// --- Data Structures ---

#[derive(Debug, Clone)]
enum Constant {
    Nil,
    Boolean(bool),
    Integer(i32),
    Float(f64),
    String(String),
    List(Vec<Constant>),
    Code(Box<CodeObject>),
    Dict(Vec<(Constant, Constant)>),
}

// Implement PartialEq for Comparisons
impl PartialEq for Constant {
    fn eq(&self, other: &Self) -> bool {
        match (self, other) {
            (Constant::Nil, Constant::Nil) => true,
            (Constant::Boolean(a), Constant::Boolean(b)) => a == b,
            (Constant::Integer(a), Constant::Integer(b)) => a == b,
            (Constant::Float(a), Constant::Float(b)) => a == b,
            (Constant::String(a), Constant::String(b)) => a == b,
            _ => false,
        }
    }
}

// Implement PartialOrd for Comparisons
impl PartialOrd for Constant {
    fn partial_cmp(&self, other: &Self) -> Option<std::cmp::Ordering> {
        match (self, other) {
            (Constant::Integer(a), Constant::Integer(b)) => a.partial_cmp(b),
            (Constant::Float(a), Constant::Float(b)) => a.partial_cmp(b),
            (Constant::Integer(a), Constant::Float(b)) => (*a as f64).partial_cmp(b),
            (Constant::Float(a), Constant::Integer(b)) => a.partial_cmp(&(*b as f64)),
            _ => None,
        }
    }
}

#[derive(Debug, Clone)]
struct CodeObject {
    name: String,
    args: Vec<String>,
    constants: Vec<Constant>,
    instructions: Vec<(u8, Constant)>,
}

// --- VM Runtime ---

struct VM {
    stack: Vec<Constant>,
}

impl VM {
    fn new() -> Self {
        VM { stack: Vec::new() }
    }

    fn run(&mut self, code: CodeObject) {
        // println!("[VM] Memulai Eksekusi...");

        for (_i, (op, arg)) in code.instructions.iter().enumerate() {
            match op {
                1 => { // PUSH_CONST
                    self.stack.push(arg.clone());
                },
                2 => { // POP
                    if self.stack.pop().is_none() {
                        panic!("Stack underflow on POP");
                    }
                },
                3 => { // DUP
                    if let Some(val) = self.stack.last() {
                        self.stack.push(val.clone());
                    } else {
                        panic!("Stack underflow on DUP");
                    }
                },
                4 => { // ADD
                    let b = self.stack.pop().expect("Stack underflow");
                    let a = self.stack.pop().expect("Stack underflow");
                    match (a, b) {
                         (Constant::Integer(ia), Constant::Integer(ib)) => self.stack.push(Constant::Integer(ia + ib)),
                         (Constant::Float(fa), Constant::Float(fb)) => self.stack.push(Constant::Float(fa + fb)),
                         (Constant::String(sa), Constant::String(sb)) => self.stack.push(Constant::String(sa + &sb)),
                         (Constant::Integer(ia), Constant::Float(fb)) => self.stack.push(Constant::Float(ia as f64 + fb)),
                         (Constant::Float(fa), Constant::Integer(ib)) => self.stack.push(Constant::Float(fa + ib as f64)),
                         _ => panic!("Type mismatch for ADD"),
                    }
                },
                5 => { // SUB
                    let b = self.stack.pop().expect("Stack underflow");
                    let a = self.stack.pop().expect("Stack underflow");
                    match (a, b) {
                         (Constant::Integer(ia), Constant::Integer(ib)) => self.stack.push(Constant::Integer(ia - ib)),
                         (Constant::Float(fa), Constant::Float(fb)) => self.stack.push(Constant::Float(fa - fb)),
                         (Constant::Integer(ia), Constant::Float(fb)) => self.stack.push(Constant::Float(ia as f64 - fb)),
                         (Constant::Float(fa), Constant::Integer(ib)) => self.stack.push(Constant::Float(fa - ib as f64)),
                         _ => panic!("Type mismatch for SUB"),
                    }
                },
                6 => { // MUL
                    let b = self.stack.pop().expect("Stack underflow");
                    let a = self.stack.pop().expect("Stack underflow");
                    match (a, b) {
                         (Constant::Integer(ia), Constant::Integer(ib)) => self.stack.push(Constant::Integer(ia * ib)),
                         (Constant::Float(fa), Constant::Float(fb)) => self.stack.push(Constant::Float(fa * fb)),
                         (Constant::Integer(ia), Constant::Float(fb)) => self.stack.push(Constant::Float(ia as f64 * fb)),
                         (Constant::Float(fa), Constant::Integer(ib)) => self.stack.push(Constant::Float(fa * ib as f64)),
                         _ => panic!("Type mismatch for MUL"),
                    }
                },
                7 => { // DIV
                    let b = self.stack.pop().expect("Stack underflow");
                    let a = self.stack.pop().expect("Stack underflow");
                    match (a, b) {
                         (Constant::Integer(ia), Constant::Integer(ib)) => self.stack.push(Constant::Integer(ia / ib)),
                         (Constant::Float(fa), Constant::Float(fb)) => self.stack.push(Constant::Float(fa / fb)),
                         (Constant::Integer(ia), Constant::Float(fb)) => self.stack.push(Constant::Float(ia as f64 / fb)),
                         (Constant::Float(fa), Constant::Integer(ib)) => self.stack.push(Constant::Float(fa / ib as f64)),
                         _ => panic!("Type mismatch for DIV"),
                    }
                },
                8 => { // MOD
                    let b = self.stack.pop().expect("Stack underflow");
                    let a = self.stack.pop().expect("Stack underflow");
                    match (a, b) {
                         (Constant::Integer(ia), Constant::Integer(ib)) => self.stack.push(Constant::Integer(ia % ib)),
                         (Constant::Float(fa), Constant::Float(fb)) => self.stack.push(Constant::Float(fa % fb)),
                         _ => panic!("Type mismatch for MOD"),
                    }
                },
                9 => { // EQ
                    let b = self.stack.pop().expect("Stack underflow");
                    let a = self.stack.pop().expect("Stack underflow");
                    self.stack.push(Constant::Boolean(a == b));
                },
                10 => { // NEQ
                    let b = self.stack.pop().expect("Stack underflow");
                    let a = self.stack.pop().expect("Stack underflow");
                    self.stack.push(Constant::Boolean(a != b));
                },
                11 => { // GT
                    let b = self.stack.pop().expect("Stack underflow");
                    let a = self.stack.pop().expect("Stack underflow");
                    self.stack.push(Constant::Boolean(a > b));
                },
                12 => { // LT
                    let b = self.stack.pop().expect("Stack underflow");
                    let a = self.stack.pop().expect("Stack underflow");
                    self.stack.push(Constant::Boolean(a < b));
                },
                13 => { // GTE
                    let b = self.stack.pop().expect("Stack underflow");
                    let a = self.stack.pop().expect("Stack underflow");
                    self.stack.push(Constant::Boolean(a >= b));
                },
                14 => { // LTE
                    let b = self.stack.pop().expect("Stack underflow");
                    let a = self.stack.pop().expect("Stack underflow");
                    self.stack.push(Constant::Boolean(a <= b));
                },
                15 => { // NOT
                    let a = self.stack.pop().expect("Stack underflow");
                    match a {
                        Constant::Boolean(b) => self.stack.push(Constant::Boolean(!b)),
                        _ => panic!("Type mismatch for NOT"),
                    }
                },
                16 => { // AND
                    let b = self.stack.pop().expect("Stack underflow");
                    let a = self.stack.pop().expect("Stack underflow");
                    match (a, b) {
                        (Constant::Boolean(ba), Constant::Boolean(bb)) => self.stack.push(Constant::Boolean(ba && bb)),
                         _ => panic!("Type mismatch for AND"),
                    }
                },
                17 => { // OR
                    let b = self.stack.pop().expect("Stack underflow");
                    let a = self.stack.pop().expect("Stack underflow");
                    match (a, b) {
                        (Constant::Boolean(ba), Constant::Boolean(bb)) => self.stack.push(Constant::Boolean(ba || bb)),
                         _ => panic!("Type mismatch for OR"),
                    }
                },
                53 => { // PRINT
                    if let Constant::Integer(count) = arg {
                        let count = *count as usize;
                        if self.stack.len() < count {
                            panic!("Stack underflow on PRINT");
                        }
                        // Ambil N item teratas tanpa membalik urutan (FIFO untuk argumen print)
                        let start_idx = self.stack.len() - count;
                        let args: Vec<Constant> = self.stack.drain(start_idx..).collect();

                        for (idx, val) in args.iter().enumerate() {
                            if idx > 0 { print!(" "); }
                            match val {
                                Constant::String(s) => print!("{}", s),
                                Constant::Integer(n) => print!("{}", n),
                                Constant::Float(f) => print!("{}", f),
                                Constant::Boolean(b) => print!("{}", b),
                                Constant::Nil => print!("nil"),
                                _ => print!("{:?}", val),
                            }
                        }
                        println!(); // Baris baru
                    } else {
                        panic!("PRINT argument must be Integer");
                    }
                },
                48 => { // RET
                    // Untuk skrip level atas, RET berarti selesai
                    return;
                },
                _ => {
                    // Abaikan opcode yang belum diimplementasikan
                }
            }
        }
    }
}

// --- Deserializer (Reader) ---

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

    fn read_float(&mut self) -> Option<f64> {
        let bytes = self.read_bytes(8)?;
        Some(f64::from_le_bytes(bytes.try_into().ok()?))
    }

    fn read_string_raw(&mut self) -> Option<String> {
        let len = self.read_int()?;
        if len < 0 { return None; }
        let bytes = self.read_bytes(len as usize)?;
        String::from_utf8(bytes).ok()
    }

    fn read_constant(&mut self) -> Option<Constant> {
        let tag = self.read_byte()?;
        match tag {
            1 => Some(Constant::Nil),
            2 => {
                let val = self.read_byte()?;
                Some(Constant::Boolean(val == 1))
            },
            3 => Some(Constant::Integer(self.read_int()?)),
            4 => Some(Constant::Float(self.read_float()?)),
            5 => Some(Constant::String(self.read_string_raw()?)),
            6 => {
                let count = self.read_int()?;
                let mut list = Vec::new();
                for _ in 0..count {
                    list.push(self.read_constant()?);
                }
                Some(Constant::List(list))
            },
            7 => {
                let co = self.read_code_object()?;
                Some(Constant::Code(Box::new(co)))
            },
            8 => {
                let count = self.read_int()?;
                let mut dict = Vec::new();
                for _ in 0..count {
                    let k = self.read_constant()?;
                    let v = self.read_constant()?;
                    dict.push((k, v));
                }
                Some(Constant::Dict(dict))
            },
            _ => {
                println!("Unknown Constant Tag: {}", tag);
                None
            }
        }
    }

    fn read_code_object(&mut self) -> Option<CodeObject> {
        let name = self.read_string_raw()?;

        let arg_count = self.read_byte()?;
        let mut args = Vec::new();
        for _ in 0..arg_count {
            args.push(self.read_string_raw()?);
        }

        let const_count = self.read_int()?;
        let mut constants = Vec::new();
        for _ in 0..const_count {
            constants.push(self.read_constant()?);
        }

        let instr_count = self.read_int()?;
        let mut instructions = Vec::new();
        for _ in 0..instr_count {
            let op = self.read_byte()?;
            let arg = self.read_constant()?;
            instructions.push((op, arg));
        }

        Some(CodeObject {
            name,
            args,
            constants,
            instructions
        })
    }
}

fn main() -> io::Result<()> {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        println!("Usage: morph_vm <file.mvm>");
        return Ok(());
    }
    let filename = &args[1];

    let mut file = File::open(filename)?;
    let mut buffer = Vec::new();
    file.read_to_end(&mut buffer)?;

    let mut reader = Reader::new(buffer);

    // Verify Header
    let magic = reader.read_bytes(10).expect("Gagal membaca Magic Bytes");
    if magic != MAGIC {
        panic!("Invalid Magic Bytes");
    }

    let _ver = reader.read_byte().expect("Gagal membaca Versi");
    let _flags = reader.read_byte().expect("Gagal membaca Flags");
    let _ts = reader.read_int().expect("Gagal membaca Timestamp");

    // Read Root CodeObject
    if let Some(tag) = reader.read_byte() {
        if tag != 7 {
            panic!("Expected Root Tag 7 (CodeObject), got {}", tag);
        }

        if let Some(co) = reader.read_code_object() {
            // Execute
            let mut vm = VM::new();
            vm.run(co);

        } else {
            panic!("Gagal memparsing CodeObject");
        }
    } else {
        panic!("File kosong setelah header");
    }

    Ok(())
}
