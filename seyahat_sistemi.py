"""
╔══════════════════════════════════════════════════════════════╗
║       ✈️  Seyahat Planlama — Sistem & Rapor Katmanı          ║
╚══════════════════════════════════════════════════════════════╝
"""

from seyahat import (Seyahat, Konaklama, Plan,
                     UlasimTuru, KonaklamaTuru, PlanDurumu)
from datetime import datetime
from typing import Optional
import json
import os


# ==================== RAPOR SINIFI ====================

class SeyahatRaporu:
    """
    Sistem genelinde seyahat, konaklama ve bütçe raporları üretir.
    """

    def __init__(self, sistem: 'SeyahatSistemi'):
        self._sistem = sistem

    def seyahat_ozet_raporu(self) -> list:
        """Her seyahat için özet bilgi satırı döndürür"""
        satirlar = []
        for s in self._sistem.get_seyahatler().values():
            konaklamalar = [k for k in self._sistem.get_tum_konaklamalar()
                            if k.get_seyahat().get_seyahat_id() == s.get_seyahat_id()
                            and not k.get_iptal_mi()]
            planlar = [p for p in self._sistem.get_tum_planlar()
                       if p.get_seyahat().get_seyahat_id() == s.get_seyahat_id()]
            satirlar.append({
                "seyahat_id":    s.get_seyahat_id(),
                "gidis_yeri":    s.get_gidis_yeri(),
                "tarihler":      (f"{s.get_baslangic_tar().strftime('%d.%m.%Y')} – "
                                  f"{s.get_bitis_tar().strftime('%d.%m.%Y')}"),
                "sure":          f"{s.get_sure_gun()} gün",
                "ulasim":        s.get_ulasim_turu().value,
                "butce":         f"₺{s.get_butce():,.0f}",
                "harcanan":      f"₺{s.get_harcanan():,.0f}",
                "kalan":         f"₺{s.get_kalan_butce():,.0f}",
                "kullanim":      f"%{s.get_butce_kullanim_orani():.1f}",
                "konaklama_say": len(konaklamalar),
                "plan_say":      len(planlar),
                "aktif":         "✅ Aktif" if s.get_aktif_mi() else "🔒 Pasif"
            })
        return satirlar

    def butce_raporu(self) -> dict:
        """Tüm seyahatlerin bütçe özetini döndürür"""
        seyahatler = self._sistem.get_seyahatler().values()
        toplam_butce   = sum(s.get_butce()   for s in seyahatler)
        toplam_harcama = sum(s.get_harcanan() for s in self._sistem.get_seyahatler().values())
        return {
            "Toplam Seyahat":    len(self._sistem.get_seyahatler()),
            "Toplam Bütçe":      f"₺{toplam_butce:,.2f}",
            "Toplam Harcama":    f"₺{toplam_harcama:,.2f}",
            "Kalan Bütçe":       f"₺{toplam_butce - toplam_harcama:,.2f}",
            "Ort. Bütçe/Seyahat": (f"₺{toplam_butce / len(self._sistem.get_seyahatler()):,.2f}"
                                    if self._sistem.get_seyahatler() else "₺0"),
        }

    def aktivite_raporu(self) -> dict:
        """En çok aktivite içeren planları ve maliyetleri döndürür"""
        planlar = self._sistem.get_tum_planlar()
        if not planlar:
            return {}
        toplam_aktivite = sum(len(p.get_aktiviteler()) for p in planlar)
        toplam_maliyet  = sum(p.get_toplam_maliyet()  for p in planlar)
        return {
            "Toplam Plan":         len(planlar),
            "Toplam Aktivite":     toplam_aktivite,
            "Aktivite Maliyeti":   f"₺{toplam_maliyet:,.2f}",
            "Ort. Aktivite/Plan":  f"{toplam_aktivite / len(planlar):.1f}" if planlar else "0",
        }


# ==================== ANA SİSTEM SINIFI ====================

class SeyahatSistemi:
    """
    Tüm seyahat, konaklama ve plan işlemlerini merkezi olarak yöneten sınıf.
    (EtkinlikSistemi'nin karşılığı)
    """

    VERI_DOSYASI = "seyahat_verileri.json"

    def __init__(self):
        self._seyahatler   = {}   # {seyahat_id: Seyahat}
        self._konaklamalar = []   # List[Konaklama]
        self._planlar      = []   # List[Plan]
        self._sonraki_kid  = 1    # Konaklama ID sayacı
        self._sonraki_pid  = 1    # Plan ID sayacı

    # ─── SEYAHAT CRUD ───

    def seyahat_ekle(self, seyahat: Seyahat) -> tuple:
        if seyahat.get_seyahat_id() in self._seyahatler:
            return False, "Bu ID zaten mevcut."
        if seyahat.get_bitis_tar() <= seyahat.get_baslangic_tar():
            return False, "Dönüş tarihi, gidiş tarihinden sonra olmalı."
        self._seyahatler[seyahat.get_seyahat_id()] = seyahat
        return True, f"'{seyahat.get_gidis_yeri()}' seyahati eklendi."

    def seyahat_sil(self, seyahat_id: str) -> tuple:
        if seyahat_id not in self._seyahatler:
            return False, "Seyahat bulunamadı."
        aktif_kon = [k for k in self._konaklamalar
                     if k.get_seyahat().get_seyahat_id() == seyahat_id and not k.get_iptal_mi()]
        if aktif_kon:
            return False, f"{len(aktif_kon)} aktif rezervasyon var. Önce iptal edin."
        ad = self._seyahatler[seyahat_id].get_gidis_yeri()
        # İlgili plan ve konaklamaları temizle
        self._konaklamalar = [k for k in self._konaklamalar
                              if k.get_seyahat().get_seyahat_id() != seyahat_id]
        self._planlar = [p for p in self._planlar
                         if p.get_seyahat().get_seyahat_id() != seyahat_id]
        del self._seyahatler[seyahat_id]
        return True, f"'{ad}' seyahati silindi."

    def get_seyahatler(self) -> dict:
        return self._seyahatler.copy()

    def get_aktif_seyahatler(self) -> dict:
        return {k: v for k, v in self._seyahatler.items() if v.get_aktif_mi()}

    def get_seyahat(self, seyahat_id: str) -> Optional[Seyahat]:
        return self._seyahatler.get(seyahat_id)

    # ─── KONAKLAMA CRUD ───

    def konaklama_ekle(self, seyahat_id: str, otel_adi: str,
                       tur: KonaklamaTuru, fiyat_gece: float,
                       checkin: datetime, checkout: datetime,
                       adres: str = "") -> tuple:
        if seyahat_id not in self._seyahatler:
            return False, "Seyahat bulunamadı."
        seyahat = self._seyahatler[seyahat_id]
        if not seyahat.get_aktif_mi():
            return False, "Pasif seyahate konaklama eklenemez."
        if checkout <= checkin:
            return False, "Çıkış tarihi girişten sonra olmalı."

        kid = f"K{self._sonraki_kid:04d}"
        self._sonraki_kid += 1
        k = Konaklama(kid, seyahat, otel_adi, tur, fiyat_gece, checkin, checkout, adres)
        ok, msg = k.rezervasyon_olustur()
        if ok:
            self._konaklamalar.append(k)
        return ok, msg

    def konaklama_iptal_et(self, konaklama_id: str) -> tuple:
        k = next((x for x in self._konaklamalar
                  if x.get_konaklama_id() == konaklama_id and not x.get_iptal_mi()), None)
        if not k:
            return False, "Geçerli rezervasyon bulunamadı."
        return k.rezervasyon_iptal_et()

    def get_tum_konaklamalar(self) -> list:
        return list(self._konaklamalar)

    def get_gecerli_konaklamalar(self) -> list:
        return [k for k in self._konaklamalar if not k.get_iptal_mi()]

    def get_seyahat_konaklamalari(self, seyahat_id: str) -> list:
        return [k for k in self._konaklamalar
                if k.get_seyahat().get_seyahat_id() == seyahat_id]

    # ─── PLAN CRUD ───

    def plan_olustur(self, seyahat_id: str, rota: list = None,
                     notlar: str = "") -> tuple:
        if seyahat_id not in self._seyahatler:
            return False, "Seyahat bulunamadı.", None
        seyahat = self._seyahatler[seyahat_id]

        pid = f"P{self._sonraki_pid:04d}"
        self._sonraki_pid += 1
        p = Plan(pid, seyahat, rota or [], notlar)
        self._planlar.append(p)
        return True, f"Plan {pid} oluşturuldu.", p

    def plan_sil(self, plan_id: str) -> tuple:
        p = next((x for x in self._planlar if x.get_plan_id() == plan_id), None)
        if not p:
            return False, "Plan bulunamadı."
        # Aktivite maliyetlerini bütçeye geri ver
        for aktivite, maliyet in p.get_aktiviteler().items():
            if maliyet > 0:
                p.get_seyahat().harcama_cikar(maliyet)
        self._planlar.remove(p)
        return True, f"Plan {plan_id} silindi."

    def get_tum_planlar(self) -> list:
        return list(self._planlar)

    def get_seyahat_planlari(self, seyahat_id: str) -> list:
        return [p for p in self._planlar
                if p.get_seyahat().get_seyahat_id() == seyahat_id]

    def get_plan(self, plan_id: str) -> Optional[Plan]:
        return next((p for p in self._planlar if p.get_plan_id() == plan_id), None)

    # ─── RAPOR ───

    def rapor_olustur(self) -> SeyahatRaporu:
        return SeyahatRaporu(self)

    def detayli_ozet(self) -> dict:
        konaklamalar = self.get_gecerli_konaklamalar()
        planlar      = self.get_tum_planlar()
        seyahatler   = self.get_seyahatler()
        toplam_butce = sum(s.get_butce()    for s in seyahatler.values())
        toplam_har   = sum(s.get_harcanan() for s in seyahatler.values())
        return {
            "Toplam Seyahat":        len(seyahatler),
            "Aktif Seyahat":         len(self.get_aktif_seyahatler()),
            "Toplam Konaklama":      len(konaklamalar),
            "Toplam Plan":           len(planlar),
            "Toplam Bütçe":          f"₺{toplam_butce:,.2f}",
            "Toplam Harcama":        f"₺{toplam_har:,.2f}",
            "Kalan Bütçe":           f"₺{toplam_butce - toplam_har:,.2f}",
        }

    # ─── VERİ KAYIT/YÜKLEME ───

    def verileri_kaydet(self) -> bool:
        try:
            data = {
                "seyahatler":        [s.to_dict() for s in self._seyahatler.values()],
                "konaklamalar":      [k.to_dict() for k in self._konaklamalar],
                "planlar":           [p.to_dict() for p in self._planlar],
                "sonraki_kid":       self._sonraki_kid,
                "sonraki_pid":       self._sonraki_pid,
            }
            with open(self.VERI_DOSYASI, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False

    def verileri_yukle(self) -> bool:
        if not os.path.exists(self.VERI_DOSYASI):
            return False
        try:
            with open(self.VERI_DOSYASI, "r", encoding="utf-8") as f:
                data = json.load(f)

            self._seyahatler = {}
            for sd in data.get("seyahatler", []):
                s = Seyahat.from_dict(sd)
                self._seyahatler[s.get_seyahat_id()] = s

            self._konaklamalar = []
            for kd in data.get("konaklamalar", []):
                sid = kd["seyahat_id"]
                if sid not in self._seyahatler:
                    continue
                s = self._seyahatler[sid]
                k = Konaklama(
                    kd["konaklama_id"], s,
                    kd["otel_adi"], KonaklamaTuru(kd["tur"]),
                    kd["fiyat_gece"],
                    datetime.fromisoformat(kd["checkin"]),
                    datetime.fromisoformat(kd["checkout"]),
                    kd.get("adres", "")
                )
                k._iptal_mi     = kd.get("iptal_mi", False)
                k._toplam_ucret = kd.get("toplam_ucret", 0.0)
                self._konaklamalar.append(k)

            self._planlar = []
            for pd in data.get("planlar", []):
                sid = pd["seyahat_id"]
                if sid not in self._seyahatler:
                    continue
                s = self._seyahatler[sid]
                p = Plan(pd["plan_id"], s, pd.get("rota", []), pd.get("notlar", ""))
                p._aktiviteler = pd.get("aktiviteler", {})
                p._durum       = PlanDurumu(pd.get("durum", "Taslak"))
                p._toplam_aktivite_maliyeti = pd.get("toplam_aktivite_maliyeti", 0.0)
                self._planlar.append(p)

            self._sonraki_kid = data.get("sonraki_kid", 1)
            self._sonraki_pid = data.get("sonraki_pid", 1)
            return True
        except Exception:
            return False
