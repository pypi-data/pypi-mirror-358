# __init__.py
# Bu dosya paketin başlangıç noktası olarak çalışır.
# Alt modülleri yükler, sürüm bilgileri tanımlar ve geriye dönük uyumluluk için uyarılar sağlar.

from __future__ import annotations
import importlib
import warnings
import os
# if os.getenv("DEVELOPMENT") == "true":
    # importlib.reload(kececifractals) # F821 undefined name 'kececifractals'

# Göreli modül içe aktarmaları
# F401 hatasını önlemek için sadece kullanacağınız şeyleri dışa aktarın
# Aksi halde linter'lar "imported but unused" uyarısı verir
try:
    from .kececifractals import *  # gerekirse burada belirli fonksiyonları seçmeli yapmak daha güvenlidir
    from . import kececifractals  # Modülün kendisine doğrudan erişim isteniyorsa
except ImportError as e:
    warnings.warn(f"Gerekli modül yüklenemedi: {e}", ImportWarning)

# Eski bir fonksiyonun yer tutucusu - gelecekte kaldırılacak
def eski_fonksiyon():
    """
    Kaldırılması planlanan eski bir fonksiyondur.
    Lütfen alternatif fonksiyonları kullanın.
    """
    warnings.warn(
        "eski_fonksiyon() artık kullanılmamaktadır ve gelecekte kaldırılacaktır. "
        "Lütfen yeni alternatif fonksiyonları kullanın. "
        "Keçeci Fractals; Python 3.9-3.14 sürümlerinde sorunsuz çalışmalıdır.",
        category=DeprecationWarning,
        stacklevel=2
    )


# Paket sürüm numarası
__version__ = "0.1.1"
