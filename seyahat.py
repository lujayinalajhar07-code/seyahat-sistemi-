"""
╔══════════════════════════════════════════════════════════════╗
║       ✈️  Seyahat Planlama Uygulaması                        ║
║       OOP prensipleri ile geliştirilmiş, modüler yapı        ║
║       Sınıflar: Seyahat | Konaklama | Plan                   ║
╚══════════════════════════════════════════════════════════════╝

Proje 9 — Seyahat Planlama Uygulaması
Etkinlik Kayıt Sistemi mimarisi baz alınarak dönüştürülmüştür.

Etkinlik      → Seyahat      (seyahat bilgisi ve bütçesi)
Katilimci     → Konaklama    (otel/konaklama bilgisi ve fiyatı)
Bilet         → Plan         (rota ve aktiviteler)
EtkinlikSistemi → SeyahatSistemi (merkezi yönetici)
"""

from enum import Enum
from datetime import datetime, date
from typing import Optional, List
import json
import os


# ==================== ENUMS ====================

class UlasimTuru(Enum):
    """Ulaşım türlerini standart ve kontrollü şekilde tutar"""
    UCAK    = "Uçak"
    TREN    = "Tren"
    OTOBUS  = "Otobüs"
    ARAC    = "Özel Araç"
    GEMI    = "Gemi/Feribot"


class KonaklamaTuru(Enum):
    """Konaklama türleri"""
    OTEL      = "Otel"
    HOSTEL    = "Hostel"
    AIRBNB    = "Airbnb"
    KAMP      = "Kamp"
    AKRABA    = "Akraba/Tanıdık"


class PlanDurumu(Enum):
    """Plan durumları"""
    TASLAK    = "Taslak"
    ONAYLANDI = "Onaylandı"
    TAMAMLANDI = "Tamamlandı"
    IPTAL     = "İptal"


# ==================== MODEL SINIFLAR ====================

class Seyahat:
    """
    Seyahat bilgilerini ve bütçesini yöneten sınıf.

    Özellikler:
        seyahat_id    : Benzersiz seyahat kimliği
        gidis_yeri    : Hedef şehir/ülke
        baslangic_tar : Gidiş tarihi
        bitis_tar     : Dönüş tarihi
        ulasim_turu   : Ulaşım şekli (UlasimTuru enum)
        butce          : Toplam bütçe (TL)
        notlar         : Ek notlar
    """

    def __init__(self, seyahat_id: str, gidis_yeri: str,
                 baslangic_tar: datetime, bitis_tar: datetime,
                 ulasim_turu: UlasimTuru, butce: float, notlar: str = ""):
        self._seyahat_id    = seyahat_id
        self._gidis_yeri    = gidis_yeri
        self._baslangic_tar = baslangic_tar
        self._bitis_tar     = bitis_tar
        self._ulasim_turu   = ulasim_turu
        self._butce         = butce
        self._notlar        = notlar
        self._aktif_mi      = True
        self._harcanan      = 0.0   # Konaklama + plan harcamaları

    # === Getter Metotları ===
    def get_seyahat_id(self) -> str:        return self._seyahat_id
    def get_gidis_yeri(self) -> str:        return self._gidis_yeri
    def get_baslangic_tar(self) -> datetime: return self._baslangic_tar
    def get_bitis_tar(self) -> datetime:    return self._bitis_tar
    def get_ulasim_turu(self) -> UlasimTuru: return self._ulasim_turu
    def get_butce(self) -> float:           return self._butce
    def get_notlar(self) -> str:            return self._notlar
    def get_aktif_mi(self) -> bool:         return self._aktif_mi
    def get_harcanan(self) -> float:        return self._harcanan
    def get_kalan_butce(self) -> float:     return self._butce - self._harcanan

    def get_sure_gun(self) -> int:
        """Seyahat süresini gün olarak döndürür"""
        delta = self._bitis_tar - self._baslangic_tar
        return max(1, delta.days)

    # === İş Mantığı Metotları ===
    def harcama_ekle(self, tutar: float) -> tuple:
        """Bütçeden harcama düşer, kontrol yapar"""
        if tutar < 0:
            return False, "Tutar negatif olamaz."
        if self._harcanan + tutar > self._butce:
            return False, f"Bütçe aşılıyor! Kalan: ₺{self.get_kalan_butce():.2f}"
        self._harcanan += tutar
        return True, f"₺{tutar:.2f} harcama eklendi."

    def harcama_cikar(self, tutar: float) -> None:
        """Plan/konaklama iptali durumunda harcamayı geri alır"""
        self._harcanan = max(0.0, self._harcanan - tutar)

    def durum_guncelle(self, aktif: bool) -> None:
        self._aktif_mi = aktif

    def butce_kullanim_orani(self) -> float:
        if self._butce == 0:
            return 0.0
        return (self._harcanan / self._butce) * 100

    def to_dict(self) -> dict:
        return {
            "seyahat_id":    self._seyahat_id,
            "gidis_yeri":    self._gidis_yeri,
            "baslangic_tar": self._baslangic_tar.isoformat(),
            "bitis_tar":     self._bitis_tar.isoformat(),
            "ulasim_turu":   self._ulasim_turu.value,
            "butce":         self._butce,
            "notlar":        self._notlar,
            "aktif_mi":      self._aktif_mi,
            "harcanan":      self._harcanan
        }

    @classmethod
    def from_dict(cls, data: dict):
        s = cls(
            data["seyahat_id"],
            data["gidis_yeri"],
            datetime.fromisoformat(data["baslangic_tar"]),
            datetime.fromisoformat(data["bitis_tar"]),
            UlasimTuru(data["ulasim_turu"]),
            data["butce"],
            data.get("notlar", "")
        )
        s._aktif_mi = data.get("aktif_mi", True)
        s._harcanan = data.get("harcanan", 0.0)
        return s

    def __repr__(self) -> str:
        return f"Seyahat({self._seyahat_id}, {self._gidis_yeri}, ₺{self._butce})"


# ─────────────────────────────────────────────────────────────

class Konaklama:
    """
    Konaklama bilgilerini ve fiyatını yöneten sınıf.

    Özellikler:
        konaklama_id   : Benzersiz konaklama kimliği
        seyahat        : Bağlı olduğu Seyahat nesnesi
        otel_adi       : Konaklama yeri adı
        tur            : Konaklama türü (KonaklamaTuru enum)
        fiyat_gece     : Gecelik fiyat (TL)
        checkin        : Giriş tarihi
        checkout       : Çıkış tarihi
        adres          : Konaklama adresi
    """

    def __init__(self, konaklama_id: str, seyahat: 'Seyahat',
                 otel_adi: str, tur: KonaklamaTuru,
                 fiyat_gece: float, checkin: datetime, checkout: datetime,
                 adres: str = ""):
        self._konaklama_id = konaklama_id
        self._seyahat      = seyahat
        self._otel_adi     = otel_adi
        self._tur          = tur
        self._fiyat_gece   = fiyat_gece
        self._checkin      = checkin
        self._checkout     = checkout
        self._adres        = adres
        self._iptal_mi     = False
        self._toplam_ucret = 0.0

    # === Getter Metotları ===
    def get_konaklama_id(self) -> str:    return self._konaklama_id
    def get_seyahat(self):                return self._seyahat
    def get_otel_adi(self) -> str:        return self._otel_adi
    def get_tur(self) -> KonaklamaTuru:   return self._tur
    def get_fiyat_gece(self) -> float:    return self._fiyat_gece
    def get_checkin(self) -> datetime:    return self._checkin
    def get_checkout(self) -> datetime:   return self._checkout
    def get_adres(self) -> str:           return self._adres
    def get_iptal_mi(self) -> bool:       return self._iptal_mi
    def get_toplam_ucret(self) -> float:  return self._toplam_ucret

    def get_gece_sayisi(self) -> int:
        delta = self._checkout - self._checkin
        return max(1, delta.days)

    # === İş Mantığı Metotları ===
    def rezervasyon_olustur(self) -> tuple:
        """Konaklama rezervasyonu oluşturur ve seyahat bütçesinden düşer"""
        gece = self.get_gece_sayisi()
        self._toplam_ucret = round(self._fiyat_gece * gece, 2)
        ok, msg = self._seyahat.harcama_ekle(self._toplam_ucret)
        if not ok:
            self._toplam_ucret = 0.0
            return False, msg
        return True, (f"Rezervasyon oluşturuldu: {self._otel_adi}, "
                      f"{gece} gece, ₺{self._toplam_ucret:.2f}")

    def rezervasyon_iptal_et(self) -> tuple:
        """Rezervasyonu iptal eder, bütçeyi geri verir"""
        if self._iptal_mi:
            return False, "Rezervasyon zaten iptal edilmiş."
        self._iptal_mi = True
        self._seyahat.harcama_cikar(self._toplam_ucret)
        return True, f"{self._otel_adi} rezervasyonu iptal edildi."

    def to_dict(self) -> dict:
        return {
            "konaklama_id": self._konaklama_id,
            "seyahat_id":   self._seyahat.get_seyahat_id(),
            "otel_adi":     self._otel_adi,
            "tur":          self._tur.value,
            "fiyat_gece":   self._fiyat_gece,
            "checkin":      self._checkin.isoformat(),
            "checkout":     self._checkout.isoformat(),
            "adres":        self._adres,
            "iptal_mi":     self._iptal_mi,
            "toplam_ucret": self._toplam_ucret
        }

    def __repr__(self) -> str:
        return f"Konaklama({self._konaklama_id}, {self._otel_adi})"


# ─────────────────────────────────────────────────────────────

class Plan:
    """
    Seyahat rotasını ve aktivitelerini yöneten sınıf.

    Özellikler:
        plan_id      : Benzersiz plan kimliği
        seyahat      : Bağlı olduğu Seyahat nesnesi
        rota         : Ziyaret edilecek yerler listesi
        aktiviteler  : Yapılacaklar listesi (dict: isim → maliyet)
        durum        : Plan durumu (PlanDurumu enum)
        notlar       : Ek notlar
    """

    def __init__(self, plan_id: str, seyahat: 'Seyahat',
                 rota: List[str] = None, notlar: str = ""):
        self._plan_id     = plan_id
        self._seyahat     = seyahat
        self._rota        = rota if rota else []
        self._aktiviteler = {}   # {aktivite_adi: maliyet}
        self._durum       = PlanDurumu.TASLAK
        self._notlar      = notlar
        self._olusturma   = datetime.now()
        self._toplam_aktivite_maliyeti = 0.0

    # === Getter Metotları ===
    def get_plan_id(self) -> str:          return self._plan_id
    def get_seyahat(self):                 return self._seyahat
    def get_rota(self) -> List[str]:       return list(self._rota)
    def get_aktiviteler(self) -> dict:     return dict(self._aktiviteler)
    def get_durum(self) -> PlanDurumu:     return self._durum
    def get_notlar(self) -> str:           return self._notlar
    def get_olusturma(self) -> datetime:   return self._olusturma
    def get_toplam_maliyet(self) -> float: return self._toplam_aktivite_maliyeti

    # === İş Mantığı Metotları ===
    def rota_ekle(self, yer: str) -> tuple:
        """Rotaya yeni bir yer ekler"""
        if yer in self._rota:
            return False, f"'{yer}' zaten rotada mevcut."
        self._rota.append(yer)
        return True, f"'{yer}' rotaya eklendi."

    def rota_cikar(self, yer: str) -> tuple:
        """Rotadan bir yeri çıkarır"""
        if yer not in self._rota:
            return False, f"'{yer}' rotada bulunamadı."
        self._rota.remove(yer)
        return True, f"'{yer}' rotadan çıkarıldı."

    def aktivite_ekle(self, aktivite: str, maliyet: float = 0.0) -> tuple:
        """Plana yeni aktivite ekler ve maliyeti bütçeden düşer"""
        if aktivite in self._aktiviteler:
            return False, f"'{aktivite}' zaten planda mevcut."
        if maliyet > 0:
            ok, msg = self._seyahat.harcama_ekle(maliyet)
            if not ok:
                return False, msg
        self._aktiviteler[aktivite] = maliyet
        self._toplam_aktivite_maliyeti += maliyet
        return True, f"'{aktivite}' (₺{maliyet:.2f}) eklendi."

    def aktivite_sil(self, aktivite: str) -> tuple:
        """Aktiviteyi siler ve maliyeti bütçeye geri verir"""
        if aktivite not in self._aktiviteler:
            return False, f"'{aktivite}' bulunamadı."
        maliyet = self._aktiviteler.pop(aktivite)
        self._toplam_aktivite_maliyeti -= maliyet
        if maliyet > 0:
            self._seyahat.harcama_cikar(maliyet)
        return True, f"'{aktivite}' silindi."

    def durum_guncelle(self, durum: PlanDurumu) -> None:
        self._durum = durum

    def to_dict(self) -> dict:
        return {
            "plan_id":     self._plan_id,
            "seyahat_id":  self._seyahat.get_seyahat_id(),
            "rota":        self._rota,
            "aktiviteler": self._aktiviteler,
            "durum":       self._durum.value,
            "notlar":      self._notlar,
            "olusturma":   self._olusturma.isoformat(),
            "toplam_aktivite_maliyeti": self._toplam_aktivite_maliyeti
        }

    def __repr__(self) -> str:
        return f"Plan({self._plan_id}, {self._seyahat.get_gidis_yeri()}, {self._durum.value})"
