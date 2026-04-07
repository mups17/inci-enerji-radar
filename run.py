"""
GitHub Actions entry point.
energy_monitor_v6.py'yi çalıştırır, üretilen HTML'i docs/index.html'e taşır.
"""
import subprocess, sys, os, glob, shutil, datetime

print(f"\n🚀 Günlük Enerji Raporu — {datetime.datetime.utcnow().strftime('%d %B %Y, %H:%M UTC')}")
print("="*60)

# Ana scripti çalıştır
result = subprocess.run([sys.executable, "energy_monitor_v6.py"], check=False)

if result.returncode != 0:
    print("❌ Script hata ile tamamlandı")
    sys.exit(1)

# Üretilen HTML'i bul ve docs/ klasörüne taşı
files = sorted(glob.glob("energy_rapor_*.html"), reverse=True)
if not files:
    print("❌ HTML dosyası bulunamadı")
    sys.exit(1)

os.makedirs("docs", exist_ok=True)
shutil.copy(files[0], "docs/index.html")

size_kb = os.path.getsize("docs/index.html") // 1024
print(f"\n✅ docs/index.html güncellendi ({size_kb} KB)")
print(f"   Kaynak: {files[0]}")
