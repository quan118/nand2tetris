// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)

// Put your code here.

@R2
M=0 // R[2]=0

(LOOP)
@R1
D=M // D = R[1]

@END
D;JLE // If R[1] <= 0 go to @END

@R0
D=M // D = R[0]
@R2
M=D+M // R[2] += R[0]

@R1
M=M-1 // R[1]--

@LOOP
0;JMP

(END)
@END
0;JMP
