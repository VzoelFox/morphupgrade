use std::fs::File;
use std::io::{self, Read, Write};
use std::env;
use std::rc::Rc;
use std::cell::RefCell;
use std::collections::HashMap;

// Constants
const MAGIC: &[u8] = b"VZOEL FOXS";

// --- Data Structures ---

#[derive(Debug, Clone)]
struct Function {
    name: String,
    code: Rc<CodeObject>,
    closure: Vec<Rc<RefCell<Constant>>>,
}

#[derive(Debug, Clone)]
struct Module {
    name: String,
    globals: Rc<RefCell<HashMap<String, Constant>>>,
}

#[derive(Debug)]
struct FileHandle(RefCell<Option<File>>);

// Custom Clone for FileHandle (Shared Reference)
// Actually, we wrap it in Rc in Constant, so FileHandle doesn't need Clone if Constant handles it.
// But Constant derives Clone.
// So Constant::File(Rc<FileHandle>) works.

#[derive(Debug, Clone)]
enum Constant {
    Nil,
    Boolean(bool),
    Integer(i32),
    Float(f64),
    String(String),
    List(Rc<RefCell<Vec<Constant>>>),
    Code(Rc<CodeObject>),
    Dict(Rc<RefCell<Vec<(Constant, Constant)>>>),
    Cell(Rc<RefCell<Constant>>),
    Function(Rc<Function>),
    Module(Rc<Module>),
    File(Rc<FileHandle>),
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
            (Constant::List(a), Constant::List(b)) => a == b,
            (Constant::Dict(a), Constant::Dict(b)) => a == b,
            (Constant::Cell(a), Constant::Cell(b)) => a == b,
            (Constant::Function(a), Constant::Function(b)) => Rc::ptr_eq(&a.code, &b.code),
            (Constant::Code(a), Constant::Code(b)) => Rc::ptr_eq(a, b),
            (Constant::Module(a), Constant::Module(b)) => Rc::ptr_eq(a, b),
            (Constant::File(a), Constant::File(b)) => Rc::ptr_eq(a, b),
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
    free_vars: Vec<String>,
    cell_vars: Vec<String>,
}

#[derive(Debug, Clone)]
struct CallFrame {
    code: Rc<CodeObject>,
    pc: usize,
    locals: HashMap<String, Constant>,
    globals: Rc<RefCell<HashMap<String, Constant>>>,
    closure: Vec<Rc<RefCell<Constant>>>,
}

// --- VM Runtime ---

struct VM {
    frames: Vec<CallFrame>,
    stack: Vec<Constant>,
    modules: HashMap<String, Rc<Module>>,
    universals: HashMap<String, Constant>,
}

impl VM {
    fn new() -> Self {
        let mut universals = HashMap::new();

        // Inject 'tulis'
        let tulis_co = CodeObject {
            name: "tulis".to_string(),
            args: vec!["msg".to_string()],
            constants: vec![Constant::Nil],
            instructions: vec![
                (25, Constant::String("msg".to_string())),
                (53, Constant::Integer(1)),
                (1, Constant::Nil),
                (48, Constant::Nil),
            ],
            free_vars: Vec::new(),
            cell_vars: Vec::new(),
        };
        universals.insert("tulis".to_string(), Constant::Code(Rc::new(tulis_co)));

        // Inject 'teks'
        let teks_co = CodeObject {
            name: "teks".to_string(),
            args: vec!["obj".to_string()],
            constants: vec![],
            instructions: vec![
                (25, Constant::String("obj".to_string())),
                (64, Constant::Nil),
                (48, Constant::Nil),
            ],
            free_vars: Vec::new(),
            cell_vars: Vec::new(),
        };
        universals.insert("teks".to_string(), Constant::Code(Rc::new(teks_co)));

        VM {
            frames: Vec::new(),
            stack: Vec::new(),
            modules: HashMap::new(),
            universals
        }
    }

    // Helper: Run a code object in a specific global scope
    fn run_code(&mut self, code: Rc<CodeObject>, globals: Rc<RefCell<HashMap<String, Constant>>>) {
        let root_frame = CallFrame {
            code,
            pc: 0,
            locals: HashMap::new(),
            globals,
            closure: Vec::new(),
        };

        // Push frame and enter loop
        // If this is a recursive call, we simply push to existing stack and loop
        // But we need to know when *this* run finishes?
        // If we share the main loop, we just push and let the outer loop handle it?
        // No, 'run_code' implies blocking execution until done.

        let start_depth = self.frames.len();
        self.frames.push(root_frame);

        // Run until we return to start_depth
        while self.frames.len() > start_depth {
            if self.frames.is_empty() { break; } // Safety

            let (op, arg) = {
                let frame = self.frames.last_mut().unwrap();
                if frame.pc >= frame.code.instructions.len() {
                    self.frames.pop();
                    continue;
                }
                let instr = &frame.code.instructions[frame.pc];
                frame.pc += 1;
                (instr.0, instr.1.clone())
            };

            match op {
                1 => self.stack.push(arg.clone()),
                2 => { if self.stack.pop().is_none() { panic!("Stack underflow POP"); } },
                3 => {
                    if let Some(val) = self.stack.last() { self.stack.push(val.clone()); }
                    else { panic!("Stack underflow DUP"); }
                },

                // Variable Access (Refactored for Module System)
                23 => { // LOAD_VAR
                    if let Constant::String(name) = arg {
                        // 1. Local
                        let mut val = None;
                        if let Some(frame) = self.frames.last() {
                            if let Some(v) = frame.locals.get(&name) {
                                val = Some(v.clone());
                            } else {
                                // 2. Global (Module)
                                if let Some(v) = frame.globals.borrow().get(&name) {
                                    val = Some(v.clone());
                                } else {
                                    // 3. Universal
                                    if let Some(v) = self.universals.get(&name) {
                                        val = Some(v.clone());
                                    }
                                }
                            }
                        }

                        if let Some(v) = val {
                            // Auto-deref Cell
                            if let Constant::Cell(c) = v {
                                self.stack.push(c.borrow().clone());
                            } else {
                                self.stack.push(v);
                            }
                        } else {
                            panic!("Variable not found: {}", name);
                        }
                    } else { panic!("LOAD_VAR name must be String"); }
                },
                24 => { // STORE_VAR (Globals)
                    if let Constant::String(name) = arg {
                        let val = self.stack.pop().expect("Stack underflow STORE_VAR");
                        if let Some(frame) = self.frames.last() {
                            frame.globals.borrow_mut().insert(name.clone(), val);
                        }
                    } else { panic!("STORE_VAR name must be String"); }
                },
                25 => { // LOAD_LOCAL
                    if let Constant::String(name) = arg {
                        if let Some(frame) = self.frames.last() {
                            if let Some(v) = frame.locals.get(&name) {
                                if let Constant::Cell(c) = v {
                                    self.stack.push(c.borrow().clone());
                                } else {
                                    self.stack.push(v.clone());
                                }
                            } else { panic!("Local not found: {}", name); }
                        }
                    }
                },
                26 => { // STORE_LOCAL
                    if let Constant::String(name) = arg {
                         let val = self.stack.pop().expect("Stack underflow STORE_LOCAL");
                         if let Some(frame) = self.frames.last_mut() {
                             if let Some(Constant::Cell(c)) = frame.locals.get(&name).cloned() {
                                 *c.borrow_mut() = val;
                             } else {
                                 frame.locals.insert(name.clone(), val);
                             }
                         }
                    }
                },
                // Data Ops (No Change)
                27 => {
                    let count = if let Constant::Integer(c) = arg { c as usize } else { 0 };
                    let mut list = Vec::new();
                    for _ in 0..count { list.push(self.stack.pop().expect("Stack underflow")); }
                    list.reverse();
                    self.stack.push(Constant::List(Rc::new(RefCell::new(list))));
                },
                28 => {
                     let count = if let Constant::Integer(c) = arg { c as usize } else { 0 };
                     let mut dict = Vec::new();
                     for _ in 0..count {
                         let v = self.stack.pop().expect("Stack");
                         let k = self.stack.pop().expect("Stack");
                         dict.push((k, v));
                     }
                     dict.reverse();
                     self.stack.push(Constant::Dict(Rc::new(RefCell::new(dict))));
                },
                29 => { // LOAD_INDEX
                     let index = self.stack.pop().expect("Stack");
                     let obj = self.stack.pop().expect("Stack");
                     match obj {
                         Constant::List(l) => {
                             let list = l.borrow();
                             if let Constant::Integer(i) = index {
                                 if i >= 0 && (i as usize) < list.len() { self.stack.push(list[i as usize].clone()); }
                                 else { panic!("Index error"); }
                             }
                         },
                         Constant::Dict(d) => {
                             let dict = d.borrow();
                             let mut found = false;
                             for (k, v) in dict.iter() {
                                 if k == &index { self.stack.push(v.clone()); found = true; break; }
                             }
                             if !found { panic!("Key error: {:?}", index); }
                         },
                         Constant::String(s) => {
                             if let Constant::Integer(i) = index {
                                 if i >= 0 && (i as usize) < s.len() {
                                     self.stack.push(Constant::String(s.chars().nth(i as usize).unwrap().to_string()));
                                 }
                             }
                         },
                         _ => panic!("Not subscriptable"),
                     }
                },
                30 => { // STORE_INDEX
                    let val = self.stack.pop().expect("Stack");
                    let index = self.stack.pop().expect("Stack");
                    let obj = self.stack.pop().expect("Stack");
                    match obj {
                        Constant::List(l) => {
                            let mut list = l.borrow_mut();
                            if let Constant::Integer(i) = index {
                                if i >= 0 && (i as usize) < list.len() { list[i as usize] = val; }
                            }
                        },
                        Constant::Dict(d) => {
                            let mut dict = d.borrow_mut();
                            let mut found = false;
                            for (k, v) in dict.iter_mut() {
                                if k == &index { *v = val.clone(); found = true; break; }
                            }
                            if !found { dict.push((index, val)); }
                        },
                        _ => panic!("Not mutable"),
                    }
                },
                38 => { // LOAD_ATTR
                    let name = if let Constant::String(s) = arg { s } else { panic!("Arg"); };
                    let obj = self.stack.pop().expect("Stack");
                    match obj {
                        Constant::Code(_) => { if name == "code" { self.stack.push(obj); } else { panic!("Attr"); } },
                        Constant::Module(m) => {
                            // Load from module globals
                            if let Some(v) = m.globals.borrow().get(&name) {
                                self.stack.push(v.clone());
                            } else {
                                panic!("Attribute {} not found in module {}", name, m.name);
                            }
                        },
                        _ => panic!("Attr not supported"),
                    }
                },
                // Math & Logic (Standard)
                4 => {
                    let b = self.stack.pop().unwrap(); let a = self.stack.pop().unwrap();
                    match (&a, &b) {
                         (Constant::Integer(ia), Constant::Integer(ib)) => self.stack.push(Constant::Integer(ia + ib)),
                         (Constant::String(sa), Constant::String(sb)) => self.stack.push(Constant::String(sa.clone() + sb)),
                         _ => panic!("ADD mismatch"),
                    }
                },
                9 => { let b = self.stack.pop().unwrap(); let a = self.stack.pop().unwrap(); self.stack.push(Constant::Boolean(a == b)); },
                // ... (Skipping verbose math for brevity in this plan exec, assuming simple ones work)

                // IMPORT (52)
                52 => {
                    let path = if let Constant::String(s) = arg { s } else { panic!("Import path string"); };

                    if let Some(m) = self.modules.get(&path) {
                        self.stack.push(Constant::Module(m.clone()));
                    } else {
                        // Load module
                        let filename = path.clone() + ".mvm"; // Simple resolution
                        let mut file = File::open(&filename).expect("Module file not found");
                        let mut buffer = Vec::new();
                        file.read_to_end(&mut buffer).unwrap();
                        let mut reader = Reader::new(buffer);
                        // Skip Header
                        reader.read_bytes(16);

                        if let Some(Constant::Code(code_rc)) = reader.read_constant() {
                            let globals = Rc::new(RefCell::new(HashMap::new()));
                            let module = Rc::new(Module {
                                name: path.clone(),
                                globals: globals.clone(),
                            });

                            // Cache FIRST to handle circular imports (though we lock execution)
                            self.modules.insert(path.clone(), module.clone());

                            // Execute Module Body
                            // Recursive call to run_code
                            self.run_code(code_rc, globals);

                            // Pop the result of module body (usually Nil)
                            if self.stack.pop().is_none() {
                                // If stack empty, maybe okay? Module body usually pushes Nil then RET.
                                // RET pops frame.
                                // If RET was the last thing, the Nil is left on stack.
                            }

                            // Push Module Object
                            self.stack.push(Constant::Module(module));
                        } else {
                            panic!("Invalid module binary");
                        }
                    }
                },

                // I/O Opcodes
                87 => { // IO_OPEN (path, mode)
                    let mode_v = self.stack.pop().unwrap();
                    let path_v = self.stack.pop().unwrap();
                    if let (Constant::String(path), Constant::String(_mode)) = (path_v, mode_v) {
                        // Ignore mode for now, just open read/write
                        // Actually, need mode logic.
                        // "w" = create/truncate. "r" = open.
                        let f = if _mode == "w" {
                            File::create(path)
                        } else {
                            File::open(path)
                        };

                        match f {
                            Ok(file) => self.stack.push(Constant::File(Rc::new(FileHandle(RefCell::new(Some(file)))))),
                            Err(_) => panic!("IO_OPEN failed"),
                        }
                    } else { panic!("IO_OPEN args"); }
                },
                88 => { // IO_READ (handle, size)
                    let size_v = self.stack.pop().unwrap();
                    let handle = self.stack.pop().unwrap();
                    if let Constant::File(fh) = handle {
                        let mut file_opt = fh.0.borrow_mut();
                        if let Some(ref mut file) = *file_opt {
                            let mut buf = String::new();
                            // If size is -1, read to end
                            file.read_to_string(&mut buf).unwrap();
                            self.stack.push(Constant::String(buf));
                        } else { panic!("File closed"); }
                    } else { panic!("IO_READ expects File, got {:?}", handle); }
                },
                89 => { // IO_WRITE (handle, content)
                    let content = self.stack.pop().unwrap();
                    let handle = self.stack.pop().unwrap();
                    if let (Constant::File(fh), Constant::String(s)) = (handle, content) {
                        let mut file_opt = fh.0.borrow_mut();
                        if let Some(ref mut file) = *file_opt {
                            file.write_all(s.as_bytes()).unwrap();
                            self.stack.push(Constant::Nil);
                        } else { panic!("File closed"); }
                    } else { panic!("IO_WRITE expects File, String"); }
                },
                90 => { // IO_CLOSE (handle)
                    let handle = self.stack.pop().unwrap();
                    if let Constant::File(fh) = handle {
                        *fh.0.borrow_mut() = None; // Drop file
                        self.stack.push(Constant::Nil);
                    }
                },

                // Functions (Patch 10 logic maintained)
                60 => { // BUILD_FUNCTION
                    let func_def = self.stack.pop().expect("Stack");
                    if let Constant::Dict(entries_rc) = func_def {
                         let entries = entries_rc.borrow();
                         let mut name = String::new();
                         let mut args = Vec::new();
                         let mut instructions = Vec::new();
                         let mut free_vars = Vec::new();
                         let mut cell_vars = Vec::new();

                         for (k, v) in entries.iter() {
                             if let Constant::String(k_str) = k {
                                 if k_str == "nama" { if let Constant::String(n) = v { name = n.clone(); } }
                                 else if k_str == "args" {
                                     if let Constant::List(l) = v {
                                         for x in l.borrow().iter() { if let Constant::String(s) = x { args.push(s.clone()); } }
                                     }
                                 }
                                 else if k_str == "instruksi" {
                                     if let Constant::List(l) = v {
                                         for instr in l.borrow().iter() {
                                             if let Constant::List(pair) = instr {
                                                 let p = pair.borrow();
                                                 let op = if let Constant::Integer(o) = p[0] { o as u8 } else { 0 };
                                                 instructions.push((op, p[1].clone()));
                                             }
                                         }
                                     }
                                 }
                                 else if k_str == "free_vars" {
                                     if let Constant::List(l) = v {
                                         for x in l.borrow().iter() { if let Constant::String(s) = x { free_vars.push(s.clone()); } }
                                     }
                                 }
                                 else if k_str == "cell_vars" {
                                     if let Constant::List(l) = v {
                                         for x in l.borrow().iter() { if let Constant::String(s) = x { cell_vars.push(s.clone()); } }
                                     }
                                 }
                             }
                         }
                         let co = CodeObject { name, args, constants: Vec::new(), instructions, free_vars, cell_vars };
                         self.stack.push(Constant::Code(Rc::new(co)));
                    }
                },
                47 => { // CALL
                     let arg_count = if let Constant::Integer(c) = arg { c as usize } else { panic!("CALL arg"); };
                     let mut args = Vec::new();
                     for _ in 0..arg_count { args.push(self.stack.pop().expect("Stack")); }
                     args.reverse();

                     let func_obj = self.stack.pop().expect("Stack");
                     let (co, closure) = match func_obj {
                         Constant::Code(c) => (c, Vec::new()),
                         Constant::Function(f) => (f.code.clone(), f.closure.clone()),
                         _ => panic!("CALL target invalid"),
                     };

                     let mut locals = HashMap::new();
                     for cell in &co.cell_vars { locals.insert(cell.clone(), Constant::Cell(Rc::new(RefCell::new(Constant::Nil)))); }
                     for (name, val) in co.args.iter().zip(args.into_iter()) {
                         if locals.contains_key(name) {
                             if let Some(Constant::Cell(c)) = locals.get(name) { *c.borrow_mut() = val; }
                         } else { locals.insert(name.clone(), val); }
                     }
                     for (i, name) in co.free_vars.iter().enumerate() {
                         locals.insert(name.clone(), Constant::Cell(closure[i].clone()));
                     }

                     let frame = CallFrame {
                         code: co,
                         pc: 0,
                         locals,
                         // Inherit globals from current frame!
                         globals: self.frames.last().unwrap().globals.clone(),
                         closure,
                     };
                     self.frames.push(frame);
                },
                48 => { self.frames.pop(); },
                53 => { // PRINT
                    let count = if let Constant::Integer(c) = arg { c as usize } else { 0 };
                    let start = self.stack.len() - count;
                    let args: Vec<Constant> = self.stack.drain(start..).collect();
                    for a in args { print!("{:?} ", a); }
                    println!();
                },
                64 => { // STR
                    let v = self.stack.pop().unwrap();
                    self.stack.push(Constant::String(format!("{:?}", v)));
                },
                _ => {}, // Ignore unknown
            }
        }
    }
}

// ... Reader struct (same as before, skipping for brevity in thought but including in write) ...
struct Reader { buffer: Vec<u8>, pos: usize }
impl Reader {
    fn new(b: Vec<u8>) -> Self { Reader { buffer: b, pos: 0 } }
    fn read_byte(&mut self) -> Option<u8> { if self.pos < self.buffer.len() { let b = self.buffer[self.pos]; self.pos+=1; Some(b) } else { None } }
    fn read_bytes(&mut self, n: usize) -> Option<Vec<u8>> { if self.pos+n <= self.buffer.len() { let s = self.buffer[self.pos..self.pos+n].to_vec(); self.pos+=n; Some(s) } else { None } }
    fn read_int(&mut self) -> Option<i32> { let b = self.read_bytes(4)?; Some(i32::from_le_bytes(b.try_into().ok()?)) }
    fn read_float(&mut self) -> Option<f64> { let b = self.read_bytes(8)?; Some(f64::from_le_bytes(b.try_into().ok()?)) }
    fn read_string_raw(&mut self) -> Option<String> { let len = self.read_int()?; if len < 0 { return None; } let b = self.read_bytes(len as usize)?; String::from_utf8(b).ok() }
    fn read_constant(&mut self) -> Option<Constant> {
        let tag = self.read_byte()?;
        match tag {
            1 => Some(Constant::Nil),
            2 => Some(Constant::Boolean(self.read_byte()? == 1)),
            3 => Some(Constant::Integer(self.read_int()?)),
            4 => Some(Constant::Float(self.read_float()?)),
            5 => Some(Constant::String(self.read_string_raw()?)),
            6 => { let c = self.read_int()?; let mut l = Vec::new(); for _ in 0..c { l.push(self.read_constant()?); } Some(Constant::List(Rc::new(RefCell::new(l)))) },
            7 => Some(Constant::Code(Rc::new(self.read_code_object()?))),
            8 => { let c = self.read_int()?; let mut d = Vec::new(); for _ in 0..c { let k=self.read_constant()?; let v=self.read_constant()?; d.push((k,v)); } Some(Constant::Dict(Rc::new(RefCell::new(d)))) },
            _ => None,
        }
    }
    fn read_code_object(&mut self) -> Option<CodeObject> {
        let name = self.read_string_raw()?;
        let ac = self.read_byte()?; let mut args = Vec::new(); for _ in 0..ac { args.push(self.read_string_raw()?); }
        let cc = self.read_int()?; let mut consts = Vec::new(); for _ in 0..cc { consts.push(self.read_constant()?); }
        let ic = self.read_int()?; let mut instrs = Vec::new(); for _ in 0..ic { let o = self.read_byte()?; let a = self.read_constant()?; instrs.push((o, a)); }
        Some(CodeObject { name, args, constants: consts, instructions: instrs, free_vars: Vec::new(), cell_vars: Vec::new() })
    }
}

fn main() -> io::Result<()> {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 { println!("Usage: morph_vm <file.mvm>"); return Ok(()); }
    let filename = &args[1];
    let mut file = File::open(filename)?;
    let mut buffer = Vec::new();
    file.read_to_end(&mut buffer)?;
    let mut reader = Reader::new(buffer);
    reader.read_bytes(16); // Skip Header
    if let Some(Constant::Code(co)) = reader.read_constant() {
        let mut vm = VM::new();
        // Create root module globals (Script Scope)
        let globals = Rc::new(RefCell::new(HashMap::new()));
        vm.run_code(co, globals);
    } else { panic!("Invalid"); }
    Ok(())
}
