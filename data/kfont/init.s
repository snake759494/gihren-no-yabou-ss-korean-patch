! Boot hook (runs from the temporary copy at the end of 0.BIN): copy the Korean font payload into the
! unused tail of the GFS directory table (survives every game mode) and the movie subtitle data into
! an unused LWRAM block, then continue to the real init.
	.section .text
	.global _kinit
_kinit:
	mov.l	.Lsrc,r1
	mov.l	.Ldst,r2
	mov.l	.Llen,r3
1:	mov.l	@r1+,r0
	mov.l	r0,@r2
	dt	r3
	bf/s	1b
	add	#4,r2
	mov.l	.Ldst2,r2
	mov.l	.Llen2,r3
	tst	r3,r3
	bt	3f
2:	mov.l	@r1+,r0
	mov.l	r0,@r2
	dt	r3
	bf/s	2b
	add	#4,r2
3:	mov.l	.Lmain,r0
	jmp	@r0
	nop
	.align	2
.Lsrc:	.long	0x06046060
.Ldst:	.long	0x06006E00
.Llen:	.long	0x11111111
.Ldst2:	.long	0x002F3800
.Llen2:	.long	0x22222222
.Lmain:	.long	0x0601125C
