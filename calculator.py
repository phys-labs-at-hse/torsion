import math
from scipy import stats
import matplotlib.pyplot as plt
import tabulate


def get_slope_error(x, y, students_t=2):
    """Return error of the slope of the line given by (x, y)"""
    assert len(x) == len(y), 'Different input lengths'
    slope = stats.linregress(x, y).slope
    D_y = stats.tstd(y) ** 2
    D_x = stats.tstd(x) ** 2
    # Formula from the MIPT lab manual
    return students_t * math.sqrt(1/(len(x) - 2) * (D_y / D_x - slope ** 2))


periods = [1.245, 2.181, 2.013, 1.712, 0.986, 0.563, 1.976, 1.670]

# Force * arm = tors_coef * angle
tors_coefs = []
tors_coefs_err = []  # list of uncertainties
arm = 0.15  # 15 cm is the distance from the axis

# Loop through 8 csvs in force-angle-csvs
for i in range(1, 9):
    file = open(f'force-angle-csvs/{i}.csv')
    next(file)  # skip the column names

    forces = []
    angles = []
    for line in file:
        force, angle = map(float, line.strip().split(', '))
        forces.append(force)
        angles.append(angle)

    torques = []
    torques_err = []
    # Arm error is around 3 mm, and force error is 0.02 N
    for force in forces:
        torques.append(arm * force)
        if force == 0:
            torques_err.append(0)
        else:
            torques_err.append(force * 3e-3 + 0.02 * arm)

    tors_coefs.append(stats.linregress(angles, torques).slope)
    tors_coefs_err.append(get_slope_error(angles, torques))

    # Verify linearity visually on a plot.
    plt.errorbar(angles, torques, xerr=1, yerr=torques_err, fmt='o')

    # Write LaTeX tabulars from the current force-angle-csv
    with open(f'latex-tabulars/{i}.tex', 'w') as tex_file:
        tex_file.write('\\begin{tabular}{|c|c|}\n')
        tex_file.write('\\hline\n')
        tex_file.write('Сила, Н & Угол, $^\circ$ \\\\ \\hline\n')
        for force, angle in zip(forces, angles):
            tex_file.write(f'{force:.2f} & {angle:.0f} \\\\ \\hline\n')
        tex_file.write('\\end{tabular}\n')

plt.grid()
plt.xlabel('Угол, °', fontsize = 18)
plt.ylabel('Момент силы, Н·м', fontsize = 18)
# plt.savefig('figures/torque-angle-plot.pdf')

# Print tors_coefs along with absolute errors
for coef, err in zip(tors_coefs, tors_coefs_err):
    print(f'{coef:.3e}, {round(err / coef * 100)}%')
print()
# All plots are indeed linear, and the slope errors are acceptable.
