	.data
data1:	.word	100
data2:	.word	200
data3:	.word	0x12345678
	.text
main:
    addi $16, $0, 10
    move $4, $16
    jal fibo
    j   fin
fibo:
    slti    $8, $4, 1
    bne $8, $0, B1
    slti    $8, $4, 2
    bne $8, $0, B2
    add $8, $2, $0
    add $2, $3, $2
    move $3, $8
    addi $4, $4, -1
    j fibo
B1:
    add $2, $0, $0
    jr  $31
B2:
    addi    $2, $0, 1
    move    $3, $0
    jr  $31
fin:
    move $17, $2