export interface User {
    id: number;
    email: string;
    full_name: string;
    phone?: string;
    is_active: boolean;
    language_preference: string;
    created_at: string;
}

export interface AuthResponse {
    access_token: string;
    refresh_token: string;
    token_type: string;
    user: User;
}

export interface Company {
    id: number;
    name: string;
    registration_number?: string;
    pan?: string;
    gstin?: string;
    industry: string;
    sub_industry?: string;
    founded_date?: string;
    employee_count?: number;
    annual_revenue?: number;
    website?: string;
    city?: string;
    state?: string;
    country: string;
    created_at: string;
    updated_at: string;
}

export interface FinancialRatios {
    company_id: number;
    liquidity: Record<string, number>;
    profitability: Record<string, number>;
    leverage: Record<string, number>;
    efficiency: Record<string, number>;
    calculated_at: string;
}

export interface HealthScore {
    company_id: number;
    overall_score: number;
    grade: string;
    score_breakdown: Record<string, number>;
    ratios: Record<string, Record<string, number>>;
    cash_flow_summary: any;
    ai_insights?: string;
}
