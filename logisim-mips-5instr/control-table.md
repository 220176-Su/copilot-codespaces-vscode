# 主控制器真值表（5 指令）

约定控制信号：

- `RegDst`：0->rt，1->rd
- `RegWrite`：寄存器写使能
- `ALUSrc`：0->寄存器，1->立即数
- `MemRead`：数据存储器读使能
- `MemWrite`：数据存储器写使能
- `MemtoReg`：0->ALUResult，1->MemData
- `Branch`：分支指令标志
- `ALUOp`：主控制器给 ALU 控制器的高层编码

| 指令 | opcode | RegDst | RegWrite | ALUSrc | MemRead | MemWrite | MemtoReg | Branch | ALUOp |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| add | 000000 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 10 |
| sub | 000000 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 10 |
| lw  | 100011 | 0 | 1 | 1 | 1 | 0 | 1 | 0 | 00 |
| sw  | 101011 | X | 0 | 1 | 0 | 1 | X | 0 | 00 |
| beq | 000100 | X | 0 | 0 | 0 | 0 | X | 1 | 01 |

`X` 表示无关项（don't care）。
