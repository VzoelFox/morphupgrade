# tests/compiler/unit/test_codegen_literals.py

import pytest
from llvmlite import ir
from compiler.codegen_llvm import LLVMCodeGenerator
from morph_engine.node_ast import NodeAngka
from morph_engine.token_morph import Token, TipeToken

def test_visit_node_angka_integer():
    """Tes visitor untuk NodeAngka dengan nilai integer."""
    codegen = LLVMCodeGenerator()
    node = NodeAngka(Token(TipeToken.ANGKA, 123))

    # Setup builder dummy
    func_type = ir.FunctionType(ir.VoidType(), [])
    func = ir.Function(codegen.module, func_type, name="test_func")
    block = func.append_basic_block("entry")
    codegen.builder = ir.IRBuilder(block)

    result = codegen.visit_NodeAngka(node)

    assert isinstance(result, ir.Constant)
    assert result.type == ir.IntType(32)
    assert result.constant == 123

def test_visit_node_angka_float():
    """Tes visitor untuk NodeAngka dengan nilai float."""
    codegen = LLVMCodeGenerator()
    node = NodeAngka(Token(TipeToken.ANGKA, 45.6))

    # Setup builder dummy
    func_type = ir.FunctionType(ir.VoidType(), [])
    func = ir.Function(codegen.module, func_type, name="test_func")
    block = func.append_basic_block("entry")
    codegen.builder = ir.IRBuilder(block)

    result = codegen.visit_NodeAngka(node)

    assert isinstance(result, ir.Constant)
    assert result.type == ir.DoubleType()
    assert result.constant == 45.6
