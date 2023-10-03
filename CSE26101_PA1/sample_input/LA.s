	.data
array:	.word	3
    	.word	123
    	.word	4346
array2: .word   0x11111111
        .word   127
	.text
main:
	addiu   $2,   $0, 1024
    addu    $3, $2, $2
    or  $4,$3,$2
    sll $6,$5,16
    la  $4,array
