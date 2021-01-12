import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import uncertainties as unc
from uncertainties import unumpy as unp
from labtables import Table


def get_slope_error(x, y, students_t=2):
    """Return error of the slope of the line given by (x, y)"""
    assert len(x) == len(y), 'Different input lengths'
    slope = stats.linregress(x, y).slope
    D_y = stats.tstd(y) ** 2
    D_x = stats.tstd(x) ** 2
    # Formula from the MIPT lab manual
    return students_t * np.sqrt(1/(len(x) - 2) * (D_y / D_x - slope ** 2))


def get_shear_modulus(tors_coef, diameter, length):
    return 32 * tors_coef * length / (np.pi * diameter ** 4)


def uscatter(x, y, add_line=False):
    """Scatter-plot arrays of uncertainties.ufloats, adding errorbars"""
    x_nom = unp.nominal_values(x)
    y_nom = unp.nominal_values(y)
    x_std = unp.std_devs(x)
    y_std = unp.std_devs(y)

    plt.errorbar(x_nom, y_nom, xerr=x_std, yerr=y_std, fmt='o')
    if add_line:
        slope, intercept = np.polyfit(x_nom, y_nom, 1)
        print(f'Plotting line with slope = {slope}, intercept = {intercept}')
        plt.plot(x_nom, slope * x_nom + intercept)


periods = [1.245, 2.181, 2.013, 1.712, 0.986, 0.563, 1.976, 1.670]
diameters = [2, 2, 2, 2, 3, 4, 2, 2]
# Diameters are in mm, so divide by 1000 to convert to SI
diameters = list(map(lambda diameter: diameter / 1000, diameters))
lengths = [0.5, 0.5, 0.4, 0.3, 0.5, 0.5, 0.5, 0.5]
actual_shmods = [80, 25, 25, 25, 25, 25, 36, 48]  # in GPa

# Add reasonable errors: 0.01 s for perios and 1% for d and l.
periods = list(map(lambda x: unc.ufloat(x, 0.01), periods))
diameters = list(map(lambda x: unc.ufloat(x, x * 0.02), diameters))
lengths = list(map(lambda x: unc.ufloat(x, x * 0.005), lengths))

# Force * arm = tors_coef * angle.
tors_coefs = []
# 15.0 ± 0.3 cm is the distance from the axis.
arm = unc.ufloat(0.15, 0.003)

# Loop through 8 csvs in force-angle-csvs
for i in range(1, 9):
    forces, angles = Table.read_csv(f'force-angle-csvs/{i}.csv')
    # Add some reasonable error, 0.02 N.
    forces = list(map(lambda x: unc.ufloat(x, 0.02), forces))
    # Convert angles to radians
    angles = list(map(lambda angle: angle * np.pi / 180, angles))

    torques = []
    for force in forces:
        torques.append(unc.nominal_value(arm * force))

    tors_coefs.append(unc.ufloat(stats.linregress(angles, torques).slope,
                                 get_slope_error(angles, torques))
    )

# Print tors_coefs along with absolute errors.
print('tors_coefs:', *tors_coefs, sep='\n')

shmods = list(map(lambda args: get_shear_modulus(*args) / 1e9,
                  zip(tors_coefs, diameters, lengths)))  # in GPa
print('shmods:', *shmods, sep='\n')

# Plot to check the relation periods**2 ~ 1/tors_coefs
uscatter(1 / np.array(tors_coefs), np.array(periods) ** 2,
         add_line=True)
plt.xlabel('$1/k$, 1/(Н·м)', fontsize=14)
plt.ylabel('Период в квадрате, $с^2$', fontsize=14)
plt.grid()
plt.xlim(left=0)
plt.ylim(bottom=0)
plt.savefig('figures/periods_vs_tors_coefs_plot.pdf',
            bbox_inches='tight')

# Write the final table
colnames = (
    '$T$, с',  # periods
    '$k$, Н·м',             # tors_coefs
    '$G$, ГПа',             # shmods
    '$G$ спр., ГПа',  # actual_shmods
)
# Convert unc.ufloats to well-formatted strings
table = Table(
    unp.nominal_values(periods),
    list(map(lambda x: f'{x:P}', tors_coefs)),
    list(map(lambda x: f'{x:P}', shmods)),
    actual_shmods,
    colnames=colnames
)
Table.write_latex(table, 'latex-tabulars/main_table.tex',
                  show_row_numbers=True)

# Calculate I0: the moment of inertia of the platform without weights.
slp = unc.ufloat(0.409, 0.409 * 0.01)  # from periods_vs_tors_coefs_plot.pdf
m2 = unc.ufloat(304.7, 0.02) / 1000    # from info.txt
a = unc.ufloat(15, 0.3) / 100
b = unc.ufloat(3, 0.1) / 100
I0 = slp / (4 * np.pi ** 2) - m2 * (a ** 2 + b ** 2 / 12)
print(f'I0 = {I0 * 1000} g * m^2')

# Calculate I0 from the 'period of weightless oscillations', info.txt
T = unc.ufloat(0.385, 0.01) * 2
k = unc.ufloat(0.261, 0.014)
I0_ = (T ** 2 * k) / (4 * np.pi ** 2)
print(f'I0_ = {I0_ * 1000} g * m^2')
print(f'I0 difference: {I0 - I0_}, which is {(I0 - I0_) / I0} of I0')
print(f'I0 relative error: {I0.std_dev / I0.nominal_value} g * m^2')
