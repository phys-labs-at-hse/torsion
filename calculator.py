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

with open('info.txt') as file:
    csv_started = False
    arm = 0.15  # 15 cm is the distance from the axis
    forces = []
    angles = []

    for line in file:
        line = line.strip()

        if line.startswith('Force (N), Angle (degrees)'):
            csv_started = True
            continue

        if not line and csv_started:
            csv_started = False  # csv ended

            torques = list(map(lambda force: force * arm, forces))

            tors_coefs.append(stats.linregress(angles, torques).slope)
            tors_coefs_err.append(get_slope_error(angles, torques))

            # Verify linearity visually. Errorsbars are my rough estimate.
            yerr = list(map(lambda torque: torque * 0.05, torques))
            plt.errorbar(angles, torques, xerr = 1, yerr = yerr, fmt = 'o')

            forces = []
            angles = []
            continue

        if csv_started:
            force, angle = map(float, line.strip().split(', '))
            forces.append(force)
            angles.append(angle)

# Print tors_coefs along with absolute errors
print(tors_coefs)
for coef, err in zip(tors_coefs, tors_coefs_err):
    print(f'{err / coef:.1e}', end=' ')

# All plots are indeed linear, and the slope errors are acceptable.
