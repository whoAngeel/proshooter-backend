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
7883bb56-8cbb-4a19-8a0c-3dec26e99fe6	EVALUACIÓN DE REACCIÓN LVL. 3	El tiro de precisión de reacción es una técnica que se utiliza para mejorar la rapidez y la precisión en el disparo. En este tipo de práctica, el tirador debe reaccionar rápidamente al blanco y disparar con precisión, lo que implica una combinación de velocidad y control.	3	 Identificar la capacidad y destreza del tirador enfrentando 3 objetivos en diferentes distancias, así como identificar su nivel de precisión en tiro de reacción.	 los tiradores se encontraran frente a sus blancos en poción relajada, brazos colgados y arma en la funda, a las orden del instructor de tiro abastecerá con un cargador de 6 cartuchos (sin cargar el arma), al sonido del shot timer desenfundaran su arma y efectuaran dos disparos en cada blanco que se encontraran en diferentes distancias 7, 15 y 20 metros	t	2025-04-15 15:34:11.545268+00	\N
7a070719-47a5-4c4b-9fac-67eff8fbca10	EVALUACIÓN DE PRECISIÓN LVL. 3	El tiro de precisión es una disciplina de tiro deportivo en la que se dispara con rifles de alta precisión a blancos de papel. Los rifles se ubican sobre apoyos frontales y posteriores, y el tirador se sitúa frente al banco, a diferencia de otras disciplinas en las que el tirador sostiene y apunta el rifle sin apoyarse.	3	Identificar su nivel de tiro así como perfeccionar la precisión, armonizar al tirador con su arma y calificar su nivel básico de tiro	los tiradores efectuaran 5 disparos posición libre a una distancia de 10 metros de distancia con un tiempo limitado de 30 segundos.	t	2025-04-15 07:31:04.111321+00	2025-04-16 01:17:56.89238+00
\.


--
-- Data for Name: individual_practice_sessions; Type: TABLE DATA; Schema: public; Owner: angel
--

COPY public.individual_practice_sessions (id, shooter_id, instructor_id, date, location, total_shots_fired, total_hits, accuracy_percentage, created_at, updated_at) FROM stdin;
513f0264-a659-45fb-8bda-752864bdae83	e8a3262f-b001-4893-bc0b-fc2742b07ad8	\N	2025-04-16 03:26:55.187132	No especificada	0	0	0	2025-04-16 03:26:55.184882+00	\N
c499dde8-3f6c-4a83-ab13-c62ebe379ac9	e8a3262f-b001-4893-bc0b-fc2742b07ad8	\N	2025-04-16 03:27:09.056818	No especificada	0	0	0	2025-04-16 03:27:09.055006+00	\N
01d8c97c-6175-4b9b-bede-bb9e882fa126	e8a3262f-b001-4893-bc0b-fc2742b07ad8	\N	2025-04-16 03:27:10.62381	No especificada	0	0	0	2025-04-16 03:27:10.622283+00	\N
fe903c86-c110-4898-abe8-7a2dea236a89	e8a3262f-b001-4893-bc0b-fc2742b07ad8	\N	2025-04-16 03:28:44.081655	No especificada	0	0	0	2025-04-16 03:28:44.079805+00	\N
dae27c1f-37a0-40f9-92ff-54a546c4133e	e8a3262f-b001-4893-bc0b-fc2742b07ad8	\N	2025-04-16 03:28:53.740172	No especificada	0	0	0	2025-04-16 03:28:53.738729+00	\N
cda77117-7a31-477c-af60-67acf3c206a4	e8a3262f-b001-4893-bc0b-fc2742b07ad8	4ff3a30f-adf3-4e75-9187-421691be760e	2025-04-16 03:29:00.678747	No especificada	0	0	0	2025-04-16 03:29:00.677174+00	\N
91d8f636-054f-40b9-b277-5a3ed1c130b0	e8a3262f-b001-4893-bc0b-fc2742b07ad8	2bc5a576-0d8e-45c7-a716-3dde16f17ee2	2025-04-16 04:44:59.289984	No especificada	0	0	0	2025-04-16 04:44:59.286685+00	\N
60e097d8-d068-481a-84b5-605e87af703c	e8a3262f-b001-4893-bc0b-fc2742b07ad8	2bc5a576-0d8e-45c7-a716-3dde16f17ee2	2025-04-16 04:55:34.444127	Especifica	19	9	47.368421052631575	2025-04-16 04:55:34.441539+00	2025-04-16 05:44:19.65372+00
488026e7-ab26-470e-a17e-6dff9b6d8b82	e8a3262f-b001-4893-bc0b-fc2742b07ad8	2bc5a576-0d8e-45c7-a716-3dde16f17ee2	2025-04-16 03:37:41.32833	Especifica	19	9	47.368421052631575	2025-04-16 03:37:41.325846+00	2025-04-16 05:45:26.704863+00
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
875133ae-2518-4b68-8377-12e3135f9490	0	0	0	0	0	0	0	0	\N	2025-03-19 07:42:11.644071+00	\N
6984365b-fbe0-4f7e-b05f-315e1bfc6b72	0	0	0	0	0	0	0	0	\N	2025-03-19 07:42:12.449431+00	\N
e8e33004-86e4-4f6c-bb12-5c66b64be11a	0	0	0	0	0	0	0	0	\N	2025-03-19 07:42:13.221134+00	\N
f79fe98f-f7a5-43fe-a454-59b2a58e1d82	0	0	0	0	0	0	0	0	\N	2025-03-19 07:42:13.98115+00	\N
df1181f8-3cf5-4e14-86e0-b05bd449b8a4	0	0	0	0	0	0	0	0	\N	2025-03-19 07:42:14.667431+00	\N
e3eafed5-2413-492b-8cc9-9bacbcea57f5	0	0	0	0	0	0	0	0	\N	2025-03-19 07:42:15.142768+00	\N
73535fd0-71bd-4433-90b6-dd8947f17a52	0	0	0	0	0	0	0	0	\N	2025-03-19 07:42:15.483195+00	\N
4ff3a30f-adf3-4e75-9187-421691be760e	0	0	0	0	0	0	0	0	\N	2025-03-19 07:42:15.838143+00	\N
c9d85482-bf95-4ff7-96d4-6d780f06c561	0	0	0	0	0	0	0	0	\N	2025-03-19 07:42:16.222066+00	\N
c890b5be-2831-4331-a4cf-57d6554d6f32	0	0	0	0	0	0	0	0	\N	2025-03-19 07:42:17.509634+00	\N
2f166656-bbb5-4f90-a0b6-bea42b49c18a	0	0	0	0	0	0	0	0	\N	2025-03-19 07:42:18.389044+00	\N
982eca16-8465-4612-9ce4-8a3a5179a95e	0	0	0	0	0	0	0	0	\N	2025-03-19 07:42:19.131982+00	\N
5bcbced5-d5ed-4cf0-b8f6-2699c976420d	0	0	0	0	0	0	0	0	\N	2025-03-19 07:42:19.93595+00	\N
e8a3262f-b001-4893-bc0b-fc2742b07ad8	0	0	0	0	0	0	0	0	\N	2025-03-19 07:42:24.818432+00	\N
0a15198d-d0e7-40f9-957d-7bf65cd8ab91	0	0	0	0	0	0	0	0	\N	2025-03-19 07:42:35.752552+00	\N
2bc5a576-0d8e-45c7-a716-3dde16f17ee2	0	0	0	0	0	0	0	0	\N	2025-04-16 04:42:33.228095+00	\N
\.


--
-- Data for Name: shooters; Type: TABLE DATA; Schema: public; Owner: angel
--

COPY public.shooters (user_id, club_id, level, range, created_at, updated_at) FROM stdin;
875133ae-2518-4b68-8377-12e3135f9490	\N	REGULAR	\N	2025-03-19 07:42:11.644071+00	\N
6984365b-fbe0-4f7e-b05f-315e1bfc6b72	\N	REGULAR	\N	2025-03-19 07:42:12.449431+00	\N
e8e33004-86e4-4f6c-bb12-5c66b64be11a	\N	REGULAR	\N	2025-03-19 07:42:13.221134+00	\N
f79fe98f-f7a5-43fe-a454-59b2a58e1d82	\N	REGULAR	\N	2025-03-19 07:42:13.98115+00	\N
df1181f8-3cf5-4e14-86e0-b05bd449b8a4	\N	REGULAR	\N	2025-03-19 07:42:14.667431+00	\N
e3eafed5-2413-492b-8cc9-9bacbcea57f5	\N	REGULAR	\N	2025-03-19 07:42:15.142768+00	\N
73535fd0-71bd-4433-90b6-dd8947f17a52	\N	REGULAR	\N	2025-03-19 07:42:15.483195+00	\N
4ff3a30f-adf3-4e75-9187-421691be760e	\N	REGULAR	\N	2025-03-19 07:42:15.838143+00	\N
c9d85482-bf95-4ff7-96d4-6d780f06c561	\N	REGULAR	\N	2025-03-19 07:42:16.222066+00	\N
c890b5be-2831-4331-a4cf-57d6554d6f32	\N	REGULAR	\N	2025-03-19 07:42:17.509634+00	\N
2f166656-bbb5-4f90-a0b6-bea42b49c18a	\N	REGULAR	\N	2025-03-19 07:42:18.389044+00	\N
982eca16-8465-4612-9ce4-8a3a5179a95e	\N	REGULAR	\N	2025-03-19 07:42:19.131982+00	\N
5bcbced5-d5ed-4cf0-b8f6-2699c976420d	\N	REGULAR	\N	2025-03-19 07:42:19.93595+00	\N
e8a3262f-b001-4893-bc0b-fc2742b07ad8	\N	REGULAR	\N	2025-03-19 07:42:24.818432+00	\N
0a15198d-d0e7-40f9-957d-7bf65cd8ab91	\N	REGULAR	\N	2025-03-19 07:42:35.752552+00	\N
2bc5a576-0d8e-45c7-a716-3dde16f17ee2	\N	REGULAR	\N	2025-04-16 04:42:33.228095+00	\N
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
60f1159c-72e0-456e-b7c9-01fa212aca98	Blanco IPSC Estándar	IPSC	Blanco estándar para competiciones IPSC	{"zones": [{"name": "A", "score": 5, "color": "brown", "bounds": {"min_x": -10, "max_x": 10, "min_y": -15, "max_y": 15}}, {"name": "C", "score": 3, "color": "brown", "bounds": {"min_x": -15, "max_x": 15, "min_y": -25, "max_y": 25}}, {"name": "D", "score": 1, "color": "brown", "bounds": {"min_x": -20, "max_x": 20, "min_y": -30, "max_y": 30}}], "penalty_zones": [{"name": "no-shoot", "penalty": -10, "color": "white", "bounds": {"min_x": 25, "max_x": 35, "min_y": -20, "max_y": 20}}], "shape": "silhouette"}	45cm x 75cm	15	t	2025-03-19 07:43:30.233464+00	\N
61cfa916-7bed-4f2e-83ef-38b7fb3b153e	Diana Olímpica	CONCENTRIC	Blanco oficial para competiciones olímpicas de tiro	{"rings": [{"radius": 5, "score": 10, "color": "black"}, {"radius": 10, "score": 9, "color": "black"}, {"radius": 15, "score": 8, "color": "black"}, {"radius": 20, "score": 7, "color": "white"}, {"radius": 25, "score": 6, "color": "white"}, {"radius": 30, "score": 5, "color": "white"}], "center": {"x": 0, "y": 0}}	40cm x 40cm	10	t	2025-03-19 07:43:37.466291+00	\N
\.


--
-- Data for Name: user_biometric_data; Type: TABLE DATA; Schema: public; Owner: angel
--

COPY public.user_biometric_data (user_id, height, weight, hand_dominance, eye_sight, time_sleep, blood_pressure, heart_rate, respiratory_rate, created_at, updated_at) FROM stdin;
0a15198d-d0e7-40f9-957d-7bf65cd8ab91	1.65	60kg	Izquierda	20/30	\N	\N	\N	\N	2025-04-03 02:05:07.698681+00	2025-04-03 02:06:07.886877+00
\.


--
-- Data for Name: user_medical_data; Type: TABLE DATA; Schema: public; Owner: angel
--

COPY public.user_medical_data (user_id, blood_type, allergies, medical_conditions, emergency_contact, created_at, updated_at) FROM stdin;
0a15198d-d0e7-40f9-957d-7bf65cd8ab91	A-	Ninguna	Hipertensión, Vitiligo	Robert Smith, 555-4040404	2025-04-03 02:02:35.219519+00	2025-04-03 02:03:34.193526+00
\.


--
-- Data for Name: user_personal_data; Type: TABLE DATA; Schema: public; Owner: angel
--

COPY public.user_personal_data (user_id, first_name, second_name, last_name1, last_name2, phone_number, date_of_birth, city, state, country, created_at, updated_at) FROM stdin;
0a15198d-d0e7-40f9-957d-7bf65cd8ab91	Elton	Valentine	Quitzon	\N	474-451-4409	2001-11-29	Oaxaca	Oaxaca	USA	2025-04-03 01:43:08.203235+00	2025-04-03 01:45:50.55167+00
e8a3262f-b001-4893-bc0b-fc2742b07ad8	Franz	Marilou	Kuvalis	\N	208-557-1510	2001-11-29	Arianetown	Oaxaca	MT	2025-04-16 04:31:50.596916+00	\N
2bc5a576-0d8e-45c7-a716-3dde16f17ee2	Cletus	Don	Dooley	\N	980-506-5170	2001-11-29	Stellaburgh	Oaxaca	CC	2025-04-16 04:44:25.68325+00	\N
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: angel
--

COPY public.users (id, email, hashed_password, role, is_active, created_at, updated_at) FROM stdin;
875133ae-2518-4b68-8377-12e3135f9490	Kennedi_Gislason36@hotmail.com	$2b$12$JIAyNSnB/GVeNdqDaC2eE.C360jlsTwgYbir/nt9ClumXyq.ac8ha	TIRADOR	t	2025-03-19 07:42:11.644071+00	\N
6984365b-fbe0-4f7e-b05f-315e1bfc6b72	Vincenza10@gmail.com	$2b$12$okgdFvHanuPhk9QHOPC9j.2VnGKiFVMAdfCY7kZBr2xBuOJXIj0ia	TIRADOR	t	2025-03-19 07:42:12.449431+00	\N
e8e33004-86e4-4f6c-bb12-5c66b64be11a	Peter13@yahoo.com	$2b$12$p5Wdhx8ffBNIhv5QaTf74u/AnJ5ZTBUVMnoFgEZD/03gZIyzZ6J2K	TIRADOR	t	2025-03-19 07:42:13.221134+00	\N
f79fe98f-f7a5-43fe-a454-59b2a58e1d82	Joany_Hodkiewicz@yahoo.com	$2b$12$LEy83JBd/VburUMJ5RTfMOx6GacGUWs.X70lD3K2czjXD3OBAGPXi	TIRADOR	t	2025-03-19 07:42:13.98115+00	\N
df1181f8-3cf5-4e14-86e0-b05bd449b8a4	Evelyn_Effertz2@yahoo.com	$2b$12$Bo/WQQjUMxYpT8vh7xXcn.lgBynmC.o/vEK1MtX/KWDxLPwq9jCFi	TIRADOR	t	2025-03-19 07:42:14.667431+00	\N
73535fd0-71bd-4433-90b6-dd8947f17a52	Celestino89@yahoo.com	$2b$12$vTdAX9dHormOC48PONZl0OT5DgFtzaBEsqeR0uDVVqxdKWiVp8j.W	TIRADOR	t	2025-03-19 07:42:15.483195+00	\N
c9d85482-bf95-4ff7-96d4-6d780f06c561	Grady.Ondricka@gmail.com	$2b$12$Zve3zTqXT3v37JpRYOJMl.JBdiO.qU.TGn38oYDHQzdKfZmuouUsO	TIRADOR	t	2025-03-19 07:42:16.222066+00	\N
c890b5be-2831-4331-a4cf-57d6554d6f32	Lavinia28@yahoo.com	$2b$12$kZrGhtcY.Ukubrxkehm7M.9hKPsiUlQ8sl4WC3pAChrEF.oVM4cUO	TIRADOR	t	2025-03-19 07:42:17.509634+00	\N
2f166656-bbb5-4f90-a0b6-bea42b49c18a	Myrtis_Hettinger@gmail.com	$2b$12$zeaYfdt9e4WFLceP/F2kVOahL9e5j8pCBMOYReriygo02j39Ik8R.	TIRADOR	t	2025-03-19 07:42:18.389044+00	\N
982eca16-8465-4612-9ce4-8a3a5179a95e	Sid.Lindgren0@gmail.com	$2b$12$9kJL2Ha41tcw3jFCs1e15.jSXkb7ZdJibO8AM1G31ol5n3sZB/jzi	TIRADOR	t	2025-03-19 07:42:19.131982+00	\N
5bcbced5-d5ed-4cf0-b8f6-2699c976420d	Freddy_Hilll97@gmail.com	$2b$12$7ZXVX5hS/B4w9LxrSsnboOCBPEfLEg3GXLR122cJUVZIE9kz5Q/tC	TIRADOR	t	2025-03-19 07:42:19.93595+00	\N
e8a3262f-b001-4893-bc0b-fc2742b07ad8	roberto.santos@yahoo.com	$2b$12$i2KWH9yDbCedfDOHV/1TCePDJA5ULcokFLiXLGUukYXeYbT8056tq	TIRADOR	t	2025-03-19 07:42:24.818432+00	\N
0a15198d-d0e7-40f9-957d-7bf65cd8ab91	whoangel@gmail.com	$2b$12$AOHVQPEUxDgZKVM8BM70CuN9bzAOcs7X1/StS92cd7SisQUXqJRZe	ADMIN	t	2025-03-19 07:42:35.752552+00	\N
e3eafed5-2413-492b-8cc9-9bacbcea57f5	Saige_Bogisich@hotmail.com	$2b$12$C/XLo1H0lA3Y3remFkNYs.gO2TnsSc550USrfVnAXCpOlqi35GahO	TIRADOR	f	2025-03-19 07:42:15.142768+00	2025-04-03 02:31:45.261839+00
4ff3a30f-adf3-4e75-9187-421691be760e	Pietro43@hotmail.com	$2b$12$oM2P0bNHNw3oq3l2fXnIqO2MvfD6zrd1jII6.CwpJjh1EvW1E81xy	INSTRUCTOR	t	2025-03-19 07:42:15.838143+00	2025-04-16 03:28:18.494362+00
2bc5a576-0d8e-45c7-a716-3dde16f17ee2	instructor@gmail.com	$2b$12$0hnXtYysyAhBt8k/9bQkmusFX8Xon1kZyhOXDlOb65vb4H.7hVCF6	INSTRUCTOR	t	2025-04-16 04:42:33.228095+00	2025-04-16 04:44:07.454847+00
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

