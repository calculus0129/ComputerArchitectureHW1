	.data
array:	.word	3
    	.word	123
    	.word	4346
array2: .word   0x11111111
        .word   127
	.text
main:
    push $8
	move $9, $10
    blt $12, $10, L
    jal L
    pop $8
    j main
L:
    la  $4,array
    jr $31
