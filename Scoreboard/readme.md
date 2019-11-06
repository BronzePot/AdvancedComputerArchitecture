# Coding for scoreboard
实现记分牌算法
## 题目内容
跑通下面的汇编指令 
`LD F6 34 R2  
LD F2 45 R3  
MULT F0 F2 F4  
SUBD F8 F6 F2  
DIVD F10 F0 F6  
ADDD F6 F8 F2`  
能够输出每个时钟周期记分牌、功能单元、寄存器组的状态  
## 感想
肝了两个晚上，不是很难，但是逻辑需要理清楚，为了达到正确的输出还时花了不少时间耐心调试，虽然代码可能不太优美，但至少还是正确实现了  
运行的代码支持LD、SD、ADDD、SUBD、DIVD、MULT命令，支持偶数编号的目标浮点寄存器F0-F30，支持偶数编号的源浮点寄存器F0-F30和其他不以F开头的源（偷了个懒）