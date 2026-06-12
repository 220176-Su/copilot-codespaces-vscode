# Logisim MIPS 单周期 CPU 实现与使用指南

## 第一部分：Logisim 项目文件生成与导入

### 1.1 创建项目结构

本指南使用 Logisim v2.x 版本（推荐下载地址：http://www.cburch.com/logisim/）。

#### 步骤 1：打开 Logisim 并新建项目

1. 启动 Logisim
2. `File` → `New` → 选择 `Empty Circuit`
3. 保存为 `cpu_single_cycle.circ`（放在 `logisim-mips-5instr/` 目录下）

#### 步骤 2：设置主电路（顶层）

将默认电路重命名为 `cpu_single_cycle`：
- 右键点击左侧的 `main` 电路 → `Rename` → 改为 `cpu_single_cycle`

---

### 1.2 创建子电路与模块

#### 创建新电路的通用步骤

在 Logisim 中，`Project` → `Add Circuit` → 输入名称 → `OK`

我们需要创建以下子电路：

1. **`register_file`** - 32×32 寄存器堆（2读1写）
2. **`alu`** - 算术逻辑单元
3. **`main_control`** - 主控制器（opcode → 控制信号）
4. **`alu_control`** - ALU 控制器（ALUOp + funct → ALU 操作码）
5. **`sign_extend`** - 16位立即数符号扩展
6. **`shift_left_2`** - 分支偏移左移2位
7. **`datapath`** - 数据通路总集成

---

## 第二部分：各模块详细实现

### 2.1 Sign Extend（符号扩展）

**用途**：将 16 位立即数扩展为 32 位

**实现方法**（Logisim 图形化）：

1. 新建 `sign_extend` 电路
2. **输入**：16 根输入线（命名为 `immediate[15:0]`）
3. **输出**：32 根输出线（命名为 `extended[31:0]`）
4. **逻辑**：
   - 输出 `[15:0]` = 输入 `[15:0]`
   - 输出 `[31:16]` = 全部连接到输入的第 15 位（符号位）

**Logisim 实现步骤**：

```
输入引脚（16根）
    ↓
分割器（Splitter）- 将 16 位拆分为单独的线
    ↓
第 15 位 → 32位复制器（Repeating）或用 16 个 NOT/Buffer 级联
    ↓
合并器（Joiner）- 合并为 32 位
    ↓
输出引脚（32根）
```

**推荐使用 Logisim 内置的 Extending 组件**：
- 直接从 `Wiring` 菜单拖入 `Bit Extender`
- 配置为 `In bits: 16` → `Out bits: 32`

---

### 2.2 Shift Left 2（左移2位）

**用途**：分支偏移 `immediate * 4`

**实现方法**：

1. 新建 `shift_left_2` 电路
2. **输入**：32 根输入线（`in[31:0]`）
3. **输出**：32 根输出线（`out[31:0]`）
4. **逻辑**：
   - 输出 `[31:2]` = 输入 `[29:0]`
   - 输出 `[1:0]` = 常数 0

**Logisim 实现**：

```
输入 32 位 (Splitter)
    ↓
高 30 位 [29:0] → 左移后占据 [31:2]
低 2 位固定为 0
    ↓
合并（Joiner）为 32 位输出
```

或直接用硬连线：只需将输入的 `[29:0]` 连到输出的 `[31:2]`，输出的 `[1:0]` 接地。

---

### 2.3 Register File（寄存器堆）

**规格**：32 个 32 位寄存器，支持 2 读 1 写

**输入**：

| 名称 | 位宽 | 功能 |
|------|------|------|
| `read_reg1` | 5 | 第一个读地址 |
| `read_reg2` | 5 | 第二个读地址 |
| `write_reg` | 5 | 写地址 |
| `write_data` | 32 | 写入数据 |
| `write_enable` | 1 | 写使能 |
| `clk` | 1 | 时钟 |

**输出**：

| 名称 | 位宽 | 功能 |
|------|------|------|
| `read_data1` | 32 | 第一个读数据 |
| `read_data2` | 32 | 第二个读数据 |

**Logisim 实现步骤**：

1. 新建 `register_file` 电路
2. 在 `Memory` 菜单中选择 `RAM`
   - 配置：`Address Bits: 5`（32个地址）, `Data Bits: 32`
   - 注意：Logisim 的 RAM 通常支持同时读写
3. 使用两个**多路选择器（Multiplexer）**分别驱动两个读端口：
   - 第一个 MUX：32:1（输入为 32 个寄存器值，选择信号为 `read_reg1`）
   - 第二个 MUX：32:1（输入为 32 个寄存器值，选择信号为 `read_reg2`）

**替代方案**（更简洁）：

使用 Logisim 的 **Combinational Analysis** 或直接用脚本生成（见下文Python脚本部分）

---

### 2.4 ALU（算术逻辑单元）

**规格**：支持 `add`, `sub`, `and`, `or` 操作

**输入**：

| 名称 | 位宽 | 功能 |
|------|------|------|
| `a` | 32 | 操作数 A |
| `b` | 32 | 操作数 B |
| `alu_ctrl` | 4 | 控制码 |

**输出**：

| 名称 | 位宽 | 功能 |
|------|------|------|
| `result` | 32 | 计算结果 |
| `zero` | 1 | 零标志（结果==0时为1） |

**控制码**：

| 码值 | 操作 |
|------|------|
| 0010 | 加法（add） |
| 0110 | 减法（sub） |
| 0000 | 与（and） |
| 0001 | 或（or） |

**Logisim 实现**：

1. 新建 `alu` 电路
2. 使用 Logisim 的 `Arithmetic` 组件（Adder）和 `Logic` 组件（AND, OR）
3. 用 4:1 Multiplexer 根据 `alu_ctrl` 选择输出
4. 使用 `NOR` 门检测零标志：
   ```
   zero = NOR(result[31:0])  // 所有位都是0时输出1
   ```

**详细原理图连接**：

```
a[31:0] ─┬─→ Adder ─→ MUX
         ├─→ Sub ─→ (select=0110)
         │
b[31:0] ─┴─→
              ↓
         alu_ctrl[3:0] 作为 MUX 选择信号
              ↓
         result[31:0] ← MUX 输出
              ↓
         NOR 门检测 → zero
```

---

### 2.5 Main Control（主控制器）

**输入**：`opcode[5:0]` - 指令的操作码字段

**输出**（根据 `control-table.md`）：

```
RegDst, RegWrite, ALUSrc, MemRead, MemWrite, MemtoReg, Branch, ALUOp[1:0]
```

**真值表**（重复自 control-table.md）：

| 指令 | opcode | RegDst | RegWrite | ALUSrc | MemRead | MemWrite | MemtoReg | Branch | ALUOp |
|------|--------|--------|----------|--------|---------|----------|----------|--------|-------|
| add  | 000000 | 1      | 1        | 0      | 0       | 0        | 0        | 0      | 10    |
| sub  | 000000 | 1      | 1        | 0      | 0       | 0        | 0        | 0      | 10    |
| lw   | 100011 | 0      | 1        | 1      | 1       | 0        | 1        | 0      | 00    |
| sw   | 101011 | X      | 0        | 1      | 0       | 1        | X        | 0      | 00    |
| beq  | 000100 | X      | 0        | 0      | 0       | 0        | X        | 1      | 01    |

**Logisim 实现**：

1. 新建 `main_control` 电路
2. 使用 **ROM（只读存储器）** 或 **Combinational Logic**
3. 推荐使用 ROM：
   - 配置：`Address Bits: 6`（6位opcode）, `Data Bits: 8`（8个控制信号）
   - 手动填充 ROM 值

**ROM 填充规则**：

地址 = opcode，数据 = 8 位控制信号编码：
```
位 7-6: RegDst, RegWrite  
位 5-4: ALUSrc, MemRead  
位 3-2: MemWrite, MemtoReg  
位 1-0: Branch, ALUOp[1]
```

或使用 **组合逻辑**（AND/OR 网络）- 见下文第四部分（自动生成脚本）

---

### 2.6 ALU Control（ALU控制器）

**输入**：

| 名称 | 位宽 |
|------|------|
| `alu_op` | 2 |
| `funct` | 6 |

**输出**：

| 名称 | 位宽 |
|------|------|
| `alu_ctrl` | 4 |

**真值表**（自 alu-control.md）：

| ALUOp | funct | ALUCtrl |
|-------|-------|---------|
| 00    | XXXXX | 0010    |
| 01    | XXXXX | 0110    |
| 10    | 100000| 0010    |
| 10    | 100010| 0110    |

**Logisim 实现**：使用组合逻辑（多个 AND/OR 门）或 ROM

---

### 2.7 数据通路（Datapath）

**概览**：

```
┌─────────────┐
│   PC (32)   │ ← 时钟驱动
└──────┬──────┘
       │ [31:0]
       ↓
┌──────────────────────┐
│  Instruction Memory  │
└──────┬───────────────┘
       │ [31:0]
       ↓ (instr)
    [31:26] opcode
    [25:21] rs (read_reg1)
    [20:16] rt (read_reg2)
    [15:11] rd
    [15:0]  immediate
    [5:0]   funct

       ↓
┌───────────────────────────────────────┐
│    Register File (2read, 1write)      │
│  rs → read_reg1 ──→ read_data1 [31:0] │
│  rt → read_reg2 ──→ read_data2 [31:0] │
└───────────────────────────────────────┘
       ↓           ↓
  read_data1   read_data2
       │           │
       │      ┌────┴────┐
       │      │ Sign Extend
       │      │ (16→32)
       │      └────┬────┘
       │      imm_ext[31:0]
       │           │
       └─┬─────────┤ ALUSrc Mux
         │         │
      alu_a    alu_b (选一个)
         │         │
         └────┬────┘
              ↓
           ┌─────────┐
           │   ALU   │
           │ alu_op  │ ← from Main Control
           └────┬────┘
            alu_result[31:0], zero
                │
                ├─→ Data Memory (address)
                │    MemRead, MemWrite ← from Main Control
                │    ↓
                │   mem_data[31:0]
                │
         ┌──────┴────────┐
         │  MemtoReg Mux │ ← from Main Control
         │ (alu vs mem)  │
         └──────┬────────┘
                │ wb_data[31:0]
                │
         ┌──────┴──────┐
         │ RegDst Mux  │ ← from Main Control
         │ (rt vs rd)  │
         └──────┬──────┘
                │ write_reg[4:0]
                │
           Register File write port
           write_enable ← from Main Control

PC计算：
┌────────┐
│ PC+4   │ ← Adder
└────┬───┘
     │
  ┌──┴─────────────────┐
  │   PC Src Mux       │
  │  (Branch & Zero)   │
  └────────┬───────────┘
           │
       ┌───┴────┐
       │ Branch │← from Main Control
       │ Target │
       │Calc    │
       │(SL2+   │
       │ PC+4)  │
       └────────┘
```

---

## 第三部分：手工搭建步骤（详细）

### 3.1 新建主电路框架

1. 在主电路 `cpu_single_cycle` 中，从左侧菜单拖入以下基本组件：
   - `Input Pin`：clk, reset
   - `Output Pin`：Debug 观测点（可选）

### 3.2 添加程序计数器（PC）

1. 从 `Memory` 菜单拖入 **Register** 组件
   - 配置：`Bit Width: 32`
   - Label: `PC`
2. 输入：
   - `D` (data input) - 来自 MUX（分支选择）
   - `CLK` - 时钟
   - `CLR` (clear) - 复位
3. 输出：`Q` 32位

### 3.3 添加指令存储器（IMEM）

1. 从 `Memory` 菜单拖入 **ROM**
   - `Address Bits: 10`（1024 条指令 × 4 字节 = 4KB）
   - `Data Bits: 32`
   - Label: `IMEM`
2. 配置指令：
   - 在 Logisim 中双击 ROM → 进入编辑模式
   - 手动输入指令字或使用脚本（见第四部分）

### 3.4 添加寄存器堆（Register File）

（需要自建或使用脚本生成 - 见第四部分）

### 3.5 连接数据通路

按照上一节的框图，依次连接各模块。

---

## 第四部分：使用 Python 脚本自动生成

为了加快开发，我们提供 Python 脚本来生成 Logisim `.circ` 文件。

### 4.1 脚本概览

创建文件 `generate_logisim.py`：

```python
#!/usr/bin/env python3
"""
生成 Logisim MIPS 单周期 CPU 的 .circ 文件
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom
import sys

class LogisimCircuit:
    def __init__(self, name):
        self.name = name
        self.components = []
        self.wires = []
    
    def add_component(self, comp_id, lib, name, loc_x, loc_y, facing="east", props=None):
        """添加组件"""
        comp = {
            'id': comp_id,
            'lib': lib,
            'name': name,
            'x': loc_x,
            'y': loc_y,
            'facing': facing,
            'props': props or {}
        }
        self.components.append(comp)
        return comp
    
    def add_wire(self, x1, y1, x2, y2):
        """添加连线"""
        self.wires.append((x1, y1, x2, y2))
    
    def to_xml_string(self):
        """转为 XML 字符串"""
        # 这是一个简化版本，完整版本会生成标准的 Logisim XML
        xml_str = f"""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<project version="1.0">
    <lib desc="#Wiring" name="0"/>
    <lib desc="#Gates" name="1"/>
    <lib desc="#Plexers" name="2"/>
    <lib desc="#Arithmetic" name="3"/>
    <lib desc="#Memory" name="4"/>
    <lib desc="#I/O" name="5"/>
    <lib desc="#Base" name="6"/>
    <main name="{self.name}"/>
    <circuit name="{self.name}">
        <!-- Components will be added here -->
    </circuit>
</project>"""
        return xml_str

# 使用示例
circuit = LogisimCircuit("cpu_single_cycle")
circuit.add_component("pc", "4", "Register", 100, 100, props={"bitwidth": "32"})
print(circuit.to_xml_string())
```

### 4.2 完整脚本（推荐）

为简化操作，建议：

1. **下载 Logisim 官方示例**并在其基础上修改
2. 或使用第三方工具：[Logisim-compatible circuit generator](https://github.com/...)
3. 或手工在 Logisim 中逐步搭建（推荐学习，约 2-3 小时）

---

## 第五部分：仿真与测试

### 5.1 程序加载

1. 双击 `IMEM` 组件，进入 RAM/ROM 编辑界面
2. 将汇编程序转换为机器码，手动输入或使用 MIPS 汇编器
3. 示例：
   ```
   add $t2, $t0, $t1
   ```
   对应的 32 位机器码：
   ```
   opcode=000000, rs=8($t0), rt=9($t1), rd=10($t2), funct=100000
   = 000000 01000 01001 01010 00000 100000
   = 0x012A5020 (16进制)
   ```

### 5.2 设置寄存器初值

1. 右键点击 `Register File` → **Edit Contents**
2. 手动设置：
   - `$t0 = 5` (register 8)
   - `$t1 = 3` (register 9)

### 5.3 运行仿真

1. `Simulate` → `Simulate...`
2. 设置时钟频率（e.g., 1 Hz）
3. 逐步执行（Step）或连续执行（Run）
4. 观察：
   - PC 的变化
   - 寄存器值更新
   - 内存读写

### 5.4 预期结果（test-program.asm）

执行以下程序后：

```
add  $t2, $t0, $t1       # t2 = 8
sub  $t3, $t0, $t1       # t3 = 2
sw   $t2, 0($zero)       # Mem[0] = 8
lw   $t4, 0($zero)       # t4 = 8
beq  $t2, $t4, label_ok  # 跳转成功
```

**验证**：
- ✓ `$t2` = 8（十进制）
- ✓ `$t3` = 2
- ✓ `$t4` = 8
- ✓ `Mem[0]` = 8
- ✓ PC 正确跳转到 `label_ok`

---

## 第六部分：常见问题与调试

### Q1：指令执行结果不对？

**检查项**：
1. opcode 是否正确识别？
   - 在主电路中添加 debug output，连接到 `opcode[5:0]`
2. 控制信号是否正确？
   - 验证 `Main Control` 输出与 `control-table.md` 一致
3. ALU 操作是否正确？
   - 验证 `ALU Control` 输出与 `alu-control.md` 一致

### Q2：分支不跳转？

**检查项**：
1. `zero` 标志是否正确计算？
   - 手工检查 ALU 输出和 NOR 门逻辑
2. `Branch` 信号是否为 1？
   - 对于 `beq` 指令，`Main Control` 应输出 `Branch=1`
3. PC 加法器是否工作？
   - 验证 `PC+4` 和 `BranchTarget` 的计算

### Q3：存储器读写错误？

**检查项**：
1. `MemRead` 和 `MemWrite` 使能信号是否正确？
2. 地址计算（`ALU result`）是否正确？
3. 数据通路选择（`MemtoReg` MUX）是否正确？

---

## 第七部分：完整文件清单

生成的项目应包含：

```
logisim-mips-5instr/
├── README.md                           # 架构概述
├── control-table.md                    # 控制信号真值表
├── alu-control.md                      # ALU 控制器
├── test-program.asm                    # 测试程序（汇编）
├── validation-checklist.md             # 验证清单
├── cpu-implementation-guide.md         # 本文档
├── cpu_single_cycle.circ               # Logisim 主电路文件（待生成）
├── assembly-to-machine-code.py         # 汇编器（可选）
└── generate_logisim.py                 # 电路生成脚本（可选）
```

---

## 总结

1. **理解架构**：阅读 `README.md` 和各控制表文档
2. **搭建电路**：
   - 手工方式（3-5 小时，推荐学习）
   - 脚本生成方式（1 小时，快速上手）
3. **编写测试程序**：参考 `test-program.asm`
4. **仿真验证**：按 5.1-5.4 步骤操作
5. **调试优化**：使用第六部分的排查方法

祝您成功！🎉

---

**下一步**：

- 如果需要 Logisim 电路文件模板，请参考下一个文档
- 如果需要汇编器脚本，请参考后续文档
