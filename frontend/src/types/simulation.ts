export enum EventType {
    MASS_BURN = "mass_burn",
    INFLATION_SPIKE = "inflation_spike",
    LIQUIDITY_INJECTION = "liquidity_injection",
    LIQUIDITY_REMOVAL = "liquidity_removal",
    MARKET_SHOCK = "market_shock"
}

export enum TimeUnit {
    MONTHS = "months",
    YEARS = "years"
}

export interface ShockEvent {
    time_step: number;
    time_unit: TimeUnit;
    event_type: EventType;
    value: number;
    description?: string;
}

export interface FormValues {
    time_step: number;
    time_unit: TimeUnit;
    event_type: EventType;
    value: number;
    description?: string;
}

export interface SimulationParams {
    initial_supply: number;
    initial_price: number;
    initial_liquidity: number;
    simulation_months: number;
    monthly_inflation: number;
    vesting_period: number;
}

export interface SimulationResults {
    supply: number[];
    price: number[];
    liquidity: number[];
    event_logs: EventLog[];
}

export interface EventLog {
    month: number;
    event_type: string;
    message: string;
    impact: {
        supply: number;
        price: number;
        liquidity: number;
    };
}
