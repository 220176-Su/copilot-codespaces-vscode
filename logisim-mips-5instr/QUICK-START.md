# Logisim MIPS 单周期 CPU - 快速开始指南（5分钟版）

## 🎯 目标

在 Logisim 中构建一个能运行 5 条指令（add、sub、lw、sw、beq）的单周期 MIPS CPU。

---

## ⏱️ 快速步骤

### 1️⃣ 准备（1分钟）

**下载并安装 Logisim**
- 官网：http://www.cburch.com/logisim/
- 版本：2.7.1 或更新版本
- 系统：Windows / macOS / Linux（需要 Java）

**验证安装**
```bash
java -jar logisim.jar
```

---

### 2️⃣ 使用汇编器生成机器码（2分钟）

**将汇编程序转换为十六进制**

```bash
# 使用提供的 Python 汇编器
python3 mips-assembler.py test-program.asm output.hex

# 输出示例：
# 012A5020  (add $t2, $t0, $t1)
# 012B5822  (sub $t3, $t0, $t1)
# AC2A0000  (sw $t2, 0($zero))
# ...
```

**或手工转换**（查看下方转换表）

---

### 3️⃣ 在 Logisim 中构建电路（20-30分钟）

#### 方案 A：手工搭建（推荐学习）

**A1. 新建项目**
```
File → New → Empty Circuit
保存为：cpu_single_cycle.circ
```

**A2. 添加基础模块**

依次从左侧菜单添加：

| 组件名 | 菜单 | 参数 |
|--------|------|------|
| Input（clk） | Wiring | - |
| Register（PC） | Memory | Bit Width: 32 |
| ROM（IMEM） | Memory | Addr: 10 bits, Data: 32 bits |
| Register File | 自建或用 RAM | 2 read, 1 write |
| ALU | Arithmetic | 支持 add, sub |
| RAM（DMEM） | Memory | Addr: 10 bits, Data: 32 bits |
| 多路器（MUX） | Plexers | 多个 |
| Output（观测点） | Wiring | - |

**A3. 连接模块**

```
PC → IMEM → 指令解析
           ↓
       Main Control
           ↓
Register File ← 控制信号
           ↓
        ALU ← 控制信号
           ↓
       DMEM
           ↓
       WriteBack → Register File
```

详见 `cpu-implementation-guide.md` 第三部分

#### 方案 B：使用脚本生成（快速）

```bash
python3 generate_logisim.py > cpu_single_cycle.circ
```

（脚本待补充，需自己完成或参考 Logisim 官方模板）

---

### 4️⃣ 导入程序代码（1分钟）

**A. 在 IMEM 中加载机器码**

1. 双击 IMEM（ROM）组件
2. 选择 `Edit Contents`
3. 粘贴机器码（十六进制）

示例：
```
地址  数据
0:    012A5020   (add $t2, $t0, $t1)
1:    012B5822   (sub $t3, $t0, $t1)
2:    AC2A0000   (sw $t2, 0($zero))
3:    8C2C0000   (lw $t4, 0($zero))
4:    104C0001   (beq $t2, $t4, label_ok)
5:    00000022   (sub $t5, $t0, $t0)
6:    014C5022   (label_ok: sub $t6, $t2, $t1)
```

**B. 设置寄存器初值**

双击 Register File → Edit Contents：
```
寄存器 8 ($t0) = 5
寄存器 9 ($t1) = 3
```

---

### 5️⃣ 运行仿真（1分钟）

1. `Simulate` → `Simulate...` 打开仿真窗口
2. 双击 `clk` 组件，设置时钟周期（e.g., 1Hz = 1000ms）
3. 按 `Step` 逐步执行或 `Run` 连续执行

**观察结果**：

| PC | 指令 | 预期结果 |
|----|------|---------|
| 0 | add $t2, $t0, $t1 | $t2 = 8 |
| 1 | sub $t3, $t0, $t1 | $t3 = 2 |
| 2 | sw $t2, 0($zero) | Mem[0] = 8 |
| 3 | lw $t4, 0($zero) | $t4 = 8 |
| 4 | beq $t2, $t4, +1 | **PC跳转到6**（不执行5） |
| 6 | sub $t6, $t2, $t1 | $t6 = 5 |

✅ **验证成功条件**：
- $t2 = 8, $t3 = 2, $t4 = 8, $t6 = 5
- Mem[0] = 8
- 分支正确跳转

---

## 📝 汇编指令转机器码速查表

### R 型指令（add/sub）

格式：`opcode(6) rs(5) rt(5) rd(5) shamt(5) funct(6)`

```
add  $rd, $rs, $rt

opcode = 000000 (0)
funct  = 100000 (32)

例：add $t2, $t0, $t1
rs = 8 ($t0)
rt = 9 ($t1)
rd = 10 ($t2)

机器码 = 0 << 26 | 8 << 21 | 9 << 16 | 10 << 11 | 0 << 6 | 32
       = 0x012A5020
```

### I 型指令（lw/sw/beq）

格式：`opcode(6) rs(5) rt(5) immediate(16)`

```
lw   $rt, immediate($rs)

opcode = 100011 (35)

例：lw $t4, 0($zero)
rs = 0 ($zero)
rt = 12 ($t4)
imm = 0

机器码 = 35 << 26 | 0 << 21 | 12 << 16 | 0
       = 0x8C2C0000
```

---

## 🐛 常见问题速解

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| PC 不自动递增 | 时钟未连接 | 检查 PC 寄存器的 CLK 输入 |
| 寄存器值不更新 | RegWrite 信号为 0 | 验证 Main Control 输出 |
| 分支不跳转 | Zero 标志或 Branch 信号错误 | 检查 ALU 的 zero 输出和 PCSrc MUX |
| 存储器读不出数据 | MemRead 信号为 0 | 检查 I 型指令的控制信号 |
| 指令解析错误 | 机器码格式不对 | 用汇编器重新生成 |

---

## 📂 文件清单

| 文件 | 说明 |
|------|------|
| `README.md` | 架构和设计思想 |
| `control-table.md` | 主控制器真值表 |
| `alu-control.md` | ALU 控制器真值表 |
| `test-program.asm` | 测试汇编程序 |
| `validation-checklist.md` | 验证检查清单 |
| `cpu-implementation-guide.md` | 详细实现指南 |
| `mips-assembler.py` | 汇编器脚本 |
| `QUICK-START.md` | 本文档 |

---

## 🚀 下一步

1. **完成基础搭建** → 运行 `test-program.asm`
2. **扩展指令集** → 添加 `and`, `or`, `slt` 等
3. **优化设计** → 加入流水线、分支预测
4. **深入学习** → 研究多周期 CPU、异常处理

---

## 📚 参考资源

- Logisim 官方文档：http://www.cburch.com/logisim/docs.html
- MIPS 指令集手册：https://en.wikipedia.org/wiki/MIPS_architecture
- 推荐教材：《计算机组织与设计》（Patterson & Hennessy）

---

**祝您成功！遇到问题请参考 `cpu-implementation-guide.md` 的第六部分。**🎉
