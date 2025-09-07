import numpy as np
import pandas as pd
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
    distance : array
        Distance along profile (m).
    anomaly : array
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


if __name__ == "__main__":
    # Example usage
    # CSV with columns: distance, anomaly
    df = pd.read_csv("profile.csv")
    distance = df["distance"].values
    anomaly = df["anomaly"].values

    dx = 10.0  # spacing (m)
    inc = 42.3  # Earth field inclination (deg)
    dec = 0.9719  # Earth field declination (deg)
    azimuth = 90.0  # Profile azimuth (deg from N over E)

    rtp_anomaly = rtp_1d(distance, anomaly, dx, inc, dec, azimuth)
    # Mirror with respect to vertical axis (amplitude flip)
    reverse_anomaly = -rtp_anomaly

    # Save and plot
    df["rtp"] = rtp_anomaly
    df.to_csv("profile_rtp.csv", index=False)

    plt.figure(figsize=(10, 5))
    plt.plot(distance, anomaly, label="Observed")
    # plt.plot(distance, rtp_anomaly, label="RTP", linestyle="--")
    plt.plot(distance, reverse_anomaly, label="RTP Reverse", linestyle="--")
    plt.xlabel("Distance (m)")
    plt.ylabel("Anomaly (nT)")
    plt.legend()
    plt.title("1D Reduction to Pole (RTP)")
    plt.show()
