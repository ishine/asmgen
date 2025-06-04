# ------------------------------------------------------------------------------
# SPDX-License-Identifier: MIT OR GPL-3.0-or-later
# Copyright (C) 2021 Stepan Nassyr <s.nassyr@fz-juelich.de>
# Copyright (C) 2021 Stepan Nassyr <s.nassyr@xcpp.org>
# ------------------------------------------------------------------------------
"""
Tests AVX fmul instruction code generation
"""
from asmgen.registers import asm_data_type as adt

from .test_avx_opd3 import test_avx_opd3

class test_avx_fmul(test_avx_opd3):
    """
    Tests AVX opd3 operations
    """
    def test_fmul_fp64(self):
        """
        Tests that the AVX generator generates correct FP64 FMUL instructions
        """

        self.assertEqual(
            "vmulpd %%xmm1,%%xmm2,%%xmm0\n",
            self.gen128.fmul(
                adreg=self.gen128.vreg(1),
                bdreg=self.gen128.vreg(2),
                cdreg=self.gen128.vreg(0),
                a_dt=adt.FP64, b_dt=adt.FP64, c_dt=adt.FP64))

        self.assertEqual(
            "vmulpd %%ymm1,%%ymm2,%%ymm0\n",
            self.gen256.fmul(
                adreg=self.gen256.vreg(1),
                bdreg=self.gen256.vreg(2),
                cdreg=self.gen256.vreg(0),
                a_dt=adt.FP64, b_dt=adt.FP64, c_dt=adt.FP64))

        self.assertEqual(
            "vmulpd %%zmm1,%%zmm2,%%zmm0\n",
            self.gen512.fmul(
                adreg=self.gen512.vreg(1),
                bdreg=self.gen512.vreg(2),
                cdreg=self.gen512.vreg(0),
                a_dt=adt.FP64, b_dt=adt.FP64, c_dt=adt.FP64))

    def test_fmul_fp32(self):
        """
        Tests that the AVX generator generates correct FP32 FMUL instructions
        """

        self.assertEqual(
            "vmulps %%xmm1,%%xmm2,%%xmm0\n",
            self.gen128.fmul(
                adreg=self.gen128.vreg(1),
                bdreg=self.gen128.vreg(2),
                cdreg=self.gen128.vreg(0),
                a_dt=adt.FP32, b_dt=adt.FP32, c_dt=adt.FP32))

        self.assertEqual(
            "vmulps %%ymm1,%%ymm2,%%ymm0\n",
            self.gen256.fmul(
                adreg=self.gen256.vreg(1),
                bdreg=self.gen256.vreg(2),
                cdreg=self.gen256.vreg(0),
                a_dt=adt.FP32, b_dt=adt.FP32, c_dt=adt.FP32))

        self.assertEqual(
            "vmulps %%zmm1,%%zmm2,%%zmm0\n",
            self.gen512.fmul(
                adreg=self.gen512.vreg(1),
                bdreg=self.gen512.vreg(2),
                cdreg=self.gen512.vreg(0),
                a_dt=adt.FP32, b_dt=adt.FP32, c_dt=adt.FP32))

    def test_fmul_fp16(self):
        """
        Tests that the AVX generator generates correct FP16 FMUL instructions
        """

        self.assertEqual(
            "vmulph %%zmm1,%%zmm2,%%zmm0\n",
            self.gen512.fmul(
                adreg=self.gen512.vreg(1),
                bdreg=self.gen512.vreg(2),
                cdreg=self.gen512.vreg(0),
                a_dt=adt.FP16, b_dt=adt.FP16, c_dt=adt.FP16))
