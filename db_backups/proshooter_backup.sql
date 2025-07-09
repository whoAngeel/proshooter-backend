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
-- Name: roleenum; Type: TYPE; Schema: public; Owner: angel
--

CREATE TYPE public.roleenum AS ENUM (
    'ADMIN',
    'TIRADOR',
    'INSTRUCTOR',
    'JEFE_INSTRUCTORES'
);


ALTER TYPE public.roleenum OWNER TO angel;

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
-- Name: shooter_stats; Type: TABLE; Schema: public; Owner: angel
--

CREATE TABLE public.shooter_stats (
    shooter_id uuid NOT NULL,
    total_shots integer NOT NULL,
    accuracy integer NOT NULL,
    average_hit_factor double precision NOT NULL,
    effectiveness double precision NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.shooter_stats OWNER TO angel;

--
-- Name: shooters; Type: TABLE; Schema: public; Owner: angel
--

CREATE TABLE public.shooters (
    user_id uuid NOT NULL,
    classification character varying NOT NULL,
    range character varying,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    club_id uuid
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
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    time_sleep character varying,
    blood_pressure character varying,
    heart_rate character varying,
    respiratory_rate character varying
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
12e24bdf7969
\.


--
-- Data for Name: ammunition; Type: TABLE DATA; Schema: public; Owner: angel
--

COPY public.ammunition (id, name, brand, caliber, ammo_type, grain_weight, velocity, description, price_per_round, is_active, created_at, updated_at) FROM stdin;
b11fc61e-490f-4fdb-a555-812e5e179f87	Gold Dot 9mm	Speer	9mm	HOLLOW_POINT	124	1150	Munición de defensa personal premium, con expansión controlada y penetración óptima.	0.95	t	2025-03-18 03:32:19.658156+00	\N
5e61f3c8-128e-47be-84ac-b1fbf360e50b	Magnum JSP	Remington	.357 Magnum	OTHER	158	1235	Munición de alto rendimiento para revólveres, ofrece potencia y precisión superiores.	1.25	t	2025-03-18 03:33:43.959572+00	\N
626e71d0-7bc1-47dc-a02a-a736ba249a03	Black Hills .223	Black Hills Ammunition	.223 Remington	MATCH	77	2750	Munición de grado match, diseñada para competiciones de precisión a media y larga distancia.	1.5	t	2025-03-18 03:33:49.957217+00	\N
309e42ee-3fa1-4b4b-a1f4-ca4adfa1565b	Slugs Brenneke	Brenneke	12 Gauge	FULL_METAL_JACKET	437	1500	Slugs de alta potencia para escopetas tácticas, excelente para entrenamiento y competiciones de recorrido.	2.25	t	2025-03-18 03:34:13.368773+00	\N
a44fc465-9aef-4d1e-8bf5-5cd325a96a1b	BTHP Match	Hornady	.308 Winchester	MATCH	168	2700	Munición de precisión con puntas de bote hueco, diseñada específicamente para competiciones de tiro a larga distancia.	2.15	t	2025-03-18 03:34:27.001076+00	\N
8a2c6849-ee4d-451c-9094-b1fc602e01d4	Competition Master	Atlanta Arms	9mm	COMPETITION	147	860	Munición especialmente formulada para competiciones IPSC y USPSA, ofrece bajo retroceso y máxima precisión.	0.85	t	2025-03-18 03:34:36.550237+00	\N
43d15827-892f-4d21-8d50-e40290a6213c	Federal Premium 9mm	Federal	9mm	OTHER	115	1180	Actualizacion 1: Munición de entrenamiento de alta calidad, ideal para prácticas y competiciones IPSC.	0.45	t	2025-03-18 03:33:13.987467+00	2025-03-18 04:00:05.847794+00
0b730e7e-29eb-445a-959e-7cb479c13faf	9mm FMJ Training	Winchester	9mm	PRACTICE	115	1190	Munición de práctica con proyectil de punta metálica completa, ideal para entrenamientos de alto volumen.	0.35	t	2025-03-18 04:02:57.696961+00	\N
e2105b3a-05c5-43ff-a030-f7a51fdfbc52	9mm Precision Elite	Fiocchi	9mm	COMPETITION	124	1100	Munición de competición con carga controlada para reducir el retroceso y mejorar la precisión en competiciones IPSC. (para glock 17 y CZ ahadow 2)	0.79	t	2025-03-18 04:03:40.729926+00	\N
17764967-0339-4233-aeaf-4e9d6872b8c2	Hydra-Shok .45 ACP	Federal Premium	.45 ACP	HOLLOW_POINT	230	900	Munición de defensa personal con diseño de punta hueca patentado para expansión controlada y penetración óptima. (para SIG Sauer P226)	1.45	t	2025-03-18 04:04:09.090223+00	\N
897af0bd-82b3-40d1-a40b-82e75e9b5079	Range Ready .45 ACP	PMC	.45 ACP	OTHER	230	830	Munición económica de entrenamiento con casquillos de latón recocido para facilitar la recarga. (para SIG Sauer P226)	0.6	t	2025-03-18 04:04:36.885033+00	\N
3205a9a5-0bdf-4801-8be7-9f33c48fc8ed	Standard Plus .22 LR	CCI	.22 LR	STANDARD	40	1070	Munición .22 LR de alta velocidad con carga estándar, ideal para entrenamiento y tiro al blanco. Para las pistolas de calibre .22 LR (Ruger Mark IV, Smith & Wesson SW22, Walther P22)	0.1	t	2025-03-18 04:04:57.238629+00	\N
d8d4c6ef-f670-4b1b-bed1-67fc6dd6a3c8	Precision Hunter .22 LR	Eley	.22 LR	MATCH	40	1085	Munición de alta precisión para competiciones, fabricada con los más altos estándares de calidad y consistencia. Para las pistolas de calibre .22 LR (Ruger Mark IV, Smith & Wesson SW22, Walther P22)	0.25	t	2025-03-18 04:05:16.818435+00	\N
6f4f3a4d-1a6a-4434-b532-4bc43221c55d	Subsonic HP .22 LR	Aguila	.22 LR	SUBSONIC	38	950	Munición subsónica con punta hueca, ideal para uso con supresores y para entrenamiento silencioso. Para las pistolas de calibre .22 LR (Ruger Mark IV, Smith & Wesson SW22, Walther P22)	0.15	t	2025-03-18 04:05:28.979203+00	\N
6854180d-c6e3-4675-b68f-e6f4cf70b2b7	SV Target .22 LR	SK	.22 LR	COMPETITION	40	1050	Munición de velocidad estándar optimizada para pistolas de competición, ofrece agrupaciones pequeñas a 25 metros. Para las pistolas de calibre .22 LR (Ruger Mark IV, Smith & Wesson SW22, Walther P22)	0.18	t	2025-03-18 04:05:41.213288+00	\N
\.


--
-- Data for Name: shooter_stats; Type: TABLE DATA; Schema: public; Owner: angel
--

COPY public.shooter_stats (shooter_id, total_shots, accuracy, average_hit_factor, effectiveness, created_at, updated_at) FROM stdin;
f1093f5f-d24b-4439-be49-344807546d36	0	0	0	0	2025-03-01 02:56:33.264702+00	\N
c394b056-0d6f-4321-8106-bda47ae5b0ba	0	0	0	0	2025-03-01 03:08:56.573257+00	\N
ede20178-1bfd-4767-a0a9-3173e60fcc3e	0	0	0	0	2025-03-05 20:21:47.675761+00	\N
186925de-f186-4994-aeb9-4c87b688aa71	0	0	0	0	2025-03-05 20:22:01.755452+00	\N
1a09af7d-5c00-47e9-ac56-474ec4162cc2	0	0	0	0	2025-03-05 20:22:11.346792+00	\N
90174db7-5436-4468-8c8f-01648a85b63d	0	0	0	0	2025-03-05 20:22:24.117905+00	\N
294c6b3f-1023-4a0e-a1bf-a5968d84220c	0	0	0	0	2025-03-05 20:22:35.598791+00	\N
a042ddb6-7875-4237-a50a-0d3db1c9af4d	0	0	0	0	2025-03-05 20:22:49.949732+00	\N
f12b9684-853e-4c8d-9ead-a2df9741f612	0	0	0	0	2025-03-05 20:23:02.271397+00	\N
\.


--
-- Data for Name: shooters; Type: TABLE DATA; Schema: public; Owner: angel
--

COPY public.shooters (user_id, classification, range, created_at, updated_at, club_id) FROM stdin;
8c7eca63-aa08-4483-a64d-64dff83ac135	TR	\N	2025-02-27 08:40:07.099095+00	\N	\N
f1093f5f-d24b-4439-be49-344807546d36	TR	\N	2025-03-01 02:56:33.251347+00	\N	\N
c394b056-0d6f-4321-8106-bda47ae5b0ba	TR	\N	2025-03-01 03:08:56.384272+00	\N	\N
186925de-f186-4994-aeb9-4c87b688aa71	TR	\N	2025-03-05 20:22:01.755452+00	\N	\N
1a09af7d-5c00-47e9-ac56-474ec4162cc2	TR	\N	2025-03-05 20:22:11.346792+00	\N	\N
294c6b3f-1023-4a0e-a1bf-a5968d84220c	TR	\N	2025-03-05 20:22:35.598791+00	\N	\N
a042ddb6-7875-4237-a50a-0d3db1c9af4d	TR	\N	2025-03-05 20:22:49.949732+00	\N	\N
f12b9684-853e-4c8d-9ead-a2df9741f612	TR	\N	2025-03-05 20:23:02.271397+00	\N	\N
ede20178-1bfd-4767-a0a9-3173e60fcc3e	TR	\N	2025-03-05 20:21:47.675761+00	2025-03-06 03:05:57.995404+00	a2c87de5-781a-4a15-aa9e-d8b92c975d26
90174db7-5436-4468-8c8f-01648a85b63d	TR	\N	2025-03-05 20:22:24.117905+00	2025-03-06 03:08:52.157931+00	a2c87de5-781a-4a15-aa9e-d8b92c975d26
\.


--
-- Data for Name: shooting_clubs; Type: TABLE DATA; Schema: public; Owner: angel
--

COPY public.shooting_clubs (id, name, description, chief_instructor_id, is_active, created_at, updated_at) FROM stdin;
a2c87de5-781a-4a15-aa9e-d8b92c975d26	Tactical Warriors	Club enfocado en la velocidad, precisión y maniobras dinámicas en competencias 2.	f12b9684-853e-4c8d-9ead-a2df9741f612	t	2025-03-05 20:48:52.194375+00	2025-03-05 20:54:59.236848+00
\.


--
-- Data for Name: targets; Type: TABLE DATA; Schema: public; Owner: angel
--

COPY public.targets (id, name, target_type, description, scoring_zones, dimensions, distance_recommended, is_active, created_at, updated_at) FROM stdin;
2e0b99c3-6af9-4070-a88a-e7b48f684a1d	Diana Olímpica	CONCENTRIC	Blanco oficial para competiciones olímpicas de tiro	{"rings": [{"radius": 5, "score": 10, "color": "black"}, {"radius": 10, "score": 9, "color": "black"}, {"radius": 15, "score": 8, "color": "black"}, {"radius": 20, "score": 7, "color": "white"}, {"radius": 25, "score": 6, "color": "white"}, {"radius": 30, "score": 5, "color": "white"}], "center": {"x": 0, "y": 0}}	40cm x 40cm	10	t	2025-03-11 06:36:56.165601+00	\N
9d83ccd6-b303-4e76-8b6f-4f97805e3c1f	Blanco IPSC Estándar para competiciones	IPSC	Blanco estándar para competiciones IPSC	{"zones": [{"name": "A", "score": 5, "color": "brown", "bounds": {"min_x": -10, "max_x": 10, "min_y": -15, "max_y": 15}}, {"name": "C", "score": 3, "color": "brown", "bounds": {"min_x": -15, "max_x": 15, "min_y": -25, "max_y": 25}}, {"name": "D", "score": 1, "color": "brown", "bounds": {"min_x": -20, "max_x": 20, "min_y": -30, "max_y": 30}}], "penalty_zones": [{"name": "no-shoot", "penalty": -10, "color": "white", "bounds": {"min_x": 25, "max_x": 35, "min_y": -20, "max_y": 20}}], "shape": "silhouette"}	45cm x 75cm	15	f	2025-03-11 07:08:22.341671+00	2025-03-11 07:25:41.072629+00
\.


--
-- Data for Name: user_biometric_data; Type: TABLE DATA; Schema: public; Owner: angel
--

COPY public.user_biometric_data (user_id, height, weight, hand_dominance, eye_sight, created_at, updated_at, time_sleep, blood_pressure, heart_rate, respiratory_rate) FROM stdin;
e6ac626d-f5fd-4474-9e00-4c13de70c90d	1.65	60kg	Derecha	20/30	2025-02-27 08:27:49.773106+00	2025-02-27 08:28:05.284572+00	\N	\N	\N	\N
f12b9684-853e-4c8d-9ead-a2df9741f612	1.65	60kg	Izquierda	20/30	2025-03-05 20:33:34.261172+00	\N	\N	\N	\N	\N
\.


--
-- Data for Name: user_medical_data; Type: TABLE DATA; Schema: public; Owner: angel
--

COPY public.user_medical_data (user_id, blood_type, allergies, medical_conditions, emergency_contact, created_at, updated_at) FROM stdin;
e6ac626d-f5fd-4474-9e00-4c13de70c90d	A-	Ninguna	Hipertensión, Sobrepeso	Robert Smith, 555-4040404	2025-02-27 08:27:19.143768+00	2025-02-27 08:27:39.320742+00
f12b9684-853e-4c8d-9ead-a2df9741f612	A-	Ninguna	Hipertensión, Obesidad	Robert Smith, 555-4040404	2025-03-05 20:25:11.686942+00	\N
\.


--
-- Data for Name: user_personal_data; Type: TABLE DATA; Schema: public; Owner: angel
--

COPY public.user_personal_data (user_id, first_name, second_name, last_name1, last_name2, phone_number, date_of_birth, city, state, country, created_at, updated_at) FROM stdin;
3c531c12-aaf3-4de8-b949-294896264ad8	John	\N	Doe	\N	555-1010101	1990-02-15	Oaxaca	Oaxaca	USA	2025-02-27 08:26:48.428239+00	2025-02-27 08:26:53.834556+00
8c7eca63-aa08-4483-a64d-64dff83ac135	Angel	Jesus	Zorrilla	Cuevas	555-1010101	1990-02-15	Oaxaca	Oaxaca	MX	2025-02-27 08:53:32.584471+00	\N
f1093f5f-d24b-4439-be49-344807546d36	Angel	Jesus	Zorrilla	Cuevas	555-1010101	1990-02-15	Oaxaca	Oaxaca	MX	2025-03-01 02:57:27.790024+00	\N
f12b9684-853e-4c8d-9ead-a2df9741f612	Jewell	Janiya	Denesik	\N	555-673-6704	2001-11-29	Nikolausbury	Oaxaca	JM	2025-03-05 20:24:41.611322+00	\N
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: angel
--

COPY public.users (id, email, hashed_password, role, is_active, created_at, updated_at) FROM stdin;
e6ac626d-f5fd-4474-9e00-4c13de70c90d	carlos.rivera@example.com	$2b$12$x2lWaubYCgkel.Hv6AfDjuUU2VU3q.AhKxuqrQX8mY.4.DkYlZIZG	TIRADOR	t	2025-02-27 08:26:13.202777+00	\N
3c531c12-aaf3-4de8-b949-294896264ad8	Usuario.32@example.com	$2b$12$2mB.lLM.PilxTJYISJCcKuCLi7wv6CU2YIOVxmF67dzeTj2u.D4B.	TIRADOR	t	2025-02-27 08:26:20.801837+00	\N
8c7eca63-aa08-4483-a64d-64dff83ac135	angelzafasd@example.com	$2b$12$JUqprAxoCPTp7e5XiBmkeOG2T52N4113b66sBzQYm.S11aZScvcBe	TIRADOR	t	2025-02-27 08:40:06.901457+00	\N
c394b056-0d6f-4321-8106-bda47ae5b0ba	Althea10@yahoo.com	$2b$12$1XKnrSWTkKJoc8ZNyx6F/.lsy8aYWRvy3MrhUoWkXD5B8qQzROqui	TIRADOR	t	2025-03-01 03:08:56.384272+00	\N
ede20178-1bfd-4767-a0a9-3173e60fcc3e	david.thompson@example.com	$2b$12$kkRYtsK5EytCF75IyBvQl.ZJFI5oPx13Jbmg9Wo1gMDEdPxCby4ZW	TIRADOR	t	2025-03-05 20:21:47.675761+00	\N
186925de-f186-4994-aeb9-4c87b688aa71	maria.lopez@yahoo.com	$2b$12$eIqccH3cGxje/N3XsXagT.ARhyvuJmLGy8fbJWvXEN5Xpks7nZ6yy	TIRADOR	t	2025-03-05 20:22:01.755452+00	\N
1a09af7d-5c00-47e9-ac56-474ec4162cc2	carlos.gomez@outlook.com	$2b$12$hC07I3ykci6ZASodU3xc1uPrGc9oD/uPI.dn6d4kI/O4Gcm8QXR3.	TIRADOR	t	2025-03-05 20:22:11.346792+00	\N
90174db7-5436-4468-8c8f-01648a85b63d	ana.fernandez@gmail.com	$2b$12$pqXZFZv8BlmvOF.RmjpNwuuHAmRYFdDn/sAAIy2pMA88bBMOQhGhq	TIRADOR	t	2025-03-05 20:22:24.117905+00	\N
294c6b3f-1023-4a0e-a1bf-a5968d84220c	pedro.ramirez@hotmail.com	$2b$12$9tkB2c9dO8dIRrnz6sJXgOjhSxMtOuYf65d6ysp4FGgfrnDNJX6oO	TIRADOR	t	2025-03-05 20:22:35.598791+00	\N
a042ddb6-7875-4237-a50a-0d3db1c9af4d	laura.torres@gmail.com	$2b$12$c6Q7fbZbjh5X/bX0s8TkRuw5sopDgpdwvJzvEIm6i/6PnssIcJA1e	TIRADOR	t	2025-03-05 20:22:49.949732+00	\N
f12b9684-853e-4c8d-9ead-a2df9741f612	roberto.santos@yahoo.com	$2b$12$ETGVz00XQCx1ZJbZKTtRyeWsAbOyF1YtJLwiXgpAscyQUoxdNeQfq	INSTRUCTOR_JEFE	t	2025-03-05 20:23:02.271397+00	2025-03-05 20:40:14.465113+00
f1093f5f-d24b-4439-be49-344807546d36	whoangel.agl@gmail.com	$2b$12$9BdzBqspgj5aFEeDy5FzwOPIDfxKP2RIOEmMFj3I.6FDmX2bqUU/W	ADMIN	t	2025-03-01 02:56:33.060574+00	\N
\.


--
-- Data for Name: weapon_ammunition_compatibility; Type: TABLE DATA; Schema: public; Owner: angel
--

COPY public.weapon_ammunition_compatibility (id, weapon_id, ammunition_id, created_at) FROM stdin;
9d669120-d672-48ed-b6d1-fcc07d2216a6	b3206bd8-2b73-4e80-8a8a-93dd47d97fca	e2105b3a-05c5-43ff-a030-f7a51fdfbc52	2025-03-18 04:11:48.014758+00
b8ec4c87-79fe-4a4e-85c8-226a9b07511b	b3206bd8-2b73-4e80-8a8a-93dd47d97fca	0b730e7e-29eb-445a-959e-7cb479c13faf	2025-03-18 04:15:20.093464+00
e481822c-0908-459c-aec0-34871e032d33	8f8116ca-8de3-41b4-b55f-143798a7e86d	17764967-0339-4233-aeaf-4e9d6872b8c2	2025-03-18 04:18:34.59932+00
a793c957-e6c8-4097-8f71-29d60b846b60	497e86b2-710c-4e97-9c8c-f3e804d1de87	e2105b3a-05c5-43ff-a030-f7a51fdfbc52	2025-03-18 04:22:02.147868+00
8c636e00-0068-4bd6-a0c3-75de3afd3a1d	b8b02b05-5cc1-42b7-9f8b-6676cab43f68	3205a9a5-0bdf-4801-8be7-9f33c48fc8ed	2025-03-18 04:25:05.279808+00
93c3f5da-264b-4d1d-9482-b5c49dbc64f3	b8b02b05-5cc1-42b7-9f8b-6676cab43f68	d8d4c6ef-f670-4b1b-bed1-67fc6dd6a3c8	2025-03-18 04:25:25.759325+00
575b60c7-b2aa-414f-b97a-9b7c0e87b3ab	0e882617-f348-4d5c-8616-677b6e61d1e8	3205a9a5-0bdf-4801-8be7-9f33c48fc8ed	2025-03-18 04:29:32.05302+00
c9083f5e-70dc-4143-aff4-84c532795e33	0e882617-f348-4d5c-8616-677b6e61d1e8	d8d4c6ef-f670-4b1b-bed1-67fc6dd6a3c8	2025-03-18 04:29:44.110006+00
5c06d761-ec56-43a8-9b9e-f4feff2dc884	0e882617-f348-4d5c-8616-677b6e61d1e8	6f4f3a4d-1a6a-4434-b532-4bc43221c55d	2025-03-18 04:30:07.562889+00
b17a0697-749e-4aee-bfea-51fdbb613376	0e882617-f348-4d5c-8616-677b6e61d1e8	6854180d-c6e3-4675-b68f-e6f4cf70b2b7	2025-03-18 04:30:53.710833+00
\.


--
-- Data for Name: weapons; Type: TABLE DATA; Schema: public; Owner: angel
--

COPY public.weapons (id, name, brand, model, serial_number, weapon_type, caliber, description, is_active, created_at, updated_at) FROM stdin;
8e5b735c-70db-426a-8024-94a41a9d5948	Colt Python	Colt	Python 2020	PY45678901	REVOLVER	.357 Magnum	Revólver de doble acción considerado como uno de los mejores revólveres jamás fabricados.	t	2025-03-18 02:14:46.860629+00	\N
79adf5f4-9971-4fdf-90a5-9af733ccd7c6	AR-15	Smith & Wesson	M&P15 Sport II	SW87654321	RIFLE	.223 Remington/5.56 NATO	Rifle semiautomático de estilo deportivo, popular para competiciones y entrenamiento.	t	2025-03-18 02:14:58.694522+00	\N
fdfa50cf-6439-4626-a72a-6aac22d09c64	Remington 700	Remington	700 PCR	REM98765432	SNIPER_RIFLE	.308 Winchester	Rifle de cerrojo de precisión, diseñado para tiro a larga distancia y competiciones.	t	2025-03-18 02:15:33.662088+00	\N
b3206bd8-2b73-4e80-8a8a-93dd47d97fca	Glock 17	Glock	17 Gen5	GLCK12345678	PISTOL	9mm	Actualización de la descripción: Pistola semiautomática de alta fiabilidad con sistema de seguridad mejorado.	t	2025-03-18 02:14:04.048973+00	2025-03-18 02:24:33.470826+00
8f8116ca-8de3-41b4-b55f-143798a7e86d	SIG Sauer P226	SIG Sauer	P226	SIG87654321	PISTOL	.45 ACP	Pistola semiautomática de servicio, conocida por su precisión y fiabilidad.	t	2025-03-18 02:24:56.255726+00	\N
497e86b2-710c-4e97-9c8c-f3e804d1de87	CZ Shadow 2	CZ	Shadow 2	CZ2468013579	PISTOL	9mm	Pistola de competición IPSC, con chasis de acero, excelente balance y precisión superior.	t	2025-03-18 02:25:17.578124+00	\N
a6446cb3-4b43-4098-ae3d-d3ebe2a42104	Benelli M4	Benelli	M4 Tactical	BEN12345789	SHOTGUN	12 Gauge	Escopeta semiautomática de uso táctico, utilizada por fuerzas militares y policiales.	f	2025-03-18 02:15:16.644032+00	2025-03-18 02:26:20.126971+00
b8b02b05-5cc1-42b7-9f8b-6676cab43f68	Pistola Estándar .22 LR	Ruger	Mark IV Target	401-23456	PISTOL	.22 LR	Pistola semiautomática de precisión para tiro al blanco.	t	2025-03-18 02:57:26.995355+00	\N
0e882617-f348-4d5c-8616-677b6e61d1e8	Pistola Compacta .22 LR	Smith & Wesson	SW22 Victory	22A1234	PISTOL	.22 LR	Pistola semiautomática ligera y personalizable.	t	2025-03-18 02:57:52.7863+00	\N
e7c7cd0a-f934-4d8c-bb82-5cf931aab95f	Pistola de Bolsillo .22 LR	Walther	P22	WAA00123	PISTOL	.22 LR	Pistola semiautomática compacta para defensa personal o práctica.	t	2025-03-18 02:58:04.753914+00	\N
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

