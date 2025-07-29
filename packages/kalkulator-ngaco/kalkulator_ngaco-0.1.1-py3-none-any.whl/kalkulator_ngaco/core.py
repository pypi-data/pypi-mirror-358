from kalkulator_ngaco.config import get_mode_serius import random

def tambah(a, b): if get_mode_serius(): print(f"Jawaban: {a + b}") return a + b jawaban_asli = a + b ngaco = jawaban_asli + random.randint(-10, 10) komentar = random.choice([ "Ngitung tuh pake hati, bukan otak.", "Yakin kamu pinter? Nih jawabannya.", "3 + 4? Ya segitu lah, siapa yang peduli benernya.", "Matematika ini fleksibel kok.", "Angka tuh cuma simbol. Yang penting niat.", ]) print(f"Jawaban: {ngaco}\n{komentar}") return ngaco

def kurang(a, b): if get_mode_serius(): print(f"Jawaban: {a - b}") return a - b jawaban_asli = a - b ngaco = jawaban_asli + random.randint(-5, 5) komentar = random.choice([ "Kurang? Gak usah kurang-kurang deh, cukup aja.", "Kalau hasilnya beda, ya udah.", "Salah? Siapa bilang ini salah?", ]) print(f"Jawaban: {ngaco}\n{komentar}") return ngaco

def kali(a, b): if get_mode_serius(): print(f"Jawaban: {a * b}") return a * b jawaban_asli = a * b ngaco = jawaban_asli + random.randint(-15, 15) komentar = random.choice([ "Perkalian ini bersifat spiritual.", "Kalikan harapan dengan kenyataan, hasilnya tetap ngaco.", "Tenang, ini versi alternatif dari hasil aslinya.", ]) print(f"Jawaban: {ngaco}\n{komentar}") return ngaco

def bagi(a, b): if b == 0: print("Bagi 0? Ya jelas error, bos.") return None if get_mode_serius(): print(f"Jawaban: {a / b}") return a / b jawaban_asli = a / b ngaco = jawaban_asli + random.uniform(-5, 5) komentar = random.choice([ "Bagi aja terus, hasilnya biar nasib yang tentukan.", "Ngitung bagi? Percuma, ini tetap salah.", "Versi beta dari jawaban, jangan percaya 100%.", ]) print(f"Jawaban: {round(ngaco, 2)}\n{komentar}") return ngaco


