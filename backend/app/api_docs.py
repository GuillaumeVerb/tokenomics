from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi


def configure_openapi_docs(app: FastAPI) -> None:
    """Configure the OpenAPI documentation for the FastAPI application."""

    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema

        openapi_schema = get_openapi(
            title="Tokenomics API",
            version="1.0.0",
            description="""
            API de simulation et d'analyse tokenomics avancée.
            
            Fonctionnalités principales:
            * Simulation de différents mécanismes tokenomics
            * Analyse comparative de scénarios
            * Visualisation et export des résultats
            """,
            routes=app.routes,
        )

        # Ajout des tags
        openapi_schema["tags"] = [
            {"name": "Simulation", "description": "Endpoints de simulation tokenomics"}
        ]

        # Définition des composants de sécurité
        openapi_schema["components"]["securitySchemes"] = {
            "bearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
        }

        # Documentation des modèles
        openapi_schema["components"]["schemas"].update(
            {
                "HTTPError": {
                    "type": "object",
                    "properties": {
                        "detail": {
                            "type": "string",
                            "description": "Description détaillée de l'erreur",
                        }
                    },
                }
            }
        )

        # Documentation des endpoints
        openapi_schema["paths"]["/simulate/constant_inflation"] = {
            "post": {
                "tags": ["Simulation"],
                "summary": "Simule une inflation constante",
                "description": """
                Simule l'évolution de la supply avec un taux d'inflation constant.
                
                Paramètres:
                * initial_supply: Supply initiale de tokens
                * inflation_rate: Taux d'inflation annuel (%)
                * duration_in_years: Durée de la simulation en années
                """,
                "security": [{"bearerAuth": []}],
                "responses": {
                    "200": {
                        "description": "Simulation réussie",
                        "content": {
                            "application/json": {
                                "example": {
                                    "simulation_data": [
                                        {"year": 0, "supply": 1000000},
                                        {"year": 1, "supply": 1050000},
                                    ],
                                    "total_supply_increase": 50000,
                                    "total_supply_increase_percentage": 5.0,
                                }
                            }
                        },
                    },
                    "400": {"$ref": "#/components/schemas/HTTPError"},
                    "401": {"description": "Non authentifié"},
                    "403": {"description": "Non autorisé"},
                },
            }
        }

        openapi_schema["paths"]["/simulate/burn"] = {
            "post": {
                "tags": ["Simulation"],
                "summary": "Simule le burning de tokens",
                "description": """
                Simule le burning de tokens selon différents mécanismes.
                
                Types de burning:
                * Continu: Taux de burn appliqué mensuellement
                * Événementiel: Burns ponctuels à des dates spécifiques
                """,
                "security": [{"bearerAuth": []}],
                "responses": {
                    "200": {
                        "description": "Simulation réussie",
                        "content": {
                            "application/json": {
                                "example": {
                                    "simulation_data": [
                                        {"month": 0, "supply": 1000000, "burned": 0},
                                        {"month": 1, "supply": 990000, "burned": 10000},
                                    ],
                                    "total_burned": 10000,
                                }
                            }
                        },
                    },
                    "400": {"$ref": "#/components/schemas/HTTPError"},
                    "401": {"description": "Non authentifié"},
                    "403": {"description": "Non autorisé"},
                },
            }
        }

        openapi_schema["paths"]["/simulate/vesting"] = {
            "post": {
                "tags": ["Simulation"],
                "summary": "Simule le vesting de tokens",
                "description": """
                Simule des schedules de vesting multiples avec cliff periods.
                
                Caractéristiques:
                * Support de multiple périodes de vesting
                * Cliff periods configurables
                * Vesting linéaire ou personnalisé
                """,
                "security": [{"bearerAuth": []}],
                "responses": {
                    "200": {
                        "description": "Simulation réussie",
                        "content": {
                            "application/json": {
                                "example": {
                                    "simulation_data": [
                                        {"month": 0, "locked": 1000000, "vested": 0},
                                        {"month": 1, "locked": 950000, "vested": 50000},
                                    ],
                                    "total_vested": 50000,
                                }
                            }
                        },
                    },
                    "400": {"$ref": "#/components/schemas/HTTPError"},
                    "401": {"description": "Non authentifié"},
                    "403": {"description": "Non autorisé"},
                },
            }
        }

        openapi_schema["paths"]["/simulate/staking"] = {
            "post": {
                "tags": ["Simulation"],
                "summary": "Simule le staking de tokens",
                "description": """
                Simule un mécanisme de staking avec récompenses.
                
                Caractéristiques:
                * Taux de participation au staking
                * Récompenses de staking
                * Périodes de lock
                """,
                "security": [{"bearerAuth": []}],
                "responses": {
                    "200": {
                        "description": "Simulation réussie",
                        "content": {
                            "application/json": {
                                "example": {
                                    "simulation_data": [
                                        {"month": 0, "staked": 0, "rewards": 0},
                                        {"month": 1, "staked": 500000, "rewards": 5000},
                                    ],
                                    "total_staked": 500000,
                                    "total_rewards": 5000,
                                }
                            }
                        },
                    },
                    "400": {"$ref": "#/components/schemas/HTTPError"},
                    "401": {"description": "Non authentifié"},
                    "403": {"description": "Non autorisé"},
                },
            }
        }

        openapi_schema["paths"]["/simulate/scenario"] = {
            "post": {
                "tags": ["Simulation"],
                "summary": "Simule un scénario tokenomics complet",
                "description": """
                Simule un scénario combinant plusieurs mécanismes tokenomics.
                
                Mécanismes supportés:
                * Inflation (constante, dynamique, halving)
                * Burning (continu, événementiel)
                * Vesting (multiple périodes)
                * Staking (avec récompenses)
                """,
                "security": [{"bearerAuth": []}],
                "responses": {
                    "200": {
                        "description": "Simulation réussie",
                        "content": {
                            "application/json": {
                                "example": {
                                    "timeline": [
                                        {
                                            "period": 0,
                                            "total_supply": 1000000,
                                            "circulating_supply": 900000,
                                            "staked": 100000,
                                        }
                                    ],
                                    "summary": {
                                        "final_supply": 1100000,
                                        "total_minted": 150000,
                                        "total_burned": 50000,
                                    },
                                }
                            }
                        },
                    },
                    "400": {"$ref": "#/components/schemas/HTTPError"},
                    "401": {"description": "Non authentifié"},
                    "403": {"description": "Non autorisé"},
                },
            }
        }

        openapi_schema["paths"]["/simulate/compare"] = {
            "post": {
                "tags": ["Simulation"],
                "summary": "Compare plusieurs scénarios tokenomics",
                "description": """
                Compare 2 à 5 scénarios tokenomics différents.
                
                Fonctionnalités:
                * Comparaison détaillée des métriques
                * Graphiques comparatifs
                * Analyse des divergences
                * Résumé des différences clés
                """,
                "security": [{"bearerAuth": []}],
                "responses": {
                    "200": {
                        "description": "Comparaison réussie",
                        "content": {
                            "application/json": {
                                "example": {
                                    "scenarios": [
                                        {
                                            "name": "Conservative",
                                            "timeline": [],
                                            "summary": {},
                                        },
                                        {
                                            "name": "Aggressive",
                                            "timeline": [],
                                            "summary": {},
                                        },
                                    ],
                                    "comparison_summary": {
                                        "supply_range": {
                                            "min": 1000000,
                                            "max": 1200000,
                                            "avg": 1100000,
                                        }
                                    },
                                }
                            }
                        },
                    },
                    "400": {"$ref": "#/components/schemas/HTTPError"},
                    "401": {"description": "Non authentifié"},
                    "403": {"description": "Non autorisé"},
                },
            }
        }

        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi
