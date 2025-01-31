from enum import Enum
from pydantic import BaseModel, Field, validator
from typing import List

class EventType(str, Enum):
    MASS_BURN = "mass_burn"  # Brûle un % des tokens en circulation
    INFLATION_SPIKE = "inflation_spike"  # Augmente soudainement l'offre
    FREEZE = "freeze"  # Gèle les transferts pendant une période
    LIQUIDITY_SHOCK = "liquidity_shock"  # Modifie brutalement la liquidité
    UNLOCK = "unlock"  # Libération anticipée de tokens
    BUYBACK = "buyback"  # Rachat et destruction de tokens

class TimeUnit(str, Enum):
    MONTH = "month"
    YEAR = "year"

class ShockEvent(BaseModel):
    time_step: int = Field(..., description="Moment de l'événement", ge=0)
    time_unit: TimeUnit = Field(default=TimeUnit.MONTH, description="Unité de temps (mois ou année)")
    event_type: EventType = Field(..., description="Type d'événement")
    value: float = Field(..., description="Valeur de l'impact (ex: 0.3 pour 30%)", ge=0, le=1)
    description: str | None = Field(default=None, description="Description optionnelle de l'événement")

    @validator('value')
    def validate_value(cls, v, values):
        event_type = values.get('event_type')
        if event_type in [EventType.MASS_BURN, EventType.INFLATION_SPIKE] and v > 1:
            raise ValueError("La valeur doit être entre 0 et 1 pour les événements de burn et d'inflation")
        return v

    def get_month(self) -> int:
        """Convertit le time_step en mois"""
        return self.time_step * (12 if self.time_unit == TimeUnit.YEAR else 1)

    def apply_event(self, supply: float) -> tuple[float, str]:
        """Applique l'événement et retourne (nouveau_supply, message_log)"""
        if self.event_type == EventType.MASS_BURN:
            new_supply = supply * (1 - self.value)
            return new_supply, f"Mass burn de {self.value*100}% des tokens en circulation"
        
        elif self.event_type == EventType.INFLATION_SPIKE:
            new_supply = supply * (1 + self.value)
            return new_supply, f"Inflation spike de {self.value*100}% sur l'offre"
        
        elif self.event_type == EventType.FREEZE:
            # Le freeze n'affecte pas directement le supply mais est loggé
            return supply, f"Freeze des transferts pendant {self.value*100}% du mois"
        
        elif self.event_type == EventType.LIQUIDITY_SHOCK:
            # La liquidité est gérée séparément
            return supply, f"Shock de liquidité de {self.value*100}%"
        
        elif self.event_type == EventType.UNLOCK:
            new_supply = supply * (1 + self.value)
            return new_supply, f"Unlock anticipé de {self.value*100}% des tokens"
        
        elif self.event_type == EventType.BUYBACK:
            new_supply = supply * (1 - self.value)
            return new_supply, f"Buyback et burn de {self.value*100}% des tokens"
        
        return supply, "Événement non géré"

class SimulationEvents(BaseModel):
    events: List[ShockEvent] = Field(default_list=[], description="Liste des événements de shock") 