# 最小联调程序（仅使用 add/sub/lw/sw/beq）
# 约定：$zero=0，仿真前手工预置寄存器
# 初值：$t0=5, $t1=3

# R 型
add  $t2, $t0, $t1       # t2 = 8
sub  $t3, $t0, $t1       # t3 = 2

# 访存
sw   $t2, 0($zero)       # Mem[0] = 8
lw   $t4, 0($zero)       # t4 = 8

# 分支
beq  $t2, $t4, label_ok  # 应跳转
sub  $t5, $t0, $t0       # 若跳转成功，此句被跳过

label_ok:
sub  $t6, $t2, $t1       # t6 = 5

# 预期结果：
# t2=8, t3=2, t4=8, t6=5, Mem[0]=8
