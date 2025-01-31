from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from app.models.shock_event import ShockEvent, SimulationEvents
from app.models.simulation import SimulationParams
from app.services.simulation import simulate_tokenomics

router = APIRouter()

@router.post("/simulate/scenario")
async def simulate_scenario(
    params: SimulationParams,
    events: SimulationEvents
) -> Dict[str, Any]:
    """
    Simule un scénario de tokenomics avec des événements de shock.
    
    Args:
        params: Paramètres de base de la simulation
        events: Liste des événements de shock à appliquer
    
    Returns:
        Dict contenant les résultats de la simulation et les logs d'événements
    """
    try:
        # Trie les événements par ordre chronologique
        sorted_events = sorted(events.events, key=lambda x: x.get_month())
        
        # Initialise les résultats
        results = {
            "supply": [],
            "price": [],
            "liquidity": [],
            "event_logs": []
        }
        
        current_supply = params.initial_supply
        current_price = params.initial_price
        current_liquidity = params.initial_liquidity
        
        # Pour chaque mois de la simulation
        for month in range(params.simulation_months):
            # Applique les événements prévus pour ce mois
            month_events = [e for e in sorted_events if e.get_month() == month]
            
            for event in month_events:
                # Applique l'événement et récupère le log
                new_supply, log = event.apply_event(current_supply)
                
                # Met à jour les valeurs
                current_supply = new_supply
                
                # Gère les effets spéciaux selon le type d'événement
                if event.event_type == "liquidity_shock":
                    current_liquidity *= (1 + event.value)
                elif event.event_type == "freeze":
                    # Réduit temporairement la liquidité
                    current_liquidity *= (1 - event.value)
                
                # Ajuste le prix en fonction des changements
                if current_supply > 0:
                    current_price = (params.initial_supply * params.initial_price) / current_supply
                
                # Enregistre le log de l'événement
                results["event_logs"].append({
                    "month": month,
                    "event_type": event.event_type,
                    "message": log,
                    "impact": {
                        "supply": current_supply,
                        "price": current_price,
                        "liquidity": current_liquidity
                    }
                })
            
            # Applique la simulation normale pour ce mois
            monthly_results = simulate_tokenomics(
                current_supply,
                current_price,
                current_liquidity,
                params
            )
            
            # Met à jour les valeurs courantes
            current_supply = monthly_results["supply"]
            current_price = monthly_results["price"]
            current_liquidity = monthly_results["liquidity"]
            
            # Enregistre les résultats
            results["supply"].append(current_supply)
            results["price"].append(current_price)
            results["liquidity"].append(current_liquidity)
        
        return results
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 