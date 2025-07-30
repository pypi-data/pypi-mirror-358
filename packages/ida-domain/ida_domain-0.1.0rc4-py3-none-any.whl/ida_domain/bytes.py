from __future__ import annotations

import logging
import struct
from enum import IntEnum, IntFlag
from typing import TYPE_CHECKING, Tuple

import ida_bytes
import ida_ida
import ida_lines
import ida_nalt
import ida_name
import ida_search
from ida_idaapi import BADADDR
from idadex import ea_t

from .decorators import check_db_open, decorate_all_methods

if TYPE_CHECKING:
    from .database import Database


class StringType(IntEnum):
    """String type constants for string operations."""

    C = ida_nalt.STRTYPE_C
    C16 = ida_nalt.STRTYPE_C_16
    C32 = ida_nalt.STRTYPE_C_32
    PASCAL = ida_nalt.STRTYPE_PASCAL
    LEN2 = ida_nalt.STRTYPE_LEN2
    LEN4 = ida_nalt.STRTYPE_LEN4
    TERMCHR = ida_nalt.STRTYPE_TERMCHR


class SearchFlags(IntFlag):
    """Search flags for text and pattern searching."""

    DOWN = ida_search.SEARCH_DOWN
    UP = ida_search.SEARCH_UP
    CASE = ida_search.SEARCH_CASE
    REGEX = ida_search.SEARCH_REGEX
    NOBRK = ida_search.SEARCH_NOBRK
    NOSHOW = ida_search.SEARCH_NOSHOW
    IDENT = ida_search.SEARCH_IDENT
    BRK = ida_search.SEARCH_BRK


class DataTypeFlags(IntEnum):
    """Data type flags for creating data items."""

    BYTE = ida_bytes.byte_flag()
    WORD = ida_bytes.word_flag()
    DWORD = ida_bytes.dword_flag()
    QWORD = ida_bytes.qword_flag()
    FLOAT = ida_bytes.float_flag()
    DOUBLE = ida_bytes.double_flag()


class ByteFlags(IntEnum):
    """Byte flag constants for flag checking operations."""

    # Data type flags
    BYTE = ida_bytes.FF_BYTE
    WORD = ida_bytes.FF_WORD
    DWORD = ida_bytes.FF_DWORD
    QWORD = ida_bytes.FF_QWORD
    FLOAT = ida_bytes.FF_FLOAT
    DOUBLE = ida_bytes.FF_DOUBLE
    STRLIT = ida_bytes.FF_STRLIT
    STRUCT = ida_bytes.FF_STRUCT
    ALIGN = ida_bytes.FF_ALIGN

    # Item type flags
    CODE = ida_bytes.FF_CODE
    DATA = ida_bytes.FF_DATA
    TAIL = ida_bytes.FF_TAIL
    UNK = ida_bytes.FF_UNK

    # Common flags
    COMM = ida_bytes.FF_COMM
    REF = ida_bytes.FF_REF
    LINE = ida_bytes.FF_LINE
    NAME = ida_bytes.FF_NAME
    LABL = ida_bytes.FF_LABL
    FLOW = ida_bytes.FF_FLOW


logger = logging.getLogger(__name__)


@decorate_all_methods(check_db_open)
class Bytes:
    """
    Handles operations related to raw data access from the IDA database.

    This class provides methods to read various data types (bytes, words, floats, etc.)
    from memory addresses in the disassembled binary.
    """

    def __init__(self, database: 'Database'):
        """
        Constructs a bytes handler for the given database.

        Args:
            database: Reference to the active IDA database.
        """
        self.m_database = database

    def _log_error(self, method_name: str, ea: ea_t, message: str = 'Failed to read data') -> None:
        """
        Helper method to log errors consistently.

        Args:
            method_name: Name of the method where the error occurred.
            ea: The effective address where the error occurred.
            message: Custom error message.
        """
        logger.error(f'{method_name}: {message} from address 0x{ea:x}')

    def get_byte(self, ea: ea_t) -> int | None:
        """
        Retrieves a single byte (8 bits) at the specified address.

        Args:
            ea: The effective address.

        Returns:
            The byte value (0-255), or None if an error occurs.
        """
        try:
            return ida_bytes.get_byte(ea)
        except Exception:
            self._log_error('get_byte', ea)
            return None

    def get_word(self, ea: ea_t) -> int | None:
        """
        Retrieves a word (16 bits/2 bytes) at the specified address.

        Args:
            ea: The effective address.

        Returns:
            The word value, or None if an error occurs.
        """
        try:
            return ida_bytes.get_word(ea)
        except Exception:
            self._log_error('get_word', ea)
            return None

    def get_dword(self, ea: ea_t) -> int | None:
        """
        Retrieves a double word (32 bits/4 bytes) at the specified address.

        Args:
            ea: The effective address.

        Returns:
            The dword value, or None if an error occurs.
        """
        try:
            return ida_bytes.get_dword(ea)
        except Exception:
            self._log_error('get_dword', ea)
            return None

    def get_qword(self, ea: ea_t) -> int | None:
        """
        Retrieves a quad word (64 bits/8 bytes) at the specified address.

        Args:
            ea: The effective address.

        Returns:
            The qword value, or None if an error occurs.
        """
        try:
            return ida_bytes.get_qword(ea)
        except Exception:
            self._log_error('get_qword', ea)
            return None

    def _read_floating_point(self, ea: ea_t, data_flags: int, method_name: str) -> float | None:
        """
        Helper method to read floating-point values from memory.

        Args:
            ea: The effective address.
            data_flags: Data flags - float flags or double flags.
            method_name: Name of the calling method for error reporting.

        Returns:
            The floating-point value, or None if an error occurs.
        """
        try:
            # Get data element size for the floating-point type
            size = ida_bytes.get_data_elsize(ea, data_flags)
        except Exception:
            self._log_error(method_name, ea, 'Failed to get data element size')
            return None

        if size <= 0 or size > 16:
            self._log_error(method_name, ea, f'Invalid size {size} for floating-point data')
            return None

        # Read bytes from address
        data = ida_bytes.get_bytes(ea, size)
        if data is None or len(data) != size:
            self._log_error(method_name, ea, 'Failed to read bytes')
            return None

        # Convert bytes to floating-point value
        try:
            # Get processor endianness
            is_little_endian = not ida_ida.inf_is_be()
            endian = '<' if is_little_endian else '>'

            if size == 4:
                # IEEE 754 single precision (32-bit float)
                return struct.unpack(f'{endian}f', data)[0]
            elif size == 8:
                # IEEE 754 double precision (64-bit double)
                return struct.unpack(f'{endian}d', data)[0]
            else:
                self._log_error(method_name, ea, f'Unsupported floating-point size: {size}')
                return None

        except (struct.error, ValueError, OverflowError) as e:
            self._log_error(method_name, ea, f'Failed to convert bytes to floating-point: {e}')
            return None

    def get_float(self, ea: ea_t) -> float | None:
        """
        Retrieves a single-precision floating-point value at the specified address.

        Args:
            ea: The effective address.

        Returns:
            The float value, or None if an error occurs.
        """
        return self._read_floating_point(ea, ida_bytes.float_flag(), 'get_float')

    def get_double(self, ea: ea_t) -> float | None:
        """
        Retrieves a double-precision floating-point value at the specified address.

        Args:
            ea: The effective address.

        Returns:
            The double value, or None if an error occurs.
        """
        return self._read_floating_point(ea, ida_bytes.double_flag(), 'get_double')

    def get_disassembly(self, ea: ea_t) -> str | None:
        """
        Retrieves the disassembly text at the specified address.

        Args:
            ea: The effective address.

        Returns:
            The disassembly string, or None if an error occurs.
        """
        try:
            # Generate disassembly line with multi-line and remove tags flags
            line = ida_lines.generate_disasm_line(
                ea, ida_lines.GENDSM_MULTI_LINE | ida_lines.GENDSM_REMOVE_TAGS
            )
            if line:
                return line
            else:
                self._log_error('get_disassembly', ea, 'Failed to generate disassembly line')
                return None
        except Exception:
            self._log_error('get_disassembly', ea, 'Exception while generating disassembly line')
            return None

    def set_byte(self, ea: ea_t, value: int) -> bool:
        """
        Sets a byte value at the specified address.

        Args:
            ea: The effective address.
            value: Byte value to set.

        Returns:
            True if successful, False otherwise.
        """
        try:
            ida_bytes.put_byte(ea, value)
            return True
        except Exception:
            self._log_error('set_byte', ea, f'Failed to set: {value}')
            return False

    def set_word(self, ea: ea_t, value: int) -> bool:
        """
        Sets a word (2 bytes) value at the specified address.

        Args:
            ea: The effective address.
            value: Word value to set.

        Returns:
            True if successful, False otherwise.
        """
        try:
            ida_bytes.put_word(ea, value)
            return True
        except Exception:
            self._log_error('set_word', ea, f'Failed to set: {value}')
            return False

    def set_dword(self, ea: ea_t, value: int) -> bool:
        """
        Sets a double word (4 bytes) value at the specified address.

        Args:
            ea: The effective address.
            value: Double word value to set.

        Returns:
            True if successful, False otherwise.
        """
        try:
            ida_bytes.put_dword(ea, value)
            return True
        except Exception:
            self._log_error('set_dword', ea, f'Failed to set: {value}')
            return False

    def set_qword(self, ea: ea_t, value: int) -> bool:
        """
        Sets a quad word (8 bytes) value at the specified address.

        Args:
            ea: The effective address.
            value: Quad word value to set.

        Returns:
            True if successful, False otherwise.
        """
        try:
            ida_bytes.put_qword(ea, value)
            return True
        except Exception:
            self._log_error('set_qword', ea, f'Failed to set: {value}')
            return False

    def set_bytes(self, ea: ea_t, data: bytes) -> bool:
        """
        Sets a sequence of bytes at the specified address.

        Args:
            ea: The effective address.
            data: Bytes to write.

        Returns:
            True if successful, False otherwise.
        """
        try:
            ida_bytes.put_bytes(ea, data)
            return True
        except Exception:
            self._log_error('set_bytes', ea, f'Failed to set: {str(data)}')
            return False

    def patch_byte(self, ea: ea_t, value: int) -> bool:
        """
        Patch a byte of the program.
        The original value is saved and can be obtained by get_original_byte().

        Args:
            ea: The effective address.
            value: Byte value to patch.

        Returns:
            True if the database has been modified, False otherwise.
        """
        try:
            return ida_bytes.patch_byte(ea, value)
        except Exception:
            self._log_error('patch_byte', ea, f'Failed to patch: {value}')
            return False

    def patch_word(self, ea: ea_t, value: int) -> bool:
        """
        Patch a word of the program.
        The original value is saved and can be obtained by get_original_word().

        Args:
            ea: The effective address.
            value: Word value to patch.

        Returns:
            True if the database has been modified, False otherwise.
        """
        try:
            return ida_bytes.patch_word(ea, value)
        except Exception:
            self._log_error('patch_word', ea, f'Failed to patch: {value}')
            return False

    def patch_dword(self, ea: ea_t, value: int) -> bool:
        """
        Patch a dword of the program.
        The original value is saved and can be obtained by get_original_dword().

        Args:
            ea: The effective address.
            value: Dword value to patch.

        Returns:
            True if the database has been modified, False otherwise.
        """
        try:
            return ida_bytes.patch_dword(ea, value)
        except Exception:
            self._log_error('patch_dword', ea, f'Failed to patch: {value}')
            return False

    def patch_qword(self, ea: ea_t, value: int) -> bool:
        """
        Patch a qword of the program.
        The original value is saved and can be obtained by get_original_qword().

        Args:
            ea: The effective address.
            value: Qword value to patch.

        Returns:
            True if the database has been modified, False otherwise.
        """
        try:
            return ida_bytes.patch_qword(ea, value)
        except Exception:
            self._log_error('patch_qword', ea, f'Failed to patch: {value}')
            return False

    def patch_bytes(self, ea: ea_t, data: bytes) -> bool:
        """
        Patch the specified number of bytes of the program.
        Original values are saved and available with get_original_bytes().

        Args:
            ea: The effective address.
            data: Bytes to patch.

        Returns:
            True if successful, False otherwise.
        """
        try:
            ida_bytes.patch_bytes(ea, data)
            return True
        except Exception:
            self._log_error('patch_bytes', ea, f'Failed to patch: {str(data)}')
            return False

    def revert_byte(self, ea: ea_t) -> bool:
        """
        Revert patched byte to its original value.

        Args:
            ea: The effective address.

        Returns:
            True if byte was patched before and reverted now, False otherwise.
        """
        try:
            return ida_bytes.revert_byte(ea)
        except Exception:
            self._log_error('revert_byte', ea, 'Failed to revert byte')
            return False

    def get_original_byte(self, ea: ea_t) -> int | None:
        """
        Get original byte value (that was before patching).

        Args:
            ea: The effective address.

        Returns:
            The original byte value, or None if an error occurs.
        """
        try:
            return ida_bytes.get_original_byte(ea)
        except Exception:
            self._log_error('get_original_byte', ea, 'Failed to get original byte')
            return None

    def get_original_word(self, ea: ea_t) -> int | None:
        """
        Get original word value (that was before patching).

        Args:
            ea: The effective address.

        Returns:
            The original word value, or None if an error occurs.
        """
        try:
            return ida_bytes.get_original_word(ea)
        except Exception:
            self._log_error('get_original_word', ea, 'Failed to get original word')
            return None

    def get_original_dword(self, ea: ea_t) -> int | None:
        """
        Get original dword value (that was before patching).

        Args:
            ea: The effective address.

        Returns:
            The original dword value, or None if an error occurs.
        """
        try:
            return ida_bytes.get_original_dword(ea)
        except Exception:
            self._log_error('get_original_dword', ea, 'Failed to get original dword')
            return None

    def get_original_qword(self, ea: ea_t) -> int | None:
        """
        Get original qword value (that was before patching).

        Args:
            ea: The effective address.

        Returns:
            The original qword value, or None if an error occurs.
        """
        try:
            return ida_bytes.get_original_qword(ea)
        except Exception:
            self._log_error('get_original_qword', ea, 'Failed to get original qword')
            return None

    # Search operations
    def find_bytes(
        self, pattern: bytes, start_ea: ea_t = None, end_ea: ea_t = None
    ) -> ea_t | None:
        """
        Finds a byte pattern in memory.

        Args:
            pattern: Byte pattern to search for.
            start_ea: Start address for search.
            end_ea: End address for search.

        Returns:
            Address where pattern was found, or None if not found.
        """
        try:
            if start_ea is None:
                start_ea = self.m_database.minimum_ea
            if end_ea is None:
                end_ea = self.m_database.maximum_ea
            ea = ida_bytes.find_bytes(pattern, start_ea, None, end_ea)
            return ea if ea != BADADDR else None
        except Exception:
            self._log_error('find_bytes', start_ea or 0, f'Failed to search: {str(pattern)}')
            return None

    def find_text(
        self,
        text: str,
        start_ea: ea_t = None,
        end_ea: ea_t = None,
        flags: SearchFlags = SearchFlags.DOWN,
    ) -> ea_t | None:
        """
        Finds a text string in memory.

        Args:
            text: Text to search for.
            start_ea: Start address for search.
            end_ea: End address for search.
            flags: Search flags (default: SearchFlags.DOWN).

        Returns:
            Address where text was found, or None if not found.
        """
        try:
            if start_ea is None:
                start_ea = self.m_database.minimum_ea
            if end_ea is None:
                end_ea = self.m_database.maximum_ea

            ea = ida_search.find_text(start_ea, 0, 0, text, flags)
            return ea if ea != BADADDR else None
        except Exception:
            self._log_error('find_text', start_ea or 0, f'Failed to search for text: {text}')
            return None

    def find_immediate(
        self, value: int, start_ea: ea_t = None, end_ea: ea_t = None
    ) -> ea_t | None:
        """
        Finds an immediate value in instructions.

        Args:
            value: Immediate value to search for.
            start_ea: Start address for search.
            end_ea: End address for search.

        Returns:
            Address where immediate was found, or None if not found.
        """
        try:
            if start_ea is None:
                start_ea = self.m_database.minimum_ea
            if end_ea is None:
                end_ea = self.m_database.maximum_ea

            result = ida_search.find_imm(start_ea, ida_search.SEARCH_DOWN, value)
            # find_imm returns a tuple (address, operand_number) or None
            if result and isinstance(result, tuple) and len(result) >= 1:
                ea = result[0]
                return ea if ea != BADADDR else None
            return None
        except Exception:
            self._log_error(
                'find_immediate', start_ea or 0, f'Failed to search for immediate: {value}'
            )
            return None

    # Data type operations
    def make_byte(self, ea: ea_t) -> bool:
        """
        Converts data at address to byte type.

        Args:
            ea: The effective address.

        Returns:
            True if successful, False otherwise.
        """
        try:
            return ida_bytes.create_data(ea, DataTypeFlags.BYTE, 1, BADADDR)
        except Exception:
            self._log_error('make_byte', ea, 'Failed to create byte data')
            return False

    def make_word(self, ea: ea_t) -> bool:
        """
        Converts data at address to word type.

        Args:
            ea: The effective address.

        Returns:
            True if successful, False otherwise.
        """
        try:
            return ida_bytes.create_data(ea, DataTypeFlags.WORD, 2, BADADDR)
        except Exception:
            self._log_error('make_word', ea, 'Failed to create word data')
            return False

    def make_dword(self, ea: ea_t) -> bool:
        """
        Converts data at address to double word type.

        Args:
            ea: The effective address.

        Returns:
            True if successful, False otherwise.
        """
        try:
            return ida_bytes.create_data(ea, DataTypeFlags.DWORD, 4, BADADDR)
        except Exception:
            self._log_error('make_dword', ea, 'Failed to create dword data')
            return False

    def make_qword(self, ea: ea_t) -> bool:
        """
        Converts data at address to quad word type.

        Args:
            ea: The effective address.

        Returns:
            True if successful, False otherwise.
        """
        try:
            return ida_bytes.create_data(ea, DataTypeFlags.QWORD, 8, BADADDR)
        except Exception:
            self._log_error('make_qword', ea, 'Failed to create qword data')
            return False

    def make_string(
        self, ea: ea_t, length: int = None, string_type: StringType = StringType.C
    ) -> bool:
        """
        Converts data at address to string type.

        Args:
            ea: The effective address.
            length: String length (auto-detect if None).
            string_type: String type (default: StringType.C).

        Returns:
            True if successful, False otherwise.
        """
        try:
            if length is None:
                # Auto-detect string length
                return ida_bytes.create_strlit(ea, 0, string_type)
            else:
                return ida_bytes.create_strlit(ea, length, string_type)
        except Exception:
            self._log_error('make_string', ea, 'Failed to create string data')
            return False

    def make_array(self, ea: ea_t, element_size: int, count: int) -> bool:
        """
        Converts data at address to array type.

        Args:
            ea: The effective address.
            element_size: Size of each array element.
            count: Number of elements.

        Returns:
            True if successful, False otherwise.
        """
        try:
            # Determine the appropriate flag based on element size
            if element_size == 1:
                flags = DataTypeFlags.BYTE
            elif element_size == 2:
                flags = DataTypeFlags.WORD
            elif element_size == 4:
                flags = DataTypeFlags.DWORD
            elif element_size == 8:
                flags = DataTypeFlags.QWORD
            else:
                # For other sizes, use byte array
                flags = DataTypeFlags.BYTE
                element_size = 1
                count = element_size * count

            return ida_bytes.create_data(ea, flags, element_size * count, BADADDR)
        except Exception:
            self._log_error(
                'make_array',
                ea,
                f'Failed to create array data (size={element_size}, count={count})',
            )
            return False

    def get_data_type(self, ea: ea_t) -> str:
        """
        Gets the data type at the specified address.

        Args:
            ea: The effective address.

        Returns:
            String representation of the data type.
        """
        try:
            flags = ida_bytes.get_flags(ea)

            if ida_bytes.is_code(flags):
                return 'code'
            elif ida_bytes.is_byte(flags):
                return 'byte'
            elif ida_bytes.is_word(flags):
                return 'word'
            elif ida_bytes.is_dword(flags):
                return 'dword'
            elif ida_bytes.is_qword(flags):
                return 'qword'
            elif ida_bytes.is_float(flags):
                return 'float'
            elif ida_bytes.is_double(flags):
                return 'double'
            elif ida_bytes.is_strlit(flags):
                return 'string'
            elif ida_bytes.is_struct(flags):
                return 'struct'
            elif ida_bytes.is_align(flags):
                return 'align'
            elif ida_bytes.is_data(flags):
                return 'data'
            else:
                return 'unknown'
        except Exception:
            self._log_error('get_data_type', ea, 'Failed to get data type')
            return 'unknown'

    def get_data_size(self, ea: ea_t) -> int:
        """
        Gets the size of the data item at the specified address.

        Args:
            ea: The effective address.

        Returns:
            Size of the data item in bytes.
        """
        try:
            return ida_bytes.get_item_size(ea)
        except Exception:
            self._log_error('get_data_size', ea, 'Failed to get data size')
            return 0

    def is_code(self, ea: ea_t) -> bool:
        """
        Checks if the address contains code.

        Args:
            ea: The effective address.

        Returns:
            True if code, False otherwise.
        """
        try:
            return ida_bytes.is_code(ida_bytes.get_flags(ea))
        except Exception:
            self._log_error('is_code', ea, 'Failed to check if code')
            return False

    def is_data(self, ea: ea_t) -> bool:
        """
        Checks if the address contains data.

        Args:
            ea: The effective address.

        Returns:
            True if data, False otherwise.
        """
        try:
            return ida_bytes.is_data(ida_bytes.get_flags(ea))
        except Exception:
            self._log_error('is_data', ea, 'Failed to check if data')
            return False

    def is_unknown(self, ea: ea_t) -> bool:
        """
        Checks if the address contains unknown/undefined data.

        Args:
            ea: The effective address.

        Returns:
            True if unknown, False otherwise.
        """
        try:
            return ida_bytes.is_unknown(ida_bytes.get_flags(ea))
        except Exception:
            self._log_error('is_unknown', ea, 'Failed to check if unknown')
            return False

    def is_head(self, ea: ea_t) -> bool:
        """
        Checks if the address is the start of a data item.

        Args:
            ea: The effective address.

        Returns:
            True if head, False otherwise.
        """
        try:
            return ida_bytes.is_head(ida_bytes.get_flags(ea))
        except Exception:
            self._log_error('is_head', ea, 'Failed to check if head')
            return False

    def is_tail(self, ea: ea_t) -> bool:
        """
        Checks if the address is part of a multi-byte data item.

        Args:
            ea: The effective address.

        Returns:
            True if tail, False otherwise.
        """
        try:
            return ida_bytes.is_tail(ida_bytes.get_flags(ea))
        except Exception:
            self._log_error('is_tail', ea, 'Failed to check if tail')
            return False

    # String operations
    def get_string(self, ea: ea_t, max_length: int = None) -> Tuple[bool, str]:
        """
        Gets a string from the specified address.

        Args:
            ea: The effective address.
            max_length: Maximum string length to read.

        Returns:
            A pair of (success flag, string).
        """
        try:
            if max_length is None:
                # Try to get string length from IDA's analysis
                str_len = ida_bytes.get_max_strlit_length(ea, ida_nalt.STRTYPE_C)
                if str_len <= 0:
                    str_len = 256  # Default max length
            else:
                str_len = max_length

            string_data = ida_bytes.get_strlit_contents(ea, str_len, ida_nalt.STRTYPE_C)
            if string_data is not None:
                try:
                    # Decode bytes to string
                    decoded_string = string_data.decode('utf-8', errors='replace')
                    return True, decoded_string
                except (UnicodeDecodeError, AttributeError):
                    # Try latin-1 as fallback
                    try:
                        decoded_string = string_data.decode('latin-1', errors='replace')
                        return True, decoded_string
                    except (UnicodeDecodeError, AttributeError):
                        return False, ''
            else:
                return False, ''
        except Exception:
            self._log_error('get_string', ea, 'Failed to get string')
            return False, ''

    def get_cstring(self, ea: ea_t, max_length: int = 1024) -> Tuple[bool, str]:
        """
        Gets a C-style null-terminated string.

        Args:
            ea: The effective address.
            max_length: Maximum string length to read (default: 1024).

        Returns:
            A pair of (success flag, string).
        """
        try:
            # Read bytes until null terminator or max_length limit
            data = []
            current_ea = ea

            for i in range(max_length):
                byte_val = ida_bytes.get_byte(current_ea)
                if byte_val == 0:  # Null terminator
                    break
                data.append(byte_val)
                current_ea += 1

            if data:
                try:
                    # Convert bytes to string
                    string_data = bytes(data)
                    decoded_string = string_data.decode('utf-8', errors='replace')
                    return True, decoded_string
                except (UnicodeDecodeError, ValueError):
                    # Try latin-1 as fallback
                    try:
                        decoded_string = string_data.decode('latin-1', errors='replace')
                        return True, decoded_string
                    except (UnicodeDecodeError, ValueError):
                        return False, ''
            else:
                return False, ''
        except Exception:
            self._log_error('get_cstring', ea, 'Failed to get C string')
            return False, ''

    def get_unicode_string(self, ea: ea_t, max_length: int = None) -> Tuple[bool, str]:
        """
        Gets a Unicode string from the specified address.

        Args:
            ea: The effective address.
            max_length: Maximum string length to read.

        Returns:
            A pair of (success flag, string).
        """
        try:
            if max_length is None:
                # Try to get string length from IDA's analysis
                str_len = ida_bytes.get_max_strlit_length(ea, ida_nalt.STRTYPE_C16)
                if str_len <= 0:
                    str_len = 512  # Default max length for Unicode
            else:
                str_len = max_length

            string_data = ida_bytes.get_strlit_contents(ea, str_len, ida_nalt.STRTYPE_C16)
            if string_data is not None:
                try:
                    # Decode UTF-16 bytes to string
                    decoded_string = string_data.decode('utf-16le', errors='replace')
                    return True, decoded_string
                except (UnicodeDecodeError, AttributeError):
                    # Try UTF-16 BE as fallback
                    try:
                        decoded_string = string_data.decode('utf-16be', errors='replace')
                        return True, decoded_string
                    except (UnicodeDecodeError, AttributeError):
                        return False, ''
            else:
                return False, ''
        except Exception:
            self._log_error('get_unicode_string', ea, 'Failed to get Unicode string')
            return False, ''

    # Utility methods
    def get_original_bytes(self, ea: ea_t, size: int) -> Tuple[bool, bytes]:
        """
        Gets the original bytes before any patches by reading individual bytes.

        Args:
            ea: The effective address.
            size: Number of bytes to read.

        Returns:
            A pair of (success flag, original bytes).
        """
        try:
            original_bytes = []
            for i in range(size):
                try:
                    orig_byte = ida_bytes.get_original_byte(ea + i)
                    original_bytes.append(orig_byte & 0xFF)  # Ensure it's a byte value
                except Exception:
                    # If we can't get original byte, try current byte
                    try:
                        current_byte = ida_bytes.get_byte(ea + i)
                        original_bytes.append(current_byte)
                    except Exception:
                        # If both fail, return what we have so far
                        break

            if original_bytes:
                return True, bytes(original_bytes)
            else:
                return False, b''
        except Exception:
            self._log_error(
                'get_original_bytes', ea, f'Failed to get original bytes (size={size})'
            )
            return False, b''

    def has_user_name(self, ea: ea_t) -> bool:
        """
        Checks if the address has a user-defined name.

        Args:
            ea: The effective address.

        Returns:
            True if has user name, False otherwise.
        """
        try:
            return ida_name.has_user_name(ida_bytes.get_flags(ea))
        except Exception:
            self._log_error('has_user_name', ea, 'Failed to check if has user name')
            return False

    def get_flags(self, ea: ea_t) -> int:
        """
        Gets the flags for the specified address.

        Args:
            ea: The effective address.

        Returns:
            Flags value.
        """
        try:
            return ida_bytes.get_flags(ea)
        except Exception:
            self._log_error('get_flags', ea, 'Failed to get flags')
            return 0

    def set_flags(self, ea: ea_t, flags: int) -> bool:
        """
        Sets the flags for the specified address.

        Args:
            ea: The effective address.
            flags: Flags to set.

        Returns:
            True if successful, False otherwise.
        """
        try:
            ida_bytes.set_flags(ea, flags)
            return True
        except Exception:
            self._log_error('set_flags', ea, f'Failed to set flags (flags={flags})')
            return False

    # Navigation helpers
    def next_head(self, ea: ea_t, max_ea: ea_t = None) -> ea_t:
        """
        Gets the next head (start of data item) after the specified address.

        Args:
            ea: The effective address.
            max_ea: Maximum address to search.

        Returns:
            Address of next head, or BADADDR if not found.
        """
        try:
            if max_ea is None:
                max_ea = self.m_database.maximum_ea
            return ida_bytes.next_head(ea, max_ea)
        except Exception:
            self._log_error('next_head', ea, 'Failed to get next head')
            return BADADDR

    def prev_head(self, ea: ea_t, min_ea: ea_t = None) -> ea_t:
        """
        Gets the previous head (start of data item) before the specified address.

        Args:
            ea: The effective address.
            min_ea: Minimum address to search.

        Returns:
            Address of previous head, or BADADDR if not found.
        """
        try:
            if min_ea is None:
                min_ea = self.m_database.minimum_ea
            return ida_bytes.prev_head(ea, min_ea)
        except Exception:
            self._log_error('prev_head', ea, 'Failed to get previous head')
            return BADADDR

    def next_addr(self, ea: ea_t) -> ea_t:
        """
        Gets the next valid address after the specified address.

        Args:
            ea: The effective address.

        Returns:
            Next valid address.
        """
        try:
            return ida_bytes.next_addr(ea)
        except Exception:
            self._log_error('next_addr', ea, 'Failed to get next address')
            return BADADDR

    def prev_addr(self, ea: ea_t) -> ea_t:
        """
        Gets the previous valid address before the specified address.

        Args:
            ea: The effective address.

        Returns:
            Previous valid address.
        """
        try:
            return ida_bytes.prev_addr(ea)
        except Exception:
            self._log_error('prev_addr', ea, 'Failed to get previous address')
            return BADADDR

    def check_flags(self, ea: ea_t, flag_mask: ByteFlags) -> bool:
        """
        Checks if the specified flags are set at the given address.

        Args:
            ea: The effective address.
            flag_mask: ByteFlags enum value(s) to check.

        Returns:
            True if all specified flags are set, False otherwise.
        """
        try:
            flags = ida_bytes.get_flags(ea)
            return (flags & flag_mask) == flag_mask
        except Exception:
            self._log_error('check_flags', ea, f'Failed to check flags (mask={flag_mask})')
            return False

    def has_any_flags(self, ea: ea_t, flag_mask: ByteFlags) -> bool:
        """
        Checks if any of the specified flags are set at the given address.

        Args:
            ea: The effective address.
            flag_mask: ByteFlags enum value(s) to check.

        Returns:
            True if any of the specified flags are set, False otherwise.
        """
        try:
            flags = ida_bytes.get_flags(ea)
            return (flags & flag_mask) != 0
        except Exception:
            self._log_error('has_any_flags', ea, f'Failed to check any flags (mask={flag_mask})')
            return False

    def get_data_type_from_flags(self, flags: int) -> str:
        """
        Gets the data type string from flags using ByteFlags enum.

        Args:
            flags: Flags value to analyze.

        Returns:
            String representation of the data type.
        """
        try:
            # Check specific data types first (more specific flags)
            if flags & ByteFlags.STRLIT:
                return 'string'
            elif flags & ByteFlags.STRUCT:
                return 'struct'
            elif flags & ByteFlags.ALIGN:
                return 'align'
            elif flags & ByteFlags.FLOAT:
                return 'float'
            elif flags & ByteFlags.DOUBLE:
                return 'double'
            elif flags & ByteFlags.QWORD:
                return 'qword'
            elif flags & ByteFlags.DWORD:
                return 'dword'
            elif flags & ByteFlags.WORD:
                return 'word'
            elif flags & ByteFlags.BYTE:
                return 'byte'
            elif flags & ByteFlags.CODE:
                return 'code'
            elif flags & ByteFlags.DATA:
                return 'data'
            else:
                return 'unknown'
        except Exception:
            return 'unknown'
