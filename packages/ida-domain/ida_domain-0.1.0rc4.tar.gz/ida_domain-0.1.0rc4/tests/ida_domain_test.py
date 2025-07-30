import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

import ida_domain  # isort: skip
import ida_idaapi  # isort: skip

idb_path: str = ''


# Global setup (runs ONCE)
@pytest.fixture(scope='module', autouse=True)
def global_setup():
    print(f'\nAPI Version: {ida_domain.__version__}')

    os.environ['IDA_NO_HISTORY'] = '1'

    """ Runs once per module: Creates temp directory and writes test binary. """
    global idb_path
    # Create a temporary folder and use it as tests working directory
    idb_path = os.path.join(tempfile.gettempdir(), 'api_tests_work_dir')
    shutil.rmtree(idb_path, ignore_errors=True)
    os.makedirs(idb_path, exist_ok=True)
    idb_path = os.path.join(tempfile.gettempdir(), 'api_tests_work_dir', 'test.bin')

    # Copy the test binary from resources folder under our tests working directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    src_path = os.path.join(current_dir, 'resources', 'test.bin')
    shutil.copy(src_path, idb_path)


# Per-test fixture (runs for each test)
@pytest.fixture(scope='function')
def test_env():
    """Runs for each test: Opens and closes the database."""
    db = ida_domain.Database()
    ida_options = ida_domain.Database.IdaCommandBuilder().new_database(True)
    assert db.open(db_path=idb_path, db_args=ida_options, save_on_close=False)
    yield db
    if db.is_open():
        db.close(False)


def test_database(test_env):
    db = test_env
    db.close(False)
    assert db.is_open() is False
    assert db.open(idb_path) is True
    assert db.is_open() is True

    db.current_ea = 0x50
    assert db.current_ea == 0x50

    assert db.minimum_ea == 0x0
    assert db.maximum_ea == 0x420

    assert db.base_address == 0x0
    assert db.module == 'test.bin'
    assert db.filesize == 3680
    assert db.md5 == 'f53ff12139b2cf71703222e79cfe0b9b'
    assert db.sha256 == '03858ca230c1755b1db18c4051c348de5b4b274ff0489ea14237f56a9f9adf30'
    assert db.crc32 == 404194086
    assert db.architecture == 'metapc'
    assert db.bitness == 64
    assert db.format == 'ELF64 for x86-64 (Relocatable)'

    metadata = db.metadata
    assert len(metadata) == 11

    assert 'test.bin' in metadata['path']
    assert metadata['module'] == 'test.bin'
    assert metadata['base_address'] == '0x0'
    assert metadata['filesize'] == '0xe60'
    assert metadata['md5'] == 'f53ff12139b2cf71703222e79cfe0b9b'
    assert metadata['sha256'] == '03858ca230c1755b1db18c4051c348de5b4b274ff0489ea14237f56a9f9adf30'
    assert metadata['crc32'] == '0x18178326'
    assert metadata['architecture'] == 'metapc'
    assert metadata['bitness'] == '0x40'
    assert metadata['format'] == 'ELF64 for x86-64 (Relocatable)'
    assert 'load_time' in metadata
    assert isinstance(metadata['load_time'], str)
    assert len(metadata['load_time']) == 19  # dummy check, expect "YYYY-MM-DD HH:MM:SS"
    db.close(False)

    # Test context manager protocol
    with ida_domain.Database() as db2:
        assert not db2.is_open()
        assert db2.open(idb_path, save_on_close=False)
        assert db2.is_open()
        func = db2.functions.get_at(0x2A3)
        assert func is not None
        assert func.start_ea == 0x2A3
        assert db2.functions.set_name(func, 'testing_function_rename')
        assert func.name == 'testing_function_rename'
    # The database should be close automatically
    assert not db2.is_open()
    # Reopen it and check the rename was discarded due to save_on_close=False
    assert db2.open(idb_path, save_on_close=False)
    assert db2.is_open()
    func = db2.functions.get_at(0x2A3)
    assert func is not None
    assert func.start_ea == 0x2A3
    assert func.name == 'add_numbers'
    db2.close(False)

    with ida_domain.Database() as db3:
        assert not db3.is_open()
        assert db3.open(idb_path, save_on_close=True)
        assert db3.is_open()
        func = db3.functions.get_at(0x2A3)
        assert func is not None
        assert func.start_ea == 0x2A3
        assert db3.functions.set_name(func, 'testing_function_rename')
        assert func.name == 'testing_function_rename'

    # The database should be close automatically
    assert not db3.is_open()
    # Reopen it and check the rename was preserved due to save_on_close=True
    assert db3.open(idb_path, save_on_close=False)
    assert db3.is_open()
    func = db3.functions.get_at(0x2A3)
    assert func is not None
    assert func.start_ea == 0x2A3
    assert func.name == 'testing_function_rename'
    db3.close(False)


def test_segment(test_env):
    db = test_env
    all_segments = db.segments.get_all()
    seg = next(all_segments)
    assert seg is not None
    assert db.segments.get_name(seg) == '.text'
    assert seg.start_ea == 0
    assert db.segments.set_name(seg, 'testing_segment_rename')
    assert db.segments.get_name(seg) == 'testing_segment_rename'

    seg = next(all_segments)
    assert seg is not None
    assert db.segments.get_name(seg) == '.data'
    assert seg.start_ea == 0x330


def test_function(test_env):
    db = test_env

    all_functions = db.functions.get_all()
    func = next(all_functions)
    assert func is not None
    assert func.name == 'test_all_operand_types'

    func = next(all_functions)
    assert func is not None
    assert func.name == 'add_numbers'
    assert func.start_ea == 0x2A3

    func = db.functions.get_at(0x2A3)
    assert func is not None
    assert func.start_ea == 0x2A3
    assert db.functions.set_name(func, 'testing_function_rename')
    assert func.name == 'testing_function_rename'
    assert db.functions.set_name(func, 'add_numbers')
    assert func.name == 'add_numbers'

    blocks = db.functions.get_basic_blocks(func)
    assert blocks.size == 1
    assert blocks[0].start_ea == 0x2A3
    assert blocks[0].end_ea == 0x2AF

    disassembly_lines = db.functions.get_disassembly(func)
    assert len(disassembly_lines) == 6

    pseudocode_lines = db.functions.get_pseudocode(func)
    assert len(pseudocode_lines) == 4

    microcode_lines = db.functions.get_microcode(func)
    assert len(microcode_lines) == 13
    assert microcode_lines[11] == '1.11 mov    cs.2, seg.2             ; 2AE u=cs.2       d=seg.2'

    # Validate expected instructions and their addresses
    expected_instructions = [
        (0x2A3, 'push    rbp'),
        (0x2A4, 'mov     rbp, rsp'),
        (0x2A7, 'mov     rax, rdi'),
        (0x2AA, 'add     rax, rsi'),
        (0x2AD, 'pop     rbp'),
        (0x2AE, 'retn'),
        (ida_idaapi.BADADDR, ''),
    ]

    instructions = db.functions.get_instructions(func)
    for i, instruction in enumerate(instructions):
        assert expected_instructions[i][0] == instruction.ea
        assert expected_instructions[i][1] == db.instructions.get_disassembly(instruction)

    func = db.functions.get_at(0x2A3)
    assert func is not None

    # Validate function signature
    expected_signature = '__int64 __fastcall(__int64, __int64)'
    assert db.functions.get_signature(func) == expected_signature

    # Check signature match
    assert db.functions.matches_signature(func, expected_signature)
    assert not db.functions.matches_signature(func, 'void __fastcall()')

    # Remove and re-create function
    assert db.functions.remove(0x2A3)
    assert db.functions.get_at(0x2A3) is None

    assert db.functions.create(0x2A3)
    assert db.functions.get_at(0x2A3) is not None

    func = db.functions.get_at(0x2A3)
    assert func is not None
    assert func.name == 'add_numbers'

    func = db.functions.get_at(0x311)
    assert func is not None
    assert func.name == 'level2_func_a'

    callers = db.functions.get_callers(func)
    assert len(callers) == 1
    assert callers[0].name == 'level1_func'

    callees = db.functions.get_callees(func)
    assert len(callees) == 1
    assert callees[0].name == 'level3_func'

    func = db.functions.get_at(0x2F7)
    assert func.name == 'level1_func'

    callers = db.functions.get_callers(func)
    assert len(callers) == 0

    callees = db.functions.get_callees(func)
    assert len(callees) == 2
    assert callees[0].name == 'level2_func_a'
    assert callees[1].name == 'level2_func_b'

    func = db.functions.get_at(0x307)
    assert func.name == 'level2_func_a'

    callers = db.functions.get_callers(func)
    assert len(callers) == 1
    assert callers[0].name == 'level1_func'

    callees = db.functions.get_callees(func)
    assert len(callees) == 1
    assert callees[0].name == 'level3_func'


def test_entries(test_env):
    db = test_env

    count = 0
    entries = db.entries.get_all()
    for _ in entries:
        count += 1
    assert count == 1

    assert db.entries.get_count() == 1
    assert db.entries.get_at_index(0) == ida_domain.entries.EntryInfo(0, 0, '_start', None)
    assert db.entries.get_by_ordinal(0) == ida_domain.entries.EntryInfo(0, 0, '_start', None)
    assert db.entries.get_by_address(0) == ida_domain.entries.EntryInfo(0, 0, '_start', None)

    assert db.entries.add(address=0xCC, name='test_entry', ordinal=1)
    assert db.entries.get_count() == 2
    assert db.entries.get_at_index(1) == ida_domain.entries.EntryInfo(1, 0xCC, 'test_entry', None)
    assert db.entries.get_by_ordinal(1) == ida_domain.entries.EntryInfo(
        1, 0xCC, 'test_entry', None
    )
    assert db.entries.get_by_address(0xCC) == ida_domain.entries.EntryInfo(
        1, 0xCC, 'test_entry', None
    )

    assert db.entries.rename(0, '_new_start')
    assert db.entries.get_at_index(0) == ida_domain.entries.EntryInfo(0, 0, '_new_start', None)

    assert db.entries.get_by_name('_new_start') == ida_domain.entries.EntryInfo(
        0, 0, '_new_start', None
    )


def test_heads(test_env):
    db = test_env

    count = 0
    heads = db.heads.get_all()
    for _ in heads:
        count += 1
    assert count == 201

    assert db.heads.get_prev(db.minimum_ea) is None
    assert db.heads.get_next(db.maximum_ea) is None

    expected = [0xC8, 0xC9, 0xCB, 0xCD, 0xCF, 0xD1, 0xD4]
    actual = []
    heads = db.heads.get_between(0xC6, 0xD6)
    for ea in heads:
        actual.append(ea)
    assert actual == expected

    assert db.heads.get_prev(0xCB) == 0xC9
    assert db.heads.get_next(0xC9) == 0xCB


def test_instruction(test_env):
    db = test_env

    count = 0
    for instruction in db.instructions.get_between(db.minimum_ea, db.maximum_ea):
        count += 1
    assert count == 197

    instruction = db.instructions.get_at(0xD6)
    assert instruction is not None
    assert db.instructions.is_valid(instruction)
    assert db.instructions.get_disassembly(instruction) == 'mov     ax, bx'
    assert db.instructions.get_operands_count(instruction) == 2

    operands = db.instructions.get_operands(instruction)
    assert len(operands) == 2
    assert isinstance(operands[0], ida_domain.operands.RegisterOperand)
    assert isinstance(operands[1], ida_domain.operands.RegisterOperand)

    operands = db.instructions.get_operands(instruction)
    assert len(operands) == 2
    assert isinstance(operands[0], ida_domain.operands.RegisterOperand)
    assert isinstance(operands[1], ida_domain.operands.RegisterOperand)

    instruction = db.instructions.get_prev(0xD6)
    assert instruction is not None
    assert instruction.ea == 0xD4
    assert db.instructions.is_valid(instruction)
    assert db.instructions.get_disassembly(instruction) == 'mov     eax, ebx'
    assert db.instructions.get_operands_count(instruction) == 2

    operands = db.instructions.get_operands(instruction)
    assert len(operands) == 2
    assert isinstance(operands[0], ida_domain.operands.RegisterOperand)
    assert isinstance(operands[1], ida_domain.operands.RegisterOperand)


def test_basic_block(test_env):
    db = test_env
    func = db.functions.get_at(0x29E)
    assert func is not None

    blocks = db.functions.get_basic_blocks(func)
    assert blocks.size == 4

    # Validate expected blocks
    expected_blocks = [(0xC4, 0x262), (0x262, 0x26B), (0x26B, 0x272), (0x272, 0x2A3)]

    for i, block in enumerate(blocks):
        assert expected_blocks[i][0] == block.start_ea, (
            f'Block start ea mismatch at index {i}, '
            f'{hex(expected_blocks[i][0])} != {hex(block.start_ea)}'
        )
        assert expected_blocks[i][1] == block.end_ea, (
            f'Block end ea mismatch at index {i}, '
            f'{hex(expected_blocks[i][1])} != {hex(block.end_ea)}'
        )

    # Validate expected instructions and their addresses
    expected_instructions = [
        (0x262, 'call    rax'),
        (0x264, 'call    qword ptr [rbx]'),
        (0x266, 'call    qword ptr [rbx+rcx*4]'),
        (0x269, 'jmp     rax'),
    ]

    instructions = db.basic_blocks.get_instructions(blocks[1])
    for i, instruction in enumerate(instructions):
        assert expected_instructions[i][0] == instruction.ea
        assert expected_instructions[i][1] == db.instructions.get_disassembly(instruction)


def test_operands(test_env):
    db = test_env

    # Test basic register operand - mov rax, rdi at 0x2A7
    instruction = db.instructions.get_at(0x2A7)
    operands = db.instructions.get_operands(instruction)

    # First operand should be rax (destination register)
    reg_op = operands[0]
    assert isinstance(reg_op, ida_domain.operands.RegisterOperand)
    assert reg_op.get_type_name() == 'register'
    assert reg_op.get_register_name() == 'rax'
    assert reg_op.register_number == 0  # rax register number
    assert reg_op.get_access_type() == 'write'
    assert reg_op.is_write() and not reg_op.is_read()

    # Test base operand info
    base_info = reg_op.get_info()
    assert base_info.number == 0
    assert base_info.type_name == 'register'
    assert base_info.access_type == 'write'
    assert base_info.is_write
    assert not base_info.is_read

    # Second operand should be rdi (source register)
    reg_op2 = operands[1]
    assert isinstance(reg_op2, ida_domain.operands.RegisterOperand)
    assert reg_op2.get_register_name() == 'rdi'
    assert reg_op2.get_access_type() == 'read'
    assert reg_op2.is_read() and not reg_op2.is_write()

    # Test immediate value - mov edi, 1 at 0x5
    instruction = db.instructions.get_at(0x5)
    operands = db.instructions.get_operands(instruction)

    imm_op = operands[1]  # Second operand should be immediate 1
    assert isinstance(imm_op, ida_domain.operands.ImmediateOperand)
    assert imm_op.get_type_name() == 'immediate'
    assert imm_op.get_value() == 1
    assert imm_op.get_hex_value() == '0x1'  # Small values stay decimal
    assert not imm_op.is_address()
    assert imm_op.get_name() is None  # Not an address

    # Test immediate info dataclass
    imm_info = imm_op.get_immediate_info()
    assert imm_info.value == 1
    assert imm_info.hex_value == '0x1'
    assert not imm_info.is_address
    assert imm_info.symbol_name is None

    # Test larger immediate value - mov rax, 1234567890ABCDEFh at 0xE2
    instruction = db.instructions.get_at(0xE2)
    operands = db.instructions.get_operands(instruction)

    large_imm_op = operands[1]
    assert isinstance(large_imm_op, ida_domain.operands.ImmediateOperand)
    large_value = large_imm_op.get_value()
    assert large_value == 0x1234567890ABCDEF
    hex_val = large_imm_op.get_hex_value()
    assert hex_val.startswith('0x')

    # Test Near Address Operands (calls/jumps)
    # Find a call instruction - call add_numbers at 0x27
    instruction = db.instructions.get_at(0x27)
    operands = db.instructions.get_operands(instruction)

    addr_op = operands[0]
    assert isinstance(addr_op, ida_domain.operands.ImmediateOperand)
    assert addr_op.get_type_name() == 'near_address'
    assert addr_op.is_address()
    symbol_name = addr_op.get_name()
    assert symbol_name == 'add_numbers'  # Should resolve to function name

    # Test address info
    addr_info = addr_op.get_immediate_info()
    assert addr_info.is_address
    assert addr_info.symbol_name == 'add_numbers'

    # Test direct memory access - mov rax, test_data at 0xFF
    instruction = db.instructions.get_at(0xFF)
    operands = db.instructions.get_operands(instruction)

    mem_op = operands[1]
    assert isinstance(mem_op, ida_domain.operands.MemoryOperand)
    assert mem_op.get_type_name() == 'direct_memory'
    assert mem_op.is_direct_memory()
    assert not mem_op.is_register_based()
    assert mem_op.get_sib_components() == (None, None, None, None)

    # Test memory address and symbol
    addr = mem_op.get_address()
    assert addr is not None
    symbol = mem_op.get_name()
    assert symbol == 'test_data'

    # Test addressing info dataclass
    addr_info = mem_op.get_addressing_info()
    assert addr_info.addressing_type == 'direct_memory'
    assert addr_info.is_direct_memory()
    assert addr_info.address == addr
    assert addr_info.symbol_name == 'test_data'

    # Test register indirect - mov rax, [rbx] at 0x125
    instruction = db.instructions.get_at(0x125)
    operands = db.instructions.get_operands(instruction)

    phrase_op = operands[1]
    assert isinstance(phrase_op, ida_domain.operands.MemoryOperand)
    assert phrase_op.get_type_name() == 'register_indirect'
    assert phrase_op.is_register_based()
    assert not phrase_op.is_direct_memory()
    assert phrase_op.get_sib_components() == ('rbx', None, None, None)

    # Test phrase number
    phrase_num = phrase_op.get_phrase_number()
    assert phrase_num is not None

    # Test formatted string
    formatted = phrase_op.get_formatted_string()
    assert '[rbx]' in formatted

    # Test addressing info
    addr_info = phrase_op.get_addressing_info()
    assert addr_info.addressing_type == 'register_indirect'
    assert addr_info.is_register_based()
    assert addr_info.phrase_number == phrase_num
    assert addr_info.formatted_string is not None

    # Test register+displacement - mov rax, [rbp+8] at 0x12D
    instruction = db.instructions.get_at(0x12D)
    operands = db.instructions.get_operands(instruction)

    disp_op = operands[1]
    assert isinstance(disp_op, ida_domain.operands.MemoryOperand)
    assert disp_op.get_type_name() == 'register_displacement'
    assert disp_op.is_register_based()
    assert disp_op.get_sib_components() == ('rbp', None, None, 8)

    # Test displacement value
    displacement = disp_op.get_displacement()
    assert displacement is not None
    assert displacement == 8  # [rbp+8]

    # Test outer displacement (should be None for simple displacement)
    outer_disp = disp_op.get_outer_displacement()
    assert outer_disp is None

    # Test has_outer_displacement flag
    assert not disp_op.has_outer_displacement()

    # Test addressing info
    addr_info = disp_op.get_addressing_info()
    assert addr_info.addressing_type == 'register_displacement'
    assert addr_info.displacement == 8
    assert not addr_info.has_outer_displacement
    assert addr_info.outer_displacement is None

    formatted = disp_op.get_formatted_string()
    assert '[rbp+' in formatted and '8' in formatted

    # Test complex displacement - mov rax, [rsi+rdi*2+8] at 0x162
    instruction = db.instructions.get_at(0x162)
    operands = db.instructions.get_operands(instruction)

    complex_disp_op = operands[1]
    assert isinstance(complex_disp_op, ida_domain.operands.MemoryOperand)
    assert complex_disp_op.get_type_name() == 'register_displacement'

    formatted = complex_disp_op.get_formatted_string()
    assert 'rsi' in formatted and 'rdi' in formatted and '*2' in formatted

    # Test Operand Value Method Consistency
    # Register operand value should be register number
    reg_val = reg_op.get_value()
    assert isinstance(reg_val, int)

    # Memory operand values vary by type
    mem_val = complex_disp_op.get_value()
    assert isinstance(mem_val, dict)  # Displacement operands return dict
    assert 'phrase' in mem_val and 'displacement' in mem_val

    # All operands should have meaningful string representations
    reg_str = str(reg_op)
    assert 'RegisterOperand' in reg_str
    assert 'Op0' in reg_str  # Operand number

    mem_str = str(mem_op)
    assert 'MemoryOperand' in mem_str
    assert complex_disp_op.get_sib_components() == ('rsi', 'rdi', 2, 8)


def test_strings(test_env):
    db = test_env

    assert db.strings.get_count() == 3

    expected_strings = [
        (0x3A0, 'Source string data'),
        (0x3D4, 'Hello, IDA!\n'),
        (0x3E1, 'Sum: Product: \n'),
    ]

    for i, (expected_addr, expected_string) in enumerate(expected_strings):
        stringsAndAddress = db.strings.get_at_index(i)
        assert stringsAndAddress[0] == expected_addr
        assert stringsAndAddress[1] == expected_string

    for i, (addr, string) in enumerate(db.strings.get_all()):
        assert addr == expected_strings[i][0], (
            f'String address mismatch at index {i}, {hex(addr)} != {hex(expected_strings[i][0])}'
        )
        assert string == expected_strings[i][1], (
            f'String mismatch at index {i}, {string} != {expected_strings[i][1]}'
        )

    from ida_domain.strings import StringType

    string_info = db.strings.get_at(0x3D4)
    assert string_info is not None
    assert string_info.address == 0x3D4
    assert string_info.content == 'Hello, IDA!\n'
    assert string_info.length == 13
    assert string_info.type == StringType.C

    string_info = db.strings.get_at(0x3E1)
    assert string_info is not None
    assert string_info.content == 'Sum: Product: \n'

    length = db.strings.get_length(0x3D4)
    assert isinstance(length, int) and length == 13

    str_type = db.strings.get_type(0x3D4)
    assert isinstance(str_type, int)
    assert str_type == StringType.C

    assert db.strings.exists_at(0x3D4) is True
    assert db.strings.exists_at(0x3E1) is True
    assert db.strings.exists_at(0x1000) is False

    strings_in_range = list(db.strings.get_between(0x3D0, 0x3F0))
    assert len(strings_in_range) >= 2  # Should include strings at 0x3D4 and 0x3E1

    found_addrs = [addr for addr, content in strings_in_range]
    assert 0x3D4 in found_addrs
    assert 0x3E1 in found_addrs

    original_count = db.strings.get_count()
    db.strings.build_string_list()  # Rebuild string list
    assert db.strings.get_count() == original_count  # Should be same count

    hello_strings = list(db.strings.find_strings_containing('Hello'))
    assert len(hello_strings) >= 1
    found_hello = False
    for addr, content in hello_strings:
        if 'Hello' in content:
            found_hello = True
            break
    assert found_hello

    hello_case_sensitive = list(db.strings.find_strings_containing('hello', case_sensitive=True))
    assert hello_case_sensitive == []

    hello_case_insensitive = list(
        db.strings.find_strings_containing('hello', case_sensitive=False)
    )
    assert hello_case_insensitive == [(980, 'Hello, IDA!\n')]

    i_case_sensitive = list(db.strings.find_strings_containing('I', case_sensitive=True))
    assert i_case_sensitive == [(980, 'Hello, IDA!\n')]

    i_case_insensitive = list(db.strings.find_strings_containing('I', case_sensitive=False))
    assert i_case_insensitive == [(928, 'Source string data'), (980, 'Hello, IDA!\n')]


def test_names(test_env):
    db = test_env

    assert db.names.get_count() == 28

    expected_names = [
        (0x0, '_start'),
        (0xC4, 'test_all_operand_types'),
        (0x272, 'skip_jumps'),
        (0x2A3, 'add_numbers'),
        (0x2AF, 'multiply_numbers'),
        (0x2BC, 'print_number'),
        (0x2D0, 'print_number.print_digit'),
        (0x2F7, 'level1_func'),
        (0x307, 'level2_func_a'),
        (0x312, 'level2_func_b'),
        (0x31D, 'level3_func'),
        (0x330, 'test_data'),
        (0x338, 'test_array'),
        (0x378, 'temp_float'),
        (0x37C, 'temp_double'),
        (0x390, 'vector_data'),
        (0x3A0, 'src_string'),
        (0x3B3, 'dst_string'),
        (0x3D4, 'hello'),
        (0x3E1, 'sum_str'),
        (0x3E6, 'product_str'),
        (0x3EF, 'newline'),
        (0x3F0, 'float_val'),
        (0x3F4, 'double_val'),
        (0x400, 'hello_len'),
        (0x408, 'sum_len'),
        (0x410, 'product_len'),
        (0x418, 'newline_len'),
    ]

    for i, (expected_addr, expected_name) in enumerate(expected_names):
        nameAndAddress = db.names.get_at_index(i)
        assert nameAndAddress[0] == expected_addr, (
            f'Name address mismatch at index {i}, {hex(nameAndAddress[0])} != {hex(expected_addr)}'
        )
        assert nameAndAddress[1] == expected_name, (
            f'Name mismatch at index {i}, {nameAndAddress[1]} != {expected_name}'
        )

    all_names = db.names.get_all()
    for i, (addr, name) in enumerate(all_names):
        assert addr == expected_names[i][0]
        assert name == expected_names[i][1]

    name = db.names.get_at(0x0)
    assert name == '_start'

    name = db.names.get_at(0x418)
    assert name == 'newline_len'

    assert db.names.get_at(db.minimum_ea) == '_start'

    from ida_domain.names import DemangleFlags, SetNameFlags

    test_addr = 0x418
    success = db.names.set_name(test_addr, 'test_name', SetNameFlags.NOCHECK)
    assert isinstance(success, bool) and success
    assert db.names.get_at(test_addr) == 'test_name'

    success = db.names.set_name(
        test_addr, 'test_name_public', SetNameFlags.PUBLIC | SetNameFlags.NOCHECK
    )
    assert isinstance(success, bool) and success
    assert db.names.get_at(test_addr) == 'test_name_public'

    success = db.names.force_name(
        test_addr, 'forced_name', SetNameFlags.FORCE | SetNameFlags.NOCHECK
    )
    assert isinstance(success, bool) and success
    assert db.names.get_at(test_addr) == 'forced_name'

    success = db.names.delete(test_addr)
    assert isinstance(success, bool) and success
    assert db.names.get_at(test_addr) == ''  # Should be empty after deletion

    assert db.names.is_valid_name('valid_name') is True
    assert db.names.is_valid_name('123invalid') is False  # Names can't start with numbers
    assert db.names.is_valid_name('') is False  # Empty names are invalid

    test_addr = 0x330  # Use test_data address

    original_public = db.names.is_public_name(test_addr)
    assert not original_public
    db.names.make_name_public(test_addr)
    assert db.names.is_public_name(test_addr) is True
    db.names.make_name_non_public(test_addr)
    assert db.names.is_public_name(test_addr) is False

    original_weak = db.names.is_weak_name(test_addr)
    assert not original_weak

    db.names.make_name_weak(test_addr)
    assert db.names.is_weak_name(test_addr) is True
    db.names.make_name_non_weak(test_addr)
    assert db.names.is_weak_name(test_addr) is False

    demangled = db.names.get_demangled_name(0x2A3)  # add_numbers function
    assert isinstance(demangled, str)
    assert demangled == 'add_numbers'

    # Test demangle_name method with a known mangled name pattern
    mangled_name = '_Z3fooi'  # Simple C++ mangled name
    demangled = db.names.demangle_name(mangled_name)
    assert isinstance(demangled, str)
    assert demangled == 'foo(int)'

    # Test demangle_name with non-mangled name (should return original)
    normal_name = 'normal_function_name'
    result = db.names.demangle_name(normal_name, DemangleFlags.DEFNONE)
    assert result is None

    assert db.names.delete(test_addr)


def test_xrefs(test_env):
    db = test_env
    expected_xrefs = [0xC4]
    expected_names = ['Ordinary_Flow']
    xrefs_to = db.xrefs.get_to(0xC6)
    for i, xrefblk in enumerate(xrefs_to):
        assert xrefblk.frm == expected_xrefs[i]
        assert db.xrefs.get_name(xrefblk) == expected_names[i]

    expected_xrefs = [0xD9]
    expected_names = ['Ordinary_Flow']
    xrefs_from = db.xrefs.get_from(0xD6)
    for i, xrefblk in enumerate(xrefs_from):
        assert xrefblk.to == expected_xrefs[i]
        assert db.xrefs.get_name(xrefblk) == expected_names[i]


def test_types(test_env):
    db = test_env
    all_types = db.types.get_names()
    count = 0
    for _ in all_types:
        count = count + 1
    assert count == 0

    type_name = db.types.get_name_at(0xB3)
    assert type_name is None

    assert not db.types.apply_named_type(0xB3, 'int')
    type_name = db.types.get_name_at(0xB3)
    assert type_name is None


def test_signature_files(test_env):
    db = test_env

    # Get available signatures
    available_sigs = db.signature_files.get_files()
    assert len(available_sigs) > 0, 'No signature files found'

    sig_files = db.signature_files.create(pat_only=True)
    assert len(sig_files) == 1
    assert sig_files[0] == f'{db.path}.pat'

    sig_files = db.signature_files.create()
    assert len(sig_files) == 2
    assert sig_files[0] == f'{db.path}.sig'
    assert sig_files[1] == f'{db.path}.pat'


def test_comments(test_env):
    db = test_env

    # Validate expected comments and their addresses
    expected_comments = [
        (0x16, 'LINUX - sys_write'),
        (0x46, 'LINUX - sys_write'),
        (0x67, 'LINUX - sys_write'),
        (0x92, 'LINUX - sys_write'),
        (0xB3, 'LINUX - sys_write'),
        (0xBD, 'LINUX - sys_exit'),
        (0x2D1, 'buf'),
        (0x2E0, 'fd'),
        (0x2E8, 'count'),
        (0x2EB, 'LINUX - sys_write'),
    ]

    for i, (addr, comment) in enumerate(db.comments.get_all(False)):
        assert expected_comments[i][0] == addr
        assert expected_comments[i][1] == comment

    # Add a new comment at address 0xae
    assert db.comments.set(0xAE, 'Testing adding comment')
    assert db.comments.get(0xAE) == 'Testing adding comment'


def test_bytes(test_env):
    db = test_env

    # Test existing getter methods
    byte_val = db.bytes.get_byte(0x3FA)
    assert byte_val == 0x19

    word_val = db.bytes.get_word(0x3F0)
    assert word_val == 0xF5C3

    dword_val = db.bytes.get_dword(0x3E8)
    assert dword_val == 0x6375646F

    qword_val = db.bytes.get_qword(0x3ED)
    assert qword_val == 0x1F4048F5C30A203A

    float_val = db.bytes.get_float(0x15C)
    assert pytest.approx(float_val, rel=3.14) == 0.0

    double_val = db.bytes.get_double(0x160)
    assert pytest.approx(double_val, rel=6.28) == 0.0

    disasm = db.bytes.get_disassembly(0x3D4)
    assert disasm == "db 'Hello, IDA!',0Ah,0"

    # Test setter methods
    test_addr = 0x330  # Use test_data address
    original_byte = db.bytes.get_byte(test_addr)
    db.bytes.set_byte(test_addr, 0xFF)
    assert db.bytes.get_byte(test_addr) == 0xFF
    db.bytes.set_byte(test_addr, original_byte)  # Restore

    # Test search operations
    pattern = b'\x48\x89\xe5'  # Common x64 prologue pattern
    found_addr = db.bytes.find_bytes(pattern)
    assert found_addr is not None

    text_addr = db.bytes.find_text('Hello')
    assert text_addr is not None

    imm_addr = db.bytes.find_immediate(1)
    assert imm_addr is not None

    # Test data type operations
    assert db.bytes.make_byte(0x330)
    assert db.bytes.make_word(0x332)
    assert db.bytes.make_dword(0x334)
    assert db.bytes.make_qword(0x338)

    # Test memory analysis
    data_type = db.bytes.get_data_type(0x330)
    assert data_type == 'byte'

    data_size = db.bytes.get_data_size(0x330)
    assert isinstance(data_size, int) and data_size == 1

    # Test types for few addresses
    assert isinstance(db.bytes.is_code(0x67), bool)
    assert db.bytes.is_code(0x67) and not db.bytes.is_code(0x330)
    assert isinstance(db.bytes.is_data(0x400), bool)
    assert db.bytes.is_data(0x330) and not db.bytes.is_data(0x67)
    assert isinstance(db.bytes.is_unknown(0x400), bool)
    assert db.bytes.is_unknown(0x323) and not db.bytes.is_unknown(0x67)
    assert isinstance(db.bytes.is_head(0x400), bool)
    assert db.bytes.is_head(0x400) and not db.bytes.is_head(0x64)
    assert isinstance(db.bytes.is_tail(0x401), bool)
    assert not db.bytes.is_tail(0x67) and db.bytes.is_tail(0x64)

    # Test string operations
    success, string_val = db.bytes.get_string(0x3D4)
    assert isinstance(success, bool) and success
    assert isinstance(string_val, str) and string_val == 'Hello, IDA!\n'

    success, cstring_val = db.bytes.get_cstring(0x3D4)
    assert isinstance(success, bool) and success
    assert isinstance(cstring_val, str) and cstring_val == 'Hello, IDA!\n'

    success, unicode_val = db.bytes.get_unicode_string(0x3D4)
    assert isinstance(success, bool) and not success
    assert isinstance(unicode_val, str) and unicode_val == ''

    # Test utility methods
    success, orig_bytes = db.bytes.get_original_bytes(0x330, 4)
    assert isinstance(success, bool) and success
    assert isinstance(orig_bytes, bytes) and orig_bytes == b'\xef\xcd\xab\x90'

    has_name = db.bytes.has_user_name(0x330)
    assert isinstance(has_name, bool) and not has_name

    flags = db.bytes.get_flags(0x330)
    assert isinstance(flags, int) and flags == 0x5400

    # Test navigation helpers
    next_head = db.bytes.next_head(0x330)
    assert isinstance(next_head, int) and next_head == 0x332

    prev_head = db.bytes.prev_head(0x340)
    assert isinstance(prev_head, int) and prev_head == 0x338

    next_addr = db.bytes.next_addr(0x330)
    assert isinstance(next_addr, int) and next_addr == 0x331

    prev_addr = db.bytes.prev_addr(0x340)
    assert isinstance(prev_addr, int) and prev_addr == 0x33F

    # Test patching operations
    test_patch_addr = 0x330  # Use test_data address for patching tests

    # Get original values first
    original_byte = db.bytes.get_byte(test_patch_addr)
    original_word = db.bytes.get_word(test_patch_addr)
    original_dword = db.bytes.get_dword(test_patch_addr)
    original_qword = db.bytes.get_qword(test_patch_addr)

    # Test patch_byte
    patch_result = db.bytes.patch_byte(test_patch_addr, 0xAB)
    assert isinstance(patch_result, bool)
    assert db.bytes.get_byte(test_patch_addr) == 0xAB

    # Test get_original_byte
    orig_byte = db.bytes.get_original_byte(test_patch_addr)
    assert isinstance(orig_byte, int) and orig_byte == original_byte

    # Test revert_byte
    revert_result = db.bytes.revert_byte(test_patch_addr)
    assert isinstance(revert_result, bool) and revert_result
    assert db.bytes.get_byte(test_patch_addr) == original_byte

    # Test patch_word
    patch_result = db.bytes.patch_word(test_patch_addr, 0xCDEF)
    assert isinstance(patch_result, bool)
    assert db.bytes.get_word(test_patch_addr) == 0xCDEF

    # Test get_original_word
    orig_word = db.bytes.get_original_word(test_patch_addr)
    assert isinstance(orig_word, int) and orig_word == original_word

    # Test patch_dword
    patch_result = db.bytes.patch_dword(test_patch_addr, 0x12345678)
    assert isinstance(patch_result, bool)
    assert db.bytes.get_dword(test_patch_addr) == 0x12345678

    # Test get_original_dword
    orig_dword = db.bytes.get_original_dword(test_patch_addr)
    assert isinstance(orig_dword, int) and orig_dword == original_dword

    # Test patch_qword
    patch_result = db.bytes.patch_qword(test_patch_addr, 0x123456789ABCDEF0)
    assert isinstance(patch_result, bool)
    assert db.bytes.get_qword(test_patch_addr) == 0x123456789ABCDEF0

    # Test get_original_qword
    orig_qword = db.bytes.get_original_qword(test_patch_addr)
    assert isinstance(orig_qword, int) and orig_qword == original_qword

    # Test patch_bytes
    test_bytes = b'\x90\x90\x90\x90'  # NOP instructions
    patch_result = db.bytes.patch_bytes(test_patch_addr, test_bytes)
    assert isinstance(patch_result, bool) and patch_result

    # Verify the bytes were patched
    for i, expected_byte in enumerate(test_bytes):
        actual_byte = db.bytes.get_byte(test_patch_addr + i)
        assert actual_byte == expected_byte

    # Test get_original_bytes for patched area
    success, orig_bytes = db.bytes.get_original_bytes(test_patch_addr, len(test_bytes))
    assert isinstance(success, bool) and success
    assert isinstance(orig_bytes, bytes) and orig_bytes == b'\xef\xcd\xab\x90'

    # Test new flag checking methods using ByteFlags enum
    from ida_domain.bytes import ByteFlags

    # Test check_flags method
    code_addr = 0x0  # Known code address
    data_addr = 0x338  # Known data address

    # Test checking for code flags
    has_code_flag = db.bytes.check_flags(code_addr, ByteFlags.CODE)
    assert isinstance(has_code_flag, bool) and has_code_flag

    # Test checking for data flags
    has_data_flag = db.bytes.check_flags(data_addr, ByteFlags.DATA)
    assert isinstance(has_data_flag, bool) and has_data_flag

    # Test has_any_flags method
    has_any_code_or_data = db.bytes.has_any_flags(code_addr, ByteFlags.CODE | ByteFlags.DATA)
    assert isinstance(has_any_code_or_data, bool) and has_any_code_or_data

    has_any_byte_or_word = db.bytes.has_any_flags(data_addr, ByteFlags.BYTE | ByteFlags.WORD)
    assert isinstance(has_any_byte_or_word, bool) and has_any_byte_or_word

    # Test get_data_type_from_flags method
    code_flags = db.bytes.get_flags(code_addr)
    data_type_from_flags = db.bytes.get_data_type_from_flags(code_flags)
    assert isinstance(data_type_from_flags, str) and data_type_from_flags == 'string'

    data_flags = db.bytes.get_flags(data_addr)
    data_type_from_flags = db.bytes.get_data_type_from_flags(data_flags)
    assert isinstance(data_type_from_flags, str) and data_type_from_flags == 'string'

    # Test enum usage in search operations
    from ida_domain.bytes import SearchFlags, StringType

    # Test SearchFlags enum usage
    text_addr_with_flags = db.bytes.find_text('Hello', flags=SearchFlags.DOWN | SearchFlags.CASE)
    assert text_addr_with_flags is not None

    # Test StringType enum usage (create a string with specific type)
    string_addr = 0x3D4
    string_created = db.bytes.make_string(string_addr, string_type=StringType.C)
    assert isinstance(string_created, bool) and string_created


def test_ida_command_builder():
    # Test default state produces empty args
    builder = ida_domain.Database.IdaCommandBuilder()
    assert builder.build_args() == ''

    # Test auto analysis option
    builder = ida_domain.Database.IdaCommandBuilder()
    # Default is true, should only add flag if false
    assert builder.auto_analysis(True).build_args() == ''

    builder = ida_domain.Database.IdaCommandBuilder()
    assert builder.auto_analysis(False).build_args() == '-a'

    # Test loading address option
    builder = ida_domain.Database.IdaCommandBuilder()
    assert builder.set_loading_address(0x1000).build_args() == '-b1000'

    # Test new database option
    builder = ida_domain.Database.IdaCommandBuilder()
    assert builder.new_database().build_args() == '-c'

    # Test compiler option
    builder = ida_domain.Database.IdaCommandBuilder()
    assert builder.set_compiler('gcc').build_args() == '-Cgcc'

    builder = ida_domain.Database.IdaCommandBuilder()
    assert builder.set_compiler('gcc', 'x64').build_args() == '-Cgcc:x64'

    # Test first pass directive option
    builder = ida_domain.Database.IdaCommandBuilder()
    assert builder.add_first_pass_directive('VPAGESIZE=8192').build_args() == '-dVPAGESIZE=8192'

    # Add multiple directives
    builder = ida_domain.Database.IdaCommandBuilder()
    builder.add_first_pass_directive('DIR1')
    builder.add_first_pass_directive('DIR2')
    assert builder.build_args() == '-dDIR1 -dDIR2'

    # Test second pass directive option
    builder = ida_domain.Database.IdaCommandBuilder()
    assert builder.add_second_pass_directive('OPTION=VALUE').build_args() == '-DOPTION=VALUE'

    # Test disable FPP instructions option
    builder = ida_domain.Database.IdaCommandBuilder()
    assert builder.disable_fpp_instructions().build_args() == '-f'

    # Test entry point option
    builder = ida_domain.Database.IdaCommandBuilder()
    assert builder.set_entry_point(0x401000).build_args() == '-i401000'

    # Test JIT debugger option
    builder = ida_domain.Database.IdaCommandBuilder()
    assert builder.set_jit_debugger(True).build_args() == '-I1'

    builder = ida_domain.Database.IdaCommandBuilder()
    assert builder.set_jit_debugger(False).build_args() == '-I0'

    # Test log file option
    builder = ida_domain.Database.IdaCommandBuilder()
    assert builder.set_log_file('debug.log').build_args() == '-Ldebug.log'

    # Test disable mouse option
    builder = ida_domain.Database.IdaCommandBuilder()
    assert builder.disable_mouse().build_args() == '-M'

    # Test plugin options
    builder = ida_domain.Database.IdaCommandBuilder()
    assert builder.set_plugin_options('opt1=val1').build_args() == '-Oopt1=val1'

    # Test output database option (should also set -c flag)
    builder = ida_domain.Database.IdaCommandBuilder()
    assert builder.set_output_database('output.idb').build_args() == '-c -ooutput.idb'

    # Test processor option
    builder = ida_domain.Database.IdaCommandBuilder()
    assert builder.set_processor('arm').build_args() == '-parm'

    # Test database compression options
    builder = ida_domain.Database.IdaCommandBuilder()
    assert builder.compress_database().build_args() == '-P+'

    builder = ida_domain.Database.IdaCommandBuilder()
    assert builder.pack_database().build_args() == '-P'

    builder = ida_domain.Database.IdaCommandBuilder()
    assert builder.no_pack_database().build_args() == '-P-'

    # Test run debugger option
    builder = ida_domain.Database.IdaCommandBuilder()
    assert builder.run_debugger().build_args() == '-r'

    builder = ida_domain.Database.IdaCommandBuilder()
    assert builder.run_debugger('debug-options').build_args() == '-rdebug-options'

    # Test load resources option
    builder = ida_domain.Database.IdaCommandBuilder()
    assert builder.load_resources().build_args() == '-R'

    # Test run script option
    builder = ida_domain.Database.IdaCommandBuilder()
    assert builder.run_script('analyze.py').build_args() == '-Sanalyze.py'

    builder = ida_domain.Database.IdaCommandBuilder()
    args = ['arg1', 'arg with spaces', '--flag=value']
    assert (
        builder.run_script('script.py', args).build_args()
        == '-S"script.py arg1 "arg with spaces" --flag=value"'
    )

    # Test file type option
    builder = ida_domain.Database.IdaCommandBuilder()
    assert builder.set_file_type('PE').build_args() == '-TPE'

    builder = ida_domain.Database.IdaCommandBuilder()
    assert builder.set_file_type('ZIP', 'classes.dex').build_args() == '-TZIP:classes.dex'

    # Test empty database option
    builder = ida_domain.Database.IdaCommandBuilder()
    assert builder.empty_database().build_args() == '-t'

    # Test Windows directory option
    builder = ida_domain.Database.IdaCommandBuilder()
    assert builder.set_windows_directory('C:\\Windows').build_args() == '-WC:\\Windows'

    # Test no segmentation option
    builder = ida_domain.Database.IdaCommandBuilder()
    assert builder.no_segmentation().build_args() == '-x'

    # Test debug flags option
    # Test with numeric flags
    builder = ida_domain.Database.IdaCommandBuilder()
    assert builder.set_debug_flags(0x404).build_args() == '-z404'

    # Test with named flags
    builder = ida_domain.Database.IdaCommandBuilder()
    flags = ['flirt', 'type_system']
    assert builder.set_debug_flags(flags).build_args() == '-z4004'

    # Test method chaining
    builder = ida_domain.Database.IdaCommandBuilder()
    args = (
        builder.auto_analysis(False).set_log_file('analysis.log').set_processor('arm').build_args()
    )
    assert args == '-a -Lanalysis.log -parm'

    # Test complex scenario
    builder = ida_domain.Database.IdaCommandBuilder()
    args = (
        builder.new_database(True)
        .set_compiler('gcc', 'x64')
        .set_processor('arm')
        .run_script('analyze.py', ['deep', '--verbose'])
        .build_args()
    )
    assert args == '-c -Cgcc:x64 -parm -S"analyze.py deep --verbose"'

    # Test another complex scenario
    builder = ida_domain.Database.IdaCommandBuilder()
    args = (
        builder.set_output_database('project.idb')
        .compress_database()
        .set_file_type('ZIP', 'classes.dex')
        .set_debug_flags(0x10004)  # debugger + flirt
        .build_args()
    )
    assert args == '-c -oproject.idb -P+ -TZIP:classes.dex -z10004'

    # Test getter methods that are available
    builder = ida_domain.Database.IdaCommandBuilder()

    assert builder._auto_analysis
    builder.auto_analysis(False)
    assert not builder._auto_analysis


def test_api_examples(test_env):
    examples = [
        'analyze_functions.py',
        'analyze_strings.py',
        'analyze_types.py',
        'analyze_bytes.py',
        'explore_database.py',
        'analyze_database.py',
        'explore_flirt.py',
        'quick_example.py',
        'my_first_script.py',
    ]
    for example in examples:
        script_path = Path(__file__).parent.parent / 'examples' / example
        cmd = [sys.executable, str(script_path), '-f', str(idb_path)]

        result = subprocess.run(cmd, capture_output=True, text=True)

        print(f'Example {script_path} outputs')
        print('\n[STDOUT]')
        print(result.stdout)
        print('[STDERR]')
        print(result.stderr)

        assert result.returncode == 0, f'Example {script_path} failed to run'

    # analyze_xrefs.py requires additional arguments
    script_path = Path(__file__).parent.parent / 'examples' / 'analyze_xrefs.py'
    cmd = [sys.executable, str(script_path), '-f', str(idb_path), '-a', '0xd6']

    result = subprocess.run(cmd, capture_output=True, text=True)

    print(f'Example {script_path} outputs')
    print('\n[STDOUT]')
    print(result.stdout)
    print('[STDERR]')
    print(result.stderr)

    assert result.returncode == 0, f'Example {script_path} failed to run'
