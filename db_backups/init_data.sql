--
-- PostgreSQL database dump
--

-- Dumped from database version 14.15
-- Dumped by pg_dump version 14.15

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: angel
--

COPY public.alembic_version (version_num) FROM stdin;
b186523e1e25
\.


--
-- Data for Name: ammunition; Type: TABLE DATA; Schema: public; Owner: angel
--

COPY public.ammunition (id, name, brand, caliber, ammo_type, grain_weight, velocity, description, price_per_round, is_active, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: exercise_types; Type: TABLE DATA; Schema: public; Owner: angel
--

COPY public.exercise_types (id, name, description, difficulty, objective, development, is_active, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: angel
--

COPY public.users (id, email, hashed_password, role, is_active, created_at, updated_at) FROM stdin;
b15f2ca5-fc34-4dd9-a3f2-ab20ef5adb4e	Dorothea.Blick@gmail.com	$2b$12$1hFYoiKnJHlwA7jUxSOS9eIskgWnk2m6MkDsPaI68W4USwtU9bbNq	TIRADOR	t	2025-04-17 05:45:23.45775+00	\N
d085ac34-cf29-4e29-8073-3706f33bd9ce	Dillon41@yahoo.com	$2b$12$bUtW3OV.W/E70Mh4cNpr1ewaNCFMQI3LOuZd.lGDZF0bH8VW/PqTq	TIRADOR	t	2025-04-17 05:45:24.335909+00	\N
c9ec8ee3-a3a2-4ffa-baf5-3118f7c1aeb9	Oma27@gmail.com	$2b$12$B6ESJDRrVO.9EszAS59Q2eA8UEQEETVt2EBzHZsdghJIvws/waRDi	TIRADOR	t	2025-04-17 05:45:25.194526+00	\N
166cf21c-36a1-48f6-89dc-2039a3b0b830	Kenya_Kling85@yahoo.com	$2b$12$mIAxDa.fEL0oBMoPLMon5OEvcrBQz1eCeKnR9vn66k09yGv0Zigk6	TIRADOR	t	2025-04-17 05:45:25.971196+00	\N
efbb5904-76b3-40a2-9d69-6fd6341dbd1c	Ena.Adams45@gmail.com	$2b$12$O.5AulH/HS4.HZnZUi5tSuvhfM0BKeGn7nYPUcwcF3oTEQXmmjdI.	TIRADOR	t	2025-04-17 05:45:26.665704+00	\N
05a61ec7-f03f-4355-bbb7-8a457507032a	Israel.Towne@gmail.com	$2b$12$7sIpEyU327b8wQBUtR3r4.Hm8ej/mAPrmXW8dym3dlbYExq405vVu	TIRADOR	t	2025-04-17 05:45:27.366691+00	\N
7f339557-2f6a-49e1-980d-5b617ab0c14d	Lori.Spinka@hotmail.com	$2b$12$HqYNrUD7CAsvctq9MYyAxufvBvwZcYXfUWRmfFOMNQkIA2Rsw..By	TIRADOR	t	2025-04-17 05:45:28.043699+00	\N
70df5cc6-16ce-4970-bc3c-704f68182d76	Sheridan.Lowe@yahoo.com	$2b$12$MMrczQMSe2zxvA3tf2Wn0Ou3XF.lX/EaHbAunRMPOeUP7Q2ZTcNaq	TIRADOR	t	2025-04-17 05:45:28.66806+00	\N
4b793194-7331-418e-aa99-81e5048fb43f	Brooks_Harris60@yahoo.com	$2b$12$sUfdz83Wk3hvYzkhFBhmWuS342vXRK2y1fKiBC9sU.0xfFLLlzP0i	TIRADOR	t	2025-04-17 05:45:29.286383+00	\N
98c625c7-e253-4a11-928d-591f9d7aeb3d	Mariam43@hotmail.com	$2b$12$VQaf.CVx6geEGVgwdOlaNuUwNlmdiUseFZsjg.1wdAeY9AMqs.wNC	TIRADOR	t	2025-04-17 05:45:29.876596+00	\N
330e9640-bc50-410f-a6a5-2a30b0c9e012	Melody_Quitzon@hotmail.com	$2b$12$CW/vUHXqJtp1guhhkBoh5ewr8kIxoNdNt3Qa0PYNXAUZh5ToA3s.O	TIRADOR	t	2025-04-17 05:45:30.454675+00	\N
cd908e5e-ab7c-4ef8-b2d2-cec083c513b6	instructor@gmail.com	$2b$12$VbZMQx17l5ZO.wlxuTObqOOKfNfi1p57SLusJbulloOJPG3lunSe6	TIRADOR	t	2025-04-19 00:20:36.482791+00	\N
c06c19df-eb1a-4e45-8302-4666c7448d1e	rolando.admin@gmail.com	$2b$12$lw2zQ2//6OL5DliXskP9Mu8UMd6dULhsRHC8RU5CrfN4SWAqu9a6K	TIRADOR	t	2025-04-19 00:20:42.451919+00	\N
c58bc32b-a0c9-42fc-9c6b-870640695d8a	whoangel@gmail.com	$2b$12$xfC1l0eDJoG6j2toHnAOYe9iuTnchS8Vjx0EEYa3eL12w1brOyVby	TIRADOR	t	2025-04-19 00:20:46.267197+00	\N
8056ea85-5ccb-4719-907c-55f45d0139c4	roberto.santos@yahoo.com	$2b$12$vZ/6wX96ZPjlLN9BTrs81u7o.3f.0XQzyREi7iDZS2fr7QDXrJcdq	TIRADOR	t	2025-04-19 00:20:48.83205+00	\N
\.


--
-- Data for Name: shooting_clubs; Type: TABLE DATA; Schema: public; Owner: angel
--

COPY public.shooting_clubs (id, name, description, chief_instructor_id, is_active, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: shooters; Type: TABLE DATA; Schema: public; Owner: angel
--

COPY public.shooters (user_id, club_id, level, range, created_at, updated_at) FROM stdin;
b15f2ca5-fc34-4dd9-a3f2-ab20ef5adb4e	\N	REGULAR	\N	2025-04-17 05:45:23.45775+00	\N
d085ac34-cf29-4e29-8073-3706f33bd9ce	\N	REGULAR	\N	2025-04-17 05:45:24.335909+00	\N
c9ec8ee3-a3a2-4ffa-baf5-3118f7c1aeb9	\N	REGULAR	\N	2025-04-17 05:45:25.194526+00	\N
166cf21c-36a1-48f6-89dc-2039a3b0b830	\N	REGULAR	\N	2025-04-17 05:45:25.971196+00	\N
efbb5904-76b3-40a2-9d69-6fd6341dbd1c	\N	REGULAR	\N	2025-04-17 05:45:26.665704+00	\N
05a61ec7-f03f-4355-bbb7-8a457507032a	\N	REGULAR	\N	2025-04-17 05:45:27.366691+00	\N
7f339557-2f6a-49e1-980d-5b617ab0c14d	\N	REGULAR	\N	2025-04-17 05:45:28.043699+00	\N
70df5cc6-16ce-4970-bc3c-704f68182d76	\N	REGULAR	\N	2025-04-17 05:45:28.66806+00	\N
4b793194-7331-418e-aa99-81e5048fb43f	\N	REGULAR	\N	2025-04-17 05:45:29.286383+00	\N
98c625c7-e253-4a11-928d-591f9d7aeb3d	\N	REGULAR	\N	2025-04-17 05:45:29.876596+00	\N
330e9640-bc50-410f-a6a5-2a30b0c9e012	\N	REGULAR	\N	2025-04-17 05:45:30.454675+00	\N
cd908e5e-ab7c-4ef8-b2d2-cec083c513b6	\N	REGULAR	\N	2025-04-19 00:20:36.482791+00	\N
c06c19df-eb1a-4e45-8302-4666c7448d1e	\N	REGULAR	\N	2025-04-19 00:20:42.451919+00	\N
c58bc32b-a0c9-42fc-9c6b-870640695d8a	\N	REGULAR	\N	2025-04-19 00:20:46.267197+00	\N
8056ea85-5ccb-4719-907c-55f45d0139c4	\N	REGULAR	\N	2025-04-19 00:20:48.83205+00	\N
\.


--
-- Data for Name: individual_practice_sessions; Type: TABLE DATA; Schema: public; Owner: angel
--

COPY public.individual_practice_sessions (id, shooter_id, instructor_id, date, location, total_shots_fired, total_hits, accuracy_percentage, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: practice_evaluations; Type: TABLE DATA; Schema: public; Owner: angel
--

COPY public.practice_evaluations (id, session_id, evaluator_id, final_score, classification, strengths, weaknesses, recomendations, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: targets; Type: TABLE DATA; Schema: public; Owner: angel
--

COPY public.targets (id, name, target_type, description, scoring_zones, dimensions, distance_recommended, is_active, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: weapons; Type: TABLE DATA; Schema: public; Owner: angel
--

COPY public.weapons (id, name, brand, model, serial_number, weapon_type, caliber, description, is_active, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: practice_exercises; Type: TABLE DATA; Schema: public; Owner: angel
--

COPY public.practice_exercises (id, session_id, exercise_type_id, distance, firing_cadence, time_limit, ammunition_allocated, ammunition_used, hits, accuracy_percentage, reaction_time, created_at, updated_at, target_id, weapon_id, ammunition_id) FROM stdin;
\.


--
-- Data for Name: shooter_performance_logs; Type: TABLE DATA; Schema: public; Owner: angel
--

COPY public.shooter_performance_logs (id, shooter_id, metric_type, metric_value, context, notes, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: shooter_stats; Type: TABLE DATA; Schema: public; Owner: angel
--

COPY public.shooter_stats (shooter_id, total_shots, accuracy, reaction_shots, presicion_shots, draw_time_avg, reload_time_avg, average_hit_factor, effectiveness, common_error_zones, created_at, updated_at) FROM stdin;
b15f2ca5-fc34-4dd9-a3f2-ab20ef5adb4e	0	0	0	0	0	0	0	0	\N	2025-04-17 05:45:23.45775+00	\N
d085ac34-cf29-4e29-8073-3706f33bd9ce	0	0	0	0	0	0	0	0	\N	2025-04-17 05:45:24.335909+00	\N
c9ec8ee3-a3a2-4ffa-baf5-3118f7c1aeb9	0	0	0	0	0	0	0	0	\N	2025-04-17 05:45:25.194526+00	\N
166cf21c-36a1-48f6-89dc-2039a3b0b830	0	0	0	0	0	0	0	0	\N	2025-04-17 05:45:25.971196+00	\N
efbb5904-76b3-40a2-9d69-6fd6341dbd1c	0	0	0	0	0	0	0	0	\N	2025-04-17 05:45:26.665704+00	\N
05a61ec7-f03f-4355-bbb7-8a457507032a	0	0	0	0	0	0	0	0	\N	2025-04-17 05:45:27.366691+00	\N
7f339557-2f6a-49e1-980d-5b617ab0c14d	0	0	0	0	0	0	0	0	\N	2025-04-17 05:45:28.043699+00	\N
70df5cc6-16ce-4970-bc3c-704f68182d76	0	0	0	0	0	0	0	0	\N	2025-04-17 05:45:28.66806+00	\N
4b793194-7331-418e-aa99-81e5048fb43f	0	0	0	0	0	0	0	0	\N	2025-04-17 05:45:29.286383+00	\N
98c625c7-e253-4a11-928d-591f9d7aeb3d	0	0	0	0	0	0	0	0	\N	2025-04-17 05:45:29.876596+00	\N
330e9640-bc50-410f-a6a5-2a30b0c9e012	0	0	0	0	0	0	0	0	\N	2025-04-17 05:45:30.454675+00	\N
cd908e5e-ab7c-4ef8-b2d2-cec083c513b6	0	0	0	0	0	0	0	0	\N	2025-04-19 00:20:36.482791+00	\N
c06c19df-eb1a-4e45-8302-4666c7448d1e	0	0	0	0	0	0	0	0	\N	2025-04-19 00:20:42.451919+00	\N
c58bc32b-a0c9-42fc-9c6b-870640695d8a	0	0	0	0	0	0	0	0	\N	2025-04-19 00:20:46.267197+00	\N
8056ea85-5ccb-4719-907c-55f45d0139c4	0	0	0	0	0	0	0	0	\N	2025-04-19 00:20:48.83205+00	\N
\.


--
-- Data for Name: target_images; Type: TABLE DATA; Schema: public; Owner: angel
--

COPY public.target_images (id, exercise_id, file_path, file_size, content_type, uploaded_at, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: target_analyses; Type: TABLE DATA; Schema: public; Owner: angel
--

COPY public.target_analyses (id, target_image_id, analysis_timestamp, total_impacts_detected, zone_distribution, impact_coordinates, analysis_confidence, analysis_method, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: shooting_recommendations; Type: TABLE DATA; Schema: public; Owner: angel
--

COPY public.shooting_recommendations (id, analysis_id, primary_issue_zone, primary_issue_zone_description, secondary_issue_zone, secondary_issue_zone_description, recommended_exercises, recommendation_description, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: user_biometric_data; Type: TABLE DATA; Schema: public; Owner: angel
--

COPY public.user_biometric_data (user_id, height, weight, hand_dominance, eye_sight, time_sleep, blood_pressure, heart_rate, respiratory_rate, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: user_medical_data; Type: TABLE DATA; Schema: public; Owner: angel
--

COPY public.user_medical_data (user_id, blood_type, allergies, medical_conditions, emergency_contact, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: user_personal_data; Type: TABLE DATA; Schema: public; Owner: angel
--

COPY public.user_personal_data (user_id, first_name, second_name, last_name1, last_name2, phone_number, date_of_birth, city, state, country, created_at, updated_at) FROM stdin;
8056ea85-5ccb-4719-907c-55f45d0139c4	Lorna	Antonio	Gutmann	\N	792-717-3305	2001-11-29	Blaine	Oaxaca	ID	2025-04-19 00:21:11.140908+00	\N
\.


--
-- Data for Name: weapon_ammunition_compatibility; Type: TABLE DATA; Schema: public; Owner: angel
--

COPY public.weapon_ammunition_compatibility (id, weapon_id, ammunition_id, created_at) FROM stdin;
\.


--
-- PostgreSQL database dump complete
--

