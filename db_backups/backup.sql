
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
    updated_at timestamp with time zone,
    evaluation_pending boolean
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
    updated_at timestamp with time zone,
    posture_rating integer,
    grip_rating integer,
    sight_alignment_rating integer,
    trigger_control_rating integer,
    breathing_rating integer,
    primary_issue_zone character varying,
    secondary_issue_zone character varying,
    avg_reaction_time double precision,
    avg_draw_time double precision,
    avg_reload_time double precision,
    hit_factor double precision,
    date timestamp without time zone NOT NULL
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
    updated_at timestamp with time zone,
    trend_accuracy double precision,
    last_10_sessions_avg double precision,
    precision_exercise_accuracy double precision,
    reaction_exercise_accuracy double precision,
    movement_exercise_accuracy double precision
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
    updated_at timestamp with time zone,
    nickname character varying,
    license_file character varying
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
    updated_at timestamp with time zone,
    genre character varying NOT NULL
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
585e90d35362
\.


--
-- Data for Name: ammunition; Type: TABLE DATA; Schema: public; Owner: angel
--

COPY public.ammunition (id, name, brand, caliber, ammo_type, grain_weight, velocity, description, price_per_round, is_active, created_at, updated_at) FROM stdin;
9134025a-944a-4d7c-bd97-1648ae8e83e8	SV Target .22 LR	SK	.22 LR	COMPETITION	40	1050	Munición de velocidad estándar optimizada para pistolas de competición, ofrece agrupaciones pequeñas a 25 metros. Para las pistolas de calibre .22 LR (Ruger Mark IV, Smith & Wesson SW22, Walther P22)	0.18	t	2025-05-19 07:21:39.207143+00	\N
59d137e3-4e8d-4a42-8766-f7e66501008e	9mm Luger FMJ	Federal	9mm	STANDARD	115	1180	Munición estándar 9mm Luger con punta encamisada (Full Metal Jacket) para práctica y tiro general.	0.5	t	2025-05-19 07:21:48.570347+00	\N
37e8438f-2a4d-4dca-8700-e54f4092769d	7.62x39mm FMJ	Wolf	7.62x39mm	STANDARD	123	2330	Munición estándar 7.62x39mm con punta encamisada (Full Metal Jacket), común para rifles AK-47.	0.4	t	2025-05-19 07:22:35.33512+00	\N
e42e0f37-5552-475b-bc16-b4684b9db90e	9mm Luger Punta hueca	Speer	9mm	HOLLOW_POINT	124	1150	Munición 9mm Luger con punta hueca (Jacketed Hollow Point) diseñada para defensa personal.	0.75	t	2025-05-19 07:23:44.773199+00	\N
\.


--
-- Data for Name: exercise_types; Type: TABLE DATA; Schema: public; Owner: angel
--

COPY public.exercise_types (id, name, description, difficulty, objective, development, is_active, created_at, updated_at) FROM stdin;
576d5c29-3db5-4735-b432-63f4db72fc0b	EVALUACIÓN DE PRECISION LVL. 3	El tiro de precisión de reacción es una técnica que se utiliza para mejorar la rapidez y la precisión en el disparo. En este tipo de práctica, el tirador debe reaccionar rápidamente al blanco y disparar con precisión, lo que implica una combinación de velocidad y control.	3	 Identificar la capacidad y destreza del tirador enfrentando 3 objetivos en diferentes distancias, así como identificar su nivel de precisión en tiro de reacción.	 los tiradores se encontraran frente a sus blancos en poción relajada, brazos colgados y arma en la funda, a las orden del instructor de tiro abastecerá con un cargador de 6 cartuchos (sin cargar el arma), al sonido del shot timer desenfundaran su arma y efectuaran dos disparos en cada blanco que se encontraran en diferentes distancias 7, 15 y 20 metros	t	2025-05-19 07:39:45.295014+00	\N
\.


--
-- Data for Name: individual_practice_sessions; Type: TABLE DATA; Schema: public; Owner: angel
--

COPY public.individual_practice_sessions (id, shooter_id, instructor_id, date, location, total_shots_fired, total_hits, accuracy_percentage, created_at, updated_at, evaluation_pending) FROM stdin;
d2f4af45-cf8a-4e9c-8002-0bf78657cb1c	1b9db5f4-7062-46b3-a399-edbabe0ae740	3e2ccb71-1640-4cba-b95d-3a0916e813de	2025-05-19 07:40:43.914389	No especificada	39	38	97.43589743589743	2025-05-19 07:40:43.912396+00	2025-05-19 08:31:17.052689+00	f
f981188b-b599-45cd-82f8-9338442758d3	1b9db5f4-7062-46b3-a399-edbabe0ae740	3e2ccb71-1640-4cba-b95d-3a0916e813de	2025-05-21 00:34:45.378768	No especificada	13	9	69.23076923076923	2025-05-21 00:34:45.37419+00	2025-05-21 00:37:31.481192+00	f
\.


--
-- Data for Name: practice_evaluations; Type: TABLE DATA; Schema: public; Owner: angel
--

COPY public.practice_evaluations (id, session_id, evaluator_id, final_score, classification, strengths, weaknesses, recomendations, created_at, updated_at, posture_rating, grip_rating, sight_alignment_rating, trigger_control_rating, breathing_rating, primary_issue_zone, secondary_issue_zone, avg_reaction_time, avg_draw_time, avg_reload_time, hit_factor, date) FROM stdin;
5944706c-b22e-44e4-9c53-19210802d515	f981188b-b599-45cd-82f8-9338442758d3	\N	69.2	MEDIO	\N	\N	\N	2025-05-21 00:37:31.481192+00	\N	8	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-05-21 00:27:58.888767
fa66cb8a-a655-4495-840c-08f50a3d555d	d2f4af45-cf8a-4e9c-8002-0bf78657cb1c	\N	97.4	EXPERTO	\N	\N	\N	2025-05-19 08:31:17.052689+00	2025-05-21 01:19:06.194346+00	\N	7	\N	\N	10	\N	\N	\N	\N	\N	\N	2025-05-19 08:31:15.852853
\.


--
-- Data for Name: practice_exercises; Type: TABLE DATA; Schema: public; Owner: angel
--

COPY public.practice_exercises (id, session_id, exercise_type_id, distance, firing_cadence, time_limit, ammunition_allocated, ammunition_used, hits, accuracy_percentage, reaction_time, created_at, updated_at, target_id, weapon_id, ammunition_id) FROM stdin;
d40a699e-feb2-4d26-9d5d-34fba6265177	d2f4af45-cf8a-4e9c-8002-0bf78657cb1c	576d5c29-3db5-4735-b432-63f4db72fc0b	10 metros	\N	\N	35	29	29	100	\N	2025-05-19 07:46:25.50297+00	\N	9f3fb4e1-681c-497c-b237-9eb87f0e1502	fdf40c58-128a-4505-a771-c22ac45fc20f	e42e0f37-5552-475b-bc16-b4684b9db90e
1b8afbfe-b40d-4721-b7e7-41f1cf242820	d2f4af45-cf8a-4e9c-8002-0bf78657cb1c	576d5c29-3db5-4735-b432-63f4db72fc0b	10 metros	\N	\N	10	10	9	90	\N	2025-05-19 07:47:06.672195+00	\N	9f3fb4e1-681c-497c-b237-9eb87f0e1502	fdf40c58-128a-4505-a771-c22ac45fc20f	e42e0f37-5552-475b-bc16-b4684b9db90e
1acf5d16-dd4f-4672-b138-93a6db6f9b0e	f981188b-b599-45cd-82f8-9338442758d3	576d5c29-3db5-4735-b432-63f4db72fc0b	5 metros	\N	\N	20	13	9	69.23076923076923	\N	2025-05-21 00:36:06.866451+00	\N	9f3fb4e1-681c-497c-b237-9eb87f0e1502	fdf40c58-128a-4505-a771-c22ac45fc20f	e42e0f37-5552-475b-bc16-b4684b9db90e
\.


--
-- Data for Name: shooter_performance_logs; Type: TABLE DATA; Schema: public; Owner: angel
--

COPY public.shooter_performance_logs (id, shooter_id, metric_type, metric_value, context, notes, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: shooter_stats; Type: TABLE DATA; Schema: public; Owner: angel
--

COPY public.shooter_stats (shooter_id, total_shots, accuracy, reaction_shots, presicion_shots, draw_time_avg, reload_time_avg, average_hit_factor, effectiveness, common_error_zones, created_at, updated_at, trend_accuracy, last_10_sessions_avg, precision_exercise_accuracy, reaction_exercise_accuracy, movement_exercise_accuracy) FROM stdin;
bb63e773-85b9-4283-aaff-becb82e5401b	0	0	0	0	0	0	0	0	\N	2025-05-19 04:05:33.607473+00	\N	0	0	0	0	0
398b551e-a65d-4681-bcb7-57590175edd9	0	0	0	0	0	0	0	0	\N	2025-05-19 04:05:44.424631+00	\N	0	0	0	0	0
ce9ee56d-a1fb-4e96-8fba-2d818d617820	0	0	0	0	0	0	0	0	\N	2025-05-19 04:05:46.538431+00	\N	0	0	0	0	0
dc261747-8a4b-4d6e-ad72-8ffc5d0eb543	0	0	0	0	0	0	0	0	\N	2025-05-19 04:05:47.613805+00	\N	0	0	0	0	0
85a91223-af1e-49e3-8df1-cce041b7ae65	0	0	0	0	0	0	0	0	\N	2025-05-19 04:05:48.596866+00	\N	0	0	0	0	0
987bb77e-5593-4748-a864-12d403109c06	0	0	0	0	0	0	0	0	\N	2025-05-19 04:05:49.434503+00	\N	0	0	0	0	0
aa2b81fc-af08-4504-a4e9-1956d5b80dce	0	0	0	0	0	0	0	0	\N	2025-05-19 06:49:00.859734+00	\N	0	0	0	0	0
1e932276-868a-4ca3-9830-b5c1cd1ab22d	0	0	0	0	0	0	0	0	\N	2025-05-19 06:49:03.089748+00	\N	0	0	0	0	0
6283360b-9288-4f9b-8994-4aa78f170296	0	0	0	0	0	0	0	0	\N	2025-05-19 06:49:03.929102+00	\N	0	0	0	0	0
5ca4a711-81f9-4da5-aea2-499fbb4a9a9b	0	0	0	0	0	0	0	0	\N	2025-05-19 06:49:04.520027+00	\N	0	0	0	0	0
5e4773c7-ddad-4b34-9fc3-ee02cb3bfadb	0	0	0	0	0	0	0	0	\N	2025-05-19 06:49:05.20807+00	\N	0	0	0	0	0
e4aee615-0851-4d40-94af-c8239aeef856	0	0	0	0	0	0	0	0	\N	2025-05-19 06:49:05.842574+00	\N	0	0	0	0	0
89792f23-d896-43f3-b452-e90dc6126223	0	0	0	0	0	0	0	0	\N	2025-05-19 06:49:06.435442+00	\N	0	0	0	0	0
e371cdf0-cebd-489d-8fef-569eee2cca26	0	0	0	0	0	0	0	0	\N	2025-05-19 06:49:59.317962+00	\N	0	0	0	0	0
95a95791-b33d-427a-aa23-a6a0d64c155a	0	0	0	0	0	0	0	0	\N	2025-05-19 06:50:02.560235+00	\N	0	0	0	0	0
3e2ccb71-1640-4cba-b95d-3a0916e813de	0	0	0	0	0	0	0	0	\N	2025-05-19 06:50:05.767794+00	\N	0	0	0	0	0
f520d2ce-3662-4b6a-859f-2058c0b3ea84	0	0	0	0	0	0	0	0	\N	2025-05-19 06:59:06.789501+00	\N	0	0	0	0	0
ff858c1c-c20c-4f00-85ce-5710d3d34a2c	0	0	0	0	0	0	0	0	\N	2025-05-19 06:59:07.590205+00	\N	0	0	0	0	0
fd6d5c95-6efb-41f0-9dbd-db7c6fc2a99c	0	0	0	0	0	0	0	0	\N	2025-05-19 06:59:08.394531+00	\N	0	0	0	0	0
1b9db5f4-7062-46b3-a399-edbabe0ae740	52	90	0	0	0	0	0	0	\N	2025-05-19 06:49:19.198957+00	2025-05-21 00:37:31.510798+00	-28.200000000000003	83.30000000000001	0	0	0
e80d49ad-3d95-4084-b781-2b18ea7e190a	0	0	0	0	0	0	0	0	\N	2025-05-21 01:58:41.520785+00	\N	0	0	0	0	0
4bffa0d0-612a-4da6-95b1-1c6e41340f32	0	0	0	0	0	0	0	0	\N	2025-05-21 02:51:50.47758+00	\N	0	0	0	0	0
\.


--
-- Data for Name: shooters; Type: TABLE DATA; Schema: public; Owner: angel
--

COPY public.shooters (user_id, club_id, level, range, created_at, updated_at, nickname, license_file) FROM stdin;
bb63e773-85b9-4283-aaff-becb82e5401b	\N	REGULAR	\N	2025-05-19 04:05:33.607473+00	\N	\N	\N
398b551e-a65d-4681-bcb7-57590175edd9	\N	REGULAR	\N	2025-05-19 04:05:44.424631+00	\N	\N	\N
ce9ee56d-a1fb-4e96-8fba-2d818d617820	\N	REGULAR	\N	2025-05-19 04:05:46.538431+00	\N	\N	\N
dc261747-8a4b-4d6e-ad72-8ffc5d0eb543	\N	REGULAR	\N	2025-05-19 04:05:47.613805+00	\N	\N	\N
85a91223-af1e-49e3-8df1-cce041b7ae65	\N	REGULAR	\N	2025-05-19 04:05:48.596866+00	\N	\N	\N
987bb77e-5593-4748-a864-12d403109c06	\N	REGULAR	\N	2025-05-19 04:05:49.434503+00	\N	\N	\N
aa2b81fc-af08-4504-a4e9-1956d5b80dce	\N	REGULAR	\N	2025-05-19 06:49:00.859734+00	\N	\N	\N
1e932276-868a-4ca3-9830-b5c1cd1ab22d	\N	REGULAR	\N	2025-05-19 06:49:03.089748+00	\N	\N	\N
5ca4a711-81f9-4da5-aea2-499fbb4a9a9b	\N	REGULAR	\N	2025-05-19 06:49:04.520027+00	\N	\N	\N
5e4773c7-ddad-4b34-9fc3-ee02cb3bfadb	\N	REGULAR	\N	2025-05-19 06:49:05.20807+00	\N	\N	\N
e4aee615-0851-4d40-94af-c8239aeef856	\N	REGULAR	\N	2025-05-19 06:49:05.842574+00	\N	\N	\N
89792f23-d896-43f3-b452-e90dc6126223	\N	REGULAR	\N	2025-05-19 06:49:06.435442+00	\N	\N	\N
e371cdf0-cebd-489d-8fef-569eee2cca26	\N	REGULAR	\N	2025-05-19 06:49:59.317962+00	\N	\N	\N
95a95791-b33d-427a-aa23-a6a0d64c155a	\N	REGULAR	\N	2025-05-19 06:50:02.560235+00	\N	\N	\N
3e2ccb71-1640-4cba-b95d-3a0916e813de	\N	REGULAR	\N	2025-05-19 06:50:05.767794+00	\N	\N	\N
f520d2ce-3662-4b6a-859f-2058c0b3ea84	\N	REGULAR	\N	2025-05-19 06:59:06.789501+00	\N	\N	\N
ff858c1c-c20c-4f00-85ce-5710d3d34a2c	\N	REGULAR	\N	2025-05-19 06:59:07.590205+00	\N	\N	\N
fd6d5c95-6efb-41f0-9dbd-db7c6fc2a99c	\N	REGULAR	\N	2025-05-19 06:59:08.394531+00	\N	\N	\N
e80d49ad-3d95-4084-b781-2b18ea7e190a	\N	REGULAR	\N	2025-05-21 01:58:41.520785+00	\N	\N	\N
4bffa0d0-612a-4da6-95b1-1c6e41340f32	\N	REGULAR	\N	2025-05-21 02:51:50.47758+00	\N	\N	\N
1b9db5f4-7062-46b3-a399-edbabe0ae740	\N	REGULAR	Soldado	2025-05-19 06:49:19.198957+00	2025-05-24 22:28:32.230119+00	\N	\N
6283360b-9288-4f9b-8994-4aa78f170296	\N	CONFIABLE	\N	2025-05-19 06:49:03.929102+00	2025-05-24 22:29:20.422309+00	\N	\N
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
9f3fb4e1-681c-497c-b237-9eb87f0e1502	Diana Olímpica	CONCENTRIC	Blanco oficial para competiciones olímpicas de tiro	{"rings": [{"radius": 5, "score": 10, "color": "black"}, {"radius": 10, "score": 9, "color": "black"}, {"radius": 15, "score": 8, "color": "black"}, {"radius": 20, "score": 7, "color": "white"}, {"radius": 25, "score": 6, "color": "white"}, {"radius": 30, "score": 5, "color": "white"}], "center": {"x": 0, "y": 0}}	40cm x 40cm	10	t	2025-05-19 07:06:41.291387+00	\N
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

COPY public.user_personal_data (user_id, first_name, second_name, last_name1, last_name2, phone_number, date_of_birth, city, state, country, created_at, updated_at, genre) FROM stdin;
95a95791-b33d-427a-aa23-a6a0d64c155a	Narciso	Tyree	Senger	\N	483-948-7657	2001-11-29	Juddmouth	Oaxaca	ZA	2025-05-19 07:29:10.258204+00	\N	N/A
1b9db5f4-7062-46b3-a399-edbabe0ae740	Brianne	Rosendo	Klein	\N	642-616-6802	2001-11-29	West Natalie	Oaxaca	AR	2025-05-19 07:29:35.932471+00	\N	N/A
e371cdf0-cebd-489d-8fef-569eee2cca26	Kevin	Alize	Pollich	\N	782-863-1797	2001-11-29	Haleymouth	Oaxaca	MS	2025-05-19 07:29:50.628024+00	\N	N/A
3e2ccb71-1640-4cba-b95d-3a0916e813de	Zora	Wilfrid	Schneider	\N	320-898-2906	2001-11-29	Vivianechester	Oaxaca	MZ	2025-05-19 07:30:03.443265+00	\N	N/A
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: angel
--

COPY public.users (id, email, hashed_password, role, is_active, created_at, updated_at) FROM stdin;
bb63e773-85b9-4283-aaff-becb82e5401b	Emmanuelle.Dach27@gmail.com	$2b$12$sYjV2MzIGwmz3rwpW0BgR.557RWgX0D2F6JtHw6PnvekDchsA2M3S	TIRADOR	t	2025-05-19 04:05:33.607473+00	\N
398b551e-a65d-4681-bcb7-57590175edd9	Torrey.Fisher@gmail.com	$2b$12$7jxkzQl5MLmpDWifpyEzbOr1v6QbXsbsVN97oVsHZT4njktzr2Fei	TIRADOR	t	2025-05-19 04:05:44.424631+00	\N
ce9ee56d-a1fb-4e96-8fba-2d818d617820	Abbie_Stark92@gmail.com	$2b$12$UpbkdhrZX4luZ15gGzHRuudBibkPmjJkSVw6Dtdz6.7QghXi.vVrK	TIRADOR	t	2025-05-19 04:05:46.538431+00	\N
dc261747-8a4b-4d6e-ad72-8ffc5d0eb543	Lulu_Rutherford@gmail.com	$2b$12$8kq1FEnHo1clJ55ryd4ZtOunwht3vRFmmw/0sAdRTVIorwnEFJiRi	TIRADOR	t	2025-05-19 04:05:47.613805+00	\N
85a91223-af1e-49e3-8df1-cce041b7ae65	Abbey87@yahoo.com	$2b$12$jUdsgTSqV976FxB8/A1biO6QIWZHbNtjuVWXVMBEB47MCySMbMhWK	TIRADOR	t	2025-05-19 04:05:48.596866+00	\N
987bb77e-5593-4748-a864-12d403109c06	Michel.Grady@gmail.com	$2b$12$Yk2Wszqe9knsHPrVmtvvZ.rsKDZ/OvJW1h0ZcNahH5r5DF3fTApiC	TIRADOR	t	2025-05-19 04:05:49.434503+00	\N
aa2b81fc-af08-4504-a4e9-1956d5b80dce	Bethany_Ortiz@gmail.com	$2b$12$nreU298Fl.sreJIyvfG/eejjJ1m/WMAlerO040UYCR8WZtND4oVEq	TIRADOR	t	2025-05-19 06:49:00.859734+00	\N
1e932276-868a-4ca3-9830-b5c1cd1ab22d	Quincy54@gmail.com	$2b$12$ZJUHF100EQhRqpKPkKUQ0uUnjkE3zmSzHfqG2oq4Po7aAOmOT6dl.	TIRADOR	t	2025-05-19 06:49:03.089748+00	\N
6283360b-9288-4f9b-8994-4aa78f170296	Emmie22@hotmail.com	$2b$12$V886TAiHdjjMvY5S7qQJseK61HAgwz9IlgW3WeoKJSjHyydPlh6z6	TIRADOR	t	2025-05-19 06:49:03.929102+00	\N
5ca4a711-81f9-4da5-aea2-499fbb4a9a9b	Paul29@gmail.com	$2b$12$fDsHqn9XvjSXESxIjkD/8eqHn10/WU9tWZRKrlDhM87/ZrWluaryC	TIRADOR	t	2025-05-19 06:49:04.520027+00	\N
5e4773c7-ddad-4b34-9fc3-ee02cb3bfadb	Nathanial12@hotmail.com	$2b$12$w.WlIj3cGQ.ffgBwTj6c0uW63t9uSWXtfcp0gbUdrxM/xmFcEFTAC	TIRADOR	t	2025-05-19 06:49:05.20807+00	\N
e4aee615-0851-4d40-94af-c8239aeef856	Penelope.Rutherford@hotmail.com	$2b$12$9hanRNMx0.FwkGFYfAToZeOyuwdvVFUOcKb7VeLBdHY5YyVjl0PYS	TIRADOR	t	2025-05-19 06:49:05.842574+00	\N
89792f23-d896-43f3-b452-e90dc6126223	Lyric39@yahoo.com	$2b$12$rHjDhNejgEs2iAvmWIDY.e5PfGNBVSuuLYMTbwXJxidLbz9rWthRS	TIRADOR	t	2025-05-19 06:49:06.435442+00	\N
1b9db5f4-7062-46b3-a399-edbabe0ae740	roberto.santos@yahoo.com	$2b$12$VeS3KN2EvpNdEHrYW1by/OIJeA0ryGt7wQS0mjbKQHy.J8IX1xcQa	TIRADOR	t	2025-05-19 06:49:19.198957+00	\N
f520d2ce-3662-4b6a-859f-2058c0b3ea84	Raheem3@yahoo.com	$2b$12$RJwsu4cfiboUFKaEvEn3yut/lcZ0AeR48gmj/Q9htSUo7C.CfTiyK	TIRADOR	t	2025-05-19 06:59:06.789501+00	\N
ff858c1c-c20c-4f00-85ce-5710d3d34a2c	Luella_Abshire19@yahoo.com	$2b$12$Xmg8dlYNXpLsOKI6R3GZKONkeE5PoV80gDitMDqaWgwSboRdqNg7u	TIRADOR	t	2025-05-19 06:59:07.590205+00	\N
fd6d5c95-6efb-41f0-9dbd-db7c6fc2a99c	Abby.Stamm@hotmail.com	$2b$12$mnteSRDW1mnVqWL7DeJz5ePltEbJ9hjdWJRco.3E81czTKDioLO7a	TIRADOR	t	2025-05-19 06:59:08.394531+00	\N
95a95791-b33d-427a-aa23-a6a0d64c155a	rolando.admin@gmail.com	$2b$12$szzklwPT2x81Cy2jZvvE1ehrk6/0DedIZAFk3SLHHJvoGHDo5rAW.	ADMIN	t	2025-05-19 06:50:02.560235+00	\N
3e2ccb71-1640-4cba-b95d-3a0916e813de	instructor@gmail.com	$2b$12$VvpGveVmM2FY.aqVuZLB9OtM2xI23OayoJ/G8LEUi5Xl2ROMph4du	INSTRUCTOR	t	2025-05-19 06:50:05.767794+00	2025-05-19 07:32:45.388129+00
e371cdf0-cebd-489d-8fef-569eee2cca26	whoangel@gmail.com	$2b$12$MV98CiaZaZGiQDlsgDNseOhO30u3UaUbHkS7gu3ewFGuGw22CoreK	INSTRUCTOR_JEFE	t	2025-05-19 06:49:59.317962+00	2025-05-19 07:34:37.699443+00
e80d49ad-3d95-4084-b781-2b18ea7e190a	Cheyenne_Lesch@yahoo.com	$2b$12$Av5eNjHxylk7hdTxtHQxKOGXjYMmf1UsF0/HZHFSqslg/SKfGaJqi	TIRADOR	t	2025-05-21 01:58:41.520785+00	\N
4bffa0d0-612a-4da6-95b1-1c6e41340f32	Verner_Runte@hotmail.com	$2b$12$1TLAxR1hJu/AIEM0BxOmNetBRJ7Ud.ES.JaGE06gpocHT0IAZGhaK	TIRADOR	t	2025-05-21 02:51:50.47758+00	\N
\.


--
-- Data for Name: weapon_ammunition_compatibility; Type: TABLE DATA; Schema: public; Owner: angel
--

COPY public.weapon_ammunition_compatibility (id, weapon_id, ammunition_id, created_at) FROM stdin;
cb349321-df73-468e-8df6-d4c7a139b68a	3253672d-7540-4ace-888f-c4caf7e616ad	37e8438f-2a4d-4dca-8700-e54f4092769d	2025-05-19 07:26:38.111439+00
b83346a3-fcf0-41e3-8ec8-ba32b5d1b8e5	3253672d-7540-4ace-888f-c4caf7e616ad	59d137e3-4e8d-4a42-8766-f7e66501008e	2025-05-19 07:27:02.36333+00
65426bb4-9bf2-4dc0-aa1a-d5856c4bdf64	fdf40c58-128a-4505-a771-c22ac45fc20f	e42e0f37-5552-475b-bc16-b4684b9db90e	2025-05-19 07:27:44.930853+00
\.


--
-- Data for Name: weapons; Type: TABLE DATA; Schema: public; Owner: angel
--

COPY public.weapons (id, name, brand, model, serial_number, weapon_type, caliber, description, is_active, created_at, updated_at) FROM stdin;
fdf40c58-128a-4505-a771-c22ac45fc20f	Glock 19	Glock	Gen 5	G19-GEN5-12345	PISTOL	9mm	Una pistola semiautomática compacta y popular.	t	2025-05-19 07:19:07.010008+00	\N
3253672d-7540-4ace-888f-c4caf7e616ad	AK-47	Kalashnikov	Avtomat Kalashnikova образца 1947 года	AK47-762-001	RIFLE	7.62x39mm	Un rifle de asalto icónico y robusto.	t	2025-05-19 07:20:01.729963+00	\N
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
-- Name: ix_shooters_nickname; Type: INDEX; Schema: public; Owner: angel
--

CREATE UNIQUE INDEX ix_shooters_nickname ON public.shooters USING btree (nickname);


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
