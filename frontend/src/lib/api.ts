/**
 * lib/api.ts
 * Typed API client for the Marathi Kundali backend.
 * All fetch calls go through here — no raw fetch in components.
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

// ---------- Types ----------

export interface PlaceCandidate {
  display_name: string;
  latitude: number;
  longitude: number;
  tz_iana: string;
}

export interface RashiInfo    { value: number; name_en: string; name_mr: string; }
export interface NakshatraInfo { value: number; name_en: string; name_mr: string; pada: number; }
export interface GanaInfo     { value: string; name_mr: string; }
export interface NadiInfo     { value: string; name_mr: string; }
export interface VarnaInfo    { value: string; name_mr: string; }

export interface LockedFields {
  planet_positions: boolean;
  navamsa_chart: boolean;
  mangal_dosha: boolean;
  dasha: boolean;
  written_analysis: boolean;
}

export interface PlanetPosition {
  planet_en: string;
  planet_mr: string;
  rashi: RashiInfo;
  degree_in_rashi: number;
  house: number;
  nakshatra: NakshatraInfo;
  retrograde: boolean;
  is_exalted: boolean;
  is_debilitated: boolean;
}

export interface DashaInfo {
  mahadasha_lord_en: string;
  mahadasha_lord_mr: string;
  mahadasha_start: string;
  mahadasha_end: string;
  antardasha_lord_en: string;
  antardasha_lord_mr: string;
  antardasha_start: string;
  antardasha_end: string;
}

export interface MangalDoshaInfo {
  is_manglik: boolean;
  severity?: string;
  reference_point: string;
  mars_house: number | null;
  cancellation_applied: boolean;
  cancellation_rule: string | null;
  explanation_mr: string;
  explanation_en: string;
}

export interface WrittenAnalysis {
  rashi_analysis_mr: string;
  nakshatra_analysis_mr: string;
  lagna_analysis_mr: string;
  gana_analysis_mr: string;
  nadi_analysis_mr: string;
  dasha_analysis_mr: string;
}

export interface KundaliResponse {
  id: string;
  name: string;
  gender: string;
  dob: string;
  time_of_birth: string | null;
  time_accuracy: 'exact' | 'approximate' | 'unknown';
  place_text: string;
  latitude: number;
  longitude: number;
  tz_iana: string;
  lagna_reliable: boolean;
  rashi: RashiInfo | null;
  nakshatra: NakshatraInfo | null;
  lagna: RashiInfo | null;
  gana: GanaInfo | null;
  nadi: NadiInfo | null;
  varna: VarnaInfo | null;
  chart_d1_svg: string | null;
  paid: boolean;
  resume_token: string;
  locked: LockedFields;
  created_at: string;
  // Paid fields (only present when paid=true)
  planet_positions?: PlanetPosition[];
  navamsa_chart_svg?: string | null;
  chalit_chart_svg?: string | null;
  moon_chart_svg?: string | null;
  mangal_dosha?: MangalDoshaInfo;
  dasha?: DashaInfo;
  written_analysis?: WrittenAnalysis;
  avakahada?: AvakahadaInfo | null;
  mahadasha_table?: MahadashaPeriodInfo[];
  pdf_url?: string | null;
}

export interface AvakahadaInfo {
  nakshatra_mr: string;
  nakshatra_en: string;
  nakshatra_pada: number;
  rashi_mr: string;
  rashi_en: string;
  lagna_mr: string;
  lagna_en: string;
  karana_mr: string;
  karana_en: string;
  varna_mr: string;
  varna_en: string;
  vashya_mr: string;
  vashya_en: string;
  tatva_mr: string;
  tatva_en: string;
  gana_mr: string;
  gana_en: string;
  nadi_mr: string;
  nadi_en: string;
  yoni_mr: string;
  yoni_en: string;
}

export interface MahadashaPeriodInfo {
  lord_en: string;
  lord_mr: string;
  start_date: string;
  end_date: string;
  years: number;
}

export interface KundaliCreatePayload {
  name: string;
  gender: 'male' | 'female';
  dob: string;            // YYYY-MM-DD
  time_of_birth: string | null;  // HH:MM or null
  time_accuracy: 'exact' | 'approximate' | 'unknown';
  place_query: string;
  latitude: number;
  longitude: number;
  tz_iana: string;
  rahu_mode?: 'true_node' | 'mean_node';
}

// ---------- KootaRow ----------
export interface KootaRow {
  name_en: string;
  name_mr: string;
  points_earned: number;
  points_max: number;
  notes_mr: string;
  notes_en: string;
}

export interface DoshaCancellation {
  dosha_name: string;
  is_present: boolean;
  is_cancelled: boolean;
  cancellation_rule_mr: string | null;
  explanation_mr: string;
  explanation_en: string;
}

export interface MatchResponse {
  id: string;
  bride_name: string;
  groom_name: string;
  total_score: number;
  total_max: number;
  bride_manglik: boolean | null;
  groom_manglik: boolean | null;
  paid: boolean;
  locked: Record<string, boolean>;
  created_at: string;
  // Paid fields
  koota_breakdown?: KootaRow[];
  nadi_dosha?: DoshaCancellation;
  bhakoot_dosha?: DoshaCancellation;
  mangal_compatibility?: string;
  verdict_mr?: string;
  verdict_en?: string;
  pdf_url?: string | null;
}

// ---------- Fetch helpers ----------

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    let message = `API error ${res.status}`;
    try { const body = await res.json(); message = body.detail ?? message; } catch {}
    throw new Error(message);
  }
  return res.json();
}

// ---------- API functions ----------

export async function geocodePlace(query: string): Promise<PlaceCandidate[]> {
  const data = await apiFetch<{ places: PlaceCandidate[] }>(
    `/api/v1/geocode?query=${encodeURIComponent(query)}&limit=6`
  );
  return data.places;
}

export async function createKundali(payload: KundaliCreatePayload): Promise<KundaliResponse> {
  return apiFetch<KundaliResponse>('/api/v1/kundalis', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function getKundali(id: string): Promise<KundaliResponse> {
  return apiFetch<KundaliResponse>(`/api/v1/kundalis/${id}`);
}
