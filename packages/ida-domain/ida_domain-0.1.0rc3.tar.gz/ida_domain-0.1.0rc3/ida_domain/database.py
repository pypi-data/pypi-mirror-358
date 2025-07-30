from __future__ import annotations

import logging
from datetime import datetime
from typing import TYPE_CHECKING, Dict, List, Optional

import ida_ida
import ida_idaapi
import ida_kernwin
import ida_loader
import ida_nalt
from idadex import ea_t

from .basic_blocks import BasicBlocks
from .bytes import Bytes
from .comments import Comments
from .decorators import check_db_open
from .entries import Entries
from .functions import Functions
from .heads import Heads
from .instructions import Instructions
from .names import Names
from .segments import Segments
from .signature_files import SignatureFiles
from .strings import Strings
from .types import Types
from .xrefs import Xrefs

if TYPE_CHECKING:
    from .basic_blocks import BasicBlocks
    from .instructions import Instructions


logger = logging.getLogger(__name__)


class Database:
    """
    Provides access and control over the loaded IDA database.

    Can be used as a context manager for automatic resource cleanup:

    Example:
        # Open and automatically close a database
        with Database() as db:
            if db.open("path/to/file.exe", save_on_close=True):
                # Work with the database
                print(f"Loaded: {db.path}")
        # Database is automatically closed here

        # Or use without context manager
        db = Database()
        if db.open("path/to/file.exe", save_on_close=True):
            # Work with database
            db.close()  # Uses save_on_close=True automatically
    """

    # List of property names that should be included in metadata
    _metadata_properties = [
        'path',
        'module',
        'base_address',
        'filesize',
        'md5',
        'sha256',
        'crc32',
        'architecture',
        'bitness',
        'format',
        'load_time',
    ]

    def __init__(self):
        """
        Constructs a new interface to the IDA database.

        Note:
            When running inside IDA, this refers to the currently open database.
            Use open() to load a new database when using IDA as a library.
        """
        self.save_on_close = False

    def __enter__(self) -> 'Database':
        """
        Enter the context manager.

        Returns:
            The Database instance for use in the with statement.
        """
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        """
        Exit the context manager.

        Automatically closes the database if running as a library and save_on_close is enabled.

        Args:
            exc_type: Exception type if an exception occurred, None otherwise.
            exc_value: Exception instance if an exception occurred, None otherwise.
            traceback: Traceback object if an exception occurred, None otherwise.

        Returns:
            False to allow exceptions to propagate (does not suppress exceptions).
        """
        if self.is_open() and ida_kernwin.is_ida_library(None, 0, None):
            self.close(save=self.save_on_close)
        return False

    def open(
        self,
        db_path: str,
        db_args: Optional['Database.IdaCommandBuilder'] = None,
        save_on_close=False,
    ) -> bool:
        """
        Opens a database from the specified file path.

        Args:
            db_path: Path to the input file.
            db_args: Command builder responsible for passing arguments to IDA kernel.
            save_on_close: Default behavior for saving changes on close. Used automatically
            when exiting context manager, but can be overridden in explicit close() calls.

        Returns:
            True if the database was successfully opened, false otherwise.

        Note:
            This function is available only when running IDA as a library.
            When running inside the IDA GUI, simply construct a Database() instance
            to refer to the currently open database. Use is_open() to check if a
            database is loaded.
        """
        if ida_kernwin.is_ida_library(None, 0, None):
            run_auto_analysis = True if db_args is None else db_args.auto_analysis_enabled
            # We can open a new database only in the context of idalib
            import idapro

            res = idapro.open_database(
                db_path, run_auto_analysis, '' if db_args is None else db_args.build_args()
            )
            if res != 0:
                logger.error(f'{self.open.__qualname__}: Failed to open database {db_path}')
                return False
            self.save_on_close = save_on_close
            return True
        else:
            # No database available
            logger.error(
                f'{self.open.__qualname__}: Open is available only when running as a library.'
            )
            return False

    def is_open(self) -> bool:
        """
        Checks if the database is loaded.

        Returns:
            True if a database is open, false otherwise.
        """
        idb_path = ida_loader.get_path(ida_loader.PATH_TYPE_IDB)

        return idb_path is not None and len(idb_path) > 0

    @check_db_open
    def close(self, save: Optional[bool] = None) -> None:
        """
        Closes the currently open database.

        Args:
            save: If provided, saves/discards changes accordingly.
                  If None, uses the save_on_close setting from open().

        Note:
            This function is available only when running IDA as a library.
            When running inside the IDA GUI, we have no control on the database lifecycle.
        """
        # Use save_on_close as default if save parameter is not explicitly provided
        save_flag = save if save is not None else self.save_on_close

        if ida_kernwin.is_ida_library(None, 0, None):
            import idapro

            idapro.close_database(save_flag)
        else:
            logger.error(
                f'{self.close.__qualname__}: Close is available only when running as a library.'
            )

    @property
    @check_db_open
    def current_ea(self) -> ea_t:
        """
        The current effective address (equivalent to the "screen EA" in IDA GUI).
        """
        return ida_kernwin.get_screen_ea()

    @current_ea.setter
    @check_db_open
    def current_ea(self, ea: int) -> None:
        """
        Sets the current effective address (equivalent to the "screen EA" in IDA GUI).
        """
        if ida_kernwin.is_ida_library(None, 0, None):
            import idapro

            idapro.set_screen_ea(ea)
        else:
            ida_kernwin.jumpto(ea)

    @property
    @check_db_open
    def minimum_ea(self) -> ea_t:
        """
        The minimum effective address from this database.
        """
        return ida_ida.inf_get_min_ea()

    @property
    @check_db_open
    def maximum_ea(self) -> ea_t:
        """
        The maximum effective address from this database.
        """
        return ida_ida.inf_get_max_ea()

    @property
    @check_db_open
    def base_address(self) -> Optional[ea_t]:
        """
        The image base address of this database.
        """
        base_addr = ida_nalt.get_imagebase()
        return base_addr if base_addr != ida_idaapi.BADADDR else None

    # Individual metadata properties
    @property
    @check_db_open
    def path(self) -> Optional[str]:
        """The input file path."""
        input_path = ida_nalt.get_input_file_path()
        return input_path if input_path else None

    @property
    @check_db_open
    def module(self) -> Optional[str]:
        """The module name."""
        module_name = ida_nalt.get_root_filename()
        return module_name if module_name else None

    @property
    @check_db_open
    def filesize(self) -> Optional[int]:
        """The input file size."""
        file_size = ida_nalt.retrieve_input_file_size()
        return file_size if file_size > 0 else None

    @property
    @check_db_open
    def md5(self) -> Optional[str]:
        """The MD5 hash of the input file."""
        md5_hash = ida_nalt.retrieve_input_file_md5()
        return md5_hash.hex() if md5_hash else None

    @property
    @check_db_open
    def sha256(self) -> Optional[str]:
        """The SHA256 hash of the input file."""
        sha256_hash = ida_nalt.retrieve_input_file_sha256()
        return sha256_hash.hex() if sha256_hash else None

    @property
    @check_db_open
    def crc32(self) -> Optional[int]:
        """The CRC32 checksum of the input file."""
        crc32 = ida_nalt.retrieve_input_file_crc32()
        return crc32 if crc32 != 0 else None

    @property
    @check_db_open
    def architecture(self) -> Optional[str]:
        """The processor architecture."""
        arch = ida_ida.inf_get_procname()
        return arch if arch else None

    @property
    @check_db_open
    def bitness(self) -> Optional[int]:
        """The application bitness (32/64)."""
        bitness = ida_ida.inf_get_app_bitness()
        return bitness if bitness > 0 else None

    @property
    @check_db_open
    def format(self) -> Optional[str]:
        """The file format type."""
        file_format = ida_loader.get_file_type_name()
        return file_format if file_format else None

    @property
    @check_db_open
    def load_time(self) -> Optional[str]:
        """The database load time."""
        ctime = ida_nalt.get_idb_ctime()
        return datetime.fromtimestamp(ctime).strftime('%Y-%m-%d %H:%M:%S') if ctime else None

    @property
    @check_db_open
    def metadata(self) -> Dict[str, str]:
        """
        Map of key-value metadata about the current database.
        Dynamically built from all metadata properties.
        """
        metadata = {}

        for prop_name in self._metadata_properties:
            try:
                value = getattr(self, prop_name)
                if value is not None:
                    # Check if value is a number and convert to hex string
                    if isinstance(value, int):
                        metadata[prop_name] = f'0x{value:x}'
                    elif isinstance(value, str):
                        metadata[prop_name] = value
                    else:
                        # For other types, convert to string
                        metadata[prop_name] = str(value)
            except Exception:
                # Skip properties that might fail to access
                continue

        return metadata

    @property
    def segments(self) -> Segments:
        """Handler that provides access to memory segment-related operations."""
        return Segments(self)

    @property
    def functions(self) -> Functions:
        """Handler that provides access to function-related operations."""
        return Functions(self)

    @property
    def basic_blocks(self) -> BasicBlocks:
        """Handler that provides access to basic block-related operations."""
        return BasicBlocks(self)

    @property
    def instructions(self) -> Instructions:
        """Handler that provides access to instruction-related operations."""
        return Instructions(self)

    @property
    def comments(self) -> Comments:
        """Handler that provides access to user comment-related operations."""
        return Comments(self)

    @property
    def entries(self) -> Entries:
        """Handler that provides access to entries operations."""
        return Entries(self)

    @property
    def heads(self) -> Heads:
        """Handler that provides access to user heads operations."""
        return Heads(self)

    @property
    def strings(self) -> Strings:
        """Handler that provides access to string-related operations."""
        return Strings(self)

    @property
    def names(self) -> Names:
        """Handler that provides access to name-related operations."""
        return Names(self)

    @property
    def types(self) -> Types:
        """Handler that provides access to type-related operations."""
        return Types(self)

    @property
    def bytes(self) -> Bytes:
        """Handler that provides access to byte-level memory operations."""
        return Bytes(self)

    @property
    def signature_files(self) -> SignatureFiles:
        """Handler that provides access to signature file operations."""
        return SignatureFiles(self)

    @property
    def xrefs(self) -> Xrefs:
        """Handler that provides access to cross-reference (xref) operations."""
        return Xrefs(self)

    class IdaCommandBuilder:
        """
        Builder class for constructing IDA command line arguments.

        This class provides an interface to build IDA command line arguments
        for passing them in the database open call.

        Usage:
            builder = Database.IdaCommandBuilder()
            builder.auto_analysis(False).autonomous(True).set_loading_address(0x400000)
            args = builder.build_args()
        """

        def __init__(self):
            """Initialize the command builder with default values."""
            self._auto_analysis = True  # -a: Auto analysis enabled by default
            self._has_loading_address = False  # -b: Loading address not set
            self._loading_address = 0
            self._new_database = False  # -c: Don't create new database by default
            self._has_compiler = False  # -C: Compiler not set
            self._compiler = ''
            self._first_pass_directives = []  # -d: First pass configuration directives
            self._second_pass_directives = []  # -D: Second pass configuration directives
            self._disable_fpp = False  # -f: FPP instructions enabled by default
            self._has_entry_point = False  # -i: Entry point not set
            self._entry_point = 0
            self._jit_debugger = None  # -I: JIT debugger setting
            self._log_file = None  # -L: Log file not set
            self._disable_mouse = False  # -M: Mouse enabled by default
            self._plugin_options = None  # -O: Plugin options not set
            self._output_database = None  # -o: Output database not set
            self._processor = None  # -p: Processor type not set
            self._db_compression = None  # -P: Database compression ('compress', 'pack', 'no_pack')
            self._run_debugger = None  # -r: Debugger options not set
            self._load_resources = False  # -R: Don't load resources by default
            self._script_file = None  # -S: Script file not set
            self._script_args = []
            self._file_type = None  # -T: File type not set
            self._file_member = None
            self._empty_database = False  # -t: Don't create empty database by default
            self._windows_dir = None  # -W: Windows directory not set
            self._no_segmentation = False  # -x: Create segmentation by default
            self._debug_flags = 0  # -z: Debug flags not set

        def auto_analysis(self, enabled=True):
            """
            Control automatic analysis (-a switch).

            Args:
                enabled: If False, disables auto analysis (-a).
                        If True, enables auto analysis (-a-).

            Returns:
                Self for method chaining.
            """
            self._auto_analysis = enabled
            return self

        def set_loading_address(self, address: int):
            """
            Set the loading address (-b#### switch).

            Args:
                address: Loading address as a hexadecimal number, in paragraphs.
                        A paragraph is 16 bytes.

            Returns:
                Self for method chaining.
            """
            self._has_loading_address = True
            self._loading_address = address
            return self

        def new_database(self, enabled=True):
            """
            Disassemble a new file by deleting the old database (-c switch).

            Args:
                enabled: True to create a new database, deleting any existing one.

            Returns:
                Self for method chaining.
            """
            self._new_database = enabled
            return self

        def set_compiler(self, name: str, abi: str = ''):
            """
            Set compiler in format name:abi (-C#### switch).

            Args:
                name: Compiler name.
                abi: Application Binary Interface (optional).

            Returns:
                Self for method chaining.
            """
            self._has_compiler = True
            self._compiler = f'{name}:{abi}' if abi else name
            return self

        def add_first_pass_directive(self, directive: str):
            """
            Add a configuration directive for the first pass (-d switch).

            Configuration directives are processed at the first pass.
            Example: "VPAGESIZE=8192"

            Args:
                directive: Configuration directive string.

            Returns:
                Self for method chaining.
            """
            self._first_pass_directives.append(directive)
            return self

        def add_second_pass_directive(self, directive: str):
            """
            Add a configuration directive for the second pass (-D switch).

            Configuration directives are processed at the second pass.

            Args:
                directive: Configuration directive string.

            Returns:
                Self for method chaining.
            """
            self._second_pass_directives.append(directive)
            return self

        def disable_fpp_instructions(self, disabled=True):
            """
            Disable FPP (Floating Point Processor) instructions (-f switch).

            This option is specific to IBM PC only.

            Args:
                disabled: True to disable FPP instructions.

            Returns:
                Self for method chaining.
            """
            self._disable_fpp = disabled
            return self

        def set_entry_point(self, address: int):
            """
            Set the program entry point (-i#### switch).

            Args:
                address: Entry point address as hexadecimal number.

            Returns:
                Self for method chaining.
            """
            self._has_entry_point = True
            self._entry_point = address
            return self

        def set_jit_debugger(self, enabled=True):
            """
            Set IDA as just-in-time debugger (-I# switch).

            Args:
                enabled: True to enable (1), False to disable (0).

            Returns:
                Self for method chaining.
            """
            self._jit_debugger = int(enabled)
            return self

        def set_log_file(self, filename: str):
            """
            Set the name of the log file (-L#### switch).

            Args:
                filename: Path to the log file.

            Returns:
                Self for method chaining.
            """
            self._log_file = filename
            return self

        def disable_mouse(self, disabled=True):
            """
            Disable mouse support (-M switch).

            This option is for text mode only.

            Args:
                disabled: True to disable mouse support.

            Returns:
                Self for method chaining.
            """
            self._disable_mouse = disabled
            return self

        def set_plugin_options(self, options: str):
            """
            Set options to pass to plugins (-O#### switch).

            Note: This switch is not available in the IDA Home edition.

            Args:
                options: Options string to pass to plugins.

            Returns:
                Self for method chaining.
            """
            self._plugin_options = options
            return self

        def set_output_database(self, path: str):
            """
            Specify the output database path (-o#### switch).

            This automatically implies creating a new database (-c).

            Args:
                path: Path to the output database file.

            Returns:
                Self for method chaining.
            """
            self._output_database = path
            self._new_database = True  # Implies -c
            return self

        def set_processor(self, processor_type: str):
            """
            Set the processor type (-p#### switch).

            Args:
                processor_type: Processor type identifier.

            Returns:
                Self for method chaining.
            """
            self._processor = processor_type
            return self

        def compress_database(self):
            """
            Compress database to create zipped idb (-P+ switch).

            Returns:
                Self for method chaining.
            """
            self._db_compression = 'compress'
            return self

        def pack_database(self):
            """
            Pack database to create unzipped idb (-P switch).

            Returns:
                Self for method chaining.
            """
            self._db_compression = 'pack'
            return self

        def no_pack_database(self):
            """
            Do not pack database (-P- switch).

            Note: This is not recommended. See Abort command documentation.

            Returns:
                Self for method chaining.
            """
            self._db_compression = 'no_pack'
            return self

        def run_debugger(self, options: str = ''):
            """
            Immediately run the built-in debugger (-r### switch).

            Args:
                options: Debugger options string.

            Returns:
                Self for method chaining.
            """
            self._run_debugger = options
            return self

        def load_resources(self, enabled=True):
            """
            Load MS Windows exe file resources (-R switch).

            Args:
                enabled: True to load Windows resources.

            Returns:
                Self for method chaining.
            """
            self._load_resources = enabled
            return self

        def run_script(self, script_file: str, args: List[str] = []):
            """
            Execute a script file when the database is opened (-S### switch).

            The script file extension determines which extlang will run the script.
            Command line arguments can be passed after the script name.

            The passed parameters are stored in the "ARGV" global IDC variable:
            - Use "ARGV.count" to determine the number of arguments
            - The first argument "ARGV[0]" contains the script name

            Note: This switch is not available in the IDA Home edition.

            Args:
                script_file: Path to the script file.
                args: List of command line arguments to pass to the script.

            Returns:
                Self for method chaining.
            """
            self._script_file = script_file
            self._script_args = args
            return self

        def set_file_type(self, file_type: str, member: str = ''):
            """
            Interpret the input file as the specified file type (-T### switch).

            The file type is specified as a prefix of a file type visible in the
            'load file' dialog box. IDA does not display the 'load file' dialog
            when this option is used.

            To specify archive member, put it after the colon character.
            You can specify nested paths: -T<ftype>[:<member>{:<ftype>:<member>}[:<ftype>]]

            Examples:
                - set_file_type("ZIP", "classes.dex") -> -TZIP:classes.dex

            Args:
                file_type: File type prefix.
                member: Archive member name (optional).

            Returns:
                Self for method chaining.
            """
            self._file_type = file_type
            self._file_member = member
            return self

        def empty_database(self, enabled=True):
            """
            Create an empty database (-t switch).

            Args:
                enabled: True to create an empty database.

            Returns:
                Self for method chaining.
            """
            self._empty_database = enabled
            return self

        def set_windows_directory(self, directory: str):
            """
            Specify MS Windows directory (-W### switch).

            Args:
                directory: Path to Windows directory.

            Returns:
                Self for method chaining.
            """
            self._windows_dir = directory
            return self

        def no_segmentation(self, enabled=True):
            """
            Do not create segmentation (-x switch).

            Used in pair with Dump database command.
            This switch affects EXE and COM format files only.

            Args:
                enabled: True to disable segmentation.

            Returns:
                Self for method chaining.
            """
            self._no_segmentation = enabled
            return self

        def set_debug_flags(self, flags):
            """
            Set debug flags (-z switch).

            Debug flags can be specified as an integer or list of flag names.

            Available debug flags:
                - drefs (0x00000001): Data references
                - offsets (0x00000002): Offsets
                - flirt (0x00000004): FLIRT signatures
                - idp (0x00000008): IDP module
                - ldr (0x00000010): Loader module
                - plugin (0x00000020): Plugin module
                - ids (0x00000040): IDS files
                - config (0x00000080): Config file
                - heap (0x00000100): Check heap
                - licensing (0x00000200): Licensing
                - demangler (0x00000400): Demangler
                - queue (0x00000800): Queue
                - rollback (0x00001000): Rollback
                - already_data_or_code (0x00002000): Already data or code
                - type_system (0x00004000): Type system
                - notifications (0x00008000): Show all notifications
                - debugger (0x00010000): Debugger
                - debugger_appcall (0x00020000): Debugger appcall
                - source_debugger (0x00040000): Source-level debugger
                - accessibility (0x00080000): Accessibility
                - network (0x00100000): Network
                - stack_analysis (0x00200000): Full stack analysis (simplex method)
                - debug_info (0x00400000): Handling of debug info (e.g. pdb, dwarf)
                - lumina (0x00800000): Lumina

            Args:
                flags: Integer value or list of flag names.

            Returns:
                Self for method chaining.
            """
            if isinstance(flags, int):
                self._debug_flags = flags
            elif isinstance(flags, list):
                self._debug_flags = self._parse_debug_flag_names(flags)
            return self

        def build_args(self):
            """
            Build the complete command line arguments string.

            Constructs the command line arguments based on all the configured options.
            This method processes all the settings and generates the appropriate
            IDA command line switches.

            Returns:
                String containing all command line arguments separated by spaces.
            """
            args = []

            # -a: Disable auto analysis
            if not self._auto_analysis:
                args.append('-a')
            # -b####: Loading address in hexadecimal paragraphs
            if self._has_loading_address:
                args.append(f'-b{self._loading_address:X}')
            # -c: Create new database
            if self._new_database:
                args.append('-c')
            # -C####: Set compiler
            if self._has_compiler:
                args.append(f'-C{self._compiler}')
            # -d: First pass directives
            args += [f'-d{d}' for d in self._first_pass_directives]
            # -D: Second pass directives
            args += [f'-D{d}' for d in self._second_pass_directives]
            # -f: Disable FPP instructions
            if self._disable_fpp:
                args.append('-f')
            # -i####: Entry point in hexadecimal
            if self._has_entry_point:
                args.append(f'-i{self._entry_point:X}')
            # -I#: JIT debugger setting
            if self._jit_debugger is not None:
                args.append(f'-I{self._jit_debugger}')
            # -L####: Log file
            if self._log_file:
                args.append(f'-L{self._log_file}')
            # -M: Disable mouse
            if self._disable_mouse:
                args.append('-M')
            # -o####: Output database
            if self._output_database:
                args.append(f'-o{self._output_database}')
            # -O####: Plugin options
            if self._plugin_options:
                args.append(f'-O{self._plugin_options}')
            # -p####: Processor type
            if self._processor:
                args.append(f'-p{self._processor}')
            # -P+/-: Database compression
            if self._db_compression:
                comp_map = {'compress': '-P+', 'pack': '-P', 'no_pack': '-P-'}
                args.append(comp_map[self._db_compression])
            # -r###: Run debugger
            if self._run_debugger is not None:
                args.append(f'-r{self._run_debugger}')
            # -R: Load resources
            if self._load_resources:
                args.append('-R')
            # -S###: Script execution
            if self._script_file:
                full = self._script_file + ''.join(
                    f' {self._quote_if_needed(arg)}' for arg in self._script_args
                )
                args.append(f'-S"{full}"' if self._script_args else f'-S{self._script_file}')
            # -t: Empty database
            if self._empty_database:
                args.append('-t')
            # -T###: File type specification
            if self._file_type:
                type_spec = f'-T{self._file_type}'
                if self._file_member:
                    type_spec += f':{self._file_member}'
                args.append(type_spec)
            # -W###: Windows directory
            if self._windows_dir:
                args.append(f'-W{self._windows_dir}')
            # -x: No segmentation
            if self._no_segmentation:
                args.append('-x')
            # -z: Debug flags in hexadecimal
            if self._debug_flags != 0:
                args.append(f'-z{self._debug_flags:X}')

            return ' '.join(args)

        def _quote_if_needed(self, s: str) -> str:
            """
            Quote a string if it contains spaces.

            Used internally for script arguments that may contain spaces.

            Args:
                s: String to potentially quote.

            Returns:
                Quoted string if it contains spaces, original string otherwise.
            """
            return f'"{s}"' if ' ' in s else s

        def _parse_debug_flag_names(self, flag_names: List[str]) -> int:
            """
            Parse debug flag names into their corresponding integer values.

            Converts a list of debug flag names into a combined integer value
            by OR-ing the individual flag values together.

            Args:
                flag_names: List of debug flag names (see set_debug_flags documentation).

            Returns:
                Combined integer value of all specified debug flags.
            """
            flag_map = {
                'drefs': 0x00000001,  # Data references
                'offsets': 0x00000002,  # Offsets
                'flirt': 0x00000004,  # FLIRT signatures
                'idp': 0x00000008,  # IDP module
                'ldr': 0x00000010,  # Loader module
                'plugin': 0x00000020,  # Plugin module
                'ids': 0x00000040,  # IDS files
                'config': 0x00000080,  # Config file
                'heap': 0x00000100,  # Check heap
                'licensing': 0x00000200,  # Licensing
                'demangler': 0x00000400,  # Demangler
                'queue': 0x00000800,  # Queue
                'rollback': 0x00001000,  # Rollback
                'already_data_or_code': 0x00002000,  # Already data or code
                'type_system': 0x00004000,  # Type system
                'notifications': 0x00008000,  # Show all notifications
                'debugger': 0x00010000,  # Debugger
                'debugger_appcall': 0x00020000,  # Debugger appcall
                'source_debugger': 0x00040000,  # Source-level debugger
                'accessibility': 0x00080000,  # Accessibility
                'network': 0x00100000,  # Network
                'stack_analysis': 0x00200000,  # Full stack analysis (simplex method)
                'debug_info': 0x00400000,  # Handling of debug info (e.g. pdb, dwarf)
                'lumina': 0x00800000,  # Lumina
            }

            value = 0
            for name in flag_names:
                if name in flag_map:
                    value |= flag_map[name]
                else:
                    logger.error(
                        f"{self._parse_debug_flag_names.__qualname__}: Unknown debug flag '{name}'"
                    )
            return value

        @property
        def auto_analysis_enabled(self) -> bool:
            """
            Check if auto analysis is enabled.

            Returns:
                True if auto analysis is enabled, False otherwise.
            """
            return self._auto_analysis
