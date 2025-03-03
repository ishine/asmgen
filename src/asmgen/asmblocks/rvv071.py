from asmgen.asmblocks.noarch import reg_tracker
from asmgen.asmblocks.noarch import asm_data_type, asm_index_type
from asmgen.asmblocks.noarch import vreg,freg,greg

from asmgen.asmblocks.riscv64 import riscv64

from typing import TypeAlias

class rvv071_vreg(vreg):
    def __init__(self, reg_idx : int):
        self.reg_str = f"v{reg_idx}";

    def __str__(self) -> str:
        return self.reg_str;

class rvv071(riscv64):

    greg_type : TypeAlias = greg
    freg_type : TypeAlias = freg
    vreg_type : TypeAlias = vreg

    def supportedby_cpuinfo(self, cpuinfo) -> bool:
         isa_idx = cpuinfo.find("rv64")
         if -1 == isa_idx:
             return False
         isa_idx = isa_idx+4
         extensions = cpuinfo[isa_idx:].split()[0]
         return "v" in extensions

    #dt_suffixes = {
    #        asm_data_type.DOUBLE : "e64",
    #        asm_data_type.SINGLE : "e32",
    #        }
    dt_suffixes = {
            asm_data_type.DOUBLE : "e",
            asm_data_type.SINGLE : "w",
            }
    it_suffixes = {
            asm_index_type.INT64 : "ei64",
            asm_index_type.INT32 : "ei32",
            asm_index_type.INT16 : "ei16",
            asm_index_type.INT8  : "ei8",
            }

    def isaquirks(self, rt : reg_tracker, dt : asm_data_type):
        tmpreg_idx = rt.reserve_any_greg()
        tmpreg = self.greg(tmpreg_idx)
        asmblock = self.vsetvlmax(tmpreg, dt)
        rt.unuse_greg(tmpreg_idx)
        return asmblock

    def jvzero(self, vreg1, freg, vreg2, greg, label, datatype):
        dt_suf = self.fdt_suffixes[datatype]
        asmblock  = self.asmwrap(f"fmv.{dt_suf}.x {freg},zero")
        # vec filled with 1 where element not-zero
        asmblock += self.asmwrap(f"vmfne.vf {vreg2},{vreg1},{freg}")
        # greg has number of elements that are not zero
        asmblock += self.asmwrap(f"vcpop.m {greg},{vreg2}")
        # if non-zero number of elements are non-zero, i.e greg has non-zero number,
        # we do not have zero, so we don't jump
        # So we jump when zero
        asmblock += self.asmwrap(f"beqz {greg},{label}")
        return asmblock

    def is_vla(self):
        return True

    def indexable_elements(self, datatype):
        return self.simd_size/datatype.value

    @property
    def max_vregs(self):
        return 32

    @property
    def simd_size(self):
        return 1

    def simd_size_to_greg(self, reg, datatype):
        asmblock  = self.asmwrap(f"csrr {reg}, vl")
        asmblock += self.asmwrap(f"slli {reg}, {reg}, {datatype.value.bit_length()-1}")
        return asmblock

    @property
    def c_simd_size_function(self):
        result  = "size_t get_simd_size() {\n"
        result += "    size_t byte_size = 0;\n"
        result += "    __asm__ volatile(\n"
        result += "        "+self.asmwrap("addi t0, zero, 60")
        result += "        "+self.asmwrap("slli t0, t0, 5")
        result += "        "+self.asmwrap("vsetvli %[byte_size], t0, e8,m1")
        result += "    : [byte_size] \"=r\" (byte_size)\n"
        result += "    :\n"
        result += "    : \"t0\"\n"
        result += "    );\n"
        result += "    return byte_size;\n"
        result += "}"
        return result


    # TODO: These don't change between 0.7.1 and 1.0, could be deduplicated

    def fmul(self, avreg : vreg_type, bvreg : vreg_type, cvreg : vreg_type,
             datatype : asm_data_type) -> str:
        return self.asmwrap(f"vfmul.vv {cvreg},{avreg},{bvreg}")

    def fmul_vf(self, avreg : vreg_type, bfreg : freg_type, cvreg : vreg_type,
                datatype : asm_data_type) -> str:
        return self.asmwrap(f"vfmul.vf {cvreg},{avreg},{bfreg}")

    def fma(self, avreg : vreg_type, bvreg : vreg_type, cvreg : vreg_type,
            datatype : asm_data_type) -> str:
        return self.asmwrap(f"vfmacc.vv {cvreg},{avreg},{bvreg}")

    def fma_np(self, avreg : vreg_type, bvreg : vreg_type, cvreg : vreg_type,
            datatype : asm_data_type) -> str:
        return self.asmwrap(f"vfnmsac.vv {cvreg},{avreg},{bvreg}")

    def fma_vf(self, avreg : vreg_type, bfreg : freg_type, cvreg : vreg_type,
               datatype : asm_data_type) -> str:
        return self.asmwrap(f"vfmacc.vf {cvreg},{bfreg},{avreg}")

    def fma_np_vf(self, avreg : vreg_type, bfreg : freg_type, cvreg : vreg_type,
               datatype : asm_data_type) -> str:
        return self.asmwrap(f"vfnmsac.vf {cvreg},{bfreg},{avreg}")

    def fma_idx(self, avreg : vreg_type, bvreg : vreg_type, cvreg : vreg_type,
                idx : int, datatype : asm_data_type) -> str:
        raise NotImplementedError("RVV doesn't have an indexed FMA")

    def fma_np_idx(self, avreg : vreg_type, bfreg : freg_type, cvreg : vreg_type,
                   idx : int, datatype : asm_data_type) -> str:
        raise NotImplementedError("RVV doesn't have an indexed FMA")

    @property
    def has_add_greg_voff(self) -> bool:
        return False

    def add_greg_voff(self, reg, offset, datatype):
        raise NotImplementedError("RVV doesn't have an instruction to add a vector offset to a gp register")
        
    def zero_vreg(self, reg, datatype):
        return self.asmwrap(f"vmv.v.i {reg},0")

    def vreg(self, reg_idx : int) -> rvv071_vreg:
        return rvv071_vreg(reg_idx)

    @property
    def min_load_voff(self):
        return 0

    @property
    def max_load_voff(self):
        return 0

    def load_vector(self, a, ignored_offset, v, datatype):
        assert isinstance(datatype, asm_data_type), f"Not an asm_data_type: {datatype}"
        dt_suf = self.dt_suffixes[datatype]
        return self.asmwrap(f"vl{dt_suf}.v {v}, ({a})")

    # I'm not seeing equivalents in RVV, I think you're supposed to do things differently
    # (LMUL > 1?), vector index?
    def load_vector_voff(self, a, ignored_offset, v, datatype):
        return self.load_vector(a, ignored_offset, v, datatype)

    def load_vector_dist1(self, a, offset, v, datatype):
        assert isinstance(datatype, asm_data_type), f"Not an asm_data_type: {datatype}"
        dt_suf = self.dt_suffixes[datatype]
        # This is slow on a certain architecture and doesn't support offsets
        return self.asmwrap(f"vls{dt_suf}.v {v}, ({a}), zero")

    def load_vector_dist1_boff(self, a, offset, v, datatype):
        return self.load_vector_dist1(a, offset, v, datatype)
    
    def load_vector_dist1_inc(self, a, ignored_offset, v, datatype):
        raise NotImplementedError("RVV has no vector loads with address increment")

    def store_vector(self, a, voffset, v, datatype):
        assert isinstance(datatype, asm_data_type), f"Not an asm_data_type: {datatype}"

    def store_vector_voff(self, a, voffset, v, datatype):
        if voffset != 0:
            raise NotImplementedError("RVV has no vector stores with address offset")
        self.store_vector(a, voffset, v, datatype)

        dt_suf = self.dt_suffixes[datatype]
        return self.asmwrap(f"vs{dt_suf}.v {v}, ({a})")

    def vsetvlmax(self, reg, datatype):
        assert isinstance(datatype, asm_data_type), f"Not an asm_data_type: {datatype}"
        dt_size = 'e'+str(datatype.value*8)
        asmblock  = "        "+self.asmwrap(f"addi {reg}, zero, 60")
        asmblock += "        "+self.asmwrap(f"slli {reg}, {reg}, {6-datatype.value.bit_length()}")
        asmblock += self.asmwrap(f"vsetvli {reg}, {reg}, {dt_size}, m1")
        return asmblock

    def load_vector_immstride(self, areg : greg_type, byte_stride : int,
                    vreg : vreg_type, datatype : asm_data_type):
        raise NotImplementedError("RVV has no load with immediate stride")

    def load_vector_gregstride(self, areg : greg_type, sreg : greg_type,
                    vreg : vreg_type, datatype : asm_data_type):
        dt_suf = self.dt_suffixes[datatype]
        return self.asmwrap(f"vls{dt_suf}.v {vreg}, ({areg}), {sreg}")

    def load_vector_gather(self, areg : greg_type, offvreg : vreg_type,
                           vreg : vreg_type, datatype : asm_data_type,
                           indextype : asm_index_type):
        dt_suf = self.it_suffixes[indextype]
        return self.asmwrap(f"vlx{dt_suf}.v {vreg}, ({areg}), {offvreg}")

    def store_vector_immstride(self, areg : greg_type, byte_stride : int,
                    vreg : vreg_type, datatype : asm_data_type):
        raise NotImplementedError("RVV has no store with immediate stride")

    def store_vector_gregstride(self, areg : greg_type, sreg : greg_type,
                    vreg : vreg_type, datatype : asm_data_type):
        dt_suf = self.dt_suffixes[datatype]
        return self.asmwrap(f"vss{dt_suf}.v {vreg}, ({areg}), {sreg}")

    def store_vector_scatter(self, areg : greg_type, offvreg : vreg_type,
                             vreg : vreg_type, datatype : asm_data_type,
                             indextype : asm_index_type):
        dt_suf = self.it_suffixes[indextype]
        return self.asmwrap(f"vsux{dt_suf}.v {vreg}, ({areg}), {offvreg}")
