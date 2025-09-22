"""DLL injection utilities for security research and testing.

This module provides Windows DLL injection capabilities for educational
security research purposes, specifically for testing security mechanisms
in educational software like Respondus LockDown Browser.

Educational Context:
    This tool is designed for authorized security research and testing
    to understand how security mechanisms work in educational environments.
    Use only with proper authorization and for legitimate research purposes.
"""

import subprocess
from ctypes import byref, c_int, c_long, c_ulong, create_string_buffer, windll
from typing import Optional

from .logging_utils import get_security_logger, log_exceptions, setup_module_logging

# Module-level logging setup
logger = setup_module_logging(__name__)
security_logger = get_security_logger("dll_injection")


class DLLInjectionError(Exception):
    """Custom exception for DLL injection failures."""

    pass


class ProcessAccessError(Exception):
    """Custom exception for process access failures."""

    pass


class MemoryAllocationError(Exception):
    """Custom exception for memory allocation failures."""

    pass


class DLLInjector:
    """Windows DLL injection utility for security research.

    This class provides methods to inject DLLs into running processes
    for educational security testing purposes. All operations are logged
    comprehensively for audit and debugging purposes.

    Security Context:
        Designed for authorized testing of security mechanisms in
        educational software environments. Use responsibly and only
        with proper authorization.
    """

    # Windows API constants
    ACCESS_MASK: int = 0x000F0000 | 0x00100000 | 0x00000FFF  # PROCESS_ALL_ACCESS
    MEM_FLAGS: int = 0x00001000 | 0x00002000  # MEM_COMMIT | MEM_RESERVE
    FREE_MEM: int = 0x8000  # MEM_RELEASE
    RWX_PERMISSIONS: int = 0x40  # PAGE_EXECUTE_READWRITE

    def __init__(self) -> None:
        """Initialize the DLL injector with proper logging and state management."""
        logger.info("Initializing DLL injector for security research")
        security_logger.info("DLL injector created - authorized use only")

        self.k32 = windll.kernel32
        self.u32 = windll.user32
        self.process_id: c_ulong = c_ulong()
        self.proc_handle: Optional[int] = None

        logger.debug("DLL injector initialization complete")

    @log_exceptions(logger)
    def launch_target(self, exe_path: str) -> int:
        """Launch a target executable and return its process ID.

        Args:
            exe_path: Full path to the executable to launch

        Returns:
            Process ID of the launched process

        Raises:
            OSError: If the executable cannot be launched
            DLLInjectionError: If process launch fails
        """
        logger.info(f"Launching target executable: {exe_path}")
        security_logger.info(f"Starting process for security testing: {exe_path}")

        try:
            process = subprocess.Popen([exe_path], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
            pid = process.pid
            logger.info(f"Successfully launched target process with PID: {pid}")
            security_logger.info(f"Target process started successfully (PID: {pid})")
            return pid
        except OSError as e:
            logger.error(f"Failed to launch target executable {exe_path}: {str(e)}")
            security_logger.error(f"Process launch failed: {str(e)}")
            raise DLLInjectionError(f"Could not launch target: {str(e)}") from e

    @log_exceptions(logger)
    def attach_to_pid(self, pid: int) -> None:
        """Attach to a running process by process ID.

        Args:
            pid: Process ID to attach to

        Raises:
            ProcessAccessError: If the process cannot be accessed
            DLLInjectionError: If attachment fails
        """
        logger.info(f"Attempting to attach to process PID: {pid}")
        security_logger.info(f"Attaching to target process for security testing (PID: {pid})")

        # Clean up any existing connections first
        self.cleanup()

        self.process_id = c_ulong(pid)
        self.proc_handle = self.k32.OpenProcess(self.ACCESS_MASK, 0, pid)

        if not self.proc_handle:
            error_code = windll.kernel32.GetLastError()
            error_msg = f"Failed to open process {pid} (Error code: {error_code})"
            logger.error(error_msg)
            security_logger.error(f"Process access denied: {error_msg}")
            raise ProcessAccessError(error_msg)

        logger.info(f"Successfully attached to process PID: {pid}")
        security_logger.info(f"Process attachment successful (PID: {pid})")

    @log_exceptions(logger)
    def cleanup(self) -> None:
        """Clean up process handles and resources.

        Raises:
            DLLInjectionError: If cleanup fails
        """
        if self.proc_handle:
            logger.debug(f"Cleaning up process handle for PID: {self.process_id.value}")
            result = self.k32.CloseHandle(self.proc_handle)
            if not result:
                error_code = windll.kernel32.GetLastError()
                error_msg = f"Failed to close process handle (Error: {error_code})"
                logger.error(error_msg)
                raise DLLInjectionError(error_msg)

            logger.debug("Process handle cleaned up successfully")
            security_logger.debug("Process connection closed")

        self.proc_handle = None

    @log_exceptions(logger)
    def allocate_remote_buffer(self, data: bytes, length: int) -> int:
        """Allocate memory buffer in remote process.

        Args:
            data: Data to write to the allocated buffer
            length: Size of buffer to allocate

        Returns:
            Memory address of allocated buffer

        Raises:
            MemoryAllocationError: If memory allocation fails
        """
        logger.debug(f"Allocating remote buffer of {length} bytes")

        address = self.k32.VirtualAllocEx(self.proc_handle, None, c_int(length), self.MEM_FLAGS, self.RWX_PERMISSIONS)

        if not address:
            error_code = windll.kernel32.GetLastError()
            error_msg = f"Failed to allocate {length} bytes in remote process (Error: {error_code})"
            logger.error(error_msg)
            security_logger.error(f"Memory allocation failed: {error_msg}")
            raise MemoryAllocationError(error_msg)

        logger.debug(f"Successfully allocated buffer at address: 0x{address:08x}")
        self.write_to_memory(address, data)
        return address

    @log_exceptions(logger)
    def release_remote_buffer(self, addr: int, length: int) -> None:
        """Release memory buffer in remote process.

        Args:
            addr: Memory address to release
            length: Size of buffer (for logging purposes)

        Raises:
            MemoryAllocationError: If memory release fails
        """
        logger.debug(f"Releasing remote buffer at 0x{addr:08x} ({length} bytes)")

        if not self.k32.VirtualFreeEx(self.proc_handle, addr, c_int(0), self.FREE_MEM):
            error_code = windll.kernel32.GetLastError()
            error_msg = f"Failed to release memory at 0x{addr:08x} (Error: {error_code})"
            logger.error(error_msg)
            raise MemoryAllocationError(error_msg)

        logger.debug(f"Successfully released buffer at 0x{addr:08x}")

    @log_exceptions(logger)
    def get_func_address(self, dll: str, func: str) -> int:
        """Get the address of a function in a loaded DLL.

        Args:
            dll: Name of the DLL (e.g., 'kernel32.dll')
            func: Name of the function to locate

        Returns:
            Memory address of the function

        Raises:
            DLLInjectionError: If DLL or function cannot be found
        """
        logger.debug(f"Looking up function {func} in {dll}")

        module_base = self.k32.GetModuleHandleA(dll.encode("ascii"))
        if not module_base:
            error_code = windll.kernel32.GetLastError()
            error_msg = f"Failed to get handle for {dll} (Error: {error_code})"
            logger.error(error_msg)
            raise DLLInjectionError(error_msg)

        func_ptr = self.k32.GetProcAddress(module_base, func.encode("ascii"))
        if not func_ptr:
            error_code = windll.kernel32.GetLastError()
            error_msg = f"Failed to get address of {func} in {dll} (Error: {error_code})"
            logger.error(error_msg)
            raise DLLInjectionError(error_msg)

        logger.debug(f"Found {func} at address: 0x{func_ptr:08x}")
        return func_ptr

    @log_exceptions(logger)
    def run_remote_function(self, addr: int, arg_data: bytes) -> int:
        """Execute a function in the remote process.

        Args:
            addr: Address of the function to execute
            arg_data: Arguments to pass to the function

        Returns:
            Exit code returned by the remote function

        Raises:
            DLLInjectionError: If remote execution fails
        """
        logger.debug(f"Executing remote function at 0x{addr:08x} with {len(arg_data)} bytes of arguments")

        exit_code = c_long(0)
        arg_ptr = self.allocate_remote_buffer(arg_data, len(arg_data))

        try:
            thread = self.k32.CreateRemoteThread(self.proc_handle, None, None, c_long(addr), c_long(arg_ptr), None, None)

            if not thread:
                error_code = windll.kernel32.GetLastError()
                error_msg = f"Failed to create remote thread (Error: {error_code})"
                logger.error(error_msg)
                raise DLLInjectionError(error_msg)

            # Wait for thread completion
            wait_result = self.k32.WaitForSingleObject(thread, 0xFFFFFFFF)
            if wait_result == 0xFFFFFFFF:
                error_code = windll.kernel32.GetLastError()
                error_msg = f"Failed to wait for remote thread (Error: {error_code})"
                logger.error(error_msg)
                raise DLLInjectionError(error_msg)

            # Get thread exit code
            if not self.k32.GetExitCodeThread(thread, byref(exit_code)):
                error_code = windll.kernel32.GetLastError()
                error_msg = f"Failed to get thread exit code (Error: {error_code})"
                logger.error(error_msg)
                raise DLLInjectionError(error_msg)

            logger.debug(f"Remote function completed with exit code: {exit_code.value}")
            return exit_code.value

        finally:
            # Always clean up the argument buffer
            self.release_remote_buffer(arg_ptr, len(arg_data))

    @log_exceptions(logger)
    def read_memory_region(self, address: int, length: int) -> bytes:
        """Read memory from the remote process.

        Args:
            address: Memory address to read from
            length: Number of bytes to read

        Returns:
            Data read from memory

        Raises:
            DLLInjectionError: If memory read fails
        """
        logger.debug(f"Reading {length} bytes from address 0x{address:08x}")

        buf = create_string_buffer(length)
        if not self.k32.ReadProcessMemory(self.proc_handle, c_long(address), buf, length, None):
            error_code = windll.kernel32.GetLastError()
            error_msg = f"Failed to read memory at 0x{address:08x} (Error: {error_code})"
            logger.error(error_msg)
            raise DLLInjectionError(error_msg)

        logger.debug(f"Successfully read {length} bytes from 0x{address:08x}")
        return buf.raw

    @log_exceptions(logger)
    def write_to_memory(self, address: int, payload: bytes) -> None:
        """Write data to memory in the remote process.

        Args:
            address: Memory address to write to
            payload: Data to write

        Raises:
            DLLInjectionError: If memory write fails
        """
        logger.debug(f"Writing {len(payload)} bytes to address 0x{address:08x}")

        if not self.k32.WriteProcessMemory(self.proc_handle, address, payload, len(payload), None):
            error_code = windll.kernel32.GetLastError()
            error_msg = f"Failed to write to memory at 0x{address:08x} (Error: {error_code})"
            logger.error(error_msg)
            raise DLLInjectionError(error_msg)

        logger.debug(f"Successfully wrote {len(payload)} bytes to 0x{address:08x}")

    @log_exceptions(logger)
    def load_library_into_target(self, dll_bytes: bytes) -> int:
        """Load a library into the target process using LoadLibraryA.

        Args:
            dll_bytes: DLL path as bytes

        Returns:
            Base address of the loaded library

        Raises:
            DLLInjectionError: If library loading fails
        """
        logger.debug(f"Loading library: {dll_bytes.decode('ascii', errors='replace')}")

        func_ptr = self.get_func_address("kernel32.dll", "LoadLibraryA")
        result = self.run_remote_function(func_ptr, dll_bytes)

        if result == 0:
            error_msg = f"LoadLibraryA failed to load: {dll_bytes.decode('ascii', errors='replace')}"
            logger.error(error_msg)
            raise DLLInjectionError(error_msg)

        logger.info(f"Library loaded successfully at base address: 0x{result:08x}")
        return result

    @log_exceptions(logger)
    def inject_shared_library(self, dll_path: str) -> int:
        """Inject a DLL into the target process.

        This is the main entry point for DLL injection operations.

        Args:
            dll_path: Full path to the DLL file to inject

        Returns:
            Base address of the loaded DLL in the target process

        Raises:
            DLLInjectionError: If injection fails
            FileNotFoundError: If DLL file doesn't exist
        """
        import os

        if not os.path.exists(dll_path):
            error_msg = f"DLL file not found: {dll_path}"
            logger.error(error_msg)
            security_logger.error(f"Injection failed - DLL not found: {dll_path}")
            raise FileNotFoundError(error_msg)

        logger.info(f"Starting DLL injection: {dll_path}")
        security_logger.info(f"Injecting DLL for security testing: {dll_path}")

        try:
            result = self.load_library_into_target(dll_path.encode("ascii"))
            logger.info(f"DLL injection successful - base address: 0x{result:08x}")
            security_logger.info("DLL injection completed successfully")
            return result
        except Exception as e:
            logger.error(f"DLL injection failed: {str(e)}")
            security_logger.error(f"Security testing injection failed: {str(e)}")
            raise

    @log_exceptions(logger)
    def execute_exported(self, dll_path: str, base_addr: int, func_name: str, raw_args: bytes) -> int:
        """Execute an exported function from an injected DLL.

        Args:
            dll_path: Path to the DLL containing the function
            base_addr: Base address where the DLL is loaded
            func_name: Name of the exported function to execute
            raw_args: Arguments to pass to the function

        Returns:
            Return value from the executed function

        Raises:
            DLLInjectionError: If function execution fails
        """
        logger.info(f"Executing exported function {func_name} from {dll_path}")
        security_logger.info(f"Calling DLL function for security testing: {func_name}")

        offset = self.resolve_func_offset(dll_path.encode("ascii"), func_name)
        function_addr = base_addr + offset

        logger.debug(f"Function {func_name} located at offset 0x{offset:08x}, address 0x{function_addr:08x}")

        result = self.run_remote_function(function_addr, raw_args)
        logger.info(f"Function {func_name} executed successfully with result: {result}")
        return result

    @log_exceptions(logger)
    def resolve_func_offset(self, module_path: bytes, func_name: str) -> int:
        """Resolve the offset of a function within a DLL.

        Args:
            module_path: Path to the DLL as bytes
            func_name: Name of the function to locate

        Returns:
            Offset of the function from the DLL base address

        Raises:
            DLLInjectionError: If function resolution fails
        """
        dll_path_str = module_path.decode("ascii", errors="replace")
        logger.debug(f"Resolving function {func_name} offset in {dll_path_str}")

        # Temporarily load the DLL in our process to get function addresses
        temp_base = self.k32.LoadLibraryA(module_path)
        if not temp_base:
            error_code = windll.kernel32.GetLastError()
            error_msg = f"Failed to load library {dll_path_str} for offset resolution (Error: {error_code})"
            logger.error(error_msg)
            raise DLLInjectionError(error_msg)

        try:
            func_ptr = self.k32.GetProcAddress(temp_base, func_name.encode("ascii"))
            if not func_ptr:
                error_code = windll.kernel32.GetLastError()
                error_msg = f"Function {func_name} not found in {dll_path_str} (Error: {error_code})"
                logger.error(error_msg)
                raise DLLInjectionError(error_msg)

            offset = func_ptr - temp_base
            logger.debug(f"Function {func_name} found at offset 0x{offset:08x}")
            return offset

        finally:
            # Always unload the temporary library
            if not self.k32.FreeLibrary(temp_base):
                error_code = windll.kernel32.GetLastError()
                logger.warning(f"Failed to unload temporary library {dll_path_str} (Error: {error_code})")
