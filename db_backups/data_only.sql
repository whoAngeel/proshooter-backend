--
-- PostgreSQL database dump
--

-- Dumped from database version 15.13
-- Dumped by pg_dump version 15.13

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

INSERT INTO public.alembic_version VALUES ('585e90d35362');


--
-- Data for Name: ammunition; Type: TABLE DATA; Schema: public; Owner: angel
--

INSERT INTO public.ammunition VALUES ('9134025a-944a-4d7c-bd97-1648ae8e83e8', 'SV Target .22 LR', 'SK', '.22 LR', 'COMPETITION', 40, 1050, 'Munición de velocidad estándar optimizada para pistolas de competición, ofrece agrupaciones pequeñas a 25 metros. Para las pistolas de calibre .22 LR (Ruger Mark IV, Smith & Wesson SW22, Walther P22)', 0.18, true, '2025-05-19 07:21:39.207143+00', NULL);
INSERT INTO public.ammunition VALUES ('59d137e3-4e8d-4a42-8766-f7e66501008e', '9mm Luger FMJ', 'Federal', '9mm', 'STANDARD', 115, 1180, 'Munición estándar 9mm Luger con punta encamisada (Full Metal Jacket) para práctica y tiro general.', 0.5, true, '2025-05-19 07:21:48.570347+00', NULL);
INSERT INTO public.ammunition VALUES ('37e8438f-2a4d-4dca-8700-e54f4092769d', '7.62x39mm FMJ', 'Wolf', '7.62x39mm', 'STANDARD', 123, 2330, 'Munición estándar 7.62x39mm con punta encamisada (Full Metal Jacket), común para rifles AK-47.', 0.4, true, '2025-05-19 07:22:35.33512+00', NULL);
INSERT INTO public.ammunition VALUES ('e42e0f37-5552-475b-bc16-b4684b9db90e', '9mm Luger Punta hueca', 'Speer', '9mm', 'HOLLOW_POINT', 124, 1150, 'Munición 9mm Luger con punta hueca (Jacketed Hollow Point) diseñada para defensa personal.', 0.75, true, '2025-05-19 07:23:44.773199+00', NULL);


--
-- Data for Name: exercise_types; Type: TABLE DATA; Schema: public; Owner: angel
--

INSERT INTO public.exercise_types VALUES ('576d5c29-3db5-4735-b432-63f4db72fc0b', 'EVALUACIÓN DE PRECISION LVL. 3', 'El tiro de precisión de reacción es una técnica que se utiliza para mejorar la rapidez y la precisión en el disparo. En este tipo de práctica, el tirador debe reaccionar rápidamente al blanco y disparar con precisión, lo que implica una combinación de velocidad y control.', 3, ' Identificar la capacidad y destreza del tirador enfrentando 3 objetivos en diferentes distancias, así como identificar su nivel de precisión en tiro de reacción.', ' los tiradores se encontraran frente a sus blancos en poción relajada, brazos colgados y arma en la funda, a las orden del instructor de tiro abastecerá con un cargador de 6 cartuchos (sin cargar el arma), al sonido del shot timer desenfundaran su arma y efectuaran dos disparos en cada blanco que se encontraran en diferentes distancias 7, 15 y 20 metros', true, '2025-05-19 07:39:45.295014+00', NULL);


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: angel
--

INSERT INTO public.users VALUES ('bb63e773-85b9-4283-aaff-becb82e5401b', 'Emmanuelle.Dach27@gmail.com', '$2b$12$sYjV2MzIGwmz3rwpW0BgR.557RWgX0D2F6JtHw6PnvekDchsA2M3S', 'TIRADOR', true, '2025-05-19 04:05:33.607473+00', NULL);
INSERT INTO public.users VALUES ('398b551e-a65d-4681-bcb7-57590175edd9', 'Torrey.Fisher@gmail.com', '$2b$12$7jxkzQl5MLmpDWifpyEzbOr1v6QbXsbsVN97oVsHZT4njktzr2Fei', 'TIRADOR', true, '2025-05-19 04:05:44.424631+00', NULL);
INSERT INTO public.users VALUES ('ce9ee56d-a1fb-4e96-8fba-2d818d617820', 'Abbie_Stark92@gmail.com', '$2b$12$UpbkdhrZX4luZ15gGzHRuudBibkPmjJkSVw6Dtdz6.7QghXi.vVrK', 'TIRADOR', true, '2025-05-19 04:05:46.538431+00', NULL);
INSERT INTO public.users VALUES ('dc261747-8a4b-4d6e-ad72-8ffc5d0eb543', 'Lulu_Rutherford@gmail.com', '$2b$12$8kq1FEnHo1clJ55ryd4ZtOunwht3vRFmmw/0sAdRTVIorwnEFJiRi', 'TIRADOR', true, '2025-05-19 04:05:47.613805+00', NULL);
INSERT INTO public.users VALUES ('85a91223-af1e-49e3-8df1-cce041b7ae65', 'Abbey87@yahoo.com', '$2b$12$jUdsgTSqV976FxB8/A1biO6QIWZHbNtjuVWXVMBEB47MCySMbMhWK', 'TIRADOR', true, '2025-05-19 04:05:48.596866+00', NULL);
INSERT INTO public.users VALUES ('987bb77e-5593-4748-a864-12d403109c06', 'Michel.Grady@gmail.com', '$2b$12$Yk2Wszqe9knsHPrVmtvvZ.rsKDZ/OvJW1h0ZcNahH5r5DF3fTApiC', 'TIRADOR', true, '2025-05-19 04:05:49.434503+00', NULL);
INSERT INTO public.users VALUES ('aa2b81fc-af08-4504-a4e9-1956d5b80dce', 'Bethany_Ortiz@gmail.com', '$2b$12$nreU298Fl.sreJIyvfG/eejjJ1m/WMAlerO040UYCR8WZtND4oVEq', 'TIRADOR', true, '2025-05-19 06:49:00.859734+00', NULL);
INSERT INTO public.users VALUES ('1e932276-868a-4ca3-9830-b5c1cd1ab22d', 'Quincy54@gmail.com', '$2b$12$ZJUHF100EQhRqpKPkKUQ0uUnjkE3zmSzHfqG2oq4Po7aAOmOT6dl.', 'TIRADOR', true, '2025-05-19 06:49:03.089748+00', NULL);
INSERT INTO public.users VALUES ('6283360b-9288-4f9b-8994-4aa78f170296', 'Emmie22@hotmail.com', '$2b$12$V886TAiHdjjMvY5S7qQJseK61HAgwz9IlgW3WeoKJSjHyydPlh6z6', 'TIRADOR', true, '2025-05-19 06:49:03.929102+00', NULL);
INSERT INTO public.users VALUES ('5ca4a711-81f9-4da5-aea2-499fbb4a9a9b', 'Paul29@gmail.com', '$2b$12$fDsHqn9XvjSXESxIjkD/8eqHn10/WU9tWZRKrlDhM87/ZrWluaryC', 'TIRADOR', true, '2025-05-19 06:49:04.520027+00', NULL);
INSERT INTO public.users VALUES ('5e4773c7-ddad-4b34-9fc3-ee02cb3bfadb', 'Nathanial12@hotmail.com', '$2b$12$w.WlIj3cGQ.ffgBwTj6c0uW63t9uSWXtfcp0gbUdrxM/xmFcEFTAC', 'TIRADOR', true, '2025-05-19 06:49:05.20807+00', NULL);
INSERT INTO public.users VALUES ('e4aee615-0851-4d40-94af-c8239aeef856', 'Penelope.Rutherford@hotmail.com', '$2b$12$9hanRNMx0.FwkGFYfAToZeOyuwdvVFUOcKb7VeLBdHY5YyVjl0PYS', 'TIRADOR', true, '2025-05-19 06:49:05.842574+00', NULL);
INSERT INTO public.users VALUES ('89792f23-d896-43f3-b452-e90dc6126223', 'Lyric39@yahoo.com', '$2b$12$rHjDhNejgEs2iAvmWIDY.e5PfGNBVSuuLYMTbwXJxidLbz9rWthRS', 'TIRADOR', true, '2025-05-19 06:49:06.435442+00', NULL);
INSERT INTO public.users VALUES ('1b9db5f4-7062-46b3-a399-edbabe0ae740', 'roberto.santos@yahoo.com', '$2b$12$VeS3KN2EvpNdEHrYW1by/OIJeA0ryGt7wQS0mjbKQHy.J8IX1xcQa', 'TIRADOR', true, '2025-05-19 06:49:19.198957+00', NULL);
INSERT INTO public.users VALUES ('f520d2ce-3662-4b6a-859f-2058c0b3ea84', 'Raheem3@yahoo.com', '$2b$12$RJwsu4cfiboUFKaEvEn3yut/lcZ0AeR48gmj/Q9htSUo7C.CfTiyK', 'TIRADOR', true, '2025-05-19 06:59:06.789501+00', NULL);
INSERT INTO public.users VALUES ('ff858c1c-c20c-4f00-85ce-5710d3d34a2c', 'Luella_Abshire19@yahoo.com', '$2b$12$Xmg8dlYNXpLsOKI6R3GZKONkeE5PoV80gDitMDqaWgwSboRdqNg7u', 'TIRADOR', true, '2025-05-19 06:59:07.590205+00', NULL);
INSERT INTO public.users VALUES ('fd6d5c95-6efb-41f0-9dbd-db7c6fc2a99c', 'Abby.Stamm@hotmail.com', '$2b$12$mnteSRDW1mnVqWL7DeJz5ePltEbJ9hjdWJRco.3E81czTKDioLO7a', 'TIRADOR', true, '2025-05-19 06:59:08.394531+00', NULL);
INSERT INTO public.users VALUES ('95a95791-b33d-427a-aa23-a6a0d64c155a', 'rolando.admin@gmail.com', '$2b$12$szzklwPT2x81Cy2jZvvE1ehrk6/0DedIZAFk3SLHHJvoGHDo5rAW.', 'ADMIN', true, '2025-05-19 06:50:02.560235+00', NULL);
INSERT INTO public.users VALUES ('3e2ccb71-1640-4cba-b95d-3a0916e813de', 'instructor@gmail.com', '$2b$12$VvpGveVmM2FY.aqVuZLB9OtM2xI23OayoJ/G8LEUi5Xl2ROMph4du', 'INSTRUCTOR', true, '2025-05-19 06:50:05.767794+00', '2025-05-19 07:32:45.388129+00');
INSERT INTO public.users VALUES ('e371cdf0-cebd-489d-8fef-569eee2cca26', 'whoangel@gmail.com', '$2b$12$MV98CiaZaZGiQDlsgDNseOhO30u3UaUbHkS7gu3ewFGuGw22CoreK', 'INSTRUCTOR_JEFE', true, '2025-05-19 06:49:59.317962+00', '2025-05-19 07:34:37.699443+00');
INSERT INTO public.users VALUES ('e80d49ad-3d95-4084-b781-2b18ea7e190a', 'Cheyenne_Lesch@yahoo.com', '$2b$12$Av5eNjHxylk7hdTxtHQxKOGXjYMmf1UsF0/HZHFSqslg/SKfGaJqi', 'TIRADOR', true, '2025-05-21 01:58:41.520785+00', NULL);
INSERT INTO public.users VALUES ('4bffa0d0-612a-4da6-95b1-1c6e41340f32', 'Verner_Runte@hotmail.com', '$2b$12$1TLAxR1hJu/AIEM0BxOmNetBRJ7Ud.ES.JaGE06gpocHT0IAZGhaK', 'TIRADOR', true, '2025-05-21 02:51:50.47758+00', NULL);


--
-- Data for Name: shooting_clubs; Type: TABLE DATA; Schema: public; Owner: angel
--



--
-- Data for Name: shooters; Type: TABLE DATA; Schema: public; Owner: angel
--

INSERT INTO public.shooters VALUES ('bb63e773-85b9-4283-aaff-becb82e5401b', NULL, 'REGULAR', NULL, '2025-05-19 04:05:33.607473+00', NULL, NULL, NULL);
INSERT INTO public.shooters VALUES ('398b551e-a65d-4681-bcb7-57590175edd9', NULL, 'REGULAR', NULL, '2025-05-19 04:05:44.424631+00', NULL, NULL, NULL);
INSERT INTO public.shooters VALUES ('ce9ee56d-a1fb-4e96-8fba-2d818d617820', NULL, 'REGULAR', NULL, '2025-05-19 04:05:46.538431+00', NULL, NULL, NULL);
INSERT INTO public.shooters VALUES ('dc261747-8a4b-4d6e-ad72-8ffc5d0eb543', NULL, 'REGULAR', NULL, '2025-05-19 04:05:47.613805+00', NULL, NULL, NULL);
INSERT INTO public.shooters VALUES ('85a91223-af1e-49e3-8df1-cce041b7ae65', NULL, 'REGULAR', NULL, '2025-05-19 04:05:48.596866+00', NULL, NULL, NULL);
INSERT INTO public.shooters VALUES ('987bb77e-5593-4748-a864-12d403109c06', NULL, 'REGULAR', NULL, '2025-05-19 04:05:49.434503+00', NULL, NULL, NULL);
INSERT INTO public.shooters VALUES ('aa2b81fc-af08-4504-a4e9-1956d5b80dce', NULL, 'REGULAR', NULL, '2025-05-19 06:49:00.859734+00', NULL, NULL, NULL);
INSERT INTO public.shooters VALUES ('1e932276-868a-4ca3-9830-b5c1cd1ab22d', NULL, 'REGULAR', NULL, '2025-05-19 06:49:03.089748+00', NULL, NULL, NULL);
INSERT INTO public.shooters VALUES ('5ca4a711-81f9-4da5-aea2-499fbb4a9a9b', NULL, 'REGULAR', NULL, '2025-05-19 06:49:04.520027+00', NULL, NULL, NULL);
INSERT INTO public.shooters VALUES ('5e4773c7-ddad-4b34-9fc3-ee02cb3bfadb', NULL, 'REGULAR', NULL, '2025-05-19 06:49:05.20807+00', NULL, NULL, NULL);
INSERT INTO public.shooters VALUES ('e4aee615-0851-4d40-94af-c8239aeef856', NULL, 'REGULAR', NULL, '2025-05-19 06:49:05.842574+00', NULL, NULL, NULL);
INSERT INTO public.shooters VALUES ('89792f23-d896-43f3-b452-e90dc6126223', NULL, 'REGULAR', NULL, '2025-05-19 06:49:06.435442+00', NULL, NULL, NULL);
INSERT INTO public.shooters VALUES ('e371cdf0-cebd-489d-8fef-569eee2cca26', NULL, 'REGULAR', NULL, '2025-05-19 06:49:59.317962+00', NULL, NULL, NULL);
INSERT INTO public.shooters VALUES ('95a95791-b33d-427a-aa23-a6a0d64c155a', NULL, 'REGULAR', NULL, '2025-05-19 06:50:02.560235+00', NULL, NULL, NULL);
INSERT INTO public.shooters VALUES ('3e2ccb71-1640-4cba-b95d-3a0916e813de', NULL, 'REGULAR', NULL, '2025-05-19 06:50:05.767794+00', NULL, NULL, NULL);
INSERT INTO public.shooters VALUES ('f520d2ce-3662-4b6a-859f-2058c0b3ea84', NULL, 'REGULAR', NULL, '2025-05-19 06:59:06.789501+00', NULL, NULL, NULL);
INSERT INTO public.shooters VALUES ('ff858c1c-c20c-4f00-85ce-5710d3d34a2c', NULL, 'REGULAR', NULL, '2025-05-19 06:59:07.590205+00', NULL, NULL, NULL);
INSERT INTO public.shooters VALUES ('fd6d5c95-6efb-41f0-9dbd-db7c6fc2a99c', NULL, 'REGULAR', NULL, '2025-05-19 06:59:08.394531+00', NULL, NULL, NULL);
INSERT INTO public.shooters VALUES ('e80d49ad-3d95-4084-b781-2b18ea7e190a', NULL, 'REGULAR', NULL, '2025-05-21 01:58:41.520785+00', NULL, NULL, NULL);
INSERT INTO public.shooters VALUES ('4bffa0d0-612a-4da6-95b1-1c6e41340f32', NULL, 'REGULAR', NULL, '2025-05-21 02:51:50.47758+00', NULL, NULL, NULL);
INSERT INTO public.shooters VALUES ('1b9db5f4-7062-46b3-a399-edbabe0ae740', NULL, 'REGULAR', 'Soldado', '2025-05-19 06:49:19.198957+00', '2025-05-24 22:28:32.230119+00', NULL, NULL);
INSERT INTO public.shooters VALUES ('6283360b-9288-4f9b-8994-4aa78f170296', NULL, 'CONFIABLE', NULL, '2025-05-19 06:49:03.929102+00', '2025-05-24 22:29:20.422309+00', NULL, NULL);


--
-- Data for Name: individual_practice_sessions; Type: TABLE DATA; Schema: public; Owner: angel
--

INSERT INTO public.individual_practice_sessions VALUES ('d2f4af45-cf8a-4e9c-8002-0bf78657cb1c', '1b9db5f4-7062-46b3-a399-edbabe0ae740', '3e2ccb71-1640-4cba-b95d-3a0916e813de', '2025-05-19 07:40:43.914389', 'No especificada', 39, 38, 97.43589743589743, '2025-05-19 07:40:43.912396+00', '2025-05-19 08:31:17.052689+00', false);
INSERT INTO public.individual_practice_sessions VALUES ('f981188b-b599-45cd-82f8-9338442758d3', '1b9db5f4-7062-46b3-a399-edbabe0ae740', '3e2ccb71-1640-4cba-b95d-3a0916e813de', '2025-05-21 00:34:45.378768', 'No especificada', 13, 9, 69.23076923076923, '2025-05-21 00:34:45.37419+00', '2025-05-21 00:37:31.481192+00', false);


--
-- Data for Name: practice_evaluations; Type: TABLE DATA; Schema: public; Owner: angel
--

INSERT INTO public.practice_evaluations VALUES ('5944706c-b22e-44e4-9c53-19210802d515', 'f981188b-b599-45cd-82f8-9338442758d3', NULL, 69.2, 'MEDIO', NULL, NULL, NULL, '2025-05-21 00:37:31.481192+00', NULL, 8, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-05-21 00:27:58.888767');
INSERT INTO public.practice_evaluations VALUES ('fa66cb8a-a655-4495-840c-08f50a3d555d', 'd2f4af45-cf8a-4e9c-8002-0bf78657cb1c', NULL, 97.4, 'EXPERTO', NULL, NULL, NULL, '2025-05-19 08:31:17.052689+00', '2025-05-21 01:19:06.194346+00', NULL, 7, NULL, NULL, 10, NULL, NULL, NULL, NULL, NULL, NULL, '2025-05-19 08:31:15.852853');


--
-- Data for Name: targets; Type: TABLE DATA; Schema: public; Owner: angel
--

INSERT INTO public.targets VALUES ('9f3fb4e1-681c-497c-b237-9eb87f0e1502', 'Diana Olímpica', 'CONCENTRIC', 'Blanco oficial para competiciones olímpicas de tiro', '{"rings": [{"radius": 5, "score": 10, "color": "black"}, {"radius": 10, "score": 9, "color": "black"}, {"radius": 15, "score": 8, "color": "black"}, {"radius": 20, "score": 7, "color": "white"}, {"radius": 25, "score": 6, "color": "white"}, {"radius": 30, "score": 5, "color": "white"}], "center": {"x": 0, "y": 0}}', '40cm x 40cm', 10, true, '2025-05-19 07:06:41.291387+00', NULL);


--
-- Data for Name: weapons; Type: TABLE DATA; Schema: public; Owner: angel
--

INSERT INTO public.weapons VALUES ('fdf40c58-128a-4505-a771-c22ac45fc20f', 'Glock 19', 'Glock', 'Gen 5', 'G19-GEN5-12345', 'PISTOL', '9mm', 'Una pistola semiautomática compacta y popular.', true, '2025-05-19 07:19:07.010008+00', NULL);
INSERT INTO public.weapons VALUES ('3253672d-7540-4ace-888f-c4caf7e616ad', 'AK-47', 'Kalashnikov', 'Avtomat Kalashnikova образца 1947 года', 'AK47-762-001', 'RIFLE', '7.62x39mm', 'Un rifle de asalto icónico y robusto.', true, '2025-05-19 07:20:01.729963+00', NULL);


--
-- Data for Name: practice_exercises; Type: TABLE DATA; Schema: public; Owner: angel
--

INSERT INTO public.practice_exercises VALUES ('d40a699e-feb2-4d26-9d5d-34fba6265177', 'd2f4af45-cf8a-4e9c-8002-0bf78657cb1c', '576d5c29-3db5-4735-b432-63f4db72fc0b', '10 metros', NULL, NULL, 35, 29, 29, 100, NULL, '2025-05-19 07:46:25.50297+00', NULL, '9f3fb4e1-681c-497c-b237-9eb87f0e1502', 'fdf40c58-128a-4505-a771-c22ac45fc20f', 'e42e0f37-5552-475b-bc16-b4684b9db90e');
INSERT INTO public.practice_exercises VALUES ('1b8afbfe-b40d-4721-b7e7-41f1cf242820', 'd2f4af45-cf8a-4e9c-8002-0bf78657cb1c', '576d5c29-3db5-4735-b432-63f4db72fc0b', '10 metros', NULL, NULL, 10, 10, 9, 90, NULL, '2025-05-19 07:47:06.672195+00', NULL, '9f3fb4e1-681c-497c-b237-9eb87f0e1502', 'fdf40c58-128a-4505-a771-c22ac45fc20f', 'e42e0f37-5552-475b-bc16-b4684b9db90e');
INSERT INTO public.practice_exercises VALUES ('1acf5d16-dd4f-4672-b138-93a6db6f9b0e', 'f981188b-b599-45cd-82f8-9338442758d3', '576d5c29-3db5-4735-b432-63f4db72fc0b', '5 metros', NULL, NULL, 20, 13, 9, 69.23076923076923, NULL, '2025-05-21 00:36:06.866451+00', NULL, '9f3fb4e1-681c-497c-b237-9eb87f0e1502', 'fdf40c58-128a-4505-a771-c22ac45fc20f', 'e42e0f37-5552-475b-bc16-b4684b9db90e');


--
-- Data for Name: shooter_performance_logs; Type: TABLE DATA; Schema: public; Owner: angel
--



--
-- Data for Name: shooter_stats; Type: TABLE DATA; Schema: public; Owner: angel
--

INSERT INTO public.shooter_stats VALUES ('bb63e773-85b9-4283-aaff-becb82e5401b', 0, 0, 0, 0, 0, 0, 0, 0, NULL, '2025-05-19 04:05:33.607473+00', NULL, 0, 0, 0, 0, 0);
INSERT INTO public.shooter_stats VALUES ('398b551e-a65d-4681-bcb7-57590175edd9', 0, 0, 0, 0, 0, 0, 0, 0, NULL, '2025-05-19 04:05:44.424631+00', NULL, 0, 0, 0, 0, 0);
INSERT INTO public.shooter_stats VALUES ('ce9ee56d-a1fb-4e96-8fba-2d818d617820', 0, 0, 0, 0, 0, 0, 0, 0, NULL, '2025-05-19 04:05:46.538431+00', NULL, 0, 0, 0, 0, 0);
INSERT INTO public.shooter_stats VALUES ('dc261747-8a4b-4d6e-ad72-8ffc5d0eb543', 0, 0, 0, 0, 0, 0, 0, 0, NULL, '2025-05-19 04:05:47.613805+00', NULL, 0, 0, 0, 0, 0);
INSERT INTO public.shooter_stats VALUES ('85a91223-af1e-49e3-8df1-cce041b7ae65', 0, 0, 0, 0, 0, 0, 0, 0, NULL, '2025-05-19 04:05:48.596866+00', NULL, 0, 0, 0, 0, 0);
INSERT INTO public.shooter_stats VALUES ('987bb77e-5593-4748-a864-12d403109c06', 0, 0, 0, 0, 0, 0, 0, 0, NULL, '2025-05-19 04:05:49.434503+00', NULL, 0, 0, 0, 0, 0);
INSERT INTO public.shooter_stats VALUES ('aa2b81fc-af08-4504-a4e9-1956d5b80dce', 0, 0, 0, 0, 0, 0, 0, 0, NULL, '2025-05-19 06:49:00.859734+00', NULL, 0, 0, 0, 0, 0);
INSERT INTO public.shooter_stats VALUES ('1e932276-868a-4ca3-9830-b5c1cd1ab22d', 0, 0, 0, 0, 0, 0, 0, 0, NULL, '2025-05-19 06:49:03.089748+00', NULL, 0, 0, 0, 0, 0);
INSERT INTO public.shooter_stats VALUES ('6283360b-9288-4f9b-8994-4aa78f170296', 0, 0, 0, 0, 0, 0, 0, 0, NULL, '2025-05-19 06:49:03.929102+00', NULL, 0, 0, 0, 0, 0);
INSERT INTO public.shooter_stats VALUES ('5ca4a711-81f9-4da5-aea2-499fbb4a9a9b', 0, 0, 0, 0, 0, 0, 0, 0, NULL, '2025-05-19 06:49:04.520027+00', NULL, 0, 0, 0, 0, 0);
INSERT INTO public.shooter_stats VALUES ('5e4773c7-ddad-4b34-9fc3-ee02cb3bfadb', 0, 0, 0, 0, 0, 0, 0, 0, NULL, '2025-05-19 06:49:05.20807+00', NULL, 0, 0, 0, 0, 0);
INSERT INTO public.shooter_stats VALUES ('e4aee615-0851-4d40-94af-c8239aeef856', 0, 0, 0, 0, 0, 0, 0, 0, NULL, '2025-05-19 06:49:05.842574+00', NULL, 0, 0, 0, 0, 0);
INSERT INTO public.shooter_stats VALUES ('89792f23-d896-43f3-b452-e90dc6126223', 0, 0, 0, 0, 0, 0, 0, 0, NULL, '2025-05-19 06:49:06.435442+00', NULL, 0, 0, 0, 0, 0);
INSERT INTO public.shooter_stats VALUES ('e371cdf0-cebd-489d-8fef-569eee2cca26', 0, 0, 0, 0, 0, 0, 0, 0, NULL, '2025-05-19 06:49:59.317962+00', NULL, 0, 0, 0, 0, 0);
INSERT INTO public.shooter_stats VALUES ('95a95791-b33d-427a-aa23-a6a0d64c155a', 0, 0, 0, 0, 0, 0, 0, 0, NULL, '2025-05-19 06:50:02.560235+00', NULL, 0, 0, 0, 0, 0);
INSERT INTO public.shooter_stats VALUES ('3e2ccb71-1640-4cba-b95d-3a0916e813de', 0, 0, 0, 0, 0, 0, 0, 0, NULL, '2025-05-19 06:50:05.767794+00', NULL, 0, 0, 0, 0, 0);
INSERT INTO public.shooter_stats VALUES ('f520d2ce-3662-4b6a-859f-2058c0b3ea84', 0, 0, 0, 0, 0, 0, 0, 0, NULL, '2025-05-19 06:59:06.789501+00', NULL, 0, 0, 0, 0, 0);
INSERT INTO public.shooter_stats VALUES ('ff858c1c-c20c-4f00-85ce-5710d3d34a2c', 0, 0, 0, 0, 0, 0, 0, 0, NULL, '2025-05-19 06:59:07.590205+00', NULL, 0, 0, 0, 0, 0);
INSERT INTO public.shooter_stats VALUES ('fd6d5c95-6efb-41f0-9dbd-db7c6fc2a99c', 0, 0, 0, 0, 0, 0, 0, 0, NULL, '2025-05-19 06:59:08.394531+00', NULL, 0, 0, 0, 0, 0);
INSERT INTO public.shooter_stats VALUES ('1b9db5f4-7062-46b3-a399-edbabe0ae740', 52, 90, 0, 0, 0, 0, 0, 0, NULL, '2025-05-19 06:49:19.198957+00', '2025-05-21 00:37:31.510798+00', -28.200000000000003, 83.30000000000001, 0, 0, 0);
INSERT INTO public.shooter_stats VALUES ('e80d49ad-3d95-4084-b781-2b18ea7e190a', 0, 0, 0, 0, 0, 0, 0, 0, NULL, '2025-05-21 01:58:41.520785+00', NULL, 0, 0, 0, 0, 0);
INSERT INTO public.shooter_stats VALUES ('4bffa0d0-612a-4da6-95b1-1c6e41340f32', 0, 0, 0, 0, 0, 0, 0, 0, NULL, '2025-05-21 02:51:50.47758+00', NULL, 0, 0, 0, 0, 0);


--
-- Data for Name: target_images; Type: TABLE DATA; Schema: public; Owner: angel
--



--
-- Data for Name: target_analyses; Type: TABLE DATA; Schema: public; Owner: angel
--



--
-- Data for Name: shooting_recommendations; Type: TABLE DATA; Schema: public; Owner: angel
--



--
-- Data for Name: user_biometric_data; Type: TABLE DATA; Schema: public; Owner: angel
--



--
-- Data for Name: user_medical_data; Type: TABLE DATA; Schema: public; Owner: angel
--



--
-- Data for Name: user_personal_data; Type: TABLE DATA; Schema: public; Owner: angel
--

INSERT INTO public.user_personal_data VALUES ('95a95791-b33d-427a-aa23-a6a0d64c155a', 'Narciso', 'Tyree', 'Senger', NULL, '483-948-7657', '2001-11-29', 'Juddmouth', 'Oaxaca', 'ZA', '2025-05-19 07:29:10.258204+00', NULL, 'N/A');
INSERT INTO public.user_personal_data VALUES ('1b9db5f4-7062-46b3-a399-edbabe0ae740', 'Brianne', 'Rosendo', 'Klein', NULL, '642-616-6802', '2001-11-29', 'West Natalie', 'Oaxaca', 'AR', '2025-05-19 07:29:35.932471+00', NULL, 'N/A');
INSERT INTO public.user_personal_data VALUES ('e371cdf0-cebd-489d-8fef-569eee2cca26', 'Kevin', 'Alize', 'Pollich', NULL, '782-863-1797', '2001-11-29', 'Haleymouth', 'Oaxaca', 'MS', '2025-05-19 07:29:50.628024+00', NULL, 'N/A');
INSERT INTO public.user_personal_data VALUES ('3e2ccb71-1640-4cba-b95d-3a0916e813de', 'Zora', 'Wilfrid', 'Schneider', NULL, '320-898-2906', '2001-11-29', 'Vivianechester', 'Oaxaca', 'MZ', '2025-05-19 07:30:03.443265+00', NULL, 'N/A');


--
-- Data for Name: weapon_ammunition_compatibility; Type: TABLE DATA; Schema: public; Owner: angel
--

INSERT INTO public.weapon_ammunition_compatibility VALUES ('cb349321-df73-468e-8df6-d4c7a139b68a', '3253672d-7540-4ace-888f-c4caf7e616ad', '37e8438f-2a4d-4dca-8700-e54f4092769d', '2025-05-19 07:26:38.111439+00');
INSERT INTO public.weapon_ammunition_compatibility VALUES ('b83346a3-fcf0-41e3-8ec8-ba32b5d1b8e5', '3253672d-7540-4ace-888f-c4caf7e616ad', '59d137e3-4e8d-4a42-8766-f7e66501008e', '2025-05-19 07:27:02.36333+00');
INSERT INTO public.weapon_ammunition_compatibility VALUES ('65426bb4-9bf2-4dc0-aa1a-d5856c4bdf64', 'fdf40c58-128a-4505-a771-c22ac45fc20f', 'e42e0f37-5552-475b-bc16-b4684b9db90e', '2025-05-19 07:27:44.930853+00');


--
-- PostgreSQL database dump complete
--

