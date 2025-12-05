import sys
import cv2
import numpy as np
import matplotlib.pyplot as plt


def hackathon_ready():
    print("--- DIAGNOSTIKA TÍMU ---")
    print(f"Python verzia: {sys.version.split()[0]}")
    print(f"OpenCV verzia: {cv2.__version__} (Pripravené na detekciu budov)")
    print(f"Numpy verzia: {np.__version__} (Pripravené na výpočet NDVI)")

    # Test grafiky
    try:
        plt.figure(figsize=(5, 3))
        plt.plot([0, 10], [0, 10], label='Rast kvality života v Trnave')
        plt.title("Matplotlib funguje!")
        plt.legend()
        print("Grafické okno: OK (Malo by vyskočiť okno)")
        plt.show()
    except Exception as e:
        print(f"Chyba grafiky: {e}")


if __name__ == "__main__":
    hackathon_ready()