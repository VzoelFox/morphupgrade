# tests/compiler/unit/test_codegen_literals.py

import pytest
from llvmlite import ir
from compiler.codegen_llvm import LLVMCodeGenerator
from morph_engine.node_ast import NodeKonstanta
from morph_engine.token_morph import Token, TipeToken

def test_visit_node_konstanta_integer():
    """Tes visitor untuk NodeKonstanta dengan nilai integer."""
    codegen = LLVMCodeGenerator()
    token = Token(TipeToken.ANGKA, 123)
    node = NodeKonstanta(token, token.nilai)

    # Setup builder dummy
    func_type = ir.FunctionType(ir.VoidType(), [])
    func = ir.Function(codegen.module, func_type, name="test_func")
    block = func.append_basic_block("entry")
    codegen.builder = ir.IRBuilder(block)

    result = codegen.visit_NodeKonstanta(node)

    assert isinstance(result, ir.Constant)
    assert result.type == ir.IntType(32)
    assert result.constant == 123

def test_visit_node_konstanta_float():
    """Tes visitor untuk NodeKonstanta dengan nilai float."""
    codegen = LLVMCodeGenerator()
    token = Token(TipeToken.ANGKA, 45.6)
    node = NodeKonstanta(token, token.nilai)

    # Setup builder dummy
    func_type = ir.FunctionType(ir.VoidType(), [])
    func = ir.Function(codegen.module, func_type, name="test_func")
    block = func.append_basic_block("entry")
    codegen.builder = ir.IRBuilder(block)

    result = codegen.visit_NodeKonstanta(node)

    assert isinstance(result, ir.Constant)
    assert result.type == ir.DoubleType()
    assert result.constant == 45.6
