from pathlib import Path
from matplotlib import pyplot as plt

header = (
'''---
    format_version: "1.0"
    notes: ["from file {}"]
    filter:
        type: "FIR"
        symmetry: "NONE"
''')

outdir = Path('./temp')
outdir.mkdir(exist_ok=True)
for f in Path('.').glob('*.txt'):
    with open(f, 'r') as fid:
        coeffs = fid.readlines()
    f_coeffs = [float(x) for x in coeffs]
    # fig, ax = plt.subplots()
    # ax.plot(f_coeffs)
    # ax.set_title(f.name)
    # plt.show()
        
    f_out = outdir / (f.stem + '.yaml')
    with open(f_out, 'w') as fid:
        fid.write(header.format(f.name))
        if 'LIN' in f.stem:
            delay = f_coeffs.index(max(f_coeffs))
        elif "MIN" in f.stem:
            delay = 0
        else:
            raise ValueError(f'Neither "LIN" nor "MIN" in ELOPS FIR file "{f.name}"')
        sum_coeffs = sum(f_coeffs)  # NOT the coefficient divisor???
        fid.write(f'        delay.samples: {delay:.0f}\n')
        # fid.write(f'        coefficient_divisor: {sum(f_coeffs)}\n')
        fid.write('        coefficients:\n')
        for c in coeffs:
            if c[0] == '-':
                fid.write(f'          - {c}')
            else:
                fid.write(f'          -  {c}')
