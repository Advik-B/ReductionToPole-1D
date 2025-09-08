import numpy as np
import matplotlib.pyplot as plt


def tukey_window(n, alpha=0.1):
    """Return a Tukey window of length n."""
    return np.hanning(int(alpha * (n - 1)))[:int(alpha * (n - 1) // 2)].tolist() + \
        [1.0] * (n - int(alpha * (n - 1))) + \
        np.hanning(int(alpha * (n - 1)))[int(alpha * (n - 1) // 2):].tolist()


def rtp_1d(distance, anomaly, dx, inc, dec, azimuth):
    """
    Apply 1D Reduction to Pole (RTP) filter.

    Parameters
    ----------
    distance : np.ndarray
        Distance along profile (m).
    anomaly : np.ndarray
        Magnetic anomaly (nT).
    dx : float
        Sampling interval (m).
    inc, dec : float
        Earth's field inclination and declination (degrees).
    azimuth : float
        Profile azimuth (deg from North to East).

    Returns
    -------
    rtp_anomaly : array
        RTP-transformed anomaly (nT).
    """
    n = len(anomaly)
    # Detrend
    anomaly = anomaly - np.polyval(np.polyfit(distance, anomaly, 1), distance)
    # Apply taper
    win = np.array(tukey_window(n, alpha=0.1))
    anomaly = anomaly * win

    # FFT
    spec = np.fft.fft(anomaly, n=2 ** int(np.ceil(np.log2(n * 2))))  # pad to 2x power of 2
    k = np.fft.fftfreq(len(spec), d=dx) * 2 * np.pi  # wavenumber (rad/m)

    # Angles to radians
    I0 = np.deg2rad(inc)
    D0 = np.deg2rad(dec)
    theta = np.deg2rad(azimuth)

    # Profile direction vector
    kx = np.cos(theta)
    ky = np.sin(theta)

    # Inducing field vector (unit)
    Fx = np.cos(I0) * np.cos(D0)
    Fy = np.cos(I0) * np.sin(D0)
    Fz = np.sin(I0)

    # RTP operator (1D simplification along profile)
    # Formula: scale factor = (Fz) / (Fx*cosθ + Fy*sinθ + i*Fz*sign(k))
    op = np.zeros_like(spec, dtype=complex)
    for i, ki in enumerate(k):
        if ki == 0:
            op[i] = 1.0
        else:
            sign = np.sign(ki)
            denom = Fx * kx + Fy * ky + 1j * Fz * sign
            op[i] = (Fz) / denom

    spec_rtp = spec * op

    # Inverse FFT
    rtp = np.fft.ifft(spec_rtp).real[:n]
    return rtp

def graph_rtp(anomaly: np.ndarray, rtp_anomaly: np.ndarray, distance: np.ndarray, title: str = "1D Reduction to Pole (RTP)") -> None:
    plt.figure(figsize=(10, 5))
    plt.plot(distance, anomaly, label="Observed")
    plt.plot(distance, rtp_anomaly, label="RTP", linestyle="--")
    plt.xlabel("Distance (m)")
    plt.ylabel("Anomaly (nT)")
    plt.legend()
    plt.title(title)