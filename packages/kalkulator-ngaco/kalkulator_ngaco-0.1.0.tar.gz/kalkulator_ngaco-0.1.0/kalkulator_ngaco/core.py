from kalkulator_ngaco.config import get_mode_serius
import random

MODE_SERIUS = get_mode_serius()

def tambah(a, b):
    if MODE_SERIUS:
        print(f"Jawaban: {a + b}")
        return a + b
    # sisanya seperti versi ngaco
