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
31790490-7a2e-4fb6-8d9d-aeae84fc7c4d	SV Target .22 LR	SK	.22 LR	COMPETITION	40	1050	Munición de velocidad estándar optimizada para pistolas de competición, ofrece agrupaciones pequeñas a 25 metros. Para las pistolas de calibre .22 LR (Ruger Mark IV, Smith & Wesson SW22, Walther P22)	0.18	t	2025-04-21 21:25:47.75613+00	\N
e01cbc42-5229-435d-a397-38039e5f300e	Precision Hunter .22 LR	Eley	.22 LR	MATCH	40	1085	Munición de alta precisión para competiciones, fabricada con los más altos estándares de calidad y consistencia. Para las pistolas de calibre .22 LR (Ruger Mark IV, Smith & Wesson SW22, Walther P22)	0.25	t	2025-04-21 21:26:09.234394+00	\N
\.


--
-- Data for Name: exercise_types; Type: TABLE DATA; Schema: public; Owner: angel
--

COPY public.exercise_types (id, name, description, difficulty, objective, development, is_active, created_at, updated_at) FROM stdin;
dd68ff64-d5f7-4118-a11e-95060b886e44	EVALUACIÓN DE PRECISION LVL. 2	El tiro de precisión de reacción es una técnica que se utiliza para mejorar la rapidez y la precisión en el disparo. En este tipo de práctica, el tirador debe reaccionar rápidamente al blanco y disparar con precisión, lo que implica una combinación de velocidad y control.	3	 Identificar la capacidad y destreza del tirador enfrentando 3 objetivos en diferentes distancias, así como identificar su nivel de precisión en tiro de reacción.	 los tiradores se encontraran frente a sus blancos en poción relajada, brazos colgados y arma en la funda, a las orden del instructor de tiro abastecerá con un cargador de 6 cartuchos (sin cargar el arma), al sonido del shot timer desenfundaran su arma y efectuaran dos disparos en cada blanco que se encontraran en diferentes distancias 7, 15 y 20 metros	t	2025-04-21 21:14:06.810732+00	\N
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
8056ea85-5ccb-4719-907c-55f45d0139c4	roberto.santos@yahoo.com	$2b$12$vZ/6wX96ZPjlLN9BTrs81u7o.3f.0XQzyREi7iDZS2fr7QDXrJcdq	TIRADOR	t	2025-04-19 00:20:48.83205+00	\N
c06c19df-eb1a-4e45-8302-4666c7448d1e	rolando.admin@gmail.com	$2b$12$lw2zQ2//6OL5DliXskP9Mu8UMd6dULhsRHC8RU5CrfN4SWAqu9a6K	ADMIN	t	2025-04-19 00:20:42.451919+00	\N
cd908e5e-ab7c-4ef8-b2d2-cec083c513b6	instructor@gmail.com	$2b$12$VbZMQx17l5ZO.wlxuTObqOOKfNfi1p57SLusJbulloOJPG3lunSe6	INSTRUCTOR	t	2025-04-19 00:20:36.482791+00	2025-04-21 20:58:41.659111+00
c58bc32b-a0c9-42fc-9c6b-870640695d8a	whoangel@gmail.com	$2b$12$xfC1l0eDJoG6j2toHnAOYe9iuTnchS8Vjx0EEYa3eL12w1brOyVby	INSTRUCTOR_JEFE	t	2025-04-19 00:20:46.267197+00	2025-04-21 21:00:19.344713+00
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
15b01cd8-ec79-451b-b2a2-080297119765	8056ea85-5ccb-4719-907c-55f45d0139c4	cd908e5e-ab7c-4ef8-b2d2-cec083c513b6	2025-04-21 21:04:52.285418	No especificada	148	104	70.27027027027027	2025-04-21 21:04:52.283545+00	2025-04-22 02:48:48.006859+00
da0f10a3-b3d2-43d4-8615-68d29bf0564c	8056ea85-5ccb-4719-907c-55f45d0139c4	cd908e5e-ab7c-4ef8-b2d2-cec083c513b6	2025-04-22 00:27:13.02242	No especificada	223	165	73.99103139013454	2025-04-22 00:27:13.019051+00	2025-04-22 03:14:56.025476+00
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
105f37e4-878c-4e21-ba7e-bdbd61455857	Diana Olímpica	CONCENTRIC	Blanco oficial para competiciones olímpicas de tiro	{"rings": [{"radius": 5, "score": 10, "color": "black"}, {"radius": 10, "score": 9, "color": "black"}, {"radius": 15, "score": 8, "color": "black"}, {"radius": 20, "score": 7, "color": "white"}, {"radius": 25, "score": 6, "color": "white"}, {"radius": 30, "score": 5, "color": "white"}], "center": {"x": 0, "y": 0}}	40cm x 40cm	10	t	2025-04-21 21:22:17.455676+00	\N
ad59af6a-06c6-4077-97a5-80dda4de6308	Blanco IPSC Estándar	IPSC	Blanco estándar para competiciones IPSC	{"zones": [{"name": "A", "score": 5, "color": "brown", "bounds": {"min_x": -10, "max_x": 10, "min_y": -15, "max_y": 15}}, {"name": "C", "score": 3, "color": "brown", "bounds": {"min_x": -15, "max_x": 15, "min_y": -25, "max_y": 25}}, {"name": "D", "score": 1, "color": "brown", "bounds": {"min_x": -20, "max_x": 20, "min_y": -30, "max_y": 30}}], "penalty_zones": [{"name": "no-shoot", "penalty": -10, "color": "white", "bounds": {"min_x": 25, "max_x": 35, "min_y": -20, "max_y": 20}}], "shape": "silhouette"}	45cm x 75cm	15	t	2025-04-22 00:24:34.687205+00	\N
\.


--
-- Data for Name: weapons; Type: TABLE DATA; Schema: public; Owner: angel
--

COPY public.weapons (id, name, brand, model, serial_number, weapon_type, caliber, description, is_active, created_at, updated_at) FROM stdin;
58e5871e-14be-41eb-a14a-b268a5ee7be8	Pistola de Bolsillo .22 LR	Walther	P22	WAA00123	PISTOL	.22 LR	Pistola semiautomática compacta para defensa personal o práctica.	t	2025-04-21 21:23:57.899466+00	\N
32b466c7-59df-47a5-b613-ad7ac84a05c8	Pistola Compacta .22 LR	Smith & Wesson	SW22 Victory	22A1234	PISTOL	.22 LR	Pistola semiautomática ligera y personalizable.	t	2025-04-21 21:26:32.124411+00	\N
e0271254-653a-47da-921c-4fd09794d3ba	Pistola Estándar .22 LR	Ruger	Mark IV Target	401-23456	PISTOL	.22 LR	Pistola semiautomática de precisión para tiro al blanco.	t	2025-04-21 21:26:41.11168+00	\N
\.


--
-- Data for Name: practice_exercises; Type: TABLE DATA; Schema: public; Owner: angel
--

COPY public.practice_exercises (id, session_id, exercise_type_id, distance, firing_cadence, time_limit, ammunition_allocated, ammunition_used, hits, accuracy_percentage, reaction_time, created_at, updated_at, target_id, weapon_id, ammunition_id) FROM stdin;
5801487d-678e-4188-9b2c-a39446420c3e	15b01cd8-ec79-451b-b2a2-080297119765	dd68ff64-d5f7-4118-a11e-95060b886e44	10 metros	\N	\N	18	18	5	27.77777777777778	\N	2025-04-21 21:33:47.941103+00	\N	105f37e4-878c-4e21-ba7e-bdbd61455857	e0271254-653a-47da-921c-4fd09794d3ba	31790490-7a2e-4fb6-8d9d-aeae84fc7c4d
03c4359e-ba4b-4418-9495-2f90ff58129d	15b01cd8-ec79-451b-b2a2-080297119765	dd68ff64-d5f7-4118-a11e-95060b886e44	20 metros	\N	\N	30	30	24	80	\N	2025-04-22 00:24:00.65618+00	\N	105f37e4-878c-4e21-ba7e-bdbd61455857	e0271254-653a-47da-921c-4fd09794d3ba	31790490-7a2e-4fb6-8d9d-aeae84fc7c4d
0bcc0d06-a06c-4c27-80d1-dea73a4c82d5	15b01cd8-ec79-451b-b2a2-080297119765	dd68ff64-d5f7-4118-a11e-95060b886e44	20 metros	\N	\N	30	30	24	80	\N	2025-04-22 00:25:00.812464+00	\N	ad59af6a-06c6-4077-97a5-80dda4de6308	e0271254-653a-47da-921c-4fd09794d3ba	31790490-7a2e-4fb6-8d9d-aeae84fc7c4d
3773f939-98c5-44f5-9785-e15bf64474d1	15b01cd8-ec79-451b-b2a2-080297119765	dd68ff64-d5f7-4118-a11e-95060b886e44	20 metros	\N	\N	40	40	28	70	\N	2025-04-22 00:26:36.992785+00	\N	ad59af6a-06c6-4077-97a5-80dda4de6308	58e5871e-14be-41eb-a14a-b268a5ee7be8	31790490-7a2e-4fb6-8d9d-aeae84fc7c4d
528b3a74-11a2-4308-9831-e9f82722abc4	da0f10a3-b3d2-43d4-8615-68d29bf0564c	dd68ff64-d5f7-4118-a11e-95060b886e44	10 metros	\N	\N	30	29	10	34.48275862068966	\N	2025-04-22 00:30:20.263016+00	\N	ad59af6a-06c6-4077-97a5-80dda4de6308	58e5871e-14be-41eb-a14a-b268a5ee7be8	31790490-7a2e-4fb6-8d9d-aeae84fc7c4d
e5be3b8b-06b7-46d2-b423-fe1569a931fa	da0f10a3-b3d2-43d4-8615-68d29bf0564c	dd68ff64-d5f7-4118-a11e-95060b886e44	20 metros	\N	\N	40	29	10	34.48275862068966	\N	2025-04-22 00:30:51.914648+00	\N	ad59af6a-06c6-4077-97a5-80dda4de6308	58e5871e-14be-41eb-a14a-b268a5ee7be8	31790490-7a2e-4fb6-8d9d-aeae84fc7c4d
50717754-4819-445e-9b77-2b0d6cae96db	da0f10a3-b3d2-43d4-8615-68d29bf0564c	dd68ff64-d5f7-4118-a11e-95060b886e44	20 metros	\N	\N	16	16	15	93.75	\N	2025-04-22 00:31:08.532925+00	\N	ad59af6a-06c6-4077-97a5-80dda4de6308	58e5871e-14be-41eb-a14a-b268a5ee7be8	31790490-7a2e-4fb6-8d9d-aeae84fc7c4d
2aabef5a-cc39-4fba-907c-9a5361afc2b5	da0f10a3-b3d2-43d4-8615-68d29bf0564c	dd68ff64-d5f7-4118-a11e-95060b886e44	20 metros	\N	\N	20	16	15	93.75	\N	2025-04-22 00:38:22.254064+00	\N	ad59af6a-06c6-4077-97a5-80dda4de6308	58e5871e-14be-41eb-a14a-b268a5ee7be8	31790490-7a2e-4fb6-8d9d-aeae84fc7c4d
b43237f5-5e9e-4f07-84c0-3a400c60b389	da0f10a3-b3d2-43d4-8615-68d29bf0564c	dd68ff64-d5f7-4118-a11e-95060b886e44	5 metros	\N	\N	25	25	19	76	\N	2025-04-22 00:41:00.935181+00	\N	ad59af6a-06c6-4077-97a5-80dda4de6308	58e5871e-14be-41eb-a14a-b268a5ee7be8	31790490-7a2e-4fb6-8d9d-aeae84fc7c4d
bae6296b-b403-472e-a0b2-3c4885ff770e	15b01cd8-ec79-451b-b2a2-080297119765	dd68ff64-d5f7-4118-a11e-95060b886e44	15 metros	\N	\N	30	30	23	76.66666666666667	\N	2025-04-21 23:50:57.714242+00	2025-04-22 02:48:47.986957+00	105f37e4-878c-4e21-ba7e-bdbd61455857	e0271254-653a-47da-921c-4fd09794d3ba	31790490-7a2e-4fb6-8d9d-aeae84fc7c4d
23305363-5d39-40bb-b857-3eb9f2406db3	da0f10a3-b3d2-43d4-8615-68d29bf0564c	dd68ff64-d5f7-4118-a11e-95060b886e44	12 metros	\N	\N	30	25	19	76	\N	2025-04-22 02:56:26.733583+00	\N	ad59af6a-06c6-4077-97a5-80dda4de6308	58e5871e-14be-41eb-a14a-b268a5ee7be8	31790490-7a2e-4fb6-8d9d-aeae84fc7c4d
465ee536-5fbb-404a-9bb6-947b2c3df95e	da0f10a3-b3d2-43d4-8615-68d29bf0564c	dd68ff64-d5f7-4118-a11e-95060b886e44	12 metros	\N	\N	30	25	19	76	\N	2025-04-22 02:57:18.772351+00	2025-04-22 02:57:37.9112+00	ad59af6a-06c6-4077-97a5-80dda4de6308	58e5871e-14be-41eb-a14a-b268a5ee7be8	31790490-7a2e-4fb6-8d9d-aeae84fc7c4d
5dd62861-7d92-4f09-a0cd-d9faa1fe7e6c	da0f10a3-b3d2-43d4-8615-68d29bf0564c	dd68ff64-d5f7-4118-a11e-95060b886e44	12 metros	\N	\N	35	29	29	100	\N	2025-04-22 03:14:43.768828+00	\N	ad59af6a-06c6-4077-97a5-80dda4de6308	58e5871e-14be-41eb-a14a-b268a5ee7be8	31790490-7a2e-4fb6-8d9d-aeae84fc7c4d
85e00e58-7c31-4ff0-a82d-a6f5d281b676	da0f10a3-b3d2-43d4-8615-68d29bf0564c	dd68ff64-d5f7-4118-a11e-95060b886e44	5 metros	\N	\N	35	29	29	100	\N	2025-04-22 03:14:56.003947+00	\N	ad59af6a-06c6-4077-97a5-80dda4de6308	58e5871e-14be-41eb-a14a-b268a5ee7be8	31790490-7a2e-4fb6-8d9d-aeae84fc7c4d
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
c2d2f2c6-1ba8-427b-b7c1-e892dfd46551	e0271254-653a-47da-921c-4fd09794d3ba	31790490-7a2e-4fb6-8d9d-aeae84fc7c4d	2025-04-21 21:28:53.410937+00
0e1ad891-bd01-4ad6-bf2d-9e0cf9cf57b4	58e5871e-14be-41eb-a14a-b268a5ee7be8	31790490-7a2e-4fb6-8d9d-aeae84fc7c4d	2025-04-22 00:25:48.644216+00
\.


--
-- PostgreSQL database dump complete
--

