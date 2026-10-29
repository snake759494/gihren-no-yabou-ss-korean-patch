ENTRY(_kentry)
_knum   = 0x06006FFC;
_kglyph = 0x06007000;
SECTIONS {
  . = 0x06006E00;
  .text : { *(.text.entry) *(.text.kdraw) *(.text*) }
  .rodata : { *(.rodata*) }
  .data : { *(.data*) }
  /DISCARD/ : { *(.comment) *(.bss*) }
}
