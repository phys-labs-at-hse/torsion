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


periods = [1.245, 2.181, 2.013, 1.712, 0.986, 0.563, 1.976, 1.670]
diameters = [2, 2, 2, 2, 3, 4, 2, 2]
# Diameters are in mm, so divide by 1000 to convert to SI
diameters = list(map(lambda diameter: diameter / 1000, diameters))
lengths = [0.5, 0.5, 0.4, 0.3, 0.5, 0.5, 0.5, 0.5]
actual_shmods = [83, 25, 25, 25, 25, 25, 37, 46]  # in GPa


# Add reasonable errors: 0.01 s for perios and 1% for d and l.
periods = list(map(lambda x: unc.ufloat(x, 0.01), periods))
diameters = list(map(lambda x: unc.ufloat(x, x * 0.01), diameters))
lengths = list(map(lambda x: unc.ufloat(x, x * 0.01), lengths))


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

    tors_coefs.append(
        unc.ufloat(
            stats.linregress(angles, torques).slope,
            get_slope_error(angles, torques)
        )
    )

# Print tors_coefs along with absolute errors.
print('tors_coefs:', *tors_coefs, sep='\n')

shmods = list(map(lambda args: get_shear_modulus(*args),
                  zip(tors_coefs, diameters, lengths)))
print('shmods:', *(np.array(shmods) / 1e9), sep='\n')


colnames = (
    '$k$, Н·м',  # tors_coefs
    '$G$, ГПа',  # shmods
    '$G$ из таблицы, ГПа',  # actual_shmods
    'Период колебаний, с',  # periods
    '$k$ по периодам, с',  # tors_coef_alt
)
