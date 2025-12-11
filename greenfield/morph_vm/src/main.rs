use std::fs::File;
use std::io::{self, Read};
use std::env;
use std::rc::Rc;

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
    Code(Rc<CodeObject>),
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

#[derive(Debug, Clone)]
struct CallFrame {
    code: Rc<CodeObject>,
    pc: usize,
    locals: std::collections::HashMap<String, Constant>,
}

// --- VM Runtime ---

struct VM {
    frames: Vec<CallFrame>,
    stack: Vec<Constant>,
    globals: std::collections::HashMap<String, Constant>,
}

impl VM {
    fn new() -> Self {
        VM { frames: Vec::new(), stack: Vec::new(), globals: std::collections::HashMap::new() }
    }

    fn run(&mut self, initial_code: CodeObject) {
        let root_frame = CallFrame {
            code: Rc::new(initial_code),
            pc: 0,
            locals: std::collections::HashMap::new(),
        };
        self.frames.push(root_frame);

        while !self.frames.is_empty() {
            let (op, arg) = {
                let frame = self.frames.last_mut().expect("No frame");
                if frame.pc >= frame.code.instructions.len() {
                    self.frames.pop();
                    continue;
                }
                let instr = &frame.code.instructions[frame.pc];
                frame.pc += 1;
                (instr.0, instr.1.clone())
            };

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
                23 => { // LOAD_VAR
                    if let Constant::String(name) = arg {
                        // Check local first
                        let val = if let Some(frame) = self.frames.last() {
                            frame.locals.get(&name).cloned()
                        } else {
                            None
                        };

                        if let Some(v) = val {
                            self.stack.push(v);
                        } else if let Some(v) = self.globals.get(&name) {
                            self.stack.push(v.clone());
                        } else {
                            panic!("Variable not found: {}", name);
                        }
                    } else {
                        panic!("LOAD_VAR name must be String");
                    }
                },
                24 => { // STORE_VAR
                    if let Constant::String(name) = arg {
                        let val = self.stack.pop().expect("Stack underflow on STORE_VAR");
                        if let Some(frame) = self.frames.last_mut() {
                            frame.locals.insert(name.clone(), val);
                        } else {
                            self.globals.insert(name.clone(), val);
                        }
                    } else {
                        panic!("STORE_VAR name must be String");
                    }
                },
                25 => { // LOAD_LOCAL
                    if let Constant::String(name) = arg {
                        if let Some(frame) = self.frames.last() {
                            if let Some(v) = frame.locals.get(&name) {
                                self.stack.push(v.clone());
                            } else {
                                panic!("Local Variable not found: {}", name);
                            }
                        } else {
                            panic!("LOAD_LOCAL used without frame");
                        }
                    } else {
                        panic!("LOAD_LOCAL name must be String");
                    }
                },
                26 => { // STORE_LOCAL
                    if let Constant::String(name) = arg {
                         let val = self.stack.pop().expect("Stack underflow on STORE_LOCAL");
                         if let Some(frame) = self.frames.last_mut() {
                             frame.locals.insert(name.clone(), val);
                         } else {
                             panic!("STORE_LOCAL used without frame");
                         }
                    } else {
                        panic!("STORE_LOCAL name must be String");
                    }
                },
                27 => { // BUILD_LIST
                    let count = if let Constant::Integer(c) = arg { c as usize } else { 0 };
                    let mut list = Vec::new();
                    for _ in 0..count {
                        list.push(self.stack.pop().expect("Stack underflow BUILD_LIST"));
                    }
                    list.reverse();
                    self.stack.push(Constant::List(list));
                },
                28 => { // BUILD_DICT
                     let count = if let Constant::Integer(c) = arg { c as usize } else { 0 };
                     let mut dict = Vec::new();
                     for _ in 0..count {
                         let v = self.stack.pop().expect("Stack underflow BUILD_DICT value");
                         let k = self.stack.pop().expect("Stack underflow BUILD_DICT key");
                         dict.push((k, v));
                     }
                     dict.reverse();
                     self.stack.push(Constant::Dict(dict));
                },
                29 => { // LOAD_INDEX
                     let index = self.stack.pop().expect("Stack underflow LOAD_INDEX index");
                     let obj = self.stack.pop().expect("Stack underflow LOAD_INDEX obj");
                     match obj {
                         Constant::List(list) => {
                             if let Constant::Integer(i) = index {
                                 if i >= 0 && (i as usize) < list.len() {
                                     self.stack.push(list[i as usize].clone());
                                 } else {
                                     panic!("Index out of bounds: {}", i);
                                 }
                             } else {
                                 panic!("List index must be Integer");
                             }
                         },
                         Constant::Dict(dict) => {
                             let mut found = false;
                             for (k, v) in &dict {
                                 if k == &index {
                                     self.stack.push(v.clone());
                                     found = true;
                                     break;
                                 }
                             }
                             if !found {
                                 panic!("Key not found in Dict: {:?}", index);
                             }
                         },
                         Constant::String(s) => {
                             if let Constant::Integer(i) = index {
                                 if i >= 0 && (i as usize) < s.len() {
                                     if let Some(c) = s.chars().nth(i as usize) {
                                         self.stack.push(Constant::String(c.to_string()));
                                     } else {
                                         panic!("String index out of bounds");
                                     }
                                 } else {
                                     panic!("String index must be Integer");
                                 }
                             }
                         },
                         _ => panic!("Not subscriptable: {:?}", obj),
                     }
                },
                4 => { // ADD
                    let b = self.stack.pop().expect("Stack underflow");
                    let a = self.stack.pop().expect("Stack underflow");
                    match (&a, &b) {
                         (Constant::Integer(ia), Constant::Integer(ib)) => self.stack.push(Constant::Integer(ia + ib)),
                         (Constant::Float(fa), Constant::Float(fb)) => self.stack.push(Constant::Float(fa + fb)),
                         (Constant::String(sa), Constant::String(sb)) => self.stack.push(Constant::String(sa.clone() + sb)),
                         (Constant::Integer(ia), Constant::Float(fb)) => self.stack.push(Constant::Float(*ia as f64 + fb)),
                         (Constant::Float(fa), Constant::Integer(ib)) => self.stack.push(Constant::Float(fa + *ib as f64)),
                         _ => panic!("Type mismatch for ADD: {:?} + {:?}", a, b),
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
                44 => { // JMP
                    if let Constant::Integer(target) = arg {
                        self.frames.last_mut().unwrap().pc = target as usize;
                    } else {
                        panic!("JMP target must be Integer");
                    }
                },
                45 => { // JMP_IF_FALSE
                    let condition = self.stack.pop().expect("Stack underflow");
                    let is_true = match condition {
                        Constant::Boolean(b) => b,
                        Constant::Nil => false,
                        Constant::Integer(i) => i != 0,
                        _ => true,
                    };
                    if !is_true {
                        if let Constant::Integer(target) = arg {
                            self.frames.last_mut().unwrap().pc = target as usize;
                        } else {
                            panic!("JMP_IF_FALSE target must be Integer");
                        }
                    }
                },
                46 => { // JMP_IF_TRUE
                    let condition = self.stack.pop().expect("Stack underflow");
                    let is_true = match condition {
                        Constant::Boolean(b) => b,
                        Constant::Nil => false,
                        Constant::Integer(i) => i != 0,
                        _ => true,
                    };
                    if is_true {
                        if let Constant::Integer(target) = arg {
                             self.frames.last_mut().unwrap().pc = target as usize;
                        } else {
                            panic!("JMP_IF_TRUE target must be Integer");
                        }
                    }
                },
                53 => { // PRINT
                    if let Constant::Integer(count) = arg {
                        let count = count as usize;
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
                60 => { // BUILD_FUNCTION
                    let func_def = self.stack.pop().expect("Stack underflow BUILD_FUNCTION");
                    if let Constant::Dict(entries) = func_def {
                         let mut name = String::new();
                         let mut args = Vec::new();
                         let mut instructions = Vec::new();

                         for (k, v) in entries {
                             if let Constant::String(k_str) = k {
                                 if k_str == "nama" {
                                     if let Constant::String(n) = v { name = n; }
                                 } else if k_str == "args" {
                                     if let Constant::List(arg_list) = v {
                                         for arg_name in arg_list {
                                             if let Constant::String(s) = arg_name {
                                                 args.push(s);
                                             }
                                         }
                                     }
                                 } else if k_str == "instruksi" {
                                     if let Constant::List(instr_list) = v {
                                         for instr in instr_list {
                                             if let Constant::List(pair) = instr {
                                                 if pair.len() >= 2 {
                                                     let op_code = if let Constant::Integer(o) = pair[0] { o as u8 } else { 0 };
                                                     let op_arg = pair[1].clone();
                                                     instructions.push((op_code, op_arg));
                                                 }
                                             }
                                         }
                                     }
                                 }
                             }
                         }

                         let co = CodeObject {
                             name,
                             args,
                             constants: Vec::new(),
                             instructions,
                         };
                         self.stack.push(Constant::Code(Rc::new(co)));
                    } else {
                        panic!("BUILD_FUNCTION argument must be Dict");
                    }
                },
                69 => { // BIT_AND
                    let b = self.stack.pop().expect("Stack underflow");
                    let a = self.stack.pop().expect("Stack underflow");
                    match (a, b) {
                        (Constant::Integer(ia), Constant::Integer(ib)) => self.stack.push(Constant::Integer(ia & ib)),
                         _ => panic!("Type mismatch for BIT_AND"),
                    }
                },
                70 => { // BIT_OR
                    let b = self.stack.pop().expect("Stack underflow");
                    let a = self.stack.pop().expect("Stack underflow");
                    match (a, b) {
                        (Constant::Integer(ia), Constant::Integer(ib)) => self.stack.push(Constant::Integer(ia | ib)),
                         _ => panic!("Type mismatch for BIT_OR"),
                    }
                },
                71 => { // BIT_XOR
                    let b = self.stack.pop().expect("Stack underflow");
                    let a = self.stack.pop().expect("Stack underflow");
                    match (a, b) {
                        (Constant::Integer(ia), Constant::Integer(ib)) => self.stack.push(Constant::Integer(ia ^ ib)),
                         _ => panic!("Type mismatch for BIT_XOR"),
                    }
                },
                72 => { // BIT_NOT
                    let a = self.stack.pop().expect("Stack underflow");
                    match a {
                        Constant::Integer(ia) => self.stack.push(Constant::Integer(!ia)),
                         _ => panic!("Type mismatch for BIT_NOT"),
                    }
                },
                73 => { // LSHIFT
                    let b = self.stack.pop().expect("Stack underflow");
                    let a = self.stack.pop().expect("Stack underflow");
                    match (a, b) {
                        (Constant::Integer(ia), Constant::Integer(ib)) => self.stack.push(Constant::Integer(ia << ib)),
                         _ => panic!("Type mismatch for LSHIFT"),
                    }
                },
                74 => { // RSHIFT
                    let b = self.stack.pop().expect("Stack underflow");
                    let a = self.stack.pop().expect("Stack underflow");
                    match (a, b) {
                        (Constant::Integer(ia), Constant::Integer(ib)) => self.stack.push(Constant::Integer(ia >> ib)),
                         _ => panic!("Type mismatch for RSHIFT"),
                    }
                },
                48 => { // RET
                    self.frames.pop();
                },
                47 => { // CALL
                     let arg_count = if let Constant::Integer(c) = arg {
                         c as usize
                     } else {
                         panic!("CALL argument count must be Integer");
                     };

                     let mut args = Vec::new();
                     for _ in 0..arg_count {
                         args.push(self.stack.pop().expect("Stack underflow on CALL args"));
                     }
                     args.reverse();

                     let func = self.stack.pop().expect("Stack underflow on CALL func");
                     if let Constant::Code(co) = func {
                         if args.len() != co.args.len() {
                             panic!("Argument mismatch: expected {}, got {}", co.args.len(), args.len());
                         }

                         let mut locals = std::collections::HashMap::new();
                         for (name, val) in co.args.iter().zip(args.into_iter()) {
                             locals.insert(name.clone(), val);
                         }

                         let frame = CallFrame {
                             code: co.clone(),
                             pc: 0,
                             locals,
                         };
                         self.frames.push(frame);
                     } else {
                         panic!("CALL target must be CodeObject");
                     }
                },
                68 => { // MAKE_FUNCTION
                    let _name = self.stack.pop();
                    // CodeObject remains on stack
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
                Some(Constant::Code(Rc::new(co)))
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
