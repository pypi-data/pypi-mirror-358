from __future__ import annotations

import logging
from enum import Enum
from typing import TYPE_CHECKING, Iterator, Tuple

import ida_bytes
from ida_ida import inf_get_max_ea, inf_get_min_ea
from ida_idaapi import BADADDR

from .decorators import check_db_open, decorate_all_methods

if TYPE_CHECKING:
    from .database import Database

logger = logging.getLogger(__name__)


class CommentKind(Enum):
    """
    Enumeration for IDA comment types.
    """

    REGULAR = 'regular'
    REPEATABLE = 'repeatable'
    ALL = 'all'


@decorate_all_methods(check_db_open)
class Comments:
    """
    Provides access to user-defined comments in the IDA database.

    IDA supports two types of comments:
    - Regular comments: Displayed at specific addresses
    - Repeatable comments: Displayed at all references to the same address
    """

    def __init__(self, database: 'Database'):
        """
        Constructs a comment manager for the given database.

        Args:
            database: Reference to the active IDA database.
        """
        self.m_database = database

    def get(self, ea: int, comment_kind: CommentKind = CommentKind.REGULAR) -> str | None:
        """
        Retrieves the comment at the specified address.

        Args:
            ea: The effective address.
            comment_kind: Type of comment to retrieve (REGULAR or REPEATABLE).

        Returns:
            The comment string, or None if no comment exists.
        """
        repeatable = comment_kind == CommentKind.REPEATABLE
        comment = ida_bytes.get_cmt(ea, repeatable)
        return comment if comment else None

    def get_any(self, ea: int) -> Tuple[bool, str]:
        """
        Retrieves any comment at the specified address, checking both regular and repeatable.

        Args:
            ea: The effective address.

        Returns:
            A tuple (success, comment string). If no comment exists, success is False.
        """
        # Try regular comment first
        comment = ida_bytes.get_cmt(ea, False)
        if comment:
            return (True, comment)

        # Try repeatable comment if no regular comment exists
        rep_comment = ida_bytes.get_cmt(ea, True)
        if rep_comment:
            return (True, rep_comment)

        return (False, '')

    def set(self, ea: int, comment: str, comment_kind: CommentKind = CommentKind.REGULAR) -> bool:
        """
        Sets a comment at the specified address.

        Args:
            ea: The effective address.
            comment: The comment text to assign.
            comment_kind: Type of comment to set (REGULAR or REPEATABLE).

        Returns:
            True if the comment was successfully set, False otherwise.
        """
        repeatable = comment_kind == CommentKind.REPEATABLE
        return ida_bytes.set_cmt(ea, comment, repeatable)

    def delete(self, ea: int, comment_kind: CommentKind = CommentKind.REGULAR) -> bool:
        """
        Deletes a comment at the specified address.

        Args:
            ea: The effective address.
            comment_kind: Type of comment to delete (REGULAR or REPEATABLE).

        Returns:
            True if the comment was successfully deleted, False otherwise.
        """
        repeatable = comment_kind == CommentKind.REPEATABLE
        return ida_bytes.set_cmt(ea, '', repeatable)

    def get_all(
        self, comment_kind: CommentKind = CommentKind.REGULAR
    ) -> Iterator[Tuple[int, str, bool]]:
        """
        Creates an iterator for comments in the database.

        Args:
            comment_kind: Type of comments to retrieve:
                - CommentType.REGULAR: Only regular comments
                - CommentType.REPEATABLE: Only repeatable comments
                - CommentType.ALL: Both regular and repeatable comments

        Yields:
            Tuples of (address, comment_text, is_repeatable) for each comment found.
        """
        current = inf_get_min_ea()
        max_ea = inf_get_max_ea()

        while current < max_ea:
            # Check for regular comment
            if comment_kind in [CommentKind.REGULAR, CommentKind.ALL]:
                regular_comment = ida_bytes.get_cmt(current, False)
                if regular_comment:
                    yield (current, regular_comment, False)

            # Check for repeatable comment
            if comment_kind in [CommentKind.REPEATABLE, CommentKind.ALL]:
                repeatable_comment = ida_bytes.get_cmt(current, True)
                if repeatable_comment:
                    yield (current, repeatable_comment, True)

            # Move to next head (instruction or data)
            next_addr = ida_bytes.next_head(current, max_ea)
            if next_addr == current or next_addr == BADADDR:
                # Prevent infinite loop if next_head fails to advance
                logger.warning(f'Failed to advance from address 0x{current:x}, stopping iteration')
                break
            current = next_addr
