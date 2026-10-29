! Hooked draw entry: anything that is not a Korean code (0x4000..0x401f) jumps straight to the
! original draw routine with registers and stack untouched (some callers pass stack arguments).
	.section .text.entry
	.global _kentry
_kentry:
	mov.l	.Lbase,r0
	sub	r0,r5
	mov	#32,r0
	cmp/hs	r0,r5
	mov.l	.Lbase,r0
	bt	.Lorig
	add	r0,r5
	mov.l	.Lkdraw,r0
	jmp	@r0
	nop
.Lorig:
	add	r0,r5
	mov.l	.Lorigfn,r0
	jmp	@r0
	nop
	.align	2
.Lbase:	.long	0x4000
.Lkdraw:	.long	_kdraw
.Lorigfn:	.long	0x601462c
