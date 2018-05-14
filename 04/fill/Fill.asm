// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.

(LOOP)
@KBD
D=M
@WHITE_COLOR
D;JEQ

(BLACK_COLOR)
@color
M=-1 // color=-1
@DRAW_INIT
0;JMP
(WHITE_COLOR)
@color
M=0 // color=0

(DRAW_INIT)
@8192
D=A
@n
M=D // n = 8192
@SCREEN
D=A
@i
M=D // i = @SCREEN

(DRAW)
@n
D=M;
@LOOP
D;JLE // if (n == 0) -> finish draw -> listen keyboard event

@color
D=M // D = color

@i
A=M
M=D // draw on the screen

@i
M=M+1 // i++
@n
M=M-1 // n--
@DRAW
0;JMP

