# built-in imports
from __future__ import annotations
from enum import Enum, auto
from typing import Callable, Tuple, List, Optional, Union, Any
import enum_tools.documentation

# third-party imports
from triton import CALLBACK, Instruction, MemoryAccess, OPCODE

# local imports
from tritondse.process_state import ProcessState
from tritondse.types import Addr, Register, Expression, Edge, SymExType, AstNode
from tritondse.thread_context import ThreadContext
from tritondse.seed import Seed
from tritondse.memory import MemoryAccessViolation
import tritondse.logging

logger = tritondse.logging.get('callback')  # get root tritondse logger


@enum_tools.documentation.document_enum
class CbPos(Enum):
    """ Enums representing callback position """
    BEFORE = auto()  # doc: Callback should be executed before the hook location interpretation
    AFTER = auto()   # doc: Callback should be executed after the hook location interpretation


@enum_tools.documentation.document_enum
class CbType(Enum):
    """ Enums representing all kind of callbacks """
    CTX_SWITCH = auto()     # doc: context-switch callback
    MEMORY_READ = auto()    # doc: memory read callback
    MEMORY_WRITE = auto()   # doc: memory write callback
    POST_RTN = auto()       # doc: routine callback (after)
    POST_ADDR = auto()      # doc: address class back (after)
    POST_EXEC = auto()      # doc: post execution callback, after a SymbolicExecutor run
    POST_INST = auto()      # doc: post instruction callback (all of them)
    PRE_ADDR = auto()       # doc: pre address callback
    PRE_EXEC = auto()       # doc: pre-execution callback (before launching a Symbolic Executor)
    PRE_INST = auto()       # doc: pre-instruction callback (all of them)
    PRE_RTN = auto()        # doc: routine callback (before)
    REG_READ = auto()       # doc: a register is read
    REG_WRITE = auto()      # doc: a register is written
    NEW_INPUT = auto()      # doc: new input has been generated
    EXPLORE_STEP = auto()   # doc: an exploration step is reached. Called in between each SymbolicExecutor run
    PRE_MNEM = auto()       # doc: callback on a specific mnemonic (as a string) (before)
    POST_MNEM = auto()      # doc: callback on a specific mnemonic (as a string) (after)
    PRE_OPCODE = auto()     # doc: callback on a specific opcode (as bytes) (before)
    POST_OPCODE = auto()    # doc: callback on a specific opcode (as bytes) (after)
    BRANCH_COV = auto()     # doc: a new branch is getting covered
    SYMEX_SOLVING = auto()  # doc: An SMT formula is getting solved
    MEM_VIOLATION = auto()  # doc: A memory violation occurred


AddrCallback            = Callable[['SymbolicExecutor', ProcessState, Addr], None]
ExplorationStepCallback = Callable[['SymbolicExplorator'], None]
InstrCallback           = Callable[['SymbolicExecutor', ProcessState, Instruction], None]
MemReadCallback         = Callable[['SymbolicExecutor', ProcessState, MemoryAccess], None]
MemWriteCallback        = Callable[['SymbolicExecutor', ProcessState, MemoryAccess, int], None]
MnemonicCallback        = Callable[['SymbolicExecutor', ProcessState, OPCODE], None]
SymExSolvingCallback    = Callable[['SymbolicExecutor', ProcessState, Edge, SymExType, AstNode, List[AstNode]], bool]
BranchCoveredCallback   = Callable[['SymbolicExecutor', ProcessState, Edge], bool]
NewInputCallback        = Callable[['SymbolicExecutor', ProcessState, Seed], Optional[Seed]]
OpcodeCallback          = Callable[['SymbolicExecutor', ProcessState, bytes], None]
RegReadCallback         = Callable[['SymbolicExecutor', ProcessState, Register], None]
RegWriteCallback        = Callable[['SymbolicExecutor', ProcessState, Register, int], None]
RtnCallback             = Callable[['SymbolicExecutor', ProcessState, str, Addr], Optional[Union[int, Expression]]]
SymExCallback           = Callable[['SymbolicExecutor', ProcessState], None]
ThreadCallback          = Callable[['SymbolicExecutor', ProcessState, ThreadContext], None]
MemoryViolationCallback = Callable[['SymbolicExecutor', ProcessState, MemoryAccessViolation], None]


class ProbeInterface(object):
    """ The Probe interface """
    def __init__(self):
        self._cbs: List[Tuple[CbType, Callable, Optional[str]]] = []  #: list of callback infos

    @property
    def callbacks(self) -> List[Tuple[CbType, Callable, Optional[Any]]]:
        return self._cbs

    def _add_callback(self, typ: CbType, callback: Callable, arg: str = None):
        """ Add a callback """
        self._cbs.append((typ, callback, arg))


class CallbackManager(object):
    """
    Class used to aggregate all callbacks that can be plugged
    inside a SymbolicExecutor running session. The internal
    structure ensure that check the presence of callback can
    be made in Log(N). All callbacks are designed to be read-only
    """

    def __init__(self):
        self._se = None

        # SymbolicExplorator callbacks
        self._step_cbs = []  # Callback called between each exploration steps

        # SymbolicExecutor callbacks
        self._pc_addr_cbs        = {}  # addresses reached
        self._opcode_cbs         = {}  # opcode before and after
        self._mnemonic_cbs       = {}  # mnemonic before and after
        self._instr_cbs          = {CbPos.BEFORE: [], CbPos.AFTER: []}  # all instructions
        self._pre_exec           = []  # before execution
        self._post_exec          = []  # after execution
        self._ctx_switch         = []  # on each thread context switch (implementing pre/post?)
        self._new_input_cbs      = []  # each time an SMT model is get
        self._branch_solving_cbs = []  # each time a branch is about to be solved
        self._branch_covered_cbs = []  # each time a branch is covered
        self._pre_rtn_cbs        = {}  # before imported routine calls ({str: [RtnCallback]})
        self._post_rtn_cbs       = {}  # after imported routine calls ({str: [RtnCallback]})
        self._mem_violation_cbs  = []  # called when an exception is raised

        # Triton callbacks
        self._mem_read_cbs  = []  # memory reads
        self._mem_write_cbs = []  # memory writes
        self._reg_read_cbs  = []  # register reads
        self._reg_write_cbs = []  # register writes
        self._empty         = True

        # Temporary mapping of function name to register
        self._func_to_register = {}

    def is_empty(self) -> bool:
        """
        Check whether a callback has already been registered or not

        :return: True if no callback were registered
        """
        return self._empty

    def is_binded(self) -> bool:
        """
        Check if the callback manager has already been bound on a given process state.

        :return: True if callbacks are bound on a process state
        """
        return bool(self._se)   # and self._se.uid == se.uid)

    def _trampoline_mem_read_cb(self, ctx, mem):
        """
        This function is the trampoline callback on memory read from triton to tritondse

        :param ctx: TritonContext
        :param mem: MemoryAccess
        :return: None
        """
        if self._se.pstate.memory.callbacks_enabled():
            for cb in self._mem_read_cbs:
                cb(self._se, self._se.pstate, mem)

    def _trampoline_mem_write_cb(self, ctx, mem, value):
        """
        This function is the trampoline callback on memory write from triton to tritondse

        :param ctx: TritonContext
        :param mem: MemoryAccess
        :param value: int
        :return: None
        """
        if self._se.pstate.memory.callbacks_enabled():
            for cb in self._mem_write_cbs:
                cb(self._se, self._se.pstate, mem, value)

    def _trampoline_reg_read_cb(self, ctx, reg):
        """
        This function is the trampoline callback on register read from triton to tritondse

        :param ctx: TritonContext
        :param reg: Register
        :return: None
        """
        for cb in self._reg_read_cbs:
            cb(self._se, self._se.pstate, reg)

    def _trampoline_reg_write_cb(self, ctx, reg, value):
        """
        This function is the trampoline callback on register write from triton to tritondse

        :param ctx: TritonContext
        :param reg: Register
        :param value: int
        :return: None
        """
        for cb in self._reg_write_cbs:
            cb(self._se, self._se.pstate, reg, value)

    def unbind(self) -> None:
        """
        Unbind callbacks from the current process state as well as from
        the Triton Context object.
        """
        if self.is_binded():
            self._se.pstate.clear_triton_callbacks()
            self._se = None

    def bind_to(self, se: 'SymbolicExecutor') -> None:
        """
        Bind callbacks on the given process state. That step is required
        to register callbacks on the Triton Context object. This is also
        used to keep a reference on the SymbolicExecutor object;

        IMPORTANT You MUST call `unbind` once you finish using the
        SymbolicExecutor.

        :param se: SymbolicExecutor on which to bind callbacks
        :type se: SymbolicExecutor
        """
        if self.is_binded() and self._se != se:
            logger.warning("Callback_manager already bound (on a different executor instance)")
        # assert not self.is_binded()

        # NOTE This creates a circular dependency between the SymbolicExecutor
        #      received and this object, as the SymbolicExecutor keeps a
        #      reference to it. Therefore, it is necessary to call `unbind`
        #      once you finish using the executor.
        self._se = se

        # Register only one trampoline by kind of callback. It will be the role
        # of the trampoline to call every registered tritondse callbacks.

        if self._mem_read_cbs:
            se.pstate.register_triton_callback(CALLBACK.GET_CONCRETE_MEMORY_VALUE, self._trampoline_mem_read_cb)

        if self._mem_write_cbs:
            se.pstate.register_triton_callback(CALLBACK.SET_CONCRETE_MEMORY_VALUE, self._trampoline_mem_write_cb)

        if self._reg_read_cbs:
            se.pstate.register_triton_callback(CALLBACK.GET_CONCRETE_REGISTER_VALUE, self._trampoline_reg_read_cb)

        if self._reg_write_cbs:
            se.pstate.register_triton_callback(CALLBACK.SET_CONCRETE_REGISTER_VALUE, self._trampoline_reg_write_cb)

        # Check if there is a program on which to register functions callback
        if self._func_to_register:
            if se.loader:
                for fname in list(self._func_to_register):
                    cbs = self._func_to_register.pop(fname)
                    addr = se.loader.find_function_addr(fname)
                    if addr:
                        for cb in cbs:
                            self.register_pre_addr_callback(addr, cb)
                    else:
                        logger.warning(f"can't find function '{fname}' in {se.loader}")
            else:
                logger.warning(f"function callback to resolve but no program provided")

    def register_addr_callback(self, pos: CbPos, addr: Addr, callback: AddrCallback) -> None:
        """
        Register a callback function on a given address before or after the execution
        of the associated instruction.

        :param pos: When to trigger the callback (before or after) execution of the instruction
        :type pos: CbPos
        :param addr: Address where to trigger the callback
        :type addr: :py:obj:`tritondse.types.Addr`
        :param callback: callback function
        :type callback: :py:obj:`tritondse.callbacks.AddrCallback`
        """
        if addr not in self._pc_addr_cbs:
            self._pc_addr_cbs[addr] = {CbPos.BEFORE: [], CbPos.AFTER: []}

        self._pc_addr_cbs[addr][pos].append(callback)
        self._empty = False

    def register_pre_addr_callback(self, addr: Addr, callback: AddrCallback) -> None:
        """
        Register pre address callback

        :param addr: Address where to trigger the callback
        :type addr: :py:obj:`tritondse.types.Addr`
        :param callback: callback function
        :type callback: :py:obj:`tritondse.callbacks.AddrCallback`
        """
        self.register_addr_callback(CbPos.BEFORE, addr, callback)

    def register_post_addr_callback(self, addr: Addr, callback: AddrCallback) -> None:
        """
        Register post-address callback. Equivalent to register a pre-address on the
        return site. *(assume the function returns)*

        :param addr: Address where to trigger the callback
        :type addr: :py:obj:`tritondse.types.Addr`
        :param callback: callback function
        :type callback: :py:obj:`tritondse.callbacks.AddrCallback`
        """
        self.register_addr_callback(CbPos.AFTER, addr, callback)

    def get_address_callbacks(self, addr: Addr) -> Tuple[List[AddrCallback], List[AddrCallback]]:
        """
        Get all the pre/post callbacks for a given address.

        :param addr: Address where to trigger the callback
        :type addr: :py:obj:`tritondse.types.Addr`
        :return: tuple of lists containing callback functions for pre/post respectively
        """
        cbs = self._pc_addr_cbs.get(addr, None)
        if cbs is not None:
            return cbs[CbPos.BEFORE], cbs[CbPos.AFTER]
        else:
            return [], []

    def register_opcode_callback(self, pos: CbPos, opcode: bytes, callback: OpcodeCallback) -> None:
        """
        Register a callback function on a given opcode before or after the execution
        of the associated instruction.

        :param pos: When to trigger the callback (before or after) execution of the instruction
        :type pos: CbPos
        :param opcode: Opcode where to trigger the callback
        :type opcode: :py:obj:`bytes`
        :param callback: callback function
        :type callback: :py:obj:`tritondse.callbacks.OpcodeCallback`
        """
        if opcode not in self._opcode_cbs:
            self._opcode_cbs[opcode] = {CbPos.BEFORE: [], CbPos.AFTER: []}

        self._opcode_cbs[opcode][pos].append(callback)
        self._empty = False

    def register_pre_opcode_callback(self, opcode: bytes, callback: OpcodeCallback) -> None:
        """
        Register pre-opcode callback.

        :param opcode: Opcode where to trigger the callback
        :type opcode: :py:obj:`bytes`
        :param callback: callback function
        :type callback: :py:obj:`tritondse.callbacks.OpcodeCallback`
        """
        self.register_opcode_callback(CbPos.BEFORE, opcode, callback)

    def register_post_opcode_callback(self, opcode: bytes, callback: OpcodeCallback) -> None:
        """
        Register post-opcode callback.

        :param opcode: Opcode where to trigger the callback
        :type opcode: :py:obj:`bytes`
        :param callback: callback function
        :type callback: :py:obj:`tritondse.callbacks.OpcodeCallback`
        """
        self.register_opcode_callback(CbPos.AFTER, opcode, callback)

    def get_opcode_callbacks(self, opcode: bytes) -> Tuple[List[OpcodeCallback], List[OpcodeCallback]]:
        """
        Get all the pre/post callbacks for a given opcode.

        :param opcode: Opcode where to trigger the callback
        :type opcode: :py:obj:`bytes`
        :return: tuple of lists containing callback functions for pre/post respectively
        """
        cbs = self._opcode_cbs.get(opcode, None)
        if cbs:
            return cbs[CbPos.BEFORE], cbs[CbPos.AFTER]
        else:
            return [], []

    def register_mnemonic_callback(self, pos: CbPos, mnemonic: OPCODE, callback: MnemonicCallback) -> None:
        """
        Register a callback function on a given mnemonic before or after the execution
        of the associated instruction.

        :param pos: When to trigger the callback (before or after) execution of the instruction
        :type pos: CbPos
        :param mnemonic: Mnemonic where to trigger the callback
        :type mnemonic: :py:obj:`OPCODE`
        :param callback: callback function
        :type callback: :py:obj:`tritondse.callbacks.MnemonicCallback`
        """
        if mnemonic not in self._mnemonic_cbs:
            self._mnemonic_cbs[mnemonic] = {CbPos.BEFORE: [], CbPos.AFTER: []}

        self._mnemonic_cbs[mnemonic][pos].append(callback)
        self._empty = False

    def register_pre_mnemonic_callback(self, mnemonic: OPCODE, callback: MnemonicCallback) -> None:
        """
        Register pre-mnemonic callback.

        :param mnemonic: Mnemonic where to trigger the callback
        :type mnemonic: :py:obj:`OPCODE`
        :param callback: callback function
        :type callback: :py:obj:`tritondse.callbacks.MnemonicCallback`
        """
        self.register_mnemonic_callback(CbPos.BEFORE, mnemonic, callback)

    def register_post_mnemonic_callback(self, mnemonic: OPCODE, callback: MnemonicCallback) -> None:
        """
        Register post-mnemonic callback.

        :param mnemonic: Mnemonic where to trigger the callback
        :type mnemonic: :py:obj:`OPCODE`
        :param callback: callback function
        :type callback: :py:obj:`tritondse.callbacks.MnemonicCallback`
        """
        self.register_mnemonic_callback(CbPos.AFTER, mnemonic, callback)

    def get_mnemonic_callbacks(self, mnemonic: OPCODE) -> Tuple[List[MnemonicCallback], List[MnemonicCallback]]:
        """
        Get all the pre/post callbacks for a given mnemonic.

        :param mnemonic: Mnemonic where to trigger the callback
        :type mnemonic: :py:obj:`OPCODE`
        :return: tuple of lists containing callback functions for pre/post respectively
        """
        cbs = self._mnemonic_cbs.get(mnemonic, None)
        if cbs:
            return cbs[CbPos.BEFORE], cbs[CbPos.AFTER]
        else:
            return [], []

    def register_function_callback(self, func_name: str, callback: AddrCallback) -> None:
        """
        Register a callback on the address of the given function name.
        The function name is only resolve when the callback manager is bound
        to a SymbolicExecutor.

        :param func_name: Function name
        :type func_name: str
        :param callback: callback function
        :type callback: :py:obj:`tritondse.callbacks.AddrCallback`
        """
        if func_name in self._func_to_register:
            self._func_to_register[func_name].append(callback)
        else:
            self._func_to_register[func_name] = [callback]

    def register_instruction_callback(self, pos: CbPos, callback: InstrCallback) -> None:
        """
        Register a callback triggered on each instruction executed, before or after its
        side effects have been applied to ProcessState.

        :param pos: before, after execution of the instruction
        :type pos: CbPos
        :param callback: callback function to trigger
        :type callback: :py:obj:`tritondse.callbacks.InstrCallback`
        """
        self._instr_cbs[pos].append(callback)
        self._empty = False

    def register_pre_instruction_callback(self, callback: InstrCallback) -> None:
        """
        Register a pre-execution callback on all instruction executed by the engine.

        :param callback: callback function to trigger
        :type callback: :py:obj:`tritondse.callbacks.InstrCallback`
        """
        self.register_instruction_callback(CbPos.BEFORE, callback)

    def register_post_instruction_callback(self, callback: InstrCallback) -> None:
        """
        Register a post-execution callback on all instruction executed by the engine.

        :param callback: callback function to trigger
        :type callback: :py:obj:`tritondse.callbacks.InstrCallback`
        """
        self.register_instruction_callback(CbPos.AFTER, callback)

    def get_instruction_callbacks(self) -> Tuple[List[InstrCallback], List[InstrCallback]]:
        """
        Get all the pre/post callbacks for instructions.

        :return: tuple of lists containing callback functions for pre/post respectively
        """
        return self._instr_cbs[CbPos.BEFORE], self._instr_cbs[CbPos.AFTER]

    def register_pre_execution_callback(self, callback: SymExCallback) -> None:
        """
        Register a callback executed after program loading, registers and memory
        initialization. Thus, this callback is called just before executing the
        first instruction.

        :param callback: Callback function to trigger
        :type callback: :py:obj:`tritondse.callbacks.SymExCallback`
        """
        self._pre_exec.append(callback)
        self._empty = False

    def register_post_execution_callback(self, callback: SymExCallback) -> None:
        """
        Register a callback executed after program loading, registers and memory
        initialization. Thus, this callback is called after executing upon program
        exit (or crash)

        :param callback: Callback function to trigger
        :type callback: :py:obj:`tritondse.callbacks.SymExCallback`
        """
        self._post_exec.append(callback)
        self._empty = False

    def register_exploration_step_callback(self, callback: ExplorationStepCallback) -> None:
        """
        Register a callback executed before each exploration step. The object
        given in parameter is the SymbolicExplorator itself.

        :param callback: Callback function to trigger
        :type callback: :py:obj:`tritondse.callbacks.ExplorationStepCallback`
        """
        self._step_cbs.append(callback)
        # self._empty = False  # Does not impact the emptiness of the callbackmanager

    def get_execution_callbacks(self) -> Tuple[List[SymExCallback], List[SymExCallback]]:
        """
        Get all the pre/post callbacks for the current symbolic execution.

        :return: tuple of lists containing callback functions for pre/post respectively
        """
        return self._pre_exec, self._post_exec

    def register_memory_read_callback(self, callback: MemReadCallback) -> None:
        """
        Register a callback that will be triggered by any read in the concrete
        memory of the process state.

        :param callback: Callback function to be called
        :type callback: :py:obj:`tritondse.callbacks.MemCallback`
        """
        self._mem_read_cbs.append(callback)
        self._empty = False

    def register_memory_write_callback(self, callback: MemWriteCallback) -> None:
        """
        Register a callback called on each write in the concrete memory state
        of the process.

        :param callback: Callback function to be called
        :type callback: :py:obj:`tritondse.callbacks.MemCallback`
        """
        self._mem_write_cbs.append(callback)
        self._empty = False

    def register_register_read_callback(self, callback: RegReadCallback) -> None:
        """
        Register a callback on each register read during the symbolic execution.

        :param callback: Callback function to be called
        :type callback: :py:obj:`tritondse.callbacks.RegReadCallback`
        """
        self._reg_read_cbs.append(callback)
        self._empty = False

    def register_register_write_callback(self, callback: RegWriteCallback) -> None:
        """
        Register a callback on each register write during the symbolic execution.

        :param callback: Callback function to be called
        :type callback: :py:obj:`tritondse.callbacks.RegReadCallback`
        """
        self._reg_write_cbs.append(callback)
        self._empty = False

    def register_thread_context_switch_callback(self, callback: ThreadCallback) -> None:
        """
        Register a callback triggered upon each thread context switch during the execution.

        :param callback: Callback to be called
        :type callback: :py:obj:`tritondse.callbacks.ThreadCallback`
        """
        self._ctx_switch.append(callback)
        self._empty = False

    def get_context_switch_callback(self) -> List[ThreadCallback]:
        """
        Get the list of all function callback to call when thread is being scheduled.

        :return: List of callbacks defined when thread is being scheduled
        """
        return self._ctx_switch

    def register_new_input_callback(self, callback: NewInputCallback) -> None:
        """
        Register a callback function called when the SMT solver find a new model namely
        a new input. This callback is called before any treatment on the input (worklist, etc.).
        It thus allows to post-process the input before it getting put in the queue.

        :param callback: callback function
        :type callback: :py:obj:`tritondse.callbacks.NewInputCallback`
        """
        self._new_input_cbs.append(callback)
        self._empty = False

    def get_new_input_callback(self) -> List[NewInputCallback]:
        """
        Get the list of all function callback to call when a new
        input is generated by SMT.

        :return: List of callbacks to call on input generation
        """
        return self._new_input_cbs

    def register_on_solving_callback(self, callback: SymExSolvingCallback) -> None:
        """
        Register a callback function called when a branch is about to
        be solved. This callback is called before the branch is solved and will
        use the result of the callback to go ahead with the solving or skip it.

        :param callback: callback function
        :type callback: :py:obj:`tritondse.callbacks.BranchSolvingCallback`
        """
        self._branch_solving_cbs.append(callback)
        self._empty = False

    def get_on_solving_callback(self) -> List[SymExSolvingCallback]:
        """
        Get the list of all function callbacks to call when a branch is about
        to be solved.

        :return: List of callbacks to call on branch solving
        """
        return self._branch_solving_cbs

    def register_on_branch_covered_callback(self, callback: BranchCoveredCallback) -> None:
        """
        Register a callback function called when a branch covered. This callback
        is called after the branch is solved.

        :param callback: callback function
        :type callback: :py:obj:`tritondse.callbacks.BranchCoveredCallback`
        """
        self._branch_covered_cbs.append(callback)
        self._empty = False

    def get_on_branch_covered_callback(self) -> List[BranchCoveredCallback]:
        """
        Get the list of all function callbacks to call when a branch is about
        to be solved.

        :return: List of callbacks to call on branch covered
        """
        return self._branch_covered_cbs

    def register_memory_violation_callback(self, callback: MemoryViolationCallback) -> None:
        """
        Register a callback function called when a memory violation occurred during the
        emulation.

        :param callback: callback function
        :type callback: :py:obj:`tritondse.callbacks.MemoryViolationCallback`
        """
        self._mem_violation_cbs.append(callback)
        self._empty = False

    def get_memory_violation_callbacks(self) -> List[MemoryViolationCallback]:
        """
        Get all memory violation callbacks.

        :return: list of memory violation callbacks
        """
        return self._mem_violation_cbs

    def get_exploration_step_callbacks(self) -> List[ExplorationStepCallback]:
        """
        Get all the exploration step callbacks

        :return: list containing callbacks
        """
        return self._step_cbs

    def register_pre_imported_routine_callback(self, routine_name: str, callback: RtnCallback) -> None:
        """
        Register a callback before call to an imported routines

        :param routine_name: the routine name
        :param callback: callback function
        :type callback: :py:obj:`tritondse.callbacks.RtnCallback`
        """
        if routine_name in self._pre_rtn_cbs:
            self._pre_rtn_cbs[routine_name].append(callback)
        else:
            self._pre_rtn_cbs[routine_name] = [callback]
        self._empty = False

    def register_post_imported_routine_callback(self, routine_name: str, callback: RtnCallback) -> None:
        """
        Register a callback, called after the call to imported routines.

        :param routine_name: the routine name
        :param callback: callback function
        :type callback: :py:obj:`tritondse.callbacks.RtnCallback`
        """
        if routine_name in self._post_rtn_cbs:
            self._post_rtn_cbs[routine_name].append(callback)
        else:
            self._post_rtn_cbs[routine_name] = [callback]
        self._empty = False

    def get_imported_routine_callbacks(self, routine_name: str) -> Tuple[List[RtnCallback], List[RtnCallback]]:
        """
        Get the list of all callbacks for an imported routine

        :param routine_name: the routine name
        :return: Tuple of list of callbacks (for pre and post)
        """
        pre_ret = (self._pre_rtn_cbs[routine_name] if routine_name in self._pre_rtn_cbs else [])
        post_ret = (self._post_rtn_cbs[routine_name] if routine_name in self._post_rtn_cbs else [])
        return pre_ret, post_ret

    def register_probe(self, probe: ProbeInterface) -> None:
        """
        Register a probe. That function will iterate the ``cbs`` attribute
        of the object, and will register each entry in self.

        .. warning:: Does not implement all CbType

        :param probe: a probe interface
        :type probe: ProbeInterface
        """
        for kind, cb, arg in probe.callbacks:
            try:
                mapping_with_args = {
                    CbType.PRE_RTN: self.register_pre_imported_routine_callback,
                    CbType.POST_RTN: self.register_post_imported_routine_callback,
                    CbType.PRE_ADDR: self.register_pre_addr_callback,
                    CbType.POST_ADDR: self.register_post_addr_callback,
                    CbType.PRE_MNEM: self.register_pre_mnemonic_callback,
                    CbType.POST_MNEM: self.register_post_mnemonic_callback,
                    CbType.PRE_OPCODE: self.register_pre_opcode_callback,
                    CbType.POST_OPCODE: self.register_post_opcode_callback,
                }
                mapping_with_args[kind](arg, cb)
            except KeyError:
                mapping = {
                    CbType.CTX_SWITCH: self.register_thread_context_switch_callback,
                    CbType.MEMORY_READ: self.register_memory_read_callback,
                    CbType.MEMORY_WRITE: self.register_memory_write_callback,
                    CbType.POST_EXEC: self.register_post_execution_callback,
                    CbType.POST_INST: self.register_post_instruction_callback,
                    CbType.PRE_EXEC: self.register_pre_execution_callback,
                    CbType.PRE_INST: self.register_pre_instruction_callback,
                    CbType.REG_READ: self.register_register_read_callback,
                    CbType.REG_WRITE: self.register_register_write_callback,
                    CbType.NEW_INPUT: self.register_new_input_callback,
                    CbType.EXPLORE_STEP: self.register_exploration_step_callback,
                    CbType.BRANCH_COV: self.register_on_branch_covered_callback,
                    CbType.SYMEX_SOLVING: self.register_on_solving_callback,
                    CbType.MEM_VIOLATION: self.register_memory_violation_callback
                }
                mapping[kind](cb)

    def fork(self) -> 'CallbackManager':
        """
        Fork the current CallbackManager in a new object instance
        (that will be unbinded). That method is used by the SymbolicExplorator
        to ensure each SymbolicExecutor running concurrently will have
        their own instance off the CallbackManager.

        :return: Fresh instance of CallbackManager
        :rtype: CallbackManager
        """
        cbs = CallbackManager()

        # SymbolicExecutor callbacks
        cbs._pc_addr_cbs        = self._pc_addr_cbs.copy()
        cbs._opcode_cbs         = self._opcode_cbs.copy()
        cbs._mnemonic_cbs       = self._mnemonic_cbs.copy()
        cbs._instr_cbs          = self._instr_cbs.copy()
        cbs._pre_exec           = self._pre_exec.copy()
        cbs._post_exec          = self._post_exec.copy()
        cbs._ctx_switch         = self._ctx_switch.copy()
        cbs._new_input_cbs      = self._new_input_cbs.copy()
        cbs._branch_solving_cbs = self._branch_solving_cbs.copy()
        cbs._branch_covered_cbs = self._branch_covered_cbs.copy()
        cbs._pre_rtn_cbs        = self._pre_rtn_cbs.copy()
        cbs._post_rtn_cbs       = self._post_rtn_cbs.copy()
        cbs._mem_violation_cbs  = self._mem_violation_cbs.copy()
        # Triton callbacks
        cbs._mem_read_cbs  = self._mem_read_cbs.copy()
        cbs._mem_write_cbs = self._mem_write_cbs.copy()
        cbs._reg_read_cbs  = self._reg_read_cbs.copy()
        cbs._reg_write_cbs = self._reg_write_cbs.copy()
        cbs._empty         = self._empty
        # Copy temporary data
        cbs._func_to_register = self._func_to_register.copy()

        return cbs

    def unregister_callback(self, callback: Callable) -> None:
        """
        Unregister the given callback from the manager.

        :param callback: callback to remove
        :return: None
        """
        for addr, itms in self._pc_addr_cbs.items():
            for loc in CbPos:
                if callback in itms[loc]:
                    itms[loc].remove(callback)

        for opcode, itms in self._opcode_cbs.items():
            for loc in CbPos:
                if callback in itms[loc]:
                    itms[loc].remove(callback)

        for mnemonic, itms in self._mnemonic_cbs.items():
            for loc in CbPos:
                if callback in itms[loc]:
                    itms[loc].remove(callback)

        for loc in CbPos:
            if callback in self._instr_cbs[loc]:
                self._instr_cbs[loc].remove(callback)

        for cb_list in [self._step_cbs, self._pre_exec, self._post_exec, self._ctx_switch, self._new_input_cbs, self._branch_solving_cbs, self._branch_covered_cbs,
                        self._mem_read_cbs, self._mem_write_cbs, self._reg_read_cbs, self._reg_write_cbs, self._mem_violation_cbs]:
            if callback in cb_list:
                cb_list.remove(callback)

        for d in [self._pre_rtn_cbs, self._post_rtn_cbs]:
            for cb_list in d.values():
                if callback in cb_list:
                    cb_list.remove(callback)

    def reset(self) -> None:
        """
        Reset all callbacks
        :return:
        """
        # SymbolicExplorator callbacks
        self._step_cbs = []  # Callback called between each exploration steps

        # SymbolicExecutor callbacks
        self._pc_addr_cbs        = {}  # addresses reached
        self._opcode_cbs         = {}  # opcode before and after
        self._mnemonic_cbs       = {}  # mnemonic before and after
        self._instr_cbs          = {CbPos.BEFORE: [], CbPos.AFTER: []}  # all instructions
        self._pre_exec           = []  # before execution
        self._post_exec          = []  # after execution
        self._ctx_switch         = []  # on each thread context switch (implementing pre/post?)
        self._new_input_cbs      = []  # each time an SMT model is get
        self._branch_solving_cbs = []  # each time a covitem is about to be solved
        self._branch_covered_cbs = []  # each time a covitem is covered
        self._pre_rtn_cbs        = {}  # before imported routine calls ({str: [RtnCallback]})
        self._post_rtn_cbs       = {}  # after imported routine calls ({str: [RtnCallback]})
        self._mem_violation_cbs  = []  # reset the memory violation calls

        # Triton callbacks
        self._mem_read_cbs  = []  # memory reads
        self._mem_write_cbs = []  # memory writes
        self._reg_read_cbs  = []  # register reads
        self._reg_write_cbs = []  # register writes
        self._empty         = True
