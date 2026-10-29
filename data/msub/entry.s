! Wrapper for the movie library's per-frame task (jump table 0x060315FC+0x29C): run the original,
! then draw the subtitle for the current video frame.
	.section .text.entry
	.global _mentry
_mentry:
	sts.l	pr,@-r15
	mov.l	.Lorig,r0
	jsr	@r0
	nop
	mov.l	r0,@-r15
	mov.l	.Lsub,r1
	jsr	@r1
	nop
	mov.l	@r15+,r0
	lds.l	@r15+,pr
	rts
	nop
	.align	2
.Lorig:	.long	0x0601DBFA
.Lsub:	.long	_msub
