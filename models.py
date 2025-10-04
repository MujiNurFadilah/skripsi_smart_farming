from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any

@dataclass
class FuzzyCalculation:
    """Data model for fuzzy calculation results"""
    kelembaban_input: float
    cuaca_input: str
    durasi_output: float
    tingkat_kebutuhan: str
    kelembaban_tanah: Optional[float] = None
    suhu: Optional[float] = None
    kelembaban_udara: Optional[float] = None
    curah_hujan: Optional[float] = None
    status_pompa: Optional[str] = None
    timestamp: Optional[datetime] = None
    id: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'kelembaban_input': self.kelembaban_input,
            'cuaca_input': self.cuaca_input,
            'durasi_output': self.durasi_output,
            'tingkat_kebutuhan': self.tingkat_kebutuhan,
            'kelembaban_tanah': self.kelembaban_tanah,
            'suhu': self.suhu,
            'kelembaban_udara': self.kelembaban_udara,
            'curah_hujan': self.curah_hujan,
            'status_pompa': self.status_pompa,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

@dataclass
class CalculationInsight:
    """Data model for calculation insights"""
    insight_type: str
    insight_data: Dict[str, Any]
    created_at: Optional[datetime] = None
    id: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'insight_type': self.insight_type,
            'insight_data': self.insight_data,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class WeatherConditions:
    """Constants for weather conditions"""
    CERAH = "Cerah"
    BERAWAN = "Berawan"
    HUJAN_RINGAN = "Hujan Ringan"
    HUJAN_LEBAT = "Hujan Lebat"
    
    @classmethod
    def get_all(cls):
        return [cls.CERAH, cls.BERAWAN, cls.HUJAN_RINGAN, cls.HUJAN_LEBAT]

class NeedLevels:
    """Constants for irrigation need levels"""
    RENDAH = "Rendah"
    SEDANG = "Sedang"
    TINGGI = "Tinggi"
    
    @classmethod
    def get_all(cls):
        return [cls.RENDAH, cls.SEDANG, cls.TINGGI]