# Database Schema (PostgreSQL)

## `users` (optional for MVP — can be session-based instead, see note)
| column | type | notes |
|---|---|---|
| id | uuid pk | |
| phone or email | text | for order confirmation / resending PDF links |
| created_at | timestamptz | |

> Note: MVP can skip full auth and instead use a **session/order-token** model — user gets a unique link to their kundali/report after payment, no login required. Simpler for low-friction Marathi-family use case. Add real accounts later if repeat-usage data justifies it.

## `birth_profiles`
| column | type | notes |
|---|---|---|
| id | uuid pk | |
| name | text | |
| gender | text | |
| dob | date | |
| time_of_birth | time | nullable — flag if unknown/approximate |
| time_accuracy | enum | exact / approximate / unknown |
| place_text | text | as entered by user |
| latitude | numeric | resolved via geocoding |
| longitude | numeric | resolved via geocoding |
| tz_iana | text | e.g. Asia/Kolkata |
| utc_datetime | timestamptz | resolved birth moment, computed once |
| created_at | timestamptz | |

## `kundalis`
| column | type | notes |
|---|---|---|
| id | uuid pk | |
| birth_profile_id | fk → birth_profiles | |
| ayanamsa | text | default 'lahiri' |
| house_system | text | default 'whole_sign' |
| rahu_mode | text | 'true_node' / 'mean_node' |
| planet_positions | jsonb | array of {planet, sign, degree, house, nakshatra, pada, retrograde} |
| lagna | jsonb | {sign, degree} |
| rashi | text | derived, denormalized for fast lookup |
| nakshatra | text | denormalized |
| pada | int | |
| gana | text | derived |
| nadi | text | derived |
| varna | text | derived |
| mangal_dosha | jsonb | {status, reference_point, cancellation_applied, rule_notes} |
| dasha_current | jsonb | {mahadasha, antardasha, start_date, end_date} |
| dasha_timeline | jsonb | nullable, stretch goal full timeline |
| chart_style | text | north_indian / south_indian, user preference |
| paid | boolean | default false |
| order_id | fk → orders | nullable until paid |
| pdf_url | text | nullable, generated after payment |
| created_at | timestamptz | |

## `matches`
| column | type | notes |
|---|---|---|
| id | uuid pk | |
| kundali_id_bride | fk → kundalis | |
| kundali_id_groom | fk → kundalis | |
| koota_breakdown | jsonb | array of {koota_name, points_earned, points_max, notes} |
| total_score | numeric | out of 36 |
| nadi_dosha | boolean | |
| bhakoot_dosha | boolean | |
| dosha_cancellations | jsonb | which doshas cancelled, by which rule |
| mangal_compatibility | jsonb | both people's manglik status + compatibility note |
| verdict_text_mr | text | Marathi templated verdict |
| verdict_text_en | text | English mirror |
| paid | boolean | default false |
| order_id | fk → orders | nullable until paid |
| pdf_url | text | nullable |
| created_at | timestamptz | |

## `biodatas`
| column | type | notes |
|---|---|---|
| id | uuid pk | |
| kundali_id | fk → kundalis | nullable, optional link for auto-fill |
| personal_info | jsonb | name, dob, height, blood group, etc. |
| family_info | jsonb | father, mother, siblings, kul-daivat, gotra, etc. |
| education_career | jsonb | |
| horoscope_info | jsonb | auto-filled from kundali if linked, editable |
| expectations | text | |
| photo_url | text | |
| template_id | text | which design template chosen |
| language | text | mr / en / both |
| pdf_url | text | |
| paid | boolean | bundled with kundali payment, or standalone flag |
| created_at | timestamptz | |

## `orders`
| column | type | notes |
|---|---|---|
| id | uuid pk | |
| product_type | enum | kundali / matching / biodata / bundle |
| amount | numeric | 100 / 50 / etc. |
| currency | text | INR |
| gateway | text | razorpay |
| gateway_order_id | text | |
| gateway_payment_id | text | nullable until paid |
| status | enum | created / paid / failed / refunded |
| related_kundali_id | fk | nullable |
| related_match_id | fk | nullable |
| related_biodata_id | fk | nullable |
| created_at | timestamptz | |
| paid_at | timestamptz | nullable |

## `geocode_cache`
| column | type | notes |
|---|---|---|
| id | uuid pk | |
| place_query | text | normalized input |
| latitude | numeric | |
| longitude | numeric | |
| tz_iana | text | |
| resolved_at | timestamptz | |

> Cache geocoding/timezone lookups aggressively — same towns get queried repeatedly, and it reduces external API cost/latency.

## Indexing Notes
- Index `orders.gateway_order_id` (webhook lookups happen by this).
- Index `birth_profiles.place_text` + `geocode_cache.place_query` for cache hits.
- Index `kundalis.paid` and `matches.paid` for access-control checks on every fetch.
