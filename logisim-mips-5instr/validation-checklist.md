# 验证清单

- [ ] add：`rd <- rs + rt` 写回正确
- [ ] sub：`rd <- rs - rt` 写回正确
- [ ] sw：地址=`rs+imm`，写数据=`rt`，内存写使能正确
- [ ] lw：地址=`rs+imm`，内存读使能与写回路径正确
- [ ] beq：`Zero=1` 时 `PCSrc=1`，跳转到 `PC+4+(imm<<2)`
- [ ] beq：`Zero=0` 时 `PCSrc=0`，下一条为 `PC+4`
- [ ] 控制器输出与 `control-table.md` 一致
- [ ] ALU 控制输出与 `alu-control.md` 一致
- [ ] 串行程序执行后寄存器/内存状态符合预期
