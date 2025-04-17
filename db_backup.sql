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
-- Name: ammotype; Type: TYPE; Schema: public; Owner: angel
--

CREATE TYPE public.ammotype AS ENUM (
    'STANDARD',
    'COMPETITION',
    'PRACTICE',
    'MATCH',
    'HOLLOW_POINT',
    'FULL_METAL_JACKET',
    'SUBSONIC',
    'OTHER'
);


ALTER TYPE public.ammotype OWNER TO angel;

--
-- Name: shooterlevelenum; Type: TYPE; Schema: public; Owner: angel
--

CREATE TYPE public.shooterlevelenum AS ENUM (
    'EXPERTO',
    'CONFIABLE',
    'MEDIO',
    'REGULAR'
);


ALTER TYPE public.shooterlevelenum OWNER TO angel;

--
-- Name: targettype; Type: TYPE; Schema: public; Owner: angel
--

CREATE TYPE public.targettype AS ENUM (
    'CONCENTRIC',
    'IPSC'
);


ALTER TYPE public.targettype OWNER TO angel;

--
-- Name: weapontypeenum; Type: TYPE; Schema: public; Owner: angel
--

CREATE TYPE public.weapontypeenum AS ENUM (
    'PISTOL',
    'RIFLE',
    'REVOLVER',
    'SHOTGUN',
    'CARBINE',
    'SMG',
    'SNIPER_RIFLE',
    'OTHER'
);


ALTER TYPE public.weapontypeenum OWNER TO angel;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: angel
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO angel;

--
-- Name: ammunition; Type: TABLE; Schema: public; Owner: angel
--

CREATE TABLE public.ammunition (
    id uuid NOT NULL,
    name character varying NOT NULL,
    brand character varying NOT NULL,
    caliber character varying NOT NULL,
    ammo_type public.ammotype NOT NULL,
    grain_weight double precision,
    velocity double precision,
    description text,
    price_per_round double precision,
    is_active boolean NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.ammunition OWNER TO angel;

--
-- Name: exercise_types; Type: TABLE; Schema: public; Owner: angel
--

CREATE TABLE public.exercise_types (
    id uuid NOT NULL,
    name character varying NOT NULL,
    description text,
    difficulty integer NOT NULL,
    objective character varying,
    development character varying,
    is_active boolean NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.exercise_types OWNER TO angel;

--
-- Name: individual_practice_sessions; Type: TABLE; Schema: public; Owner: angel
--

CREATE TABLE public.individual_practice_sessions (
    id uuid NOT NULL,
    shooter_id uuid NOT NULL,
    instructor_id uuid,
    date timestamp without time zone NOT NULL,
    location character varying NOT NULL,
    total_shots_fired integer,
    total_hits integer,
    accuracy_percentage double precision,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.individual_practice_sessions OWNER TO angel;

--
-- Name: practice_evaluations; Type: TABLE; Schema: public; Owner: angel
--

CREATE TABLE public.practice_evaluations (
    id uuid NOT NULL,
    session_id uuid NOT NULL,
    evaluator_id uuid,
    final_score double precision NOT NULL,
    classification public.shooterlevelenum NOT NULL,
    strengths character varying,
    weaknesses character varying,
    recomendations character varying,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.practice_evaluations OWNER TO angel;

--
-- Name: practice_exercises; Type: TABLE; Schema: public; Owner: angel
--

CREATE TABLE public.practice_exercises (
    id uuid NOT NULL,
    session_id uuid NOT NULL,
    exercise_type_id uuid NOT NULL,
    distance character varying NOT NULL,
    firing_cadence character varying,
    time_limit character varying,
    ammunition_allocated integer,
    ammunition_used integer,
    hits integer,
    accuracy_percentage double precision,
    reaction_time double precision,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    target_id uuid NOT NULL,
    weapon_id uuid NOT NULL,
    ammunition_id uuid NOT NULL
);


ALTER TABLE public.practice_exercises OWNER TO angel;

--
-- Name: shooter_performance_logs; Type: TABLE; Schema: public; Owner: angel
--

CREATE TABLE public.shooter_performance_logs (
    id uuid NOT NULL,
    shooter_id uuid NOT NULL,
    metric_type character varying,
    metric_value character varying,
    context character varying,
    notes character varying,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.shooter_performance_logs OWNER TO angel;

--
-- Name: shooter_stats; Type: TABLE; Schema: public; Owner: angel
--

CREATE TABLE public.shooter_stats (
    shooter_id uuid NOT NULL,
    total_shots integer NOT NULL,
    accuracy integer NOT NULL,
    reaction_shots integer NOT NULL,
    presicion_shots integer NOT NULL,
    draw_time_avg double precision NOT NULL,
    reload_time_avg double precision NOT NULL,
    average_hit_factor double precision NOT NULL,
    effectiveness double precision NOT NULL,
    common_error_zones character varying,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.shooter_stats OWNER TO angel;

--
-- Name: shooters; Type: TABLE; Schema: public; Owner: angel
--

CREATE TABLE public.shooters (
    user_id uuid NOT NULL,
    club_id uuid,
    level public.shooterlevelenum NOT NULL,
    range character varying,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.shooters OWNER TO angel;

--
-- Name: shooting_clubs; Type: TABLE; Schema: public; Owner: angel
--

CREATE TABLE public.shooting_clubs (
    id uuid NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    chief_instructor_id uuid NOT NULL,
    is_active boolean NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.shooting_clubs OWNER TO angel;

--
-- Name: shooting_recommendations; Type: TABLE; Schema: public; Owner: angel
--

CREATE TABLE public.shooting_recommendations (
    id uuid NOT NULL,
    analysis_id uuid NOT NULL,
    primary_issue_zone character varying NOT NULL,
    primary_issue_zone_description character varying NOT NULL,
    secondary_issue_zone character varying,
    secondary_issue_zone_description character varying,
    recommended_exercises json,
    recommendation_description character varying,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.shooting_recommendations OWNER TO angel;

--
-- Name: target_analyses; Type: TABLE; Schema: public; Owner: angel
--

CREATE TABLE public.target_analyses (
    id uuid NOT NULL,
    target_image_id uuid NOT NULL,
    analysis_timestamp timestamp without time zone,
    total_impacts_detected integer,
    zone_distribution json,
    impact_coordinates json,
    analysis_confidence double precision,
    analysis_method character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.target_analyses OWNER TO angel;

--
-- Name: target_images; Type: TABLE; Schema: public; Owner: angel
--

CREATE TABLE public.target_images (
    id uuid NOT NULL,
    exercise_id uuid NOT NULL,
    file_path character varying NOT NULL,
    file_size integer NOT NULL,
    content_type character varying NOT NULL,
    uploaded_at timestamp without time zone,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.target_images OWNER TO angel;

--
-- Name: targets; Type: TABLE; Schema: public; Owner: angel
--

CREATE TABLE public.targets (
    id uuid NOT NULL,
    name character varying NOT NULL,
    target_type public.targettype NOT NULL,
    description text,
    scoring_zones json,
    dimensions character varying,
    distance_recommended double precision,
    is_active boolean NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.targets OWNER TO angel;

--
-- Name: user_biometric_data; Type: TABLE; Schema: public; Owner: angel
--

CREATE TABLE public.user_biometric_data (
    user_id uuid NOT NULL,
    height character varying,
    weight character varying,
    hand_dominance character varying NOT NULL,
    eye_sight character varying,
    time_sleep character varying,
    blood_pressure character varying,
    heart_rate character varying,
    respiratory_rate character varying,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.user_biometric_data OWNER TO angel;

--
-- Name: user_medical_data; Type: TABLE; Schema: public; Owner: angel
--

CREATE TABLE public.user_medical_data (
    user_id uuid NOT NULL,
    blood_type character varying,
    allergies character varying,
    medical_conditions character varying,
    emergency_contact character varying,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.user_medical_data OWNER TO angel;

--
-- Name: user_personal_data; Type: TABLE; Schema: public; Owner: angel
--

CREATE TABLE public.user_personal_data (
    user_id uuid NOT NULL,
    first_name character varying NOT NULL,
    second_name character varying,
    last_name1 character varying NOT NULL,
    last_name2 character varying,
    phone_number character varying NOT NULL,
    date_of_birth date,
    city character varying,
    state character varying,
    country character varying,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.user_personal_data OWNER TO angel;

--
-- Name: users; Type: TABLE; Schema: public; Owner: angel
--

CREATE TABLE public.users (
    id uuid NOT NULL,
    email character varying NOT NULL,
    hashed_password character varying NOT NULL,
    role character varying NOT NULL,
    is_active boolean NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.users OWNER TO angel;

--
-- Name: weapon_ammunition_compatibility; Type: TABLE; Schema: public; Owner: angel
--

CREATE TABLE public.weapon_ammunition_compatibility (
    id uuid NOT NULL,
    weapon_id uuid NOT NULL,
    ammunition_id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.weapon_ammunition_compatibility OWNER TO angel;

--
-- Name: weapons; Type: TABLE; Schema: public; Owner: angel
--

CREATE TABLE public.weapons (
    id uuid NOT NULL,
    name character varying NOT NULL,
    brand character varying NOT NULL,
    model character varying NOT NULL,
    serial_number character varying NOT NULL,
    weapon_type public.weapontypeenum NOT NULL,
    caliber character varying NOT NULL,
    description text,
    is_active boolean NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.weapons OWNER TO angel;

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
\.


--
-- Data for Name: shooting_clubs; Type: TABLE DATA; Schema: public; Owner: angel
--

COPY public.shooting_clubs (id, name, description, chief_instructor_id, is_active, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: shooting_recommendations; Type: TABLE DATA; Schema: public; Owner: angel
--

COPY public.shooting_recommendations (id, analysis_id, primary_issue_zone, primary_issue_zone_description, secondary_issue_zone, secondary_issue_zone_description, recommended_exercises, recommendation_description, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: target_analyses; Type: TABLE DATA; Schema: public; Owner: angel
--

COPY public.target_analyses (id, target_image_id, analysis_timestamp, total_impacts_detected, zone_distribution, impact_coordinates, analysis_confidence, analysis_method, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: target_images; Type: TABLE DATA; Schema: public; Owner: angel
--

COPY public.target_images (id, exercise_id, file_path, file_size, content_type, uploaded_at, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: targets; Type: TABLE DATA; Schema: public; Owner: angel
--

COPY public.targets (id, name, target_type, description, scoring_zones, dimensions, distance_recommended, is_active, created_at, updated_at) FROM stdin;
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
\.


--
-- Data for Name: weapon_ammunition_compatibility; Type: TABLE DATA; Schema: public; Owner: angel
--

COPY public.weapon_ammunition_compatibility (id, weapon_id, ammunition_id, created_at) FROM stdin;
\.


--
-- Data for Name: weapons; Type: TABLE DATA; Schema: public; Owner: angel
--

COPY public.weapons (id, name, brand, model, serial_number, weapon_type, caliber, description, is_active, created_at, updated_at) FROM stdin;
\.


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: angel
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: ammunition ammunition_pkey; Type: CONSTRAINT; Schema: public; Owner: angel
--

ALTER TABLE ONLY public.ammunition
    ADD CONSTRAINT ammunition_pkey PRIMARY KEY (id);


--
-- Name: exercise_types exercise_types_pkey; Type: CONSTRAINT; Schema: public; Owner: angel
--

ALTER TABLE ONLY public.exercise_types
    ADD CONSTRAINT exercise_types_pkey PRIMARY KEY (id);


--
-- Name: individual_practice_sessions individual_practice_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: angel
--

ALTER TABLE ONLY public.individual_practice_sessions
    ADD CONSTRAINT individual_practice_sessions_pkey PRIMARY KEY (id);


--
-- Name: practice_evaluations practice_evaluations_pkey; Type: CONSTRAINT; Schema: public; Owner: angel
--

ALTER TABLE ONLY public.practice_evaluations
    ADD CONSTRAINT practice_evaluations_pkey PRIMARY KEY (id);


--
-- Name: practice_exercises practice_exercises_pkey; Type: CONSTRAINT; Schema: public; Owner: angel
--

ALTER TABLE ONLY public.practice_exercises
    ADD CONSTRAINT practice_exercises_pkey PRIMARY KEY (id);


--
-- Name: shooter_performance_logs shooter_performance_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: angel
--

ALTER TABLE ONLY public.shooter_performance_logs
    ADD CONSTRAINT shooter_performance_logs_pkey PRIMARY KEY (id);


--
-- Name: shooter_stats shooter_stats_pkey; Type: CONSTRAINT; Schema: public; Owner: angel
--

ALTER TABLE ONLY public.shooter_stats
    ADD CONSTRAINT shooter_stats_pkey PRIMARY KEY (shooter_id);


--
-- Name: shooters shooters_pkey; Type: CONSTRAINT; Schema: public; Owner: angel
--

ALTER TABLE ONLY public.shooters
    ADD CONSTRAINT shooters_pkey PRIMARY KEY (user_id);


--
-- Name: shooting_clubs shooting_clubs_chief_instructor_id_key; Type: CONSTRAINT; Schema: public; Owner: angel
--

ALTER TABLE ONLY public.shooting_clubs
    ADD CONSTRAINT shooting_clubs_chief_instructor_id_key UNIQUE (chief_instructor_id);


--
-- Name: shooting_clubs shooting_clubs_name_key; Type: CONSTRAINT; Schema: public; Owner: angel
--

ALTER TABLE ONLY public.shooting_clubs
    ADD CONSTRAINT shooting_clubs_name_key UNIQUE (name);


--
-- Name: shooting_clubs shooting_clubs_pkey; Type: CONSTRAINT; Schema: public; Owner: angel
--

ALTER TABLE ONLY public.shooting_clubs
    ADD CONSTRAINT shooting_clubs_pkey PRIMARY KEY (id);


--
-- Name: shooting_recommendations shooting_recommendations_pkey; Type: CONSTRAINT; Schema: public; Owner: angel
--

ALTER TABLE ONLY public.shooting_recommendations
    ADD CONSTRAINT shooting_recommendations_pkey PRIMARY KEY (id);


--
-- Name: target_analyses target_analyses_pkey; Type: CONSTRAINT; Schema: public; Owner: angel
--

ALTER TABLE ONLY public.target_analyses
    ADD CONSTRAINT target_analyses_pkey PRIMARY KEY (id);


--
-- Name: target_images target_images_pkey; Type: CONSTRAINT; Schema: public; Owner: angel
--

ALTER TABLE ONLY public.target_images
    ADD CONSTRAINT target_images_pkey PRIMARY KEY (id);


--
-- Name: targets targets_pkey; Type: CONSTRAINT; Schema: public; Owner: angel
--

ALTER TABLE ONLY public.targets
    ADD CONSTRAINT targets_pkey PRIMARY KEY (id);


--
-- Name: user_biometric_data user_biometric_data_pkey; Type: CONSTRAINT; Schema: public; Owner: angel
--

ALTER TABLE ONLY public.user_biometric_data
    ADD CONSTRAINT user_biometric_data_pkey PRIMARY KEY (user_id);


--
-- Name: user_medical_data user_medical_data_pkey; Type: CONSTRAINT; Schema: public; Owner: angel
--

ALTER TABLE ONLY public.user_medical_data
    ADD CONSTRAINT user_medical_data_pkey PRIMARY KEY (user_id);


--
-- Name: user_personal_data user_personal_data_pkey; Type: CONSTRAINT; Schema: public; Owner: angel
--

ALTER TABLE ONLY public.user_personal_data
    ADD CONSTRAINT user_personal_data_pkey PRIMARY KEY (user_id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: angel
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: weapon_ammunition_compatibility weapon_ammunition_compatibility_pkey; Type: CONSTRAINT; Schema: public; Owner: angel
--

ALTER TABLE ONLY public.weapon_ammunition_compatibility
    ADD CONSTRAINT weapon_ammunition_compatibility_pkey PRIMARY KEY (id);


--
-- Name: weapons weapons_pkey; Type: CONSTRAINT; Schema: public; Owner: angel
--

ALTER TABLE ONLY public.weapons
    ADD CONSTRAINT weapons_pkey PRIMARY KEY (id);


--
-- Name: weapons weapons_serial_number_key; Type: CONSTRAINT; Schema: public; Owner: angel
--

ALTER TABLE ONLY public.weapons
    ADD CONSTRAINT weapons_serial_number_key UNIQUE (serial_number);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: angel
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: individual_practice_sessions individual_practice_sessions_instructor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: angel
--

ALTER TABLE ONLY public.individual_practice_sessions
    ADD CONSTRAINT individual_practice_sessions_instructor_id_fkey FOREIGN KEY (instructor_id) REFERENCES public.users(id);


--
-- Name: individual_practice_sessions individual_practice_sessions_shooter_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: angel
--

ALTER TABLE ONLY public.individual_practice_sessions
    ADD CONSTRAINT individual_practice_sessions_shooter_id_fkey FOREIGN KEY (shooter_id) REFERENCES public.shooters(user_id);


--
-- Name: practice_evaluations practice_evaluations_evaluator_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: angel
--

ALTER TABLE ONLY public.practice_evaluations
    ADD CONSTRAINT practice_evaluations_evaluator_id_fkey FOREIGN KEY (evaluator_id) REFERENCES public.users(id);


--
-- Name: practice_evaluations practice_evaluations_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: angel
--

ALTER TABLE ONLY public.practice_evaluations
    ADD CONSTRAINT practice_evaluations_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.individual_practice_sessions(id);


--
-- Name: practice_exercises practice_exercises_ammunition_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: angel
--

ALTER TABLE ONLY public.practice_exercises
    ADD CONSTRAINT practice_exercises_ammunition_id_fkey FOREIGN KEY (ammunition_id) REFERENCES public.ammunition(id);


--
-- Name: practice_exercises practice_exercises_exercise_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: angel
--

ALTER TABLE ONLY public.practice_exercises
    ADD CONSTRAINT practice_exercises_exercise_type_id_fkey FOREIGN KEY (exercise_type_id) REFERENCES public.exercise_types(id);


--
-- Name: practice_exercises practice_exercises_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: angel
--

ALTER TABLE ONLY public.practice_exercises
    ADD CONSTRAINT practice_exercises_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.individual_practice_sessions(id);


--
-- Name: practice_exercises practice_exercises_target_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: angel
--

ALTER TABLE ONLY public.practice_exercises
    ADD CONSTRAINT practice_exercises_target_id_fkey FOREIGN KEY (target_id) REFERENCES public.targets(id);


--
-- Name: practice_exercises practice_exercises_weapon_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: angel
--

ALTER TABLE ONLY public.practice_exercises
    ADD CONSTRAINT practice_exercises_weapon_id_fkey FOREIGN KEY (weapon_id) REFERENCES public.weapons(id);


--
-- Name: shooter_performance_logs shooter_performance_logs_shooter_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: angel
--

ALTER TABLE ONLY public.shooter_performance_logs
    ADD CONSTRAINT shooter_performance_logs_shooter_id_fkey FOREIGN KEY (shooter_id) REFERENCES public.shooters(user_id) ON DELETE CASCADE;


--
-- Name: shooter_stats shooter_stats_shooter_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: angel
--

ALTER TABLE ONLY public.shooter_stats
    ADD CONSTRAINT shooter_stats_shooter_id_fkey FOREIGN KEY (shooter_id) REFERENCES public.shooters(user_id) ON DELETE CASCADE;


--
-- Name: shooters shooters_club_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: angel
--

ALTER TABLE ONLY public.shooters
    ADD CONSTRAINT shooters_club_id_fkey FOREIGN KEY (club_id) REFERENCES public.shooting_clubs(id);


--
-- Name: shooters shooters_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: angel
--

ALTER TABLE ONLY public.shooters
    ADD CONSTRAINT shooters_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: shooting_clubs shooting_clubs_chief_instructor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: angel
--

ALTER TABLE ONLY public.shooting_clubs
    ADD CONSTRAINT shooting_clubs_chief_instructor_id_fkey FOREIGN KEY (chief_instructor_id) REFERENCES public.users(id);


--
-- Name: shooting_recommendations shooting_recommendations_analysis_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: angel
--

ALTER TABLE ONLY public.shooting_recommendations
    ADD CONSTRAINT shooting_recommendations_analysis_id_fkey FOREIGN KEY (analysis_id) REFERENCES public.target_analyses(id);


--
-- Name: target_analyses target_analyses_target_image_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: angel
--

ALTER TABLE ONLY public.target_analyses
    ADD CONSTRAINT target_analyses_target_image_id_fkey FOREIGN KEY (target_image_id) REFERENCES public.target_images(id);


--
-- Name: target_images target_images_exercise_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: angel
--

ALTER TABLE ONLY public.target_images
    ADD CONSTRAINT target_images_exercise_id_fkey FOREIGN KEY (exercise_id) REFERENCES public.practice_exercises(id);


--
-- Name: user_biometric_data user_biometric_data_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: angel
--

ALTER TABLE ONLY public.user_biometric_data
    ADD CONSTRAINT user_biometric_data_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: user_medical_data user_medical_data_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: angel
--

ALTER TABLE ONLY public.user_medical_data
    ADD CONSTRAINT user_medical_data_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: user_personal_data user_personal_data_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: angel
--

ALTER TABLE ONLY public.user_personal_data
    ADD CONSTRAINT user_personal_data_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: weapon_ammunition_compatibility weapon_ammunition_compatibility_ammunition_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: angel
--

ALTER TABLE ONLY public.weapon_ammunition_compatibility
    ADD CONSTRAINT weapon_ammunition_compatibility_ammunition_id_fkey FOREIGN KEY (ammunition_id) REFERENCES public.ammunition(id) ON DELETE CASCADE;


--
-- Name: weapon_ammunition_compatibility weapon_ammunition_compatibility_weapon_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: angel
--

ALTER TABLE ONLY public.weapon_ammunition_compatibility
    ADD CONSTRAINT weapon_ammunition_compatibility_weapon_id_fkey FOREIGN KEY (weapon_id) REFERENCES public.weapons(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

