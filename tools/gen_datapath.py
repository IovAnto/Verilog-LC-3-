#!/usr/bin/env python3
"""Genera media/datapath-mocha.svg e media/datapath-latte.svg: lo schema del
datapath con il
ciclo fetch-decode-execute che lo attraversa.

I blocchi sono quelli del design in LC-3/: PC, MAR, RAM, IR, la control unit come
macchina a stati, il register file e la ALU.

Sincronizzazione: ogni animazione dura quanto il giro completo e si ripete
all'infinito, e i tempi dei singoli eventi stanno nei keyTimes. Per l'impulso
che scorre lungo un collegamento si usa animateMotion con keyPoints: il punto
resta fermo all'inizio del percorso, lo percorre nella sua finestra, poi resta
fermo alla fine. È l'unico modo per tenere in sincrono più elementi senza
JavaScript.

Gli stati statici degli attributi sono quelli "a riposo" (nessuna evidenziazione,
impulsi invisibili): un renderer che ignora SMIL mostra comunque lo schema
completo e leggibile.

    python3 tools/gen_datapath.py
"""

from common import TEMI, blocco_font, scrivi

LARGH, ALT = 812.0, 412.0
BW, BH = 128.0, 48.0           # dimensione di un blocco
TOT = 9.4                      # durata del giro, in secondi

# posizione (x, y) dell'angolo in alto a sinistra di ogni blocco
B = {
    "PC":      (48, 96),
    "MAR":     (232, 96),
    "RAM":     (416, 96),
    "IR":      (600, 96),
    "FSM":     (600, 196),
    "ALU":     (416, 288),
    "REG":     (232, 288),
}

ETICHETTE = {
    "PC": ("PC", "program counter"),
    "MAR": ("MAR", "memory address"),
    "RAM": ("RAM", "0x3000"),
    "IR": ("IR", "instruction"),
    "FSM": ("FSM", "control unit"),
    "ALU": ("ALU", "add / and / not"),
    "REG": ("RegFile", "R0 - R7"),
}


def centro(nome):
    x, y = B[nome]
    return x + BW / 2, y + BH / 2


def bordo_d(nome):
    x, y = B[nome]
    return x + BW, y + BH / 2


def bordo_s(nome):
    x, y = B[nome]
    return x, y + BH / 2


def bordo_g(nome):
    x, y = B[nome]
    return x + BW / 2, y + BH


def bordo_a(nome):
    x, y = B[nome]
    return x + BW / 2, y


# --------------------------------------------------------- i collegamenti
# (percorso, finestra temporale dell'impulso)

def percorsi():
    pc_r, mar_s = bordo_d("PC"), bordo_s("MAR")
    mar_r, ram_s = bordo_d("MAR"), bordo_s("RAM")
    ram_r, ir_s = bordo_d("RAM"), bordo_s("IR")
    ir_g, fsm_a = bordo_g("IR"), bordo_a("FSM")
    fsm_s = bordo_s("FSM")
    alu_d, alu_s = bordo_d("ALU"), bordo_s("ALU")
    reg_d, reg_g = bordo_d("REG"), bordo_g("REG")
    alu_g = bordo_g("ALU")

    giu = 30            # quanto scende la retroazione sotto i blocchi
    return [
        # (id, percorso, inizio, fine, etichetta, x etichetta, y etichetta)
        # fetch
        ("f1", f"M{pc_r[0]},{pc_r[1]} L{mar_s[0]},{mar_s[1]}", 0.15, 1.15,
         "addr", (pc_r[0] + mar_s[0]) / 2, pc_r[1] - 9),
        ("f2", f"M{mar_r[0]},{mar_r[1]} L{ram_s[0]},{ram_s[1]}", 1.15, 2.15,
         "read", (mar_r[0] + ram_s[0]) / 2, mar_r[1] - 9),
        ("f3", f"M{ram_r[0]},{ram_r[1]} L{ir_s[0]},{ir_s[1]}", 2.15, 3.15,
         "instr", (ram_r[0] + ir_s[0]) / 2, ram_r[1] - 9),
        # decode
        ("d1", f"M{ir_g[0]},{ir_g[1]} L{fsm_a[0]},{fsm_a[1]}", 3.75, 4.75,
         "opcode", ir_g[0] + 34, (ir_g[1] + fsm_a[1]) / 2 + 4),
        # execute: la control unit pilota la ALU, il risultato torna nel register file
        ("e1", f"M{fsm_s[0]},{fsm_s[1]} L{alu_d[0] + 36},{fsm_s[1]} "
               f"L{alu_d[0] + 36},{alu_d[1]} L{alu_d[0]},{alu_d[1]}", 5.35, 6.45,
         "control", fsm_s[0] - 34, fsm_s[1] - 9),
        ("e2", f"M{alu_s[0]},{alu_s[1]} L{reg_d[0]},{reg_d[1]}", 6.45, 7.45,
         "result", (alu_s[0] + reg_d[0]) / 2, alu_s[1] - 9),
        # retroazione: gli operandi risalgono dal register file alla ALU
        ("e3", f"M{reg_g[0]},{reg_g[1]} L{reg_g[0]},{reg_g[1] + giu} "
               f"L{alu_g[0]},{alu_g[1] + giu} L{alu_g[0]},{alu_g[1]}", 7.45, 8.45,
         "operands", (reg_g[0] + alu_g[0]) / 2, reg_g[1] + giu + 15),
    ]


# blocchi accesi: nome -> (inizio, fine)
FASI_BLOCCHI = {
    "PC": (0.05, 1.30), "MAR": (1.05, 2.30), "RAM": (2.05, 3.30),
    "IR": (3.05, 4.90), "FSM": (4.65, 6.60),
    "ALU": (6.35, 7.60), "REG": (7.35, 8.70),
}

FASI = [("FETCH", 0.0, 3.6), ("DECODE", 3.6, 5.2), ("EXECUTE", 5.2, 8.9)]


def finestra_opacita(t0, t1, valore_dentro=1, valore_fuori=0):
    k = f"0;{t0 / TOT:.5f};{t1 / TOT:.5f};1"
    v = f"{valore_fuori};{valore_dentro};{valore_fuori};{valore_fuori}"
    return (f'<animate attributeName="opacity" calcMode="discrete" values="{v}" '
            f'keyTimes="{k}" dur="{TOT}s" repeatCount="indefinite"/>')


def genera(tema):
    p = tema
    acceso = p["peach"]
    o = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {LARGH:.0f} {ALT:.0f}" '
        f'width="{LARGH:.0f}" height="{ALT:.0f}" role="img" '
        f'aria-label="Datapath del processore LC-3: il ciclo fetch, decode ed execute '
        f'attraversa PC, MAR, RAM, IR, control unit, ALU e register file">',
        blocco_font(),
        f'<rect width="{LARGH:.0f}" height="{ALT:.0f}" rx="10" fill="{p["base"]}"/>',
    ]

    # intestazione
    o.append(f'<text x="26" y="38" font-size="15" fill="{p["text"]}">LC-3 processor</text>')
    o.append(f'<text x="26" y="58" font-size="12" fill="{p["overlay0"]}">'
             f'SystemVerilog / datapath e control unit</text>')

    # etichetta di fase, in alto a destra: si accende una alla volta
    for nome, t0, t1 in FASI:
        o.append(f'<g opacity="0">{finestra_opacita(t0, t1)}'
                 f'<rect x="{LARGH - 152:.0f}" y="24" width="126" height="26" rx="4" '
                 f'fill="{p["surface0"]}"/>'
                 f'<text x="{LARGH - 89:.0f}" y="41" text-anchor="middle" font-size="12" '
                 f'letter-spacing="1.5" fill="{acceso}">{nome}</text></g>')

    # collegamenti: prima le linee a riposo con la loro etichetta, poi gli impulsi
    for _, d, t0, t1, testo, lx, ly in percorsi():
        o.append(f'<path d="{d}" fill="none" stroke="{p["surface1"]}" '
                 f'stroke-width="1.6"/>')
        o.append(f'<text x="{lx:.0f}" y="{ly:.0f}" text-anchor="middle" '
                 f'font-size="10" fill="{p["overlay0"]}">{testo}</text>')

    for pid, d, t0, t1, _, _, _ in percorsi():
        o.append(f'<path id="{pid}" d="{d}" fill="none" stroke="{acceso}" '
                 f'stroke-width="2.2" opacity="0">{finestra_opacita(t0, t1)}</path>')
        # l'impulso: fermo a inizio percorso, lo attraversa nella sua finestra
        kp = f"0;0;1;1"
        kt = f"0;{t0 / TOT:.5f};{t1 / TOT:.5f};1"
        o.append(
            f'<circle r="4.5" fill="{acceso}" opacity="0">'
            f'{finestra_opacita(t0, t1)}'
            f'<animateMotion dur="{TOT}s" repeatCount="indefinite" calcMode="linear" '
            f'path="{d}" keyPoints="{kp}" keyTimes="{kt}"/>'
            f'</circle>')

    # blocchi
    for nome, (x, y) in B.items():
        titolo, sotto = ETICHETTE[nome]
        t0, t1 = FASI_BLOCCHI[nome]
        o.append(
            f'<rect x="{x}" y="{y}" width="{BW}" height="{BH}" rx="6" '
            f'fill="{p["surface0"]}" stroke="{p["surface2"]}" stroke-width="1.2"/>')
        o.append(
            f'<rect x="{x}" y="{y}" width="{BW}" height="{BH}" rx="6" fill="none" '
            f'stroke="{acceso}" stroke-width="2.2" opacity="0">'
            f'{finestra_opacita(t0, t1)}</rect>')
        o.append(
            f'<text x="{x + BW / 2:.0f}" y="{y + 21:.0f}" text-anchor="middle" '
            f'font-size="14" fill="{p["text"]}">{titolo}</text>')
        o.append(
            f'<text x="{x + BW / 2:.0f}" y="{y + 37:.0f}" text-anchor="middle" '
            f'font-size="10" fill="{p["overlay0"]}">{sotto}</text>')

    # nota in basso
    o.append(f'<text x="26" y="{ALT - 11:.0f}" font-size="11" fill="{p["overlay0"]}">'
             f'14 dei 16 opcode implementati - RTI e l\'opcode riservato sono stub</text>')

    o.append("</svg>")
    return "".join(o)


if __name__ == "__main__":
    for tema in TEMI:
        svg = genera(tema)
        dest = scrivi("datapath", tema, svg)
        print(f"{dest.name:19} {len(svg) / 1024:5.1f} KB   giro da {TOT}s")
