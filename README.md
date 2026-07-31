# LC-3 processor

An LC-3 processor written from scratch in SystemVerilog, for the Computer Architecture
course at the University of Verona. Everything is here: the datapath, the control unit as
a finite state machine, the ALU, the register file and the RAM.

The control unit decodes the full 16-entry LC-3 opcode table. Fourteen instructions are
implemented — `BR`, `ADD`, `LD`, `ST`, `JSR`, `AND`, `LDR`, `STR`, `NOT`, `LDI`, `STI`,
`RET`/`JMP`, `LEA`, `TRAP`. `RTI` and the reserved opcode are declared but left as stubs
that print a message, since neither is needed without interrupt support.

The ALU does three operations (add, bitwise and, two's complement negate); `NOT` and
subtraction are built on top of those. Condition codes are set by a separate N/Z/P block,
and sign extension has its own modules for the 5, 6, 9 and 11 bit immediate fields.

## Layout

```
LC-3/
├── LC-3 non-hierarchical/     the version that runs
│   ├── Componenti/            design.sv, testbench.sv, and one file per module
│   ├── Output/                dump.vcd from the last simulation
│   └── makefile
└── LC-3 hierarchical (WIP)/   same processor, split into a module hierarchy — unfinished
```

`Report.pdf` in the root has the full write-up, in Italian, with the datapath drawings.

## Simulating

You need [Icarus Verilog](https://steveicarus.github.io/iverilog/). From
`LC-3/LC-3 non-hierarchical`:

```bash
make
```

That compiles the design with `iverilog`, runs it under `vvp` and drops `dump.vcd` into
`Output/`. The FSM prints its state at every step, so you can follow the fetch-decode-execute
cycle straight in the terminal.

To look at the waveforms:

```bash
gtkwave Output/dump.vcd
```

## Running your own program

The test program is written directly into the RAM's `initial` block in `Ram.sv`, as binary
literals starting at address `0x3000` — which is where the LC-3 begins execution. Address
`0x0025` holds the halt TRAP vector. Edit those cells to run something else.

## Authors

Antonio Iovine, for the Computer Architecture course, University of Verona.
