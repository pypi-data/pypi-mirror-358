from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Iterator, List, Optional

import ida_bytes
import ida_funcs
import ida_hexrays
import ida_lines
import ida_name
import ida_typeinf
from ida_funcs import func_t
from ida_idaapi import BADADDR
from idadex import ea_t

from .decorators import check_db_open, check_func_valid, decorate_all_methods

if TYPE_CHECKING:
    from .database import Database

logger = logging.getLogger(__name__)


@decorate_all_methods(check_db_open)
class Functions:
    """
    Provides access to function-related operations within the IDA database.

    This class handles function discovery, analysis, manipulation, and provides
    access to function properties like names, signatures, basic blocks, and pseudocode.
    """

    def __init__(self, database: 'Database'):
        """
        Constructs a functions handler for the given database.

        Args:
            database: Reference to the active IDA database.
        """
        self.m_database = database

    def get_between(self, start: ea_t, end: ea_t) -> Iterator[func_t]:
        """
        Retrieves functions within the specified address range.

        Args:
            start: Start address of the range (inclusive).
            end: End address of the range (exclusive).

        Yields:
            Function objects whose start address falls within the specified range.
        """
        for i in range(ida_funcs.get_func_qty()):
            func = ida_funcs.getn_func(i)
            if func is None:
                continue

            if func.start_ea >= end:
                # Functions are typically ordered by address, so we can break early
                break

            if start <= func.start_ea < end:
                yield func

    def get_all(self) -> Iterator[func_t]:
        """
        Retrieves all functions in the database.

        Returns:
            An iterator over all functions in the database.
        """
        from ida_ida import inf_get_max_ea, inf_get_min_ea

        return self.get_between(inf_get_min_ea(), inf_get_max_ea())

    def get_at(self, ea: ea_t) -> Optional[func_t]:
        """
        Retrieves the function that contains the given address.

        Args:
            ea: An effective address within the function body.

        Returns:
            The function object containing the address,
            or None if no function exists at that address.
        """
        return ida_funcs.get_func(ea)

    @check_func_valid
    def set_name(self, func: func_t, name: str, auto_correct: bool = True) -> bool:
        """
        Renames the given function.

        Args:
            func: The function instance.
            name: The new name to assign to the function.
            auto_correct: If True, allows IDA to replace invalid characters automatically.

        Returns:
            True if the function was successfully renamed, False otherwise.
        """
        if not name.strip():
            logger.error('set_name: Empty name provided')
            return False

        flags = ida_name.SN_NOCHECK if auto_correct else ida_name.SN_CHECK
        return ida_name.set_name(func.start_ea, name, flags)

    @check_func_valid
    def get_basic_blocks(self, func: func_t):
        """
        Retrieves the basic blocks that compose the given function.

        Args:
            func: The function instance.

        Returns:
            An iterator over the function's basic blocks, or empty iterator if function is invalid.
        """
        return self.m_database.basic_blocks.get_from_function(func)

    @check_func_valid
    def get_instructions(self, func: func_t):
        """
        Retrieves all instructions within the given function.

        Args:
            func: The function instance.

        Returns:
            An iterator over all instructions in the function,
            or empty iterator if function is invalid.
        """
        return self.m_database.instructions.get_between(func.start_ea, func.end_ea)

    @check_func_valid
    def get_disassembly(self, func: func_t) -> List[str]:
        """
        Retrieves the disassembly lines for the given function.

        Args:
            func: The function instance.

        Returns:
            A list of strings, each representing a line of disassembly.
            Returns empty list if function is invalid.
        """
        lines = []
        ea = func.start_ea

        while ea != BADADDR and ea < func.end_ea:
            line = ida_lines.generate_disasm_line(
                ea, ida_lines.GENDSM_MULTI_LINE | ida_lines.GENDSM_REMOVE_TAGS
            )
            if line:
                lines.append(line)

            ea = ida_bytes.next_head(ea, func.end_ea)

        return lines

    @check_func_valid
    def get_pseudocode(self, func: func_t, remove_tags: bool = True) -> List[str]:
        """
        Retrieves the decompiled pseudocode of the given function.

        Args:
            func: The function instance.
            remove_tags: If True, removes IDA color/formatting tags from the output.

        Returns:
            A list of strings, each representing a line of pseudocode. Returns empty list if
            function is invalid or decompilation fails.
        """
        try:
            # Attempt to decompile the function
            cfunc = ida_hexrays.decompile(func.start_ea)
            if cfunc is None:
                logger.debug(f'Failed to decompile function at 0x{func.start_ea:x}')
                return []

            # Extract pseudocode lines
            pseudocode = []
            sv = cfunc.get_pseudocode()
            for i in range(len(sv)):
                line = sv[i].line
                if remove_tags:
                    line = ida_lines.tag_remove(line)
                pseudocode.append(line)
            return pseudocode

        except Exception as e:
            logger.error(f'Exception during decompilation of function at 0x{func.start_ea:x}: {e}')
            return []

    @check_func_valid
    def get_microcode(self, func: func_t, remove_tags: bool = True) -> List[str]:
        """
        Retrieves the microcode of the given function.

        Args:
            func: The function instance.
            remove_tags: If True, removes IDA color/formatting tags from the output.

        Returns:
            A list of strings, each representing a line of microcode. Returns empty list if
            function is invalid or decompilation fails.
        """
        mbr = ida_hexrays.mba_ranges_t(func)
        hf = ida_hexrays.hexrays_failure_t()
        ml = ida_hexrays.mlist_t()
        mba = ida_hexrays.gen_microcode(
            mbr, hf, ml, ida_hexrays.DECOMP_WARNINGS, ida_hexrays.MMAT_GENERATED
        )

        mba.build_graph()
        total = mba.qty
        for i in range(total):
            if i == 0:
                continue

            block = mba.get_mblock(i)
            if block.type == ida_hexrays.BLT_STOP:
                continue

            vp = ida_hexrays.qstring_printer_t(None, True)
            block._print(vp)
            src = vp.s
            lines = src.splitlines()

            if not remove_tags:
                return lines

            microcode = []
            for line in lines:
                new_line = ida_lines.tag_remove(line)
                if new_line:
                    microcode.append(new_line)

            return microcode

    @check_func_valid
    def get_signature(self, func: func_t) -> str:
        """
        Retrieves the function's type signature.

        Args:
            func: The function instance.

        Returns:
            The function signature as a string,
            or empty string if unavailable or function is invalid.
        """
        try:
            signature = ida_typeinf.idc_get_type(func.start_ea)
            return signature or ''
        except Exception:
            return ''

    @check_func_valid
    def matches_signature(self, func: func_t, signature: str) -> bool:
        """
        Checks if a function matches the given signature.

        Args:
            func: The function instance.
            signature: The signature string to compare against.

        Returns:
            True if the function signature matches, False otherwise.
        """
        if not signature.strip():
            return False

        return self.get_signature(func) == signature

    @check_func_valid
    def get_name(self, func: func_t) -> str:
        """
        Retrieves the function's name.

        Args:
            func: The function instance.

        Returns:
            The function name as a string, or empty string if no name is set.
        """
        name = self.m_database.names.get_at(func.start_ea)
        return name if name is not None else ''

    def create(self, ea: ea_t) -> bool:
        """
        Creates a new function at the specified address.

        Args:
            ea: The effective address where the function should start.

        Returns:
            True if the function was successfully created, False otherwise.
        """
        return ida_funcs.add_func(ea)

    def remove(self, ea: ea_t) -> bool:
        """
        Removes the function at the specified address.

        Args:
            ea: The effective address of the function to remove.

        Returns:
            True if the function was successfully removed, False otherwise.
        """
        return ida_funcs.del_func(ea)

    @check_func_valid
    def get_callers(self, func: func_t) -> List[func_t]:
        """
        Gets all functions that call this function.

        Args:
            func: The function instance.

        Returns:
            List of calling functions.
        """
        callers = []
        caller_addrs = set()  # Use set to avoid duplicates

        # Get all call references to this function
        for xref in self.m_database.xrefs.get_calls_to(func.start_ea):
            # Get the function containing this call site
            caller_func = self.get_at(xref.frm)
            if caller_func and caller_func.start_ea not in caller_addrs:
                caller_addrs.add(caller_func.start_ea)
                callers.append(caller_func)

        return callers

    @check_func_valid
    def get_callees(self, func: func_t) -> List[func_t]:
        """
        Gets all functions called by this function.

        Args:
            func: The function instance.

        Returns:
            List of called functions.
        """
        callees = []
        callee_addrs = set()  # Use set to avoid duplicates

        # Iterate through all instructions in the function to find calls and jumps
        for inst in self.m_database.instructions.get_between(func.start_ea, func.end_ea):
            # Get call references from this instruction
            for xref in self.m_database.xrefs.get_calls_from(inst.ea):
                # Get the target function
                target_func = self.get_at(xref.to)
                if target_func and target_func.start_ea not in callee_addrs:
                    # Make sure we're not including the same function (recursive calls)
                    if target_func.start_ea != func.start_ea:
                        callee_addrs.add(target_func.start_ea)
                        callees.append(target_func)

            # Also get jump references for tail calls
            for xref in self.m_database.xrefs.get_jumps_from(inst.ea):
                # Get the target function
                target_func = self.get_at(xref.to)
                if target_func and target_func.start_ea not in callee_addrs:
                    # Make sure we're not including the same function (recursive calls)
                    if target_func.start_ea != func.start_ea:
                        callee_addrs.add(target_func.start_ea)
                        callees.append(target_func)

        return callees
