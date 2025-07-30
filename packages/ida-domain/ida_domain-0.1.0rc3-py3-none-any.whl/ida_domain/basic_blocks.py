from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import ida_gdl

from .decorators import check_db_open, decorate_all_methods

if TYPE_CHECKING:
    from ida_funcs import func_t
    from ida_gdl import qbasic_block_t
    from idadex import ea_t

    from .database import Database


logger = logging.getLogger(__name__)


class _FlowChart(ida_gdl.FlowChart):
    """
    Flowchart class used to analyze and iterate through basic blocks within
    functions or address ranges.
    """

    def __init__(self, f=None, bounds=None, flags=0):
        super().__init__(f, bounds, flags)

    def _getitem(self, index):
        """
        Internal method to access flowchart items by index.

        Args:
            index: The index of the basic block to retrieve.

        Returns:
            The basic block at the specified index.
        """
        return self._q[index]


@decorate_all_methods(check_db_open)
class BasicBlocks:
    """
    Interface for working with basic blocks in functions.

    Basic blocks are sequences of instructions with a single entry point and single exit point,
    used for control flow analysis and optimization.
    """

    def __init__(self, database: 'Database'):
        """
        Constructs a basic block handler for the given database.

        Args:
            database: Reference to the active IDA database.
        """
        self.m_database = database

    def get_instructions(self, block: 'qbasic_block_t'):
        """
        Retrieves the instructions within a given basic block.

        Args:
            block: The basic block to analyze.

        Returns:
            An instruction iterator for the block.
            Returns an empty iterator if the block is invalid.
        """
        if block is None or not hasattr(block, 'start_ea') or not hasattr(block, 'end_ea'):
            # Return empty iterator for invalid blocks (missing required address attributes)
            logger.debug('Invalid basic block provided - missing start_ea or end_ea attributes')
            return self.m_database.instructions.get_between(0, 0)

        return self.m_database.instructions.get_between(block.start_ea, block.end_ea)

    def get_from_function(self, func: 'func_t', flags=0):
        """
        Retrieves the basic blocks within a given function.

        Args:
            func: The function to retrieve basic blocks from.
            flags: Optional qflow_chart_t flags for flowchart generation (default: 0).

        Returns:
            An iterable flowchart containing the basic blocks of the function.
        """
        return _FlowChart(func, None, flags)

    def get_between(self, start: 'ea_t', end: 'ea_t', flags=0):
        """
        Retrieves the basic blocks within a given address range.

        Args:
            start: The start address of the range.
            end: The end address of the range.
            flags: Optional qflow_chart_t flags for flowchart generation (default: 0).

        Returns:
            An iterable flowchart containing the basic blocks within the specified range.
        """
        return _FlowChart(None, (start, end), flags)
