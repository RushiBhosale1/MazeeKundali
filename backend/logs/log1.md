==> Docs on specifying a port: https://render.com/docs/web-services#port-binding
INFO:     10.29.161.129:0 - "OPTIONS /api/v1/geocode?query=Sa&limit=6 HTTP/1.1" 200 OK
INFO:     10.31.107.4:0 - "OPTIONS /api/v1/geocode?query=Sat&limit=6 HTTP/1.1" 200 OK
INFO:     10.29.161.129:0 - "OPTIONS /api/v1/geocode?query=Satar&limit=6 HTTP/1.1" 200 OK
INFO:     10.25.169.129:0 - "GET /api/v1/geocode?query=Sa&limit=6 HTTP/1.1" 200 OK
INFO:     10.25.169.129:0 - "OPTIONS /api/v1/geocode?query=Sata&limit=6 HTTP/1.1" 200 OK
INFO:     10.29.161.129:0 - "OPTIONS /api/v1/geocode?query=Satara&limit=6 HTTP/1.1" 200 OK
INFO:     10.25.169.129:0 - "GET /api/v1/geocode?query=Satar&limit=6 HTTP/1.1" 200 OK
INFO:     10.31.107.4:0 - "GET /api/v1/geocode?query=Sat&limit=6 HTTP/1.1" 200 OK
INFO:     10.25.169.129:0 - "GET /api/v1/geocode?query=Satara&limit=6 HTTP/1.1" 200 OK
INFO:     10.29.161.129:0 - "GET /api/v1/geocode?query=Sata&limit=6 HTTP/1.1" 200 OK
INFO:     10.25.169.129:0 - "GET /api/v1/geocode?query=Sa&limit=6 HTTP/1.1" 200 OK
INFO:     10.29.161.129:0 - "GET /api/v1/geocode?query=Sat&limit=6 HTTP/1.1" 200 OK
INFO:     10.29.161.129:0 - "GET /api/v1/geocode?query=Satar&limit=6 HTTP/1.1" 200 OK
INFO:     10.31.107.4:0 - "GET /api/v1/geocode?query=Sata&limit=6 HTTP/1.1" 200 OK
INFO:     10.31.107.4:0 - "GET /api/v1/geocode?query=Satara&limit=6 HTTP/1.1" 200 OK
INFO:     10.31.107.4:0 - "OPTIONS /api/v1/matchings HTTP/1.1" 200 OK
2026-07-22 14:59:08,586 | INFO     | engine.chart | Computing kundali for Sonali, DOB=1994-02-05, Time=15:05:00, Place=Satara, Maharashtra, India (Asia/Kolkata)
2026-07-22 14:59:08,591 | WARNING  | engine.geocoding | Unknown IANA timezone: Asia/Kolkata, falling back to UTC+5:30
2026-07-22 14:59:08,591 | INFO     | engine.ephemeris | Swiss Ephemeris initialized with path: ./static/ephemeris
2026-07-22 14:59:08,593 | DEBUG    | engine.ephemeris | Ephemeris computed: JD=2449388.8993, Ayanamsa=23.7746°, Lagna=67.3982° sidereal
2026-07-22 14:59:08,594 | DEBUG    | engine.dasha | Dasha balance: nakshatra=Jyeshtha, lord=Mercury, fraction_remaining=0.8235, balance=5113.5 days
2026-07-22 14:59:08,594 | DEBUG    | engine.dasha | Current Dasha: Maha=Venus (2015-02-05 to 2035-02-05), Antara=Jupiter (2025-04-06 to 2027-12-06)
2026-07-22 14:59:08,594 | INFO     | engine.chart | Computing kundali for Suraj, DOB=1989-05-05, Time=13:55:00, Place=Satara, Maharashtra, India (Asia/Kolkata)
2026-07-22 14:59:08,594 | WARNING  | engine.geocoding | Unknown IANA timezone: Asia/Kolkata, falling back to UTC+5:30
2026-07-22 14:59:08,595 | INFO     | engine.ephemeris | Swiss Ephemeris initialized with path: ./static/ephemeris
2026-07-22 14:59:08,595 | DEBUG    | engine.ephemeris | Ephemeris computed: JD=2447651.8507, Ayanamsa=23.7082°, Lagna=131.2999° sidereal
2026-07-22 14:59:08,595 | DEBUG    | engine.dasha | Dasha balance: nakshatra=Bharani, lord=Venus, fraction_remaining=0.5638, balance=4118.8 days
2026-07-22 14:59:08,595 | DEBUG    | engine.dasha | Current Dasha: Maha=Rahu (2023-08-14 to 2041-08-14), Antara=Jupiter (2026-04-26 to 2028-09-19)
2026-07-22 14:59:10,185 | INFO     | sqlalchemy.engine.Engine | select pg_catalog.version()
2026-07-22 14:59:10,185 INFO sqlalchemy.engine.Engine select pg_catalog.version()
2026-07-22 14:59:10,186 | INFO     | sqlalchemy.engine.Engine | [raw sql] ()
2026-07-22 14:59:10,186 INFO sqlalchemy.engine.Engine [raw sql] ()
2026-07-22 14:59:10,468 | INFO     | sqlalchemy.engine.Engine | select current_schema()
2026-07-22 14:59:10,468 INFO sqlalchemy.engine.Engine select current_schema()
2026-07-22 14:59:10,468 INFO sqlalchemy.engine.Engine [raw sql] ()
2026-07-22 14:59:10,468 | INFO     | sqlalchemy.engine.Engine | [raw sql] ()
2026-07-22 14:59:10,750 INFO sqlalchemy.engine.Engine show standard_conforming_strings
2026-07-22 14:59:10,750 INFO sqlalchemy.engine.Engine [raw sql] ()
2026-07-22 14:59:10,750 | INFO     | sqlalchemy.engine.Engine | show standard_conforming_strings
2026-07-22 14:59:10,750 | INFO     | sqlalchemy.engine.Engine | [raw sql] ()
2026-07-22 14:59:10,960 INFO sqlalchemy.engine.Engine BEGIN (implicit)
2026-07-22 14:59:10,960 | INFO     | sqlalchemy.engine.Engine | BEGIN (implicit)
2026-07-22 14:59:10,963 INFO sqlalchemy.engine.Engine INSERT INTO birth_profiles (id, name, gender, dob, time_of_birth, time_accuracy, place_text, latitude, longitude, tz_iana, rahu_mode) VALUES ($1::UUID, $2::VARCHAR, $3::gender_enum, $4::DATE, $5::TIME WITHOUT TIME ZONE, $6::time_accuracy_enum, $7::VARCHAR, $8::FLOAT, $9::FLOAT, $10::VARCHAR, $11::rahu_mode_enum) RETURNING birth_profiles.created_at
2026-07-22 14:59:10,963 | INFO     | sqlalchemy.engine.Engine | INSERT INTO birth_profiles (id, name, gender, dob, time_of_birth, time_accuracy, place_text, latitude, longitude, tz_iana, rahu_mode) VALUES ($1::UUID, $2::VARCHAR, $3::gender_enum, $4::DATE, $5::TIME WITHOUT TIME ZONE, $6::time_accuracy_enum, $7::VARCHAR, $8::FLOAT, $9::FLOAT, $10::VARCHAR, $11::rahu_mode_enum) RETURNING birth_profiles.created_at
2026-07-22 14:59:10,963 INFO sqlalchemy.engine.Engine [generated in 0.00021s] (UUID('32b1d29a-50c4-44d8-afd8-5169dd45b25f'), 'Sonali', 'female', datetime.date(1994, 2, 5), datetime.time(15, 5), 'exact', 'Satara, Maharashtra, India', 17.636129, 74.298278, 'Asia/Kolkata', 'true_node')
2026-07-22 14:59:10,963 | INFO     | sqlalchemy.engine.Engine | [generated in 0.00021s] (UUID('32b1d29a-50c4-44d8-afd8-5169dd45b25f'), 'Sonali', 'female', datetime.date(1994, 2, 5), datetime.time(15, 5), 'exact', 'Satara, Maharashtra, India', 17.636129, 74.298278, 'Asia/Kolkata', 'true_node')
2026-07-22 14:59:11,667 INFO sqlalchemy.engine.Engine INSERT INTO birth_profiles (id, name, gender, dob, time_of_birth, time_accuracy, place_text, latitude, longitude, tz_iana, rahu_mode) VALUES ($1::UUID, $2::VARCHAR, $3::gender_enum, $4::DATE, $5::TIME WITHOUT TIME ZONE, $6::time_accuracy_enum, $7::VARCHAR, $8::FLOAT, $9::FLOAT, $10::VARCHAR, $11::rahu_mode_enum) RETURNING birth_profiles.created_at
2026-07-22 14:59:11,667 | INFO     | sqlalchemy.engine.Engine | INSERT INTO birth_profiles (id, name, gender, dob, time_of_birth, time_accuracy, place_text, latitude, longitude, tz_iana, rahu_mode) VALUES ($1::UUID, $2::VARCHAR, $3::gender_enum, $4::DATE, $5::TIME WITHOUT TIME ZONE, $6::time_accuracy_enum, $7::VARCHAR, $8::FLOAT, $9::FLOAT, $10::VARCHAR, $11::rahu_mode_enum) RETURNING birth_profiles.created_at
2026-07-22 14:59:11,667 INFO sqlalchemy.engine.Engine [cached since 0.7043s ago] (UUID('5b739c34-fa70-4cf7-aff6-b6d0bb174202'), 'Suraj', 'male', datetime.date(1989, 5, 5), datetime.time(13, 55), 'exact', 'Satara, Maharashtra, India', 17.636129, 74.298278, 'Asia/Kolkata', 'true_node')
2026-07-22 14:59:11,667 | INFO     | sqlalchemy.engine.Engine | [cached since 0.7043s ago] (UUID('5b739c34-fa70-4cf7-aff6-b6d0bb174202'), 'Suraj', 'male', datetime.date(1989, 5, 5), datetime.time(13, 55), 'exact', 'Satara, Maharashtra, India', 17.636129, 74.298278, 'Asia/Kolkata', 'true_node')
2026-07-22 14:59:11,740 INFO sqlalchemy.engine.Engine INSERT INTO matchings (id, bride_kundali_id, groom_kundali_id, bride_birth_profile_id, groom_birth_profile_id, total_score, total_max, bride_manglik, groom_manglik, bride_manglik_severity, groom_manglik_severity, paid, koota_breakdown, dosha_analysis, verdict_mr, verdict_en, pdf_url, resume_token, paid_at, expires_at) VALUES ($1::UUID, $2::UUID, $3::UUID, $4::UUID, $5::UUID, $6::FLOAT, $7::INTEGER, $8::BOOLEAN, $9::BOOLEAN, $10::VARCHAR, $11::VARCHAR, $12::BOOLEAN, $13::JSONB, $14::JSONB, $15::VARCHAR, $16::VARCHAR, $17::VARCHAR, $18::VARCHAR, $19::TIMESTAMP WITHOUT TIME ZONE, $20::TIMESTAMP WITHOUT TIME ZONE) RETURNING matchings.created_at
2026-07-22 14:59:11,740 | INFO     | sqlalchemy.engine.Engine | INSERT INTO matchings (id, bride_kundali_id, groom_kundali_id, bride_birth_profile_id, groom_birth_profile_id, total_score, total_max, bride_manglik, groom_manglik, bride_manglik_severity, groom_manglik_severity, paid, koota_breakdown, dosha_analysis, verdict_mr, verdict_en, pdf_url, resume_token, paid_at, expires_at) VALUES ($1::UUID, $2::UUID, $3::UUID, $4::UUID, $5::UUID, $6::FLOAT, $7::INTEGER, $8::BOOLEAN, $9::BOOLEAN, $10::VARCHAR, $11::VARCHAR, $12::BOOLEAN, $13::JSONB, $14::JSONB, $15::VARCHAR, $16::VARCHAR, $17::VARCHAR, $18::VARCHAR, $19::TIMESTAMP WITHOUT TIME ZONE, $20::TIMESTAMP WITHOUT TIME ZONE) RETURNING matchings.created_at
2026-07-22 14:59:11,740 INFO sqlalchemy.engine.Engine [generated in 0.00039s] (UUID('d19a985c-3f36-48f4-8780-7b075d89507b'), None, None, UUID('32b1d29a-50c4-44d8-afd8-5169dd45b25f'), UUID('5b739c34-fa70-4cf7-aff6-b6d0bb174202'), 29.5, 36, False, False, 'CANCELLED', 'NONE', False, '[{"name_en": "Varna", "name_mr": "\\u0935\\u0930\\u094d\\u0923", "points_earned": 0, "points_max": 1, "notes_mr": "\\u092e\\u0941\\u0932\\u093e\\u091 ... (14575 characters truncated) ... t": "\\u092e\\u0927\\u094d\\u092f", "girl_trait": "\\u0906\\u0926\\u0940", "area_of_life_mr": "\\u0906\\u0930\\u094b\\u0917\\u094d\\u092f / Health"}]', '{"nadi_dosha": {"dosha_name": "Nadi Dosha", "is_present": false, "is_cancelled": false, "cancellation_rule_mr": null, "explanation_mr": "\\u092e\\u09 ... (991 characters truncated) ... 06\\u0939\\u0947. \\u096d \\u0917\\u0941\\u0923.", "explanation_en": "Bhakoot Dosha (6/8) (Cancelled): Both have same Rashi lord (Mars). 7 points."}}', 'या जुळणीला उत्तम 29.5/३६ गुण मिळाले आहेत! ग्रहांची मैत्री आणि स्वभाव चांगला जुळत आहे. वैवाहिक जीवन सुखी आणि समृद्ध होईल. हा विवाह करण्यास हरकत नाही.', 'This match scores a good 29.5/36 points! Planetary friendship and temperaments align well. The married life is expected to be happy and prosperous. This is a recommended match.', None, 'Rxmjns9p8yGG_1VglEJGe357z1jbg6t6YzduZT5lLn8', None, datetime.datetime(2026, 8, 21, 14, 59, 11, 737672))
2026-07-22 14:59:11,740 | INFO     | sqlalchemy.engine.Engine | [generated in 0.00039s] (UUID('d19a985c-3f36-48f4-8780-7b075d89507b'), None, None, UUID('32b1d29a-50c4-44d8-afd8-5169dd45b25f'), UUID('5b739c34-fa70-4cf7-aff6-b6d0bb174202'), 29.5, 36, False, False, 'CANCELLED', 'NONE', False, '[{"name_en": "Varna", "name_mr": "\\u0935\\u0930\\u094d\\u0923", "points_earned": 0, "points_max": 1, "notes_mr": "\\u092e\\u0941\\u0932\\u093e\\u091 ... (14575 characters truncated) ... t": "\\u092e\\u0927\\u094d\\u092f", "girl_trait": "\\u0906\\u0926\\u0940", "area_of_life_mr": "\\u0906\\u0930\\u094b\\u0917\\u094d\\u092f / Health"}]', '{"nadi_dosha": {"dosha_name": "Nadi Dosha", "is_present": false, "is_cancelled": false, "cancellation_rule_mr": null, "explanation_mr": "\\u092e\\u09 ... (991 characters truncated) ... 06\\u0939\\u0947. \\u096d \\u0917\\u0941\\u0923.", "explanation_en": "Bhakoot Dosha (6/8) (Cancelled): Both have same Rashi lord (Mars). 7 points."}}', 'या जुळणीला उत्तम 29.5/३६ गुण मिळाले आहेत! ग्रहांची मैत्री आणि स्वभाव चांगला जुळत आहे. वैवाहिक जीवन सुखी आणि समृद्ध होईल. हा विवाह करण्यास हरकत नाही.', 'This match scores a good 29.5/36 points! Planetary friendship and temperaments align well. The married life is expected to be happy and prosperous. This is a recommended match.', None, 'Rxmjns9p8yGG_1VglEJGe357z1jbg6t6YzduZT5lLn8', None, datetime.datetime(2026, 8, 21, 14, 59, 11, 737672))
2026-07-22 14:59:11,961 INFO sqlalchemy.engine.Engine COMMIT
2026-07-22 14:59:11,961 | INFO     | sqlalchemy.engine.Engine | COMMIT
INFO:     10.31.107.4:0 - "POST /api/v1/matchings HTTP/1.1" 201 Created
2026-07-22 14:59:14,389 | INFO     | sqlalchemy.engine.Engine | BEGIN (implicit)
2026-07-22 14:59:14,389 INFO sqlalchemy.engine.Engine BEGIN (implicit)
2026-07-22 14:59:14,397 | INFO     | sqlalchemy.engine.Engine | SELECT matchings.id, matchings.bride_kundali_id, matchings.groom_kundali_id, matchings.bride_birth_profile_id, matchings.groom_birth_profile_id, matchings.total_score, matchings.total_max, matchings.bride_manglik, matchings.groom_manglik, matchings.bride_manglik_severity, matchings.groom_manglik_severity, matchings.paid, matchings.koota_breakdown, matchings.dosha_analysis, matchings.verdict_mr, matchings.verdict_en, matchings.pdf_url, matchings.resume_token, matchings.paid_at, matchings.created_at, matchings.expires_at 
FROM matchings 
WHERE matchings.id = $1::UUID
2026-07-22 14:59:14,397 | INFO     | sqlalchemy.engine.Engine | [generated in 0.00033s] (UUID('d19a985c-3f36-48f4-8780-7b075d89507b'),)
2026-07-22 14:59:14,397 INFO sqlalchemy.engine.Engine SELECT matchings.id, matchings.bride_kundali_id, matchings.groom_kundali_id, matchings.bride_birth_profile_id, matchings.groom_birth_profile_id, matchings.total_score, matchings.total_max, matchings.bride_manglik, matchings.groom_manglik, matchings.bride_manglik_severity, matchings.groom_manglik_severity, matchings.paid, matchings.koota_breakdown, matchings.dosha_analysis, matchings.verdict_mr, matchings.verdict_en, matchings.pdf_url, matchings.resume_token, matchings.paid_at, matchings.created_at, matchings.expires_at 
FROM matchings 
WHERE matchings.id = $1::UUID
2026-07-22 14:59:14,397 INFO sqlalchemy.engine.Engine [generated in 0.00033s] (UUID('d19a985c-3f36-48f4-8780-7b075d89507b'),)
2026-07-22 14:59:14,685 INFO sqlalchemy.engine.Engine SELECT birth_profiles.id AS birth_profiles_id, birth_profiles.name AS birth_profiles_name, birth_profiles.gender AS birth_profiles_gender, birth_profiles.dob AS birth_profiles_dob, birth_profiles.time_of_birth AS birth_profiles_time_of_birth, birth_profiles.time_accuracy AS birth_profiles_time_accuracy, birth_profiles.place_text AS birth_profiles_place_text, birth_profiles.latitude AS birth_profiles_latitude, birth_profiles.longitude AS birth_profiles_longitude, birth_profiles.tz_iana AS birth_profiles_tz_iana, birth_profiles.rahu_mode AS birth_profiles_rahu_mode, birth_profiles.created_at AS birth_profiles_created_at 
FROM birth_profiles 
WHERE birth_profiles.id IN ($1::UUID)
2026-07-22 14:59:14,685 INFO sqlalchemy.engine.Engine [generated in 0.00025s] (UUID('32b1d29a-50c4-44d8-afd8-5169dd45b25f'),)
2026-07-22 14:59:14,685 | INFO     | sqlalchemy.engine.Engine | SELECT birth_profiles.id AS birth_profiles_id, birth_profiles.name AS birth_profiles_name, birth_profiles.gender AS birth_profiles_gender, birth_profiles.dob AS birth_profiles_dob, birth_profiles.time_of_birth AS birth_profiles_time_of_birth, birth_profiles.time_accuracy AS birth_profiles_time_accuracy, birth_profiles.place_text AS birth_profiles_place_text, birth_profiles.latitude AS birth_profiles_latitude, birth_profiles.longitude AS birth_profiles_longitude, birth_profiles.tz_iana AS birth_profiles_tz_iana, birth_profiles.rahu_mode AS birth_profiles_rahu_mode, birth_profiles.created_at AS birth_profiles_created_at 
FROM birth_profiles 
WHERE birth_profiles.id IN ($1::UUID)
2026-07-22 14:59:14,685 | INFO     | sqlalchemy.engine.Engine | [generated in 0.00025s] (UUID('32b1d29a-50c4-44d8-afd8-5169dd45b25f'),)
2026-07-22 14:59:14,829 INFO sqlalchemy.engine.Engine SELECT birth_profiles.id AS birth_profiles_id, birth_profiles.name AS birth_profiles_name, birth_profiles.gender AS birth_profiles_gender, birth_profiles.dob AS birth_profiles_dob, birth_profiles.time_of_birth AS birth_profiles_time_of_birth, birth_profiles.time_accuracy AS birth_profiles_time_accuracy, birth_profiles.place_text AS birth_profiles_place_text, birth_profiles.latitude AS birth_profiles_latitude, birth_profiles.longitude AS birth_profiles_longitude, birth_profiles.tz_iana AS birth_profiles_tz_iana, birth_profiles.rahu_mode AS birth_profiles_rahu_mode, birth_profiles.created_at AS birth_profiles_created_at 
FROM birth_profiles 
2026-07-22 14:59:14,829 | INFO     | sqlalchemy.engine.Engine | SELECT birth_profiles.id AS birth_profiles_id, birth_profiles.name AS birth_profiles_name, birth_profiles.gender AS birth_profiles_gender, birth_profiles.dob AS birth_profiles_dob, birth_profiles.time_of_birth AS birth_profiles_time_of_birth, birth_profiles.time_accuracy AS birth_profiles_time_accuracy, birth_profiles.place_text AS birth_profiles_place_text, birth_profiles.latitude AS birth_profiles_latitude, birth_profiles.longitude AS birth_profiles_longitude, birth_profiles.tz_iana AS birth_profiles_tz_iana, birth_profiles.rahu_mode AS birth_profiles_rahu_mode, birth_profiles.created_at AS birth_profiles_created_at 
WHERE birth_profiles.id IN ($1::UUID)
FROM birth_profiles 
WHERE birth_profiles.id IN ($1::UUID)
2026-07-22 14:59:14,829 | INFO     | sqlalchemy.engine.Engine | [generated in 0.00028s] (UUID('5b739c34-fa70-4cf7-aff6-b6d0bb174202'),)
2026-07-22 14:59:14,829 INFO sqlalchemy.engine.Engine [generated in 0.00028s] (UUID('5b739c34-fa70-4cf7-aff6-b6d0bb174202'),)
2026-07-22 14:59:14,900 INFO sqlalchemy.engine.Engine COMMIT
2026-07-22 14:59:14,900 | INFO     | sqlalchemy.engine.Engine | COMMIT
INFO:     10.25.169.129:0 - "GET /api/v1/matchings/d19a985c-3f36-48f4-8780-7b075d89507b HTTP/1.1" 200 OK
INFO:     10.25.169.129:0 - "OPTIONS /api/v1/orders HTTP/1.1" 200 OK
2026-07-22 14:59:23,545 INFO sqlalchemy.engine.Engine BEGIN (implicit)
2026-07-22 14:59:23,545 | INFO     | sqlalchemy.engine.Engine | BEGIN (implicit)
2026-07-22 14:59:23,546 INFO sqlalchemy.engine.Engine SELECT matchings.id, matchings.bride_kundali_id, matchings.groom_kundali_id, matchings.bride_birth_profile_id, matchings.groom_birth_profile_id, matchings.total_score, matchings.total_max, matchings.bride_manglik, matchings.groom_manglik, matchings.bride_manglik_severity, matchings.groom_manglik_severity, matchings.paid, matchings.koota_breakdown, matchings.dosha_analysis, matchings.verdict_mr, matchings.verdict_en, matchings.pdf_url, matchings.resume_token, matchings.paid_at, matchings.created_at, matchings.expires_at 
FROM matchings 
WHERE matchings.id = $1::UUID
2026-07-22 14:59:23,546 | INFO     | sqlalchemy.engine.Engine | SELECT matchings.id, matchings.bride_kundali_id, matchings.groom_kundali_id, matchings.bride_birth_profile_id, matchings.groom_birth_profile_id, matchings.total_score, matchings.total_max, matchings.bride_manglik, matchings.groom_manglik, matchings.bride_manglik_severity, matchings.groom_manglik_severity, matchings.paid, matchings.koota_breakdown, matchings.dosha_analysis, matchings.verdict_mr, matchings.verdict_en, matchings.pdf_url, matchings.resume_token, matchings.paid_at, matchings.created_at, matchings.expires_at 
FROM matchings 
WHERE matchings.id = $1::UUID
2026-07-22 14:59:23,546 INFO sqlalchemy.engine.Engine [cached since 9.15s ago] (UUID('d19a985c-3f36-48f4-8780-7b075d89507b'),)
2026-07-22 14:59:23,546 | INFO     | sqlalchemy.engine.Engine | [cached since 9.15s ago] (UUID('d19a985c-3f36-48f4-8780-7b075d89507b'),)
2026-07-22 14:59:23,688 | INFO     | sqlalchemy.engine.Engine | SELECT birth_profiles.id AS birth_profiles_id, birth_profiles.name AS birth_profiles_name, birth_profiles.gender AS birth_profiles_gender, birth_profiles.dob AS birth_profiles_dob, birth_profiles.time_of_birth AS birth_profiles_time_of_birth, birth_profiles.time_accuracy AS birth_profiles_time_accuracy, birth_profiles.place_text AS birth_profiles_place_text, birth_profiles.latitude AS birth_profiles_latitude, birth_profiles.longitude AS birth_profiles_longitude, birth_profiles.tz_iana AS birth_profiles_tz_iana, birth_profiles.rahu_mode AS birth_profiles_rahu_mode, birth_profiles.created_at AS birth_profiles_created_at 
2026-07-22 14:59:23,688 INFO sqlalchemy.engine.Engine SELECT birth_profiles.id AS birth_profiles_id, birth_profiles.name AS birth_profiles_name, birth_profiles.gender AS birth_profiles_gender, birth_profiles.dob AS birth_profiles_dob, birth_profiles.time_of_birth AS birth_profiles_time_of_birth, birth_profiles.time_accuracy AS birth_profiles_time_accuracy, birth_profiles.place_text AS birth_profiles_place_text, birth_profiles.latitude AS birth_profiles_latitude, birth_profiles.longitude AS birth_profiles_longitude, birth_profiles.tz_iana AS birth_profiles_tz_iana, birth_profiles.rahu_mode AS birth_profiles_rahu_mode, birth_profiles.created_at AS birth_profiles_created_at 
FROM birth_profiles 
WHERE birth_profiles.id IN ($1::UUID)
2026-07-22 14:59:23,688 | INFO     | sqlalchemy.engine.Engine | [cached since 9.003s ago] (UUID('32b1d29a-50c4-44d8-afd8-5169dd45b25f'),)
FROM birth_profiles 
WHERE birth_profiles.id IN ($1::UUID)
2026-07-22 14:59:23,688 INFO sqlalchemy.engine.Engine [cached since 9.003s ago] (UUID('32b1d29a-50c4-44d8-afd8-5169dd45b25f'),)
2026-07-22 14:59:23,759 INFO sqlalchemy.engine.Engine SELECT birth_profiles.id AS birth_profiles_id, birth_profiles.name AS birth_profiles_name, birth_profiles.gender AS birth_profiles_gender, birth_profiles.dob AS birth_profiles_dob, birth_profiles.time_of_birth AS birth_profiles_time_of_birth, birth_profiles.time_accuracy AS birth_profiles_time_accuracy, birth_profiles.place_text AS birth_profiles_place_text, birth_profiles.latitude AS birth_profiles_latitude, birth_profiles.longitude AS birth_profiles_longitude, birth_profiles.tz_iana AS birth_profiles_tz_iana, birth_profiles.rahu_mode AS birth_profiles_rahu_mode, birth_profiles.created_at AS birth_profiles_created_at 
FROM birth_profiles 
WHERE birth_profiles.id IN ($1::UUID)
2026-07-22 14:59:23,759 | INFO     | sqlalchemy.engine.Engine | SELECT birth_profiles.id AS birth_profiles_id, birth_profiles.name AS birth_profiles_name, birth_profiles.gender AS birth_profiles_gender, birth_profiles.dob AS birth_profiles_dob, birth_profiles.time_of_birth AS birth_profiles_time_of_birth, birth_profiles.time_accuracy AS birth_profiles_time_accuracy, birth_profiles.place_text AS birth_profiles_place_text, birth_profiles.latitude AS birth_profiles_latitude, birth_profiles.longitude AS birth_profiles_longitude, birth_profiles.tz_iana AS birth_profiles_tz_iana, birth_profiles.rahu_mode AS birth_profiles_rahu_mode, birth_profiles.created_at AS birth_profiles_created_at 
2026-07-22 14:59:23,759 INFO sqlalchemy.engine.Engine [cached since 8.93s ago] (UUID('5b739c34-fa70-4cf7-aff6-b6d0bb174202'),)
FROM birth_profiles 
WHERE birth_profiles.id IN ($1::UUID)
2026-07-22 14:59:23,759 | INFO     | sqlalchemy.engine.Engine | [cached since 8.93s ago] (UUID('5b739c34-fa70-4cf7-aff6-b6d0bb174202'),)
2026-07-22 14:59:23,831 INFO sqlalchemy.engine.Engine INSERT INTO orders (id, product_type, kundali_id, matching_id, biodata_id, amount_paise, currency, razorpay_order_id, razorpay_payment_id, razorpay_signature, status, paid_at, customer_phone, customer_email) VALUES ($1::UUID, $2::product_type_enum, $3::UUID, $4::UUID, $5::UUID, $6::INTEGER, $7::VARCHAR, $8::VARCHAR, $9::VARCHAR, $10::VARCHAR, $11::order_status_enum, $12::TIMESTAMP WITHOUT TIME ZONE, $13::VARCHAR, $14::VARCHAR) RETURNING orders.created_at
2026-07-22 14:59:23,831 | INFO     | sqlalchemy.engine.Engine | INSERT INTO orders (id, product_type, kundali_id, matching_id, biodata_id, amount_paise, currency, razorpay_order_id, razorpay_payment_id, razorpay_signature, status, paid_at, customer_phone, customer_email) VALUES ($1::UUID, $2::product_type_enum, $3::UUID, $4::UUID, $5::UUID, $6::INTEGER, $7::VARCHAR, $8::VARCHAR, $9::VARCHAR, $10::VARCHAR, $11::order_status_enum, $12::TIMESTAMP WITHOUT TIME ZONE, $13::VARCHAR, $14::VARCHAR) RETURNING orders.created_at
2026-07-22 14:59:23,831 INFO sqlalchemy.engine.Engine [generated in 0.00030s] (UUID('6cb19b69-f01c-439a-b58c-e31c11d4dce6'), 'matching', None, UUID('d19a985c-3f36-48f4-8780-7b075d89507b'), None, 4900, 'INR', None, None, None, 'created', None, '9874563210', '')
2026-07-22 14:59:23,831 | INFO     | sqlalchemy.engine.Engine | [generated in 0.00030s] (UUID('6cb19b69-f01c-439a-b58c-e31c11d4dce6'), 'matching', None, UUID('d19a985c-3f36-48f4-8780-7b075d89507b'), None, 4900, 'INR', None, None, None, 'created', None, '9874563210', '')
2026-07-22 14:59:24,232 | DEBUG    | urllib3.connectionpool | Starting new HTTPS connection (1): api.razorpay.com:443
2026-07-22 14:59:25,079 | DEBUG    | urllib3.connectionpool | https://api.razorpay.com:443 "POST /v1/orders HTTP/1.1" 200 221
2026-07-22 14:59:25,081 INFO sqlalchemy.engine.Engine UPDATE orders SET razorpay_order_id=$1::VARCHAR WHERE orders.id = $2::UUID
2026-07-22 14:59:25,081 | INFO     | sqlalchemy.engine.Engine | UPDATE orders SET razorpay_order_id=$1::VARCHAR WHERE orders.id = $2::UUID
2026-07-22 14:59:25,081 INFO sqlalchemy.engine.Engine [generated in 0.00023s] ('order_TGadLus0NZCfwE', UUID('6cb19b69-f01c-439a-b58c-e31c11d4dce6'))
2026-07-22 14:59:25,081 | INFO     | sqlalchemy.engine.Engine | [generated in 0.00023s] ('order_TGadLus0NZCfwE', UUID('6cb19b69-f01c-439a-b58c-e31c11d4dce6'))
2026-07-22 14:59:25,226 INFO sqlalchemy.engine.Engine COMMIT
2026-07-22 14:59:25,226 | INFO     | sqlalchemy.engine.Engine | COMMIT
INFO:     10.25.169.129:0 - "POST /api/v1/orders HTTP/1.1" 201 Created
INFO:     10.31.107.4:0 - "OPTIONS /api/v1/orders/verify HTTP/1.1" 200 OK
2026-07-22 14:59:50,063 INFO sqlalchemy.engine.Engine BEGIN (implicit)
2026-07-22 14:59:50,063 | INFO     | sqlalchemy.engine.Engine | BEGIN (implicit)
2026-07-22 14:59:50,065 INFO sqlalchemy.engine.Engine SELECT orders.id, orders.product_type, orders.kundali_id, orders.matching_id, orders.biodata_id, orders.amount_paise, orders.currency, orders.razorpay_order_id, orders.razorpay_payment_id, orders.razorpay_signature, orders.status, orders.paid_at, orders.created_at, orders.customer_phone, orders.customer_email 
2026-07-22 14:59:50,065 | INFO     | sqlalchemy.engine.Engine | SELECT orders.id, orders.product_type, orders.kundali_id, orders.matching_id, orders.biodata_id, orders.amount_paise, orders.currency, orders.razorpay_order_id, orders.razorpay_payment_id, orders.razorpay_signature, orders.status, orders.paid_at, orders.created_at, orders.customer_phone, orders.customer_email 
FROM orders 
WHERE orders.razorpay_order_id = $1::VARCHAR
FROM orders 
WHERE orders.razorpay_order_id = $1::VARCHAR
2026-07-22 14:59:50,065 | INFO     | sqlalchemy.engine.Engine | [generated in 0.00019s] ('order_TGadLus0NZCfwE',)
2026-07-22 14:59:50,065 INFO sqlalchemy.engine.Engine [generated in 0.00019s] ('order_TGadLus0NZCfwE',)
2026-07-22 14:59:50,278 INFO sqlalchemy.engine.Engine UPDATE orders SET razorpay_order_id=$1::VARCHAR, razorpay_payment_id=$2::VARCHAR, razorpay_signature=$3::VARCHAR, status=$4::order_status_enum, paid_at=$5::TIMESTAMP WITHOUT TIME ZONE WHERE orders.id = $6::UUID
2026-07-22 14:59:50,278 | INFO     | sqlalchemy.engine.Engine | UPDATE orders SET razorpay_order_id=$1::VARCHAR, razorpay_payment_id=$2::VARCHAR, razorpay_signature=$3::VARCHAR, status=$4::order_status_enum, paid_at=$5::TIMESTAMP WITHOUT TIME ZONE WHERE orders.id = $6::UUID
2026-07-22 14:59:50,278 INFO sqlalchemy.engine.Engine [generated in 0.00026s] ('order_TGadLus0NZCfwE', 'pay_TGadSeBGgt1c8l', '850c95e822f94042d140da8174fc5646e3ad7401554f04a394a26b3f25f5ea3d', 'paid', datetime.datetime(2026, 7, 22, 14, 59, 50, 277391), UUID('6cb19b69-f01c-439a-b58c-e31c11d4dce6'))
2026-07-22 14:59:50,278 | INFO     | sqlalchemy.engine.Engine | [generated in 0.00026s] ('order_TGadLus0NZCfwE', 'pay_TGadSeBGgt1c8l', '850c95e822f94042d140da8174fc5646e3ad7401554f04a394a26b3f25f5ea3d', 'paid', datetime.datetime(2026, 7, 22, 14, 59, 50, 277391), UUID('6cb19b69-f01c-439a-b58c-e31c11d4dce6'))
2026-07-22 14:59:50,420 | INFO     | sqlalchemy.engine.Engine | SELECT matchings.id, matchings.bride_kundali_id, matchings.groom_kundali_id, matchings.bride_birth_profile_id, matchings.groom_birth_profile_id, matchings.total_score, matchings.total_max, matchings.bride_manglik, matchings.groom_manglik, matchings.bride_manglik_severity, matchings.groom_manglik_severity, matchings.paid, matchings.koota_breakdown, matchings.dosha_analysis, matchings.verdict_mr, matchings.verdict_en, matchings.pdf_url, matchings.resume_token, matchings.paid_at, matchings.created_at, matchings.expires_at 
FROM matchings 
2026-07-22 14:59:50,420 INFO sqlalchemy.engine.Engine SELECT matchings.id, matchings.bride_kundali_id, matchings.groom_kundali_id, matchings.bride_birth_profile_id, matchings.groom_birth_profile_id, matchings.total_score, matchings.total_max, matchings.bride_manglik, matchings.groom_manglik, matchings.bride_manglik_severity, matchings.groom_manglik_severity, matchings.paid, matchings.koota_breakdown, matchings.dosha_analysis, matchings.verdict_mr, matchings.verdict_en, matchings.pdf_url, matchings.resume_token, matchings.paid_at, matchings.created_at, matchings.expires_at 
WHERE matchings.id = $1::UUID
FROM matchings 
WHERE matchings.id = $1::UUID
2026-07-22 14:59:50,420 INFO sqlalchemy.engine.Engine [cached since 36.02s ago] (UUID('d19a985c-3f36-48f4-8780-7b075d89507b'),)
2026-07-22 14:59:50,420 | INFO     | sqlalchemy.engine.Engine | [cached since 36.02s ago] (UUID('d19a985c-3f36-48f4-8780-7b075d89507b'),)
2026-07-22 14:59:50,654 | INFO     | sqlalchemy.engine.Engine | SELECT birth_profiles.id AS birth_profiles_id, birth_profiles.name AS birth_profiles_name, birth_profiles.gender AS birth_profiles_gender, birth_profiles.dob AS birth_profiles_dob, birth_profiles.time_of_birth AS birth_profiles_time_of_birth, birth_profiles.time_accuracy AS birth_profiles_time_accuracy, birth_profiles.place_text AS birth_profiles_place_text, birth_profiles.latitude AS birth_profiles_latitude, birth_profiles.longitude AS birth_profiles_longitude, birth_profiles.tz_iana AS birth_profiles_tz_iana, birth_profiles.rahu_mode AS birth_profiles_rahu_mode, birth_profiles.created_at AS birth_profiles_created_at 
2026-07-22 14:59:50,654 INFO sqlalchemy.engine.Engine SELECT birth_profiles.id AS birth_profiles_id, birth_profiles.name AS birth_profiles_name, birth_profiles.gender AS birth_profiles_gender, birth_profiles.dob AS birth_profiles_dob, birth_profiles.time_of_birth AS birth_profiles_time_of_birth, birth_profiles.time_accuracy AS birth_profiles_time_accuracy, birth_profiles.place_text AS birth_profiles_place_text, birth_profiles.latitude AS birth_profiles_latitude, birth_profiles.longitude AS birth_profiles_longitude, birth_profiles.tz_iana AS birth_profiles_tz_iana, birth_profiles.rahu_mode AS birth_profiles_rahu_mode, birth_profiles.created_at AS birth_profiles_created_at 
FROM birth_profiles 
WHERE birth_profiles.id IN ($1::UUID)
2026-07-22 14:59:50,654 | INFO     | sqlalchemy.engine.Engine | [cached since 35.97s ago] (UUID('32b1d29a-50c4-44d8-afd8-5169dd45b25f'),)
FROM birth_profiles 
WHERE birth_profiles.id IN ($1::UUID)
2026-07-22 14:59:50,654 INFO sqlalchemy.engine.Engine [cached since 35.97s ago] (UUID('32b1d29a-50c4-44d8-afd8-5169dd45b25f'),)
2026-07-22 14:59:50,741 INFO sqlalchemy.engine.Engine SELECT birth_profiles.id AS birth_profiles_id, birth_profiles.name AS birth_profiles_name, birth_profiles.gender AS birth_profiles_gender, birth_profiles.dob AS birth_profiles_dob, birth_profiles.time_of_birth AS birth_profiles_time_of_birth, birth_profiles.time_accuracy AS birth_profiles_time_accuracy, birth_profiles.place_text AS birth_profiles_place_text, birth_profiles.latitude AS birth_profiles_latitude, birth_profiles.longitude AS birth_profiles_longitude, birth_profiles.tz_iana AS birth_profiles_tz_iana, birth_profiles.rahu_mode AS birth_profiles_rahu_mode, birth_profiles.created_at AS birth_profiles_created_at 
2026-07-22 14:59:50,741 | INFO     | sqlalchemy.engine.Engine | SELECT birth_profiles.id AS birth_profiles_id, birth_profiles.name AS birth_profiles_name, birth_profiles.gender AS birth_profiles_gender, birth_profiles.dob AS birth_profiles_dob, birth_profiles.time_of_birth AS birth_profiles_time_of_birth, birth_profiles.time_accuracy AS birth_profiles_time_accuracy, birth_profiles.place_text AS birth_profiles_place_text, birth_profiles.latitude AS birth_profiles_latitude, birth_profiles.longitude AS birth_profiles_longitude, birth_profiles.tz_iana AS birth_profiles_tz_iana, birth_profiles.rahu_mode AS birth_profiles_rahu_mode, birth_profiles.created_at AS birth_profiles_created_at 
FROM birth_profiles 
WHERE birth_profiles.id IN ($1::UUID)
2026-07-22 14:59:50,741 INFO sqlalchemy.engine.Engine [cached since 35.91s ago] (UUID('5b739c34-fa70-4cf7-aff6-b6d0bb174202'),)
FROM birth_profiles 
WHERE birth_profiles.id IN ($1::UUID)
2026-07-22 14:59:50,741 | INFO     | sqlalchemy.engine.Engine | [cached since 35.91s ago] (UUID('5b739c34-fa70-4cf7-aff6-b6d0bb174202'),)
2026-07-22 14:59:50,812 | INFO     | sqlalchemy.engine.Engine | UPDATE matchings SET paid=$1::BOOLEAN, paid_at=$2::TIMESTAMP WITHOUT TIME ZONE, expires_at=$3::TIMESTAMP WITHOUT TIME ZONE WHERE matchings.id = $4::UUID
2026-07-22 14:59:50,812 INFO sqlalchemy.engine.Engine UPDATE matchings SET paid=$1::BOOLEAN, paid_at=$2::TIMESTAMP WITHOUT TIME ZONE, expires_at=$3::TIMESTAMP WITHOUT TIME ZONE WHERE matchings.id = $4::UUID
2026-07-22 14:59:50,812 | INFO     | sqlalchemy.engine.Engine | [generated in 0.00021s] (True, datetime.datetime(2026, 7, 22, 14, 59, 50, 811414), datetime.datetime(2028, 7, 21, 14, 59, 50, 811467), UUID('d19a985c-3f36-48f4-8780-7b075d89507b'))
2026-07-22 14:59:50,812 INFO sqlalchemy.engine.Engine [generated in 0.00021s] (True, datetime.datetime(2026, 7, 22, 14, 59, 50, 811414), datetime.datetime(2028, 7, 21, 14, 59, 50, 811467), UUID('d19a985c-3f36-48f4-8780-7b075d89507b'))
2026-07-22 14:59:50,952 | INFO     | api.routers.orders | Payment verified & unlocked: order=6cb19b69-f01c-439a-b58c-e31c11d4dce6 payment=pay_TGadSeBGgt1c8l
2026-07-22 14:59:50,952 | INFO     | sqlalchemy.engine.Engine | COMMIT
2026-07-22 14:59:50,952 INFO sqlalchemy.engine.Engine COMMIT
INFO:     10.31.107.4:0 - "POST /api/v1/orders/verify HTTP/1.1" 200 OK
2026-07-22 14:59:52,429 | INFO     | sqlalchemy.engine.Engine | BEGIN (implicit)
2026-07-22 14:59:52,429 INFO sqlalchemy.engine.Engine BEGIN (implicit)
2026-07-22 14:59:52,429 INFO sqlalchemy.engine.Engine SELECT matchings.id, matchings.bride_kundali_id, matchings.groom_kundali_id, matchings.bride_birth_profile_id, matchings.groom_birth_profile_id, matchings.total_score, matchings.total_max, matchings.bride_manglik, matchings.groom_manglik, matchings.bride_manglik_severity, matchings.groom_manglik_severity, matchings.paid, matchings.koota_breakdown, matchings.dosha_analysis, matchings.verdict_mr, matchings.verdict_en, matchings.pdf_url, matchings.resume_token, matchings.paid_at, matchings.created_at, matchings.expires_at 
FROM matchings 
WHERE matchings.id = $1::UUID
2026-07-22 14:59:52,429 | INFO     | sqlalchemy.engine.Engine | SELECT matchings.id, matchings.bride_kundali_id, matchings.groom_kundali_id, matchings.bride_birth_profile_id, matchings.groom_birth_profile_id, matchings.total_score, matchings.total_max, matchings.bride_manglik, matchings.groom_manglik, matchings.bride_manglik_severity, matchings.groom_manglik_severity, matchings.paid, matchings.koota_breakdown, matchings.dosha_analysis, matchings.verdict_mr, matchings.verdict_en, matchings.pdf_url, matchings.resume_token, matchings.paid_at, matchings.created_at, matchings.expires_at 
FROM matchings 
WHERE matchings.id = $1::UUID
2026-07-22 14:59:52,429 | INFO     | sqlalchemy.engine.Engine | [cached since 38.03s ago] (UUID('d19a985c-3f36-48f4-8780-7b075d89507b'),)
2026-07-22 14:59:52,429 INFO sqlalchemy.engine.Engine [cached since 38.03s ago] (UUID('d19a985c-3f36-48f4-8780-7b075d89507b'),)
2026-07-22 14:59:52,579 INFO sqlalchemy.engine.Engine SELECT birth_profiles.id AS birth_profiles_id, birth_profiles.name AS birth_profiles_name, birth_profiles.gender AS birth_profiles_gender, birth_profiles.dob AS birth_profiles_dob, birth_profiles.time_of_birth AS birth_profiles_time_of_birth, birth_profiles.time_accuracy AS birth_profiles_time_accuracy, birth_profiles.place_text AS birth_profiles_place_text, birth_profiles.latitude AS birth_profiles_latitude, birth_profiles.longitude AS birth_profiles_longitude, birth_profiles.tz_iana AS birth_profiles_tz_iana, birth_profiles.rahu_mode AS birth_profiles_rahu_mode, birth_profiles.created_at AS birth_profiles_created_at 
2026-07-22 14:59:52,579 | INFO     | sqlalchemy.engine.Engine | SELECT birth_profiles.id AS birth_profiles_id, birth_profiles.name AS birth_profiles_name, birth_profiles.gender AS birth_profiles_gender, birth_profiles.dob AS birth_profiles_dob, birth_profiles.time_of_birth AS birth_profiles_time_of_birth, birth_profiles.time_accuracy AS birth_profiles_time_accuracy, birth_profiles.place_text AS birth_profiles_place_text, birth_profiles.latitude AS birth_profiles_latitude, birth_profiles.longitude AS birth_profiles_longitude, birth_profiles.tz_iana AS birth_profiles_tz_iana, birth_profiles.rahu_mode AS birth_profiles_rahu_mode, birth_profiles.created_at AS birth_profiles_created_at 
FROM birth_profiles 
WHERE birth_profiles.id IN ($1::UUID)
2026-07-22 14:59:52,580 INFO sqlalchemy.engine.Engine [cached since 37.89s ago] (UUID('32b1d29a-50c4-44d8-afd8-5169dd45b25f'),)
FROM birth_profiles 
WHERE birth_profiles.id IN ($1::UUID)
2026-07-22 14:59:52,580 | INFO     | sqlalchemy.engine.Engine | [cached since 37.89s ago] (UUID('32b1d29a-50c4-44d8-afd8-5169dd45b25f'),)
2026-07-22 14:59:52,650 | INFO     | sqlalchemy.engine.Engine | SELECT birth_profiles.id AS birth_profiles_id, birth_profiles.name AS birth_profiles_name, birth_profiles.gender AS birth_profiles_gender, birth_profiles.dob AS birth_profiles_dob, birth_profiles.time_of_birth AS birth_profiles_time_of_birth, birth_profiles.time_accuracy AS birth_profiles_time_accuracy, birth_profiles.place_text AS birth_profiles_place_text, birth_profiles.latitude AS birth_profiles_latitude, birth_profiles.longitude AS birth_profiles_longitude, birth_profiles.tz_iana AS birth_profiles_tz_iana, birth_profiles.rahu_mode AS birth_profiles_rahu_mode, birth_profiles.created_at AS birth_profiles_created_at 
2026-07-22 14:59:52,650 INFO sqlalchemy.engine.Engine SELECT birth_profiles.id AS birth_profiles_id, birth_profiles.name AS birth_profiles_name, birth_profiles.gender AS birth_profiles_gender, birth_profiles.dob AS birth_profiles_dob, birth_profiles.time_of_birth AS birth_profiles_time_of_birth, birth_profiles.time_accuracy AS birth_profiles_time_accuracy, birth_profiles.place_text AS birth_profiles_place_text, birth_profiles.latitude AS birth_profiles_latitude, birth_profiles.longitude AS birth_profiles_longitude, birth_profiles.tz_iana AS birth_profiles_tz_iana, birth_profiles.rahu_mode AS birth_profiles_rahu_mode, birth_profiles.created_at AS birth_profiles_created_at 
FROM birth_profiles 
WHERE birth_profiles.id IN ($1::UUID)
FROM birth_profiles 
WHERE birth_profiles.id IN ($1::UUID)
2026-07-22 14:59:52,651 | INFO     | sqlalchemy.engine.Engine | [cached since 37.82s ago] (UUID('5b739c34-fa70-4cf7-aff6-b6d0bb174202'),)
2026-07-22 14:59:52,651 INFO sqlalchemy.engine.Engine [cached since 37.82s ago] (UUID('5b739c34-fa70-4cf7-aff6-b6d0bb174202'),)
2026-07-22 14:59:52,721 | INFO     | engine.chart | Computing kundali for Sonali, DOB=1994-02-05, Time=15:05:00, Place=Satara, Maharashtra, India (Asia/Kolkata)
2026-07-22 14:59:52,722 | WARNING  | engine.geocoding | Unknown IANA timezone: Asia/Kolkata, falling back to UTC+5:30
2026-07-22 14:59:52,722 | INFO     | engine.ephemeris | Swiss Ephemeris initialized with path: ./static/ephemeris
2026-07-22 14:59:52,723 | DEBUG    | engine.ephemeris | Ephemeris computed: JD=2449388.8993, Ayanamsa=23.7746°, Lagna=67.3982° sidereal
2026-07-22 14:59:52,723 | DEBUG    | engine.dasha | Dasha balance: nakshatra=Jyeshtha, lord=Mercury, fraction_remaining=0.8235, balance=5113.5 days
2026-07-22 14:59:52,723 | DEBUG    | engine.dasha | Current Dasha: Maha=Venus (2015-02-05 to 2035-02-05), Antara=Jupiter (2025-04-06 to 2027-12-06)
2026-07-22 14:59:52,723 | INFO     | engine.chart | Computing kundali for Suraj, DOB=1989-05-05, Time=13:55:00, Place=Satara, Maharashtra, India (Asia/Kolkata)
2026-07-22 14:59:52,723 | WARNING  | engine.geocoding | Unknown IANA timezone: Asia/Kolkata, falling back to UTC+5:30
2026-07-22 14:59:52,724 | INFO     | engine.ephemeris | Swiss Ephemeris initialized with path: ./static/ephemeris
2026-07-22 14:59:52,724 | DEBUG    | engine.ephemeris | Ephemeris computed: JD=2447651.8507, Ayanamsa=23.7082°, Lagna=131.2999° sidereal
2026-07-22 14:59:52,724 | DEBUG    | engine.dasha | Dasha balance: nakshatra=Bharani, lord=Venus, fraction_remaining=0.5638, balance=4118.8 days
2026-07-22 14:59:52,724 | DEBUG    | engine.dasha | Current Dasha: Maha=Rahu (2023-08-14 to 2041-08-14), Antara=Jupiter (2026-04-26 to 2028-09-19)
2026-07-22 14:59:52,729 | INFO     | sqlalchemy.engine.Engine | COMMIT
2026-07-22 14:59:52,729 INFO sqlalchemy.engine.Engine COMMIT
INFO:     10.31.107.4:0 - "GET /api/v1/matchings/d19a985c-3f36-48f4-8780-7b075d89507b HTTP/1.1" 200 OK
2026-07-22 15:00:22,102 INFO sqlalchemy.engine.Engine BEGIN (implicit)
2026-07-22 15:00:22,102 | INFO     | sqlalchemy.engine.Engine | BEGIN (implicit)
2026-07-22 15:00:22,102 INFO sqlalchemy.engine.Engine SELECT matchings.id, matchings.bride_kundali_id, matchings.groom_kundali_id, matchings.bride_birth_profile_id, matchings.groom_birth_profile_id, matchings.total_score, matchings.total_max, matchings.bride_manglik, matchings.groom_manglik, matchings.bride_manglik_severity, matchings.groom_manglik_severity, matchings.paid, matchings.koota_breakdown, matchings.dosha_analysis, matchings.verdict_mr, matchings.verdict_en, matchings.pdf_url, matchings.resume_token, matchings.paid_at, matchings.created_at, matchings.expires_at 
FROM matchings 
2026-07-22 15:00:22,102 | INFO     | sqlalchemy.engine.Engine | SELECT matchings.id, matchings.bride_kundali_id, matchings.groom_kundali_id, matchings.bride_birth_profile_id, matchings.groom_birth_profile_id, matchings.total_score, matchings.total_max, matchings.bride_manglik, matchings.groom_manglik, matchings.bride_manglik_severity, matchings.groom_manglik_severity, matchings.paid, matchings.koota_breakdown, matchings.dosha_analysis, matchings.verdict_mr, matchings.verdict_en, matchings.pdf_url, matchings.resume_token, matchings.paid_at, matchings.created_at, matchings.expires_at 
WHERE matchings.id = $1::UUID
FROM matchings 
WHERE matchings.id = $1::UUID
2026-07-22 15:00:22,103 | INFO     | sqlalchemy.engine.Engine | [cached since 67.71s ago] (UUID('d19a985c-3f36-48f4-8780-7b075d89507b'),)
2026-07-22 15:00:22,103 INFO sqlalchemy.engine.Engine [cached since 67.71s ago] (UUID('d19a985c-3f36-48f4-8780-7b075d89507b'),)
2026-07-22 15:00:22,243 | INFO     | sqlalchemy.engine.Engine | SELECT birth_profiles.id AS birth_profiles_id, birth_profiles.name AS birth_profiles_name, birth_profiles.gender AS birth_profiles_gender, birth_profiles.dob AS birth_profiles_dob, birth_profiles.time_of_birth AS birth_profiles_time_of_birth, birth_profiles.time_accuracy AS birth_profiles_time_accuracy, birth_profiles.place_text AS birth_profiles_place_text, birth_profiles.latitude AS birth_profiles_latitude, birth_profiles.longitude AS birth_profiles_longitude, birth_profiles.tz_iana AS birth_profiles_tz_iana, birth_profiles.rahu_mode AS birth_profiles_rahu_mode, birth_profiles.created_at AS birth_profiles_created_at 
2026-07-22 15:00:22,243 INFO sqlalchemy.engine.Engine SELECT birth_profiles.id AS birth_profiles_id, birth_profiles.name AS birth_profiles_name, birth_profiles.gender AS birth_profiles_gender, birth_profiles.dob AS birth_profiles_dob, birth_profiles.time_of_birth AS birth_profiles_time_of_birth, birth_profiles.time_accuracy AS birth_profiles_time_accuracy, birth_profiles.place_text AS birth_profiles_place_text, birth_profiles.latitude AS birth_profiles_latitude, birth_profiles.longitude AS birth_profiles_longitude, birth_profiles.tz_iana AS birth_profiles_tz_iana, birth_profiles.rahu_mode AS birth_profiles_rahu_mode, birth_profiles.created_at AS birth_profiles_created_at 
FROM birth_profiles 
WHERE birth_profiles.id IN ($1::UUID)
FROM birth_profiles 
WHERE birth_profiles.id IN ($1::UUID)
2026-07-22 15:00:22,243 | INFO     | sqlalchemy.engine.Engine | [cached since 67.56s ago] (UUID('32b1d29a-50c4-44d8-afd8-5169dd45b25f'),)
2026-07-22 15:00:22,243 INFO sqlalchemy.engine.Engine [cached since 67.56s ago] (UUID('32b1d29a-50c4-44d8-afd8-5169dd45b25f'),)
2026-07-22 15:00:22,314 | INFO     | sqlalchemy.engine.Engine | SELECT birth_profiles.id AS birth_profiles_id, birth_profiles.name AS birth_profiles_name, birth_profiles.gender AS birth_profiles_gender, birth_profiles.dob AS birth_profiles_dob, birth_profiles.time_of_birth AS birth_profiles_time_of_birth, birth_profiles.time_accuracy AS birth_profiles_time_accuracy, birth_profiles.place_text AS birth_profiles_place_text, birth_profiles.latitude AS birth_profiles_latitude, birth_profiles.longitude AS birth_profiles_longitude, birth_profiles.tz_iana AS birth_profiles_tz_iana, birth_profiles.rahu_mode AS birth_profiles_rahu_mode, birth_profiles.created_at AS birth_profiles_created_at 
2026-07-22 15:00:22,314 INFO sqlalchemy.engine.Engine SELECT birth_profiles.id AS birth_profiles_id, birth_profiles.name AS birth_profiles_name, birth_profiles.gender AS birth_profiles_gender, birth_profiles.dob AS birth_profiles_dob, birth_profiles.time_of_birth AS birth_profiles_time_of_birth, birth_profiles.time_accuracy AS birth_profiles_time_accuracy, birth_profiles.place_text AS birth_profiles_place_text, birth_profiles.latitude AS birth_profiles_latitude, birth_profiles.longitude AS birth_profiles_longitude, birth_profiles.tz_iana AS birth_profiles_tz_iana, birth_profiles.rahu_mode AS birth_profiles_rahu_mode, birth_profiles.created_at AS birth_profiles_created_at 
FROM birth_profiles 
WHERE birth_profiles.id IN ($1::UUID)
FROM birth_profiles 
WHERE birth_profiles.id IN ($1::UUID)
2026-07-22 15:00:22,314 INFO sqlalchemy.engine.Engine [cached since 67.49s ago] (UUID('5b739c34-fa70-4cf7-aff6-b6d0bb174202'),)
2026-07-22 15:00:22,314 | INFO     | sqlalchemy.engine.Engine | [cached since 67.49s ago] (UUID('5b739c34-fa70-4cf7-aff6-b6d0bb174202'),)
2026-07-22 15:00:22,385 | INFO     | engine.chart | Computing kundali for Sonali, DOB=1994-02-05, Time=15:05:00, Place=Satara, Maharashtra, India (Asia/Kolkata)
2026-07-22 15:00:22,386 | WARNING  | engine.geocoding | Unknown IANA timezone: Asia/Kolkata, falling back to UTC+5:30
2026-07-22 15:00:22,386 | INFO     | engine.ephemeris | Swiss Ephemeris initialized with path: ./static/ephemeris
2026-07-22 15:00:22,386 | DEBUG    | engine.ephemeris | Ephemeris computed: JD=2449388.8993, Ayanamsa=23.7746°, Lagna=67.3982° sidereal
2026-07-22 15:00:22,386 | DEBUG    | engine.dasha | Dasha balance: nakshatra=Jyeshtha, lord=Mercury, fraction_remaining=0.8235, balance=5113.5 days
2026-07-22 15:00:22,386 | DEBUG    | engine.dasha | Current Dasha: Maha=Venus (2015-02-05 to 2035-02-05), Antara=Jupiter (2025-04-06 to 2027-12-06)
2026-07-22 15:00:22,386 | INFO     | engine.chart | Computing kundali for Suraj, DOB=1989-05-05, Time=13:55:00, Place=Satara, Maharashtra, India (Asia/Kolkata)
2026-07-22 15:00:22,387 | WARNING  | engine.geocoding | Unknown IANA timezone: Asia/Kolkata, falling back to UTC+5:30
2026-07-22 15:00:22,387 | INFO     | engine.ephemeris | Swiss Ephemeris initialized with path: ./static/ephemeris
2026-07-22 15:00:22,387 | DEBUG    | engine.ephemeris | Ephemeris computed: JD=2447651.8507, Ayanamsa=23.7082°, Lagna=131.2999° sidereal
2026-07-22 15:00:22,388 | DEBUG    | engine.dasha | Dasha balance: nakshatra=Bharani, lord=Venus, fraction_remaining=0.5638, balance=4118.8 days
2026-07-22 15:00:22,388 | DEBUG    | engine.dasha | Current Dasha: Maha=Rahu (2023-08-14 to 2041-08-14), Antara=Jupiter (2026-04-26 to 2028-09-19)
2026-07-22 15:00:34,242 | INFO     | sqlalchemy.engine.Engine | COMMIT
2026-07-22 15:00:34,242 INFO sqlalchemy.engine.Engine COMMIT
INFO:     10.25.169.129:0 - "GET /api/v1/matchings/d19a985c-3f36-48f4-8780-7b075d89507b/pdf HTTP/1.1" 200 OK