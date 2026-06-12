#!/usr/bin/env python3
"""
MIPS 汇编器 - 将汇编指令转换为机器码
支持 5 条指令：add, sub, lw, sw, beq

使用方法：
    python3 mips-assembler.py input.asm output.hex
"""

import sys
import re
from typing import Dict, List, Tuple

class MIPSAssembler:
    # 寄存器映射
    REGISTERS = {
        '$zero': 0, '$at': 1, '$v0': 2, '$v1': 3,
        '$a0': 4, '$a1': 5, '$a2': 6, '$a3': 7,
        '$t0': 8, '$t1': 9, '$t2': 10, '$t3': 11,
        '$t4': 12, '$t5': 13, '$t6': 14, '$t7': 15,
        '$s0': 16, '$s1': 17, '$s2': 18, '$s3': 19,
        '$s4': 20, '$s5': 21, '$s6': 22, '$s7': 23,
        '$t8': 24, '$t9': 25, '$k0': 26, '$k1': 27,
        '$gp': 28, '$sp': 29, '$fp': 30, '$ra': 31,
    }
    
    # 指令格式定义
    INSTRUCTIONS = {
        # R 型指令
        'add': {'type': 'R', 'opcode': 0b000000, 'funct': 0b100000},
        'sub': {'type': 'R', 'opcode': 0b000000, 'funct': 0b100010},
        
        # I 型指令
        'lw': {'type': 'I', 'opcode': 0b100011},
        'sw': {'type': 'I', 'opcode': 0b101011},
        'beq': {'type': 'I', 'opcode': 0b000100},
    }
    
    def __init__(self):
        self.labels = {}  # 标签 → 地址映射
        self.instructions = []
        self.current_address = 0
    
    def parse_register(self, reg_str: str) -> int:
        """将寄存器名转换为寄存器号"""
        reg_str = reg_str.strip().lower()
        if reg_str not in self.REGISTERS:
            raise ValueError(f"Unknown register: {reg_str}")
        return self.REGISTERS[reg_str]
    
    def parse_immediate(self, imm_str: str) -> int:
        """解析立即数（支持十进制和十六进制）"""
        imm_str = imm_str.strip()
        if imm_str.startswith('0x') or imm_str.startswith('0X'):
            return int(imm_str, 16)
        else:
            return int(imm_str)
    
    def first_pass(self, lines: List[str]) -> None:
        """第一遍：扫描标签"""
        address = 0
        for line in lines:
            # 移除注释
            line = line.split('#')[0].strip()
            if not line:
                continue
            
            # 检查标签
            if line.endswith(':'):
                label = line[:-1].strip()
                self.labels[label] = address
            else:
                address += 1
    
    def encode_r_type(self, inst_name: str, rd: int, rs: int, rt: int) -> int:
        """编码 R 型指令"""
        inst_def = self.INSTRUCTIONS[inst_name]
        opcode = inst_def['opcode']
        funct = inst_def['funct']
        
        # R 型格式：opcode(6) rs(5) rt(5) rd(5) shamt(5) funct(6)
        machine_code = (opcode << 26) | (rs << 21) | (rt << 16) | (rd << 11) | (0 << 6) | funct
        return machine_code & 0xFFFFFFFF
    
    def encode_i_type(self, inst_name: str, rt: int, rs: int, immediate: int) -> int:
        """编码 I 型指令"""
        inst_def = self.INSTRUCTIONS[inst_name]
        opcode = inst_def['opcode']
        
        # I 型格式：opcode(6) rs(5) rt(5) immediate(16)
        # 对于立即数，需要符号扩展处理
        imm_16 = immediate & 0xFFFF
        machine_code = (opcode << 26) | (rs << 21) | (rt << 16) | imm_16
        return machine_code & 0xFFFFFFFF
    
    def second_pass(self, lines: List[str]) -> List[int]:
        """第二遍：编码指令"""
        machine_codes = []
        pc = 0  # 程序计数器
        
        for line in lines:
            # 移除注释
            line = line.split('#')[0].strip()
            if not line:
                continue
            
            # 跳过标签
            if line.endswith(':'):
                continue
            
            # 解析指令
            parts = line.split()
            inst_name = parts[0].lower()
            
            if inst_name not in self.INSTRUCTIONS:
                raise ValueError(f"Unknown instruction: {inst_name}")
            
            inst_type = self.INSTRUCTIONS[inst_name]['type']
            
            if inst_type == 'R':
                # R 型：add/sub rd, rs, rt
                # 格式：inst rd, rs, rt
                rd = self.parse_register(parts[1].rstrip(','))
                rs = self.parse_register(parts[2].rstrip(','))
                rt = self.parse_register(parts[3].rstrip(','))
                machine_code = self.encode_r_type(inst_name, rd, rs, rt)
            
            elif inst_type == 'I':
                if inst_name == 'beq':
                    # beq rs, rt, label
                    rs = self.parse_register(parts[1].rstrip(','))
                    rt = self.parse_register(parts[2].rstrip(','))
                    label = parts[3]
                    
                    # 计算分支偏移
                    target_addr = self.labels[label]
                    offset = target_addr - pc - 1  # PC已经指向下一条指令
                    machine_code = self.encode_i_type(inst_name, rt, rs, offset)
                
                else:
                    # lw/sw rt, immediate(rs)
                    # 格式：lw/sw rt, imm(rs)
                    rt = self.parse_register(parts[1].rstrip(','))
                    
                    # 解析 immediate(rs) 格式
                    mem_addr = parts[2]
                    match = re.match(r'(-?\d+)\(\$(\w+)\)', mem_addr)
                    if not match:
                        raise ValueError(f"Invalid memory addressing: {mem_addr}")
                    
                    immediate = int(match.group(1))
                    rs = self.parse_register('$' + match.group(2))
                    
                    machine_code = self.encode_i_type(inst_name, rt, rs, immediate)
            
            machine_codes.append(machine_code)
            pc += 1
        
        return machine_codes
    
    def assemble(self, asm_code: str) -> List[int]:
        """组装汇编代码"""
        lines = asm_code.strip().split('\n')
        self.first_pass(lines)
        return self.second_pass(lines)
    
    def to_hex_string(self, machine_codes: List[int], word_size=4) -> str:
        """转为十六进制字符串"""
        hex_lines = []
        for code in machine_codes:
            hex_str = f"{code:0{word_size*2}X}"
            hex_lines.append(hex_str)
        return '\n'.join(hex_lines)
    
    def to_logisim_format(self, machine_codes: List[int]) -> str:
        """转为 Logisim RAM 编辑器格式"""
        lines = []
        for addr, code in enumerate(machine_codes):
            lines.append(f"{addr}: {code:08X}")
        return '\n'.join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 mips-assembler.py <input.asm> [output.hex]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    # 读取汇编文件
    try:
        with open(input_file, 'r') as f:
            asm_code = f.read()
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found")
        sys.exit(1)
    
    # 组装
    assembler = MIPSAssembler()
    try:
        machine_codes = assembler.assemble(asm_code)
    except ValueError as e:
        print(f"Assembly error: {e}")
        sys.exit(1)
    
    # 输出
    hex_output = assembler.to_hex_string(machine_codes)
    logisim_output = assembler.to_logisim_format(machine_codes)
    
    print("=== Machine Code (Hex) ===")
    print(hex_output)
    
    print("\n=== Logisim Format ===")
    print(logisim_output)
    
    if output_file:
        with open(output_file, 'w') as f:
            f.write(hex_output)
        print(f"\nSaved to {output_file}")


if __name__ == '__main__':
    main()
