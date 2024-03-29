"""CONDUCTIVITY ESTIMATOR."""
from scipy.interpolate import interp1d


def estimate_conductivity(value_lpf, value_ecs, value_pcs, temp):
    """Calculate the conductivity of LiPF6 in EC+PC mixtures."""
    if value_lpf <= 0.0 or value_pcs <= 0.0:
        raise ValueError(
            f'Cannot operate with concentrations of LPF={value_lpf} and PC={value_pcs}'
        )

    rpc1 = value_lpf / (value_ecs + value_pcs)
    lpf1 = value_pcs / (value_ecs + value_pcs)

    coefs = calculate_coefs(temp)

    sigma = (coefs[0] + coefs[1] * rpc1 + coefs[2] * lpf1 +
             coefs[3] * rpc1 * rpc1 + coefs[4] * rpc1 * lpf1 +
             coefs[5] * lpf1 * lpf1 + coefs[6] * rpc1 * rpc1 * rpc1 +
             coefs[7] * rpc1 * rpc1 * lpf1 + coefs[8] * rpc1 * lpf1 * lpf1 +
             coefs[9] * lpf1 * lpf1 * lpf1)

    result = sigma * 1e-3
    return result


def calculate_coefs(temperature):
    """Calculate the coeficients."""
    templist = [243, 253, 263, 273, 283, 293, 303, 313, 323, 333]
    coef_lists = [
        [1.0, 1.2, 1.4, 1.5, 1.5, 1.6, 1.6, 1.6, 1.6, 1.6],
        [-0.3, -0.3, 1.0, 0.4, 1.2, 1.7, 2.7, 3.0, 3.2, 3.0],
        [5.6, 8.9, 12.1, 15.9, 20.4, 25.0, 29.7, 35.1, 41.3, 47.4],
        [0.9, 0.9, 0.1, -0.1, -0.9, -1.4, -3.2, -3.2, -3.2, -2.5],
        [-2.3, -3.2, -3.9, -4.9, -5.9, -6.8, -6.9, -7.3, -7.6, -6.9],
        [-9.7, -13.6, -17.1, -21.2, -26.1, -31.0, -35.8, -41.9, -49.5, -57.2],
        [
            -0.6,
            -0.7,
            -0.3,
            -0.4,
            -0.4,
            -0.3,
            0.4,
            1.0,
            0.0,
            -0.7,
        ],
        [1.4, 1.9, 2.4, 3.3, 4.2, 5.1, 5.6, 6.2, 6.4, 6.6],
        [0.6, 0.8, 0.9, 0.9, 0.7, 0.5, 0.0, -0.6, -0.7, -1.8],
        [4.0, 5.1, 6.1, 7.3, 8.8, 10.5, 12.2, 14.6, 17.6, 21.1],
    ]

    interpolators = [interp1d(templist, coef_list) for coef_list in coef_lists]
    coefs = [
        float(interpolator(temperature)) for interpolator in interpolators
    ]
    # coefs = [1.5, 0.4, 15.9, -0.1, -4.9, -21.2, -0.4, 3.3, 0.9, 7.3]
    return coefs
