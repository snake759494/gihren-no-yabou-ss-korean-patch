ENTRY(_mentry)
SECTIONS {
  . = 0x06009B00;
  .text : { *(.text.entry) *(.text*) }
  .rodata : { *(.rodata*) }
  .data : { *(.data*) }
  .bss : { *(.bss*) *(COMMON) }
  _mdata = ALIGN(4);
}
