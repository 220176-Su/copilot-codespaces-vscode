# ALU 控制器设计

主控制器提供 `ALUOp`，R 型指令再结合 `funct` 字段决定具体运算。

## ALUOp 语义

- `00`：执行加法（用于 `lw/sw` 地址计算）
- `01`：执行减法（用于 `beq` 比较）
- `10`：R 型，由 `funct` 决定

## funct 到 ALUCtrl 映射（R 型）

| 指令 | funct | ALUCtrl |
|---|---|---|
| add | 100000 | 0010 |
| sub | 100010 | 0110 |

## 完整输出规则

| ALUOp | funct | ALUCtrl | 说明 |
|---|---|---|---|
| 00 | xxxxxx | 0010 | add |
| 01 | xxxxxx | 0110 | sub |
| 10 | 100000 | 0010 | add |
| 10 | 100010 | 0110 | sub |

其中 `ALUCtrl` 可按 Logisim ALU 的操作编码自行对齐；若编码不同，仅需保持语义一致。
