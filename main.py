import matplotlib.pyplot as plt
import pandas as pd

from common import rtp_1d, graph_rtp

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

    graph_rtp(
        anomaly=anomaly,
        distance=distance,
        rtp_anomaly=reverse_anomaly
    )

    plt.show()
