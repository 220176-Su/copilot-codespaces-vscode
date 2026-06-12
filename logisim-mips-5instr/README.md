# 单周期 MIPS（5 指令）Logisim 实现

本实现选择 5 条指令：`add`、`sub`、`lw`、`sw`、`beq`。

## 1. 指令集合与执行需求

| 指令 | 类型 | 主要行为 | 关键硬件需求 |
|---|---|---|---|
| add rd, rs, rt | R | `R[rd] = R[rs] + R[rt]` | 读寄存器、ALU 加法、写回寄存器 |
| sub rd, rs, rt | R | `R[rd] = R[rs] - R[rt]` | 读寄存器、ALU 减法、写回寄存器 |
| lw rt, imm(rs) | I | `R[rt] = Mem[R[rs]+imm]` | 符号扩展、ALU 地址计算、数据存储器读、写回 |
| sw rt, imm(rs) | I | `Mem[R[rs]+imm] = R[rt]` | 符号扩展、ALU 地址计算、数据存储器写 |
| beq rs, rt, imm | I | 若 `R[rs]==R[rt]`，`PC=PC+4+(imm<<2)` | 寄存器比较（ALU 减法+Zero）、分支地址计算、PC 选择 |

## 2. 基础模块

- `PC`（32 位寄存器）
- `Instruction Memory`（按字寻址，输出 32 位指令）
- `Register File`（2 读 1 写，32×32）
- `Main Control`（opcode -> 控制信号）
- `ALU Control`（ALUOp + funct -> ALU 控制码）
- `Sign Extend`（16 -> 32）
- `Shift Left 2`（分支偏移）
- `ALU`
- `Data Memory`
- 加法器：`PC+4` 与 `BranchTarget`
- 多路器：`RegDst`、`ALUSrc`、`MemtoReg`、`PCSrc`

## 3. 单周期数据通路连接

1. `PC -> Instruction Memory` 取指。
2. 指令字段拆分：`opcode/rs/rt/rd/funct/immediate`。
3. `Register File` 同时读 `rs` 和 `rt`。
4. `Sign Extend(immediate)` 输出 32 位立即数。
5. `ALUSrc` 决定 ALU 第二操作数（`ReadData2` 或扩展立即数）。
6. `ALU` 完成算术/比较/地址计算，输出 `ALUResult` 与 `Zero`。
7. `Data Memory` 以 `ALUResult` 作为地址执行读写。
8. `MemtoReg` 决定写回数据（`ALUResult` 或 `MemReadData`）。
9. `RegDst` 决定写回目的寄存器（`rt` 或 `rd`）。
10. `PC+4` 与 `(SignExtImm<<2)+PC+4` 形成候选下一 PC；`PCSrc = Branch & Zero` 决定分支。

## 4. 控制信号与真值表

见 `control-table.md`。

## 5. ALU 控制器

见 `alu-control.md`。

## 6. 分支路径

- `PCPlus4 = PC + 4`
- `BranchOffset = SignExtImm << 2`
- `BranchTarget = PCPlus4 + BranchOffset`
- `PCNext = (Branch & Zero) ? BranchTarget : PCPlus4`

## 7. Logisim 分层建议

- 顶层：`cpu_single_cycle.circ`（系统总线与主连线）
- 子电路：
  - `datapath`（PC、寄存器堆、ALU、存储器、MUX）
  - `main_control`
  - `alu_control`

## 8. 测试与联调

最小测试程序见 `test-program.asm`。

建议验证顺序：
1. 验证 `add/sub` 写回是否正确。
2. 验证 `sw` 写存储器地址和值。
3. 验证 `lw` 从相同地址读回。
4. 验证 `beq` 在相等时跳转、不等时顺序执行。
5. 在同一程序中串联执行，检查寄存器与内存最终状态。
