import pandas as pd
import re
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import os
from unidecode import unidecode
from collections import Counter

text = '''
Richie Rude	13:01.870	(3)	06:30.790	(42)	04:07.200	(1)	03:24.990	(1)	21:30.800	(1)	48:35.650	(1)
Jesse Melamed	13:06.040	(7)	05:54.970	(1)	04:19.340	(20)	03:26.230	(7)	21:56.200	(4)	48:42.780	(2)
Josh Carlson	13:03.620	(5)	06:00.020	(3)	04:12.940	(7)	03:42.120	(47)	21:45.600	(2)	48:44.300	(3)
Nico Lau	13:17.590	(19)	06:07.790	(9)	04:10.800	(5)	03:25.280	(2)	21:57.640	(6)	48:59.100	(4)
Martin Maes	13:06.470	(8)	06:04.020	(5)	04:10.390	(3)	03:26.950	(8)	22:11.720	(13)	48:59.550	(5)
Damien Oton	13:17.240	(18)	06:03.870	(4)	04:09.950	(2)	03:27.940	(10)	22:05.020	(9)	49:04.020	(6)
Sam Blenkinsop	12:55.250	(1)	06:18.750	(26)	04:18.370	(17)	03:34.330	(23)	21:58.150	(7)	49:04.850	(7)
Sam Hill	13:13.270	(14)	06:06.860	(6)	04:19.500	(21)	03:25.730	(5)	22:03.310	(8)	49:08.670	(8)
Curtis Keene	13:02.690	(4)	06:17.390	(22)	04:18.330	(16)	03:38.900	(39)	21:57.440	(5)	49:14.750	(9)
Justin Leov	13:13.530	(15)	06:11.730	(12)	04:15.150	(10)	03:29.000	(12)	22:13.810	(15)	49:23.220	(10)
Robin Wallner	13:16.970	(17)	05:59.940	(2)	04:21.250	(28)	03:34.740	(24)	22:11.710	(12)	49:24.610	(11)
Rémi Gauvin	13:10.640	(12)	06:15.920	(19)	04:22.120	(31)	03:31.160	(16)	22:05.380	(10)	49:25.220	(12)
Rene Wildhaber	13:18.650	(23)	06:13.700	(17)	04:17.250	(13)	03:31.100	(15)	22:05.780	(11)	49:26.480	(13)
Mckay Vezina	13:08.150	(9)	06:12.340	(13)	04:20.680	(24)	03:29.850	(13)	22:25.930	(19)	49:36.950	(14)
Matti Lehikoinen	13:17.760	(20)	06:11.400	(11)	04:15.280	(11)	03:25.710	(4)	22:29.140	(22)	49:39.290	(15)
Gregory Callaghan	13:37.910	(50)	06:12.780	(14)	04:12.180	(6)	03:25.890	(6)	22:14.080	(16)	49:42.840	(16)
Mark Scott	13:21.950	(29)	06:18.250	(24)	04:17.590	(14)	03:33.140	(20)	22:12.430	(14)	49:43.360	(17)
Jerome Clementz	13:21.420	(28)	06:13.220	(16)	04:17.800	(15)	03:27.490	(9)	22:26.990	(20)	49:46.920	(18)
Yoann Barelli	13:26.210	(33)	06:20.250	(30)	04:22.890	(33)	03:32.400	(19)	22:19.840	(18)	50:01.590	(19)
Francois Bailly-Maitre	13:32.100	(43)	06:20.000	(28)	04:18.780	(19)	03:35.250	(28)	22:17.740	(17)	50:03.870	(20)
Joe Barnes	13:28.270	(39)	06:07.610	(7)	04:16.800	(12)	03:35.840	(30)	22:43.870	(28)	50:12.390	(21)
Troy Brosnan	13:04.980	(6)	06:14.760	(18)	04:32.100	(66)	03:41.370	(45)	22:50.510	(32)	50:23.720	(22)
Cody Kelley	13:16.820	(16)	06:27.640	(37)	04:23.910	(36)	03:42.240	(48)	22:36.750	(25)	50:27.360	(23)
Joseph Nation	13:18.280	(21)	06:19.640	(27)	04:22.000	(30)	03:35.760	(29)	22:52.390	(33)	50:28.070	(24)
Thomas Lapeyrie	13:37.740	(49)	06:22.010	(31)	04:24.960	(38)	03:35.880	(31)	22:28.740	(21)	50:29.330	(25)
Luke Strobel	13:20.290	(25)	06:23.190	(32)	04:23.250	(35)	03:45.320	(49)	22:37.740	(26)	50:29.790	(26)
Peter Ostroski	13:23.610	(30)	06:34.380	(47)	04:20.900	(25)	03:28.450	(11)	22:44.930	(29)	50:32.270	(27)
Wyn Masters	13:18.410	(22)	06:30.020	(41)	04:28.470	(51)	03:45.570	(50)	22:30.170	(23)	50:32.640	(28)
Connor Fearon	12:58.900	(2)	06:35.400	(52)	04:28.580	(53)	03:37.190	(35)	22:56.170	(36)	50:36.240	(29)
Pierre Charles Georges	13:28.230	(38)	06:25.500	(34)	04:27.700	(49)	03:34.860	(26)	22:41.510	(27)	50:37.800	(30)
Theo Galy	13:20.870	(26)	06:26.300	(36)	04:25.300	(41)	03:32.270	(18)	22:56.540	(37)	50:41.280	(31)
Evan Guthrie	13:40.080	(56)	06:16.690	(21)	04:19.940	(22)	03:34.800	(25)	22:52.780	(34)	50:44.290	(32)
Iago Garay	13:27.670	(37)	06:33.610	(45)	04:23.010	(34)	03:33.730	(22)	22:48.240	(31)	50:46.260	(33)
Remy Absalon	13:27.270	(36)	06:15.930	(20)	04:18.740	(18)	03:51.450	(64)	22:52.910	(35)	50:46.300	(34)
Mathew Stuttard	13:20.280	(24)	06:35.380	(51)	04:50.930	(107)	03:36.890	(34)	22:34.070	(24)	50:57.550	(35)
Ludovic May	13:32.580	(44)	06:25.990	(35)	04:27.280	(47)	03:38.430	(38)	23:05.300	(42)	51:09.580	(36)
Ruaridh Cunningham	13:26.950	(35)	06:28.620	(39)	04:33.310	(77)	03:35.990	(32)	23:14.060	(47)	51:18.930	(37)
Tyler Morland	13:36.670	(47)	06:23.600	(33)	04:32.490	(72)	03:40.110	(41)	23:06.070	(43)	51:18.940	(38)
Daniel Wolfe	13:34.790	(45)	06:29.460	(40)	04:33.610	(78)	03:40.370	(42)	23:06.090	(44)	51:24.320	(39)
Gary Forrest	13:38.070	(51)	06:27.720	(38)	04:24.740	(37)	03:33.620	(21)	23:23.600	(55)	51:27.750	(40)
Stu Dickson	13:41.790	(57)	06:34.570	(48)	04:25.050	(39)	03:50.400	(60)	23:05.010	(41)	51:36.820	(41)
Duncan Riffle	13:39.120	(54)	06:48.010	(79)	04:31.700	(65)	03:54.300	(71)	22:47.990	(30)	51:41.120	(42)
Kyle Warner	13:47.600	(62)	06:45.480	(71)	04:22.530	(32)	03:46.150	(51)	23:00.600	(39)	51:42.360	(43)
Rupert Chapman	13:21.110	(27)	06:20.220	(29)	04:29.800	(59)	04:31.150	(110)	23:03.160	(40)	51:45.440	(44)
Shane Gayton	13:29.410	(40)	06:42.810	(64)	04:31.420	(63)	03:54.470	(72)	23:08.360	(45)	51:46.470	(45)
Michael Hannah	13:42.150	(59)	06:42.880	(65)	04:25.700	(43)	03:37.200	(36)	23:18.940	(50)	51:46.870	(46)
Stephen Matthews	13:30.850	(42)	06:38.450	(56)	04:27.550	(48)	04:05.280	(95)	23:10.130	(46)	51:52.260	(47)
Antoine Caron	13:58.010	(74)	06:34.620	(49)	04:21.000	(27)	03:34.970	(27)	23:25.610	(56)	51:54.210	(48)
Matt Ryan	13:48.500	(64)	06:33.790	(46)	04:32.440	(71)	03:40.500	(43)	23:22.100	(53)	51:57.330	(49)
Edward Masters	13:49.810	(66)	06:42.660	(63)	04:35.280	(82)	03:55.430	(73)	22:56.720	(38)	51:59.900	(50)
Chris Heath	13:36.370	(46)	06:47.870	(78)	04:30.580	(61)	03:48.470	(57)	23:25.850	(57)	52:09.140	(51)
Dylan Wolsky	13:43.360	(60)	06:44.460	(69)	04:35.270	(81)	03:48.860	(58)	23:20.360	(51)	52:12.310	(52)
Brook Macdonald	13:49.660	(65)	06:42.920	(66)	04:31.650	(64)	03:46.940	(53)	23:21.880	(52)	52:13.050	(53)
Liam Moynihan	13:52.220	(69)	06:47.860	(77)	04:29.490	(55)	03:47.770	(56)	23:23.250	(54)	52:20.590	(54)
Alexander Mcguinnis	13:50.890	(67)	06:38.670	(57)	04:25.190	(40)	03:57.890	(81)	23:28.510	(58)	52:21.150	(55)
Ben Forbes	13:54.240	(71)	06:47.630	(76)	04:28.520	(52)	03:53.360	(69)	23:18.380	(48)	52:22.130	(56)
David Harder	14:25.670	(104)	06:38.140	(55)	04:32.200	(67)	03:25.560	(3)	23:29.650	(60)	52:31.220	(57)
Chris Del Bosco	13:41.930	(58)	06:31.390	(44)	04:27.130	(46)	03:47.150	(54)	24:03.780	(76)	52:31.380	(58)
James Shirley	14:04.790	(84)	06:46.140	(74)	04:32.370	(69)	03:46.690	(52)	23:31.700	(62)	52:41.690	(59)
Cory Sullivan	13:59.170	(77)	06:40.290	(59)	04:32.910	(75)	03:56.570	(76)	23:36.380	(66)	52:45.320	(60)
Chris Johnston	13:26.550	(34)	06:18.620	(25)	04:20.120	(23)	03:38.330	(37)	25:03.910	(92)	52:47.530	(61)
Aaron Bradford	14:03.180	(81)	06:50.930	(82)	04:26.820	(44)	03:57.830	(80)	23:29.450	(59)	52:48.210	(62)
Adam Craig	14:25.370	(103)	06:31.140	(43)	04:32.900	(74)	04:00.580	(87)	23:18.800	(49)	52:48.790	(63)
Spencer Wight	14:01.720	(79)	06:36.720	(54)	04:32.760	(73)	03:52.370	(66)	23:50.460	(71)	52:54.030	(64)
Clément Benoit	13:54.530	(72)	06:42.580	(62)	04:25.460	(42)	04:13.140	(102)	23:41.890	(67)	52:57.600	(65)
Tobias Reiser	14:03.660	(82)	06:43.420	(68)	04:32.280	(68)	03:49.160	(59)	23:50.140	(70)	52:58.660	(66)
Sam Flockhart	14:34.700	(109)	06:45.870	(72)	04:29.130	(54)	03:41.500	(46)	23:31.760	(63)	53:02.960	(67)
Evan Geankoplis	13:38.110	(52)	07:06.600	(91)	04:33.270	(76)	03:57.150	(79)	23:53.630	(72)	53:08.760	(68)
Alvaro Hidalgo	14:01.060	(78)	06:50.660	(81)	04:34.590	(80)	03:47.610	(55)	24:00.830	(74)	53:14.750	(69)
Markus Reiser	14:04.020	(83)	07:00.680	(88)	04:41.540	(93)	03:57.030	(78)	23:34.510	(65)	53:17.780	(70)
Ajay Jones	14:10.880	(90)	06:54.490	(85)	04:41.990	(95)	03:31.210	(17)	24:12.450	(79)	53:31.020	(71)
Carl Jones	14:18.090	(97)	06:55.930	(86)	04:29.690	(57)	04:02.150	(88)	23:49.070	(69)	53:34.930	(72)
William Cadham	14:09.550	(89)	06:41.280	(61)	04:29.990	(60)	03:50.660	(61)	24:23.870	(81)	53:35.350	(73)
Evan Turpen	13:51.760	(68)	07:26.280	(105)	04:38.580	(88)	03:56.770	(77)	23:46.820	(68)	53:40.210	(74)
Jamie Biluk	14:12.500	(91)	06:53.700	(84)	04:37.820	(86)	03:56.520	(75)	24:11.490	(78)	53:52.030	(75)
Johnny Magis	14:15.830	(96)	07:08.080	(92)	04:42.990	(97)	04:04.490	(93)	24:01.020	(75)	54:12.410	(76)
Jonas Bahler	14:12.720	(92)	07:08.930	(93)	04:38.840	(89)	03:52.850	(67)	24:20.560	(80)	54:13.900	(77)
Nathan Riddle	14:15.260	(94)	06:44.810	(70)	04:41.960	(94)	04:03.750	(90)	24:31.110	(84)	54:16.890	(78)
Davis English	14:09.220	(88)	06:45.950	(73)	04:42.420	(96)	03:59.640	(85)	24:47.760	(88)	54:24.990	(79)
Alois Von Wurstemberger	13:58.670	(75)	07:27.770	(107)	04:41.020	(92)	04:03.780	(91)	24:36.600	(86)	54:47.840	(80)
Marco Osborne	13:23.650	(31)	06:17.590	(23)	04:21.610	(29)	03:29.910	(14)	22:19.380	(100)	49:52.140	(81)
Ty Hathaway	14:18.360	(98)	07:26.460	(106)	04:44.170	(100)	04:05.290	(96)	24:24.220	(82)	54:58.500	(82)
Santiago Perez	14:12.840	(93)	07:23.570	(101)	05:34.070	(115)	03:50.910	(62)	23:59.390	(73)	55:00.780	(83)
Tom Maes	14:37.690	(110)	07:12.000	(98)	04:43.700	(98)	04:09.970	(98)	24:27.540	(83)	55:10.900	(84)
Nick Hardin	14:04.820	(85)	07:24.020	(103)	04:46.120	(102)	04:38.200	(111)	24:34.650	(85)	55:27.810	(85)
Timothée Oppliger	14:19.140	(99)	07:29.450	(108)	04:51.980	(108)	04:02.260	(89)	24:53.430	(91)	55:36.260	(86)
Ulysse Francoglio	14:51.980	(118)	07:19.480	(100)	04:43.740	(99)	03:59.690	(86)	24:52.920	(90)	55:47.810	(87)
Drew Pautler	14:25.790	(105)	06:57.300	(87)	04:33.630	(79)	04:11.740	(100)	25:43.190	(94)	55:51.650	(88)
Cedric Carrez	14:23.900	(102)	08:15.650	(113)	04:45.280	(101)	03:53.290	(68)	24:47.470	(87)	56:05.590	(89)
Mark Milward	14:31.650	(107)	07:42.680	(109)	04:54.220	(110)	04:11.000	(99)	24:51.300	(89)	56:10.850	(90)
Shane Jensen	14:41.970	(112)	07:10.990	(96)	04:48.280	(105)	04:25.430	(108)	25:20.150	(93)	56:26.820	(91)
Chris Mandell	14:42.430	(114)	07:11.190	(97)	05:02.600	(113)	03:58.460	(82)	25:48.420	(97)	56:43.100	(92)
Kevin Smallman	14:57.680	(119)	07:23.860	(102)	04:53.310	(109)	04:30.100	(109)	25:46.510	(96)	57:31.460	(93)
Sidney Slotegraaf	14:28.110	(106)	06:40.370	(60)	04:32.430	(70)	09:03.020	(113)	23:30.120	(61)	58:14.050	(94)
Fraser Andrew	14:21.380	(100)	07:18.250	(99)	04:46.480	(103)	06:20.080	(112)	25:46.410	(95)	58:32.600	(95)
Sam Sharp	15:24.950	(120)	07:58.200	(112)	04:59.320	(111)	04:22.660	(107)	25:59.100	(98)	58:44.230	(96)
Daisuke Kurosawa	14:48.660	(115)	08:50.410	(114)	05:01.810	(112)	04:12.480	(101)	25:59.210	(99)	58:52.570	(97)
Christopher Panozzo	13:11.490	(13)	06:36.060	(53)	04:20.900	(25)	03:36.610	(33)	31:11.620	(102)	58:56.680	(98)
Geoff Kabush	22:51.570	(123)	06:39.510	(58)	04:29.550	(56)	03:53.560	(70)	23:32.050	(64)	1:01:26.240	(99)
Fabien Cousinié	13:46.710	(61)	07:05.750	(90)	04:37.630	(85)	03:59.350	(83)	32:55.090	(104)	1:02:24.530	(100)
Jubal Davis	13:30.240	(41)	06:49.300	(80)	04:30.950	(62)	03:40.970	(44)	34:53.680	(107)	1:03:25.140	(101)
Adrian Camposilvan	14:51.460	(117)	07:55.570	(111)	05:12.870	(114)	04:19.780	(105)	31:54.740	(103)	1:04:14.420	(102)
Simon Gegenheimer	14:40.430	(111)	07:09.130	(94)	04:36.830	(83)	04:15.740	(103)	34:28.510	(106)	1:05:10.640	(103)
Quentin Emeriau	14:32.260	(108)	07:25.140	(104)	04:49.760	(106)	03:50.980	(63)	25:17.100	(101)	55:55.240	(104)
Alexandre Cure	13:25.520	(32)	06:13.180	(15)	04:14.000	(8)	04:20.360	(106)	28:05.200	(105)	56:18.260	(105)
Botsy Phillips	14:42.260	(113)	07:51.320	(110)	04:48.120	(104)	04:18.940	(104)	36:50.620	(108)	1:08:31.260	(106)
Chris Keeble-Smith	13:37.120	(48)	06:34.630	(50)	04:28.210	(50)	03:51.500	(65)	42:02.180	(110)	1:10:33.640	(107)
Jordan Hodder	14:15.380	(95)	06:53.480	(83)	04:40.920	(91)	04:07.430	(97)	43:59.320	(111)	1:13:56.530	(108)
Miciades Jaque	13:56.270	(73)	10:22.240	(115)	04:38.240	(87)	03:59.360	(84)	41:42.070	(109)	1:14:38.180	(109)
James Rennie	14:05.020	(87)	28:07.530	(119)	04:37.340	(84)	03:39.440	(40)	24:09.000	(77)	1:14:38.330	(110)
'''

text2 = '''
1. 21 Jerome CLEMENTZ FRA 9:01.19 1. 3:31.42 4. 3:32.63 1. 5:19.52 1. 3:24.51 5. 3:43.59 8. 6:47.60 8. 35:20.46 1. 0 False False False 0
2. 22 Fabien BAREL FRA 9:13.80 5. 3:35.05 11. 3:34.81 2. 5:23.69 9. 3:18.53 1. 3:41.11 4. 6:46.20 7. 35:33.19 2. +12.73 False False False 0
3. 126 Wyn MASTERS NZL 9:07.99 2. 3:33.85 8. 3:35.48 4. 5:25.06 12. 3:21.08 3. 3:49.17 18. 6:43.04 3. 35:35.67 3. +15.21 False False False 0
4. 3 Justin LEOV NZL 9:12.41 4. 3:29.17 1. 3:35.83 7. 5:19.94 2. 3:32.45 17. 3:43.33 7. 6:43.57 4. 35:36.70 4. +16.24 False False False 0
5. 5 Florian NICOLAI FRA 9:10.45 3. 3:31.27 3. 3:35.70 5. 5:21.03 3. 3:21.07 2. 3:38.23 1. 7:06.38 25. 35:44.13 5. +23.67 False False False 0
6. 23 Nicolas VOUILLOZ FRA 9:17.40 6. 3:36.21 14. 3:35.44 3. 5:24.24 10. 3:25.51 7. 3:40.91 3. 6:48.59 9. 35:48.30 6. +27.84 False False False 0
7. 129 Sam BLENKINSOP NZL 9:19.66 7. 3:36.90 16. 3:38.75 12. 5:21.31 5. 3:35.35 24. 3:46.36 14. 6:42.20 2. 36:00.53 7. +40.07 False False False 0
8. 163 Matt WALKER NZL 9:21.00 9. 3:34.27 10. 3:45.45 27. 5:22.77 6. 3:29.31 11. 3:43.82 10. 6:50.42 10. 36:07.04 8. +46.58 False False False 0
9. 2 Damien OTON FRA 9:25.57 12. 3:36.53 15. 3:39.56 16. 5:30.73 22. 3:29.79 14. 3:43.60 9. 6:44.60 5. 36:10.38 9. +49.92 False False False 0
10. 112 Sam HILL AUS 9:30.15 15. 3:33.72 6. 3:37.74 10. 5:31.24 24. 3:26.24 9. 3:53.64 28. 6:39.26 1. 36:11.99 10. +51.53 False False False 0
11. 16 Greg CALLAGHAN IRE 9:33.88 18. 3:33.78 7. 3:38.14 11. 5:23.61 8. 3:24.51 5. 3:45.15 13. 7:04.15 22. 36:23.22 11. +1:02.76 False False False 0
12. 19 Richie RUDE USA 9:26.04 13. 3:30.60 2. 3:39.60 17. 5:26.06 13. 3:40.66 33. 3:42.88 6. 6:57.61 14. 36:23.45 12. +1:02.99 False False False 0
13. 4 Nico LAU FRA 9:23.75 10. 3:35.19 12. 3:38.76 13. 5:24.99 11. 3:42.48 36. 3:42.63 5. 6:59.82 18. 36:27.62 13. +1:07.16 False False False 0
14. 31 Adam CRAIG USA 9:31.72 16. 3:37.52 20. 3:47.47 33. 5:21.08 4. 3:23.21 4. 3:44.12 11. 7:09.09 31. 36:34.21 14. +1:13.75 False False False 0
15. 25 Thomas LAPEYRIE FRA 9:28.43 14. 3:38.29 24. 3:40.55 18. 5:26.47 15. 3:27.11 10. 3:56.31 35. 6:58.27 16. 36:35.43 15. +1:14.97 False False False 0
16. 8 Francois BAILLY-MAITRE FRA 9:32.32 17. 3:39.40 25. 3:51.23 40. 5:30.51 20. 3:29.38 12. 3:47.69 17. 6:53.38 11. 36:43.91 16. +1:23.45 False False False 0
17. 40 Joseph NATION NZL 9:20.34 8. 3:41.78 30. 3:42.92 21. 5:30.32 19. 3:33.25 20. 3:54.32 29. 7:08.39 28. 36:51.32 17. +1:30.86 False False False 0
18. 29 Josh CARLSON AUS 9:46.40 25. 3:37.82 21. 3:39.05 14. 5:28.77 17. 3:39.56 32. 3:47.01 15. 6:55.06 12. 36:53.67 18. +1:33.21 False False False 0
19. 127 Brook MACDONALD NZL 9:58.72 36. 3:37.33 19. 3:44.85 26. 5:32.46 28. 3:29.55 13. 3:55.45 34. 6:45.88 6. 37:04.24 19. +1:43.78 False False False 0
20. 10 Martin MAES BEL 9:52.72 30. 3:38.13 22. 3:41.98 19. 5:28.08 16. 3:39.34 31. 3:40.87 2. 7:03.49 19. 37:04.61 20. +1:44.15 False False False 0
21. 7 Joe BARNES GBR 9:50.90 28. 3:37.05 17. 3:37.58 9. 5:26.39 14. 3:32.90 18. 3:52.47 24. 7:08.04 26. 37:05.33 21. +1:44.87 False False False 0
22. 15 Bryan REGNIER FRA 9:47.93 27. 3:35.57 13. 3:39.18 15. 5:32.10 27. 3:42.50 37. 3:44.80 12. 7:05.03 23. 37:07.11 22. +1:46.65 False False False 0
23. 27 Jesse MELAMED CAN 9:38.28 21. 3:40.22 28. 3:49.48 37. 5:34.88 31. 3:41.61 34. 3:47.64 16. 7:03.97 20. 37:16.08 23. +1:55.62 False False False 0
24. 336 Karim AMOUR FRA 9:47.16 26. 3:40.11 27. 3:44.69 23. 5:33.41 30. 3:34.08 21. 3:50.08 20. 7:10.10 34. 37:19.63 24. +1:59.17 False False False 0
25. 165 Byron SCOTT NZL 10:00.49 38. 3:37.10 18. 3:46.61 29. 5:32.78 29. 3:26.02 8. 3:57.35 37. 7:10.96 35. 37:31.31 25. +2:10.85 False False False 0
26. 151 Pierre Charles GEORGES FRA 9:54.02 31. 3:45.89 41. 3:52.79 42. 5:40.77 45. 3:33.00 19. 3:50.65 23. 6:58.61 17. 37:35.73 26. +2:15.27 False False False 0
27. 34 Alex LUPATO ITA 9:43.27 24. 3:51.13 62. 3:44.84 25. 5:30.76 23. 3:41.94 35. 4:00.31 43. 7:04.11 21. 37:36.36 27. +2:15.90 False False False 0
28. 137 Dimitri TORDO FRA 9:36.72 20. 3:38.21 23. 3:42.29 20. 5:30.53 21. 3:46.06 47. 3:55.36 33. 7:27.48 58. 37:36.65 28. +2:16.19 False False False 0
29. 18 Jamie NICOLL NZL 9:40.42 23. 3:43.95 36. 3:52.95 43. 5:42.14 49. 3:36.65 27. 4:01.95 49. 7:09.06 30. 37:47.12 29. +2:26.66 False False False 0
30. 168 Hayden LEE NZL 9:54.14 32. 3:43.46 33. 3:55.41 48. 5:31.87 26. 3:35.15 23. 3:53.09 26. 7:15.04 39. 37:48.16 30. +2:27.70 False False False 0
31. 35 Mark SCOTT GBR 10:15.96 52. 3:45.82 40. 3:44.69 23. 5:35.33 32. 3:35.56 25. 3:53.57 27. 7:06.19 24. 37:57.12 31. +2:36.66 False False False 0
32. 32 Iago GARAY TAMAYO ESP 10:18.81 55. 3:42.81 32. 3:48.29 34. 5:38.21 40. 3:35.07 22. 3:49.28 19. 7:08.32 27. 38:00.79 32. +2:40.33 False False False 0
33. 13 Remy ABSALON FRA 10:02.68 41. 3:42.47 31. 3:44.38 22. 5:36.31 33. 3:36.51 26. 3:50.21 21. 7:31.61 65. 38:04.17 33. +2:43.71 False False False 0
34. 107 Robert WILLIAMS GBR 9:56.53 35. 3:44.36 37. 3:47.18 31. 5:36.63 35. 3:55.23 67. 3:58.42 39. 7:14.61 38. 38:12.96 34. +2:52.50 False False False 0
35. 117 Rupert CHAPMAN NZL 10:03.64 43. 3:50.69 61. 3:55.23 47. 5:40.27 43. 3:47.87 50. 3:59.96 41. 6:58.05 15. 38:15.71 35. +2:55.25 False False False 0
36. 164 Kurt LANCASTER NZL 10:03.38 42. 3:46.69 44. 3:53.22 44. 5:40.76 44. 3:30.78 15. 4:09.68 62. 7:20.12 47. 38:24.63 36. +3:04.17 False False False 0
37. 108 James HAMPTON NZL 10:05.22 45. 3:47.29 50. 3:46.76 30. 5:38.13 39. 3:42.73 38. 4:02.91 54. 7:22.17 52. 38:25.21 37. +3:04.75 False False False 0
38. 30 Ben CRUZ USA 9:54.48 33. 3:43.46 33. 3:55.48 49. 5:40.94 47. 3:44.06 43. 4:01.91 48. 7:31.55 64. 38:31.88 38. +3:11.42 False False False 0
39. 132 Jimmy POLLARD NZL 10:21.91 56. 3:45.28 38. 4:04.27 68. 5:36.75 36. 3:31.84 16. 4:10.18 64. 7:09.18 32. 38:39.41 39. +3:18.95 False False False 0
40. 105 Daniel WOLFE IRE 10:25.82 60. 3:47.08 48. 3:55.71 52. 5:44.25 51. 3:44.08 44. 3:54.39 30. 7:09.97 33. 38:41.30 40. +3:20.84 False False False 0
41. 182 John KIRKCALDIE NZL 10:15.15 49. 3:39.68 26. 4:05.89 72. 5:44.57 52. 3:49.46 54. 3:55.07 32. 7:13.29 36. 38:43.11 41. +3:22.65 False False False 0
42. 24 Theo GALY FRA 10:01.40 39. 3:46.79 45. 3:55.54 50. 5:47.48 59. 3:46.61 48. 3:57.02 36. 7:30.29 62. 38:45.13 42. +3:24.67 False False False 0
43. 14 Cedric GRACIA FRA 10:38.00 67. 3:45.93 42. 3:48.58 35. 5:46.97 58. 3:37.59 29. 3:52.69 25. 7:15.87 40. 38:45.63 43. +3:25.17 False False False 0
44. 134 Carl JONES NZL 10:14.26 48. 3:45.53 39. 3:57.32 57. 5:31.46 25. 3:56.56 70. 4:01.73 47. 7:20.42 49. 38:47.28 44. +3:26.82 False False False 0
45. 96 Jordan REGNIER FRA 10:16.44 54. 3:46.51 43. 3:54.54 46. 5:44.88 53. 3:50.75 59. 3:50.22 22. 7:30.02 61. 38:53.36 45. +3:32.90 False False False 0
46. 176 Nathan RANKIN NZL 10:15.88 51. 3:49.89 59. 4:00.44 63. 5:37.63 38. 3:43.07 41. 4:03.65 55. 7:25.20 56. 38:55.76 46. +3:35.30 False False False 0
47. 119 Mark WEIR USA 10:26.69 61. 3:51.86 63. 3:57.54 59. 5:40.84 46. 3:37.22 28. 4:02.64 52. 7:22.22 53. 38:59.01 47. +3:38.55 False False False 0
48. 37 Mitch ROPELATO USA 10:01.94 40. 3:47.03 47. 3:52.74 41. 5:36.55 34. 4:06.67 85. 4:14.29 73. 7:20.26 48. 38:59.48 48. +3:39.02 False False False 0
49. 95 Max SCHUMANN GER 10:11.46 46. 3:59.04 75. 3:59.85 61. 5:45.43 54. 3:43.03 40. 4:02.66 53. 7:19.76 45. 39:01.23 49. +3:40.77 False False False 0
50. 171 Kieran BENNETT NZL 10:16.24 53. 3:48.06 56. 3:56.03 53. 6:06.06 94. 3:47.17 49. 4:02.57 51. 7:08.83 29. 39:04.96 50. +3:44.50 False False False 0
51. 106 Joe FLANAGAN GBR 10:25.37 58. 3:47.64 52. 3:55.70 51. 5:53.97 74. 3:44.99 46. 4:01.08 45. 7:16.71 42. 39:05.46 51. +3:45.00 False False False 0
52. 28 Fabien COUSINIE FRA 10:50.99 75. 3:46.89 46. 3:50.12 38. 5:46.84 57. 3:44.09 45. 3:55.00 31. 7:13.35 37. 39:07.28 52. +3:46.82 False False False 0
53. 36 Cedric RAVANEL FRA 10:03.77 44. 3:52.86 64. 4:06.90 74. 5:49.97 68. 3:49.69 56. 4:00.56 44. 7:23.74 54. 39:07.49 53. +3:47.03 False False False 0
54. 39 Gary William FORREST GBR 10:15.38 50. 3:48.36 57. 3:49.15 36. 5:49.17 67. 3:57.94 71. 4:07.58 57. 7:19.93 46. 39:07.51 54. +3:47.05 False False False 0
55. 131 Ben ROBSON NZL 9:36.47 19. 3:53.89 66. 4:20.38 94. 5:43.68 50. 3:59.30 73. 4:11.31 66. 7:43.75 79. 39:28.78 55. +4:08.32 False False False 0
56. 113 Mike JONES GBR 10:21.95 57. 3:43.70 35. 3:45.80 28. 5:42.08 48. 5:06.61112. 3:59.58 40. 6:56.90 13. 39:36.62 56. +4:16.16 False False False 0
57. 162 Deon BAKER AUS 10:56.30 83. 3:48.02 55. 4:00.42 62. 5:45.73 55. 3:50.41 58. 4:00.27 42. 7:17.85 43. 39:39.00 57. +4:18.54 False False False 0
58. 153 Charly DI PASQUALE FRA 10:25.78 59. 3:59.51 78. 3:57.23 56. 5:48.45 63. 3:38.27 30. 4:18.38 84. 7:32.17 66. 39:39.79 58. +4:19.33 False False False 0
59. 166 Matt SCOLES NZL 10:48.30 72. 3:47.68 53. 4:01.78 65. 5:48.14 61. 3:54.34 64. 4:05.23 56. 7:16.64 41. 39:42.11 59. +4:21.65 False False False 0
60. 103 Johnny MAGIS BEL 10:40.22 70. 3:50.19 60. 3:57.22 55. 6:02.67 87. 3:52.04 60. 4:01.64 46. 7:19.60 44. 39:43.58 60. +4:23.12 False False False 0
61. 156 Kaine CANNAN AUS 10:27.63 62. 3:47.68 53. 3:59.03 60. 5:50.03 69. 3:54.59 65. 4:12.30 70. 7:35.57 69. 39:46.83 61. +4:26.37 False False False 0
62. 98 Sam FLANAGAN GBR 10:37.52 66. 3:59.65 79. 3:56.92 54. 5:50.63 70. 3:48.76 52. 4:07.65 58. 7:35.33 68. 39:56.46 62. +4:36.00 False False False 0
63. 133 Conor MACFARLANE NZL 10:29.30 63. 4:01.36 83. 4:09.51 78. 5:55.41 77. 3:49.23 53. 4:17.14 81. 7:21.85 50. 40:03.80 63. +4:43.34 False False False 0
64. 185 Ethan GLOVER NZL 10:38.38 69. 3:52.96 65. 4:10.68 79. 5:46.13 56. 3:52.75 62. 4:15.67 75. 7:41.81 77. 40:18.38 64. +4:57.92 False False False 0
65. 110 Joshua LEWIS GBR 11:01.05 87. 3:56.60 70. 4:04.47 69. 5:52.40 73. 3:52.97 63. 4:11.72 68. 7:23.78 55. 40:22.99 65. +5:02.53 False False False 0
66. 99 James SHIRLEY GBR 10:53.85 81. 3:58.35 74. 4:04.99 71. 5:56.99 80. 3:54.67 66. 4:10.42 65. 7:28.51 59. 40:27.78 66. +5:07.32 False False False 0
67. 100 Manuel DUCCI ITA 10:55.29 82. 4:01.30 82. 4:02.26 66. 5:52.02 71. 3:55.64 68. 4:11.67 67. 7:33.30 67. 40:31.48 67. +5:11.02 False False False 0
68. 123 Lindsay KLEIN AUS 10:58.23 84. 3:54.49 68. 4:17.94 89. 5:47.50 60. 4:04.60 82. 4:02.35 50. 7:29.30 60. 40:34.41 68. +5:13.95 False False False 0
69. 94 Dylan WOLSKY AUS 10:33.43 65. 4:03.11 89. 4:04.65 70. 5:58.50 81. 4:02.88 79. 4:12.07 69. 7:41.36 75. 40:36.00 69. +5:15.54 False False False 0
70. 148 Peter JOYNT NZL 10:40.42 71. 3:57.23 71. 4:11.95 82. 5:54.20 75. 3:52.51 61. 4:18.45 85. 7:43.88 80. 40:38.64 70. +5:18.18 False False False 0
71. 125 Ben FORBES AUS 10:49.29 73. 4:11.15100. 4:14.03 84. 5:52.17 72. 4:01.70 77. 4:09.46 60. 7:21.95 51. 40:39.75 71. +5:19.29 False False False 0
72. 158 Tom BRADSHAW NZL 10:38.12 68. 4:07.45 96. 4:00.82 64. 5:48.99 66. 4:05.53 84. 4:36.44100. 7:31.26 63. 40:48.61 72. +5:28.15 False False False 0
73. 101 Nathaniel HILLS USA 10:50.59 74. 3:59.40 77. 4:16.29 87. 5:56.66 79. 3:58.49 72. 4:12.30 70. 7:38.79 71. 40:52.52 73. +5:32.06 False False False 0
74. 167 Reuben MILLER NZL 11:16.39 89. 3:54.82 69. 4:06.67 73. 6:04.43 93. 4:01.04 75. 4:08.63 59. 7:26.77 57. 40:58.75 74. +5:38.29 False False False 0
75. 175 Tristan RAWLENCE NZL 10:51.81 77. 4:05.93 94. 4:08.49 77. 5:48.94 65. 3:50.12 57. 4:34.19 99. 7:58.12 83. 41:17.60 75. +5:57.14 False False False 0
76. 104 Macky FRANKLIN USA 11:44.73101. 4:01.37 84. 4:08.09 76. 5:54.79 76. 4:04.35 80. 4:10.05 63. 7:42.39 78. 41:45.77 76. +6:25.31 False False False 0
77. 169 Thomas LAMB NZL 10:59.54 86. 3:59.04 75. 4:17.64 88. 6:00.39 85. 4:09.34 91. 4:18.80 86. 8:01.44 85. 41:46.19 77. +6:25.73 False False False 0
78. 155 Maxime CHAPUIS SUI 10:51.50 76. 5:01.56116. 4:07.83 75. 5:48.90 64. 4:05.30 83. 4:16.17 77. 7:41.32 74. 41:52.58 78. +6:32.12 False False False 0
78. 136 Zac WILLIAMS NZL 10:53.13 79. 4:04.73 92. 4:11.08 80. 6:13.33108. 4:10.81 92. 4:22.96 90. 7:56.54 82. 41:52.58 78. +6:32.12 False False False 0
80. 120 Jason MOESCHLER USA 10:52.61 78. 4:02.45 86. 4:20.98 96. 6:06.26 95. 4:01.38 76. 4:27.13 93. 8:07.09 89. 41:57.90 80. +6:37.44 False False False 0
81. 170 Leighton KIRK NZL 11:19.33 91. 4:03.33 90. 4:13.05 83. 6:07.10 97. 4:18.60 97. 4:09.60 61. 7:48.28 81. 41:59.29 81. +6:38.83 False False False 0
82. 191 Reon BOE NZL 11:27.69 95. 3:58.33 73. 4:15.24 85. 6:12.03105. 4:08.20 88. 4:21.13 87. 7:41.49 76. 42:04.11 82. +6:43.65 False False False 0
83. 139 Dylan STUCKI USA 10:59.24 85. 3:59.73 80. 4:19.49 91. 5:58.53 82. 4:18.70 98. 4:17.48 82. 8:22.66 93. 42:15.83 83. +6:55.37 False False False 0
84. 157 Simon BUZACOTT AUS 11:19.40 92. 4:02.58 88. 4:21.68 97. 6:01.24 86. 4:07.06 86. 4:27.37 94. 8:02.00 87. 42:21.33 84. +7:00.87 False False False 0
85. 109 Paul ASTON GBR 12:09.28104. 4:02.39 85. 4:04.25 67. 6:08.27 98. 4:08.14 87. 4:12.73 72. 7:37.07 70. 42:22.13 85. +7:01.67 False False False 0
86. 186 Scott FELLERS USA 11:31.73 96. 4:02.54 87. 4:24.72 98. 6:03.02 88. 3:59.95 74. 4:21.49 88. 8:01.44 85. 42:24.89 86. +7:04.43 False False False 0
87. 159 Rob BLACKHAM NZL 11:26.89 94. 4:07.01 95. 4:38.44108. 5:48.19 62. 4:02.55 78. 4:18.28 83. 8:06.78 88. 42:28.14 87. +7:07.68 False False False 0
88. 172 Cory SULLIVAN USA 11:59.99103. 4:10.05 99. 4:20.67 95. 6:06.53 96. 4:15.91 94. 4:16.65 80. 7:39.08 72. 42:48.88 88. +7:28.42 False False False 0
89. 179 Dirk PETERS NZL 11:55.17102. 3:59.77 81. 4:26.95101. 6:00.20 83. 4:20.92102. 4:27.64 96. 7:59.76 84. 43:10.41 89. +7:49.95 False False False 0
90. 147 Edward KERLY GBR 10:53.57 80. 4:25.24111. 4:30.28103. 6:15.32110. 4:29.70105. 4:22.70 89. 8:22.06 92. 43:18.87 90. +7:58.41 False False False 0
91. 180 Chris PATTON USA 11:25.53 93. 3:57.24 72. 4:19.18 90. 6:00.29 84. 4:18.57 96. 4:30.22 98. 8:49.73104. 43:20.76 91. +8:00.30 False False False 0
92. 174 Ben SHAYLER NZL 11:38.70 99. 4:13.70106. 4:28.69102. 6:10.23102. 4:19.95100. 4:27.50 95. 8:13.24 91. 43:32.01 92. +8:11.55 False False False 0
93. 122 Tim MCCULLOUGH AUS 12:10.49105. 4:08.01 97. 4:19.54 92. 6:03.56 89. 4:04.48 81. 4:16.02 76. 8:31.03 98. 43:33.13 93. +8:12.67 False False False 0
94. 124 Isaac DENNY AUS 12:22.01109. 4:04.71 91. 4:31.45104. 6:09.88101. 4:41.90110. 4:16.47 79. 7:40.22 73. 43:46.64 94. +8:26.18 False False False 0
95. 97 Lars STERNBERG USA 10:11.98 47. 3:49.13 58. 3:53.53 45. 5:36.84 37. 3:49.47 55. 3:57.63 38. 12:30.67112. 43:49.25 95. +8:28.79 False False False 0
96. 188 Miles DAVIES NZL 11:12.75 88. 4:09.37 98. 4:26.73100. 6:09.55 99. 4:15.09 93. 5:15.57111. 8:27.98 96. 43:57.04 96. +8:36.58 False False False 0
97. 152 Mark DUNLOP NZL 11:34.72 97. 4:12.65104. 4:26.53 99. 6:12.13106. 4:25.36103. 4:29.09 97. 8:43.19103. 44:03.67 97. +8:43.21 False False False 0
98. 149 Ty HATHAWAY USA 12:35.34111. 4:12.92105. 4:11.66 81. 6:09.84100. 4:17.50 95. 4:36.83101. 8:24.56 94. 44:28.65 98. +9:08.19 False False False 0
99. 161 Guy BAR ISR 12:12.14106. 4:12.20102. 4:49.30110. 6:10.39103. 4:36.28108. 4:26.34 92. 8:32.67100. 44:59.32 99. +9:38.86 False False False 0
100. 141 Johann ROOZENBURG NZL 12:20.74108. 4:22.34109. 4:33.74106. 6:04.15 92. 4:25.68104. 4:44.04104. 8:30.16 97. 45:00.85100. +9:40.39 False False False 0
101. 187 Carl EDMONDSON NZL 13:04.40117. 4:04.76 93. 4:16.03 86. 6:24.02112. 4:33.03106. 4:25.78 91. 8:31.86 99. 45:19.88101. +9:59.42 False False False 0
102. 181 Jeremiah NEWMAN USA 11:18.04 90. 3:53.91 67. 8:08.64118. 6:03.59 90. 4:08.95 89. 4:39.47102. 8:27.66 95. 46:40.26102. +11:19.80 False False False 0
103. 190 Daniel CASTILLO COL 13:02.14116. 4:18.76108. 4:35.22107. 6:10.45104. 4:20.38101. 4:58.97108. 9:29.77108. 46:55.69103. +11:35.23 False False False 0
104. 143 Will MATHIESON NZL 12:25.25110. 4:24.24110. 4:58.58112. 6:49.35115. 4:39.44109. 4:49.29105. 8:56.24105. 47:02.39104. +11:41.93 False False False 0
105. 135 Gerard WOLFE IRE 12:49.81114. 4:12.44103. 4:32.32105. 6:12.54107. 5:42.74115. 5:06.81110. 8:38.37101. 47:15.03105. +11:54.57 False False False 0
106. 145 Sean LEADER USA 12:54.85115. 4:36.55115. 5:03.75113. 6:31.60113. 4:52.31111. 4:41.29103. 8:40.76102. 47:21.11106. +12:00.65 False False False 0
107. 178 Josh PRENTICE AUS 12:37.86112. 4:26.89112. 4:56.92111. 5:56.11 78. 4:19.53 99. 5:21.74112. 10:38.30109. 48:17.35107. +12:56.89 False False False 0
108. 150 Julian GERHARDT GER 12:48.25113. 4:31.02114. 5:08.16114. 7:02.94117. 4:33.20107. 4:56.20106. 9:19.12106. 48:18.89108. +12:58.43 False False False 0
109. 177 James PRITCHARD NZL 11:42.53100. 4:11.54101. 4:43.72109. 6:04.13 91. 3:55.73 69. 10:11.77114. 8:12.54 90. 49:01.96109. +13:41.50 False False False 0
110. 63 Taran GOIRIS AUS 13:26.37118. 4:16.59107. 5:32.14116. 6:14.45109. 5:12.25113. 4:58.57107. 10:58.82110. 50:39.19110. +15:18.73 False False False 0
111. 160 Nick BIRKHEAD NZL 15:59.90120. 4:30.51113. 5:22.00115. 6:43.55114. 5:29.19114. 5:06.62109. 9:26.60107. 52:38.37111. +17:17.91 False False False 0
112. 140 David SHEPHARD GBR 15:52.94119. 5:30.62119. 7:26.16117. 7:31.09118. 6:11.25116. 6:15.01113. 11:47.47111. 1:00:34.54112. +25:14.08 False False False 0
9 Yoann BARELLI FRA 9:38.32 22. 3:33.87 9. 3:35.75 6. 5:29.31 18. 6969 6969 6969 6969 6969 6969 6969 6969 6969 True False False 5
11 Alexandre CURE FRA 9:51.16 29. 5:27.59118. 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 True False False 3
12 Curtis KEENE USA 10:30.76 64. 3:40.31 29. 3:57.44 58. 5:40.08 42. 3:43.38 42. 4:14.82 74. 6969 6969 6969 6969 6969 True False False 7
33 Marco OSBORNE USA 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 True False False 1
38 Dan ATHERTON GBR 9:24.69 11. 3:33.57 5. 3:36.34 8. 5:23.22 7. 3:47.95 51. 6969 6969 6969 6969 6969 6969 6969 True False False 6
92 Nicolas QUERE FRA 9:59.29 37. 3:47.57 51. 3:47.19 32. 6:52.39116. 6969 6969 6969 6969 6969 6969 6969 6969 6969 True False False 5
93 Nicolas PRUDENCIO FLANO CHI 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 False True False 1
114 Gustav WILDHABER SUI 9:55.28 34. 3:47.23 49. 3:50.51 39. 5:38.51 41. 3:42.80 39. 10:53.22115. 6969 6969 6969 6969 6969 True False False 7
116 Eddie MASTERS NZL 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 False True False 1
118 Joost WICHMAN NED 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 False True False 1
130 Bryn ATKINSON AUS 11:36.48 98. 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 True False False 2
'''

rider_list = text.split('\n')[1:-1]
whistler_list = []
for rider in rider_list:
    m = rider.split()
    m[1] = m[1].upper()
    m[0:2] = [' '.join(m[0:2])]
    if any(c.isalpha() for c in m[1]):
        m[1] = m[1].upper()
        m[0:2] = [' '.join(m[0:2])]
    m[0] = unidecode(m[0])

    m[2:13:2] = [x.translate(str.maketrans('', '', '()')) for x in m[2:13:2]]

    whistler_list.append(m)


rider_list2 = text2.split('\n')[1:-1]
rotorua_list = []
for rider_idx, rider in enumerate(rider_list2): #140 David SHEPHARD GBR 15:52.94119. 5:30.62119. 7:26.16117. 7:31.09118. 6:11.25116. 6:15.01113. 11:47.47111. 1:00:34.54112. +25:14.08
    m = rider.split()

    #Get rid of the first placing
    if re.findall(r'(\.)', m[0]):
        del m[0]
    #Last name to uppercase
    m[2] = m[2].upper()

    #Join first and last name
    m[1:3] = [' '.join(m[1:3])]

    #Check if its a second last name or the country code
    if any(c.isalpha() for c in m[2]) and len(m[2]) != 3:
        m[2] = m[2].upper()
        m[1:3] = [' '.join(m[1:3])]
    m[1] = unidecode(m[1])

    #Get first split
    if m[3][-1] == '.':
        m.insert(4, m[3][-4:])
        m[3] = m[3][:-4]


    # Get second split
    if m[5][-1] == '.':
        m.insert(6, m[5][-4:])
        m[5] = m[5][:-4]


    # Get third split
    if m[7][-1] == '.':
        m.insert(8, m[7][-4:])
        m[7] = m[7][:-4]


    # Get fourth split
    if m[9][-1] == '.':
        m.insert(10, m[9][-4:])
        m[9] = m[9][:-4]

    if len(m) > 11:
        # Get fifth split
        if m[11][-1] == '.':
            m.insert(12, m[11][-4:])
            m[11] = m[11][:-4]

    if len(m) > 13:
        # Get sixth split
        if m[13][-1] == '.':
            m.insert(14, m[13][-4:])
            m[13] = m[13][:-4]

    if len(m) > 15:
        # Get seventh split
        if m[15][-1] == '.':
            m.insert(16, m[15][-4:])
            m[15] = m[15][:-4]
    if len(m) > 17:
        # Get seventh split
        if m[17][-1] == '.':
            m.insert(18, m[17][-4:])
            m[17] = m[17][:-4]

    #Get rid of the . after split position
    m[4:19:2] = [x.replace('.', '') for x in m[4:19:2]]

    #print(m[-1])
    '''
    if len(m) < 20 and rider_idx != 0:
        m.append('')
    if rider_idx == 0:
        m.append('0')
    '''
    if len(m[-5]) > 3 and m[-5] != '6969':
        m[-5] = m[-5][1:]

    print(len(m))

    rotorua_list.append(m)


full_names = ['??? DI PIERDOMENICO', 'Aaron BRADFORD', 'Aaron TOLLEY', 'Aaron TRACEY', 'Abraham JULIAS ALVAREZ', 'Adam BANZON', 'Adam BRAYTON', 'Adam CRAIG', 'Adam HALLING', 'Adam PRICE', 'Adam QUADRONI', 'Adam TAYLOR', 'Adam WIGHT', 'Addy POPE', 'Adrian CAMPOSILVAN', 'Adrian GERBER', 'Adrian JAMES', 'Adrien BARTOLE', 'Adrien CHAUVINEAU', 'Adrien DAILLY', 'Adrien HOFFER', 'Adrien PONSIN', 'Aidan BISHOP', 'Aidan BURRILL', 'Aiken COLLINGE', 'Aitor ARAMBURU', 'Aitor BADIOLA GIL', 'Ajay JONES', 'Alan BLYTH', 'Alan MCKINSTRY', 'Alan MELLON', 'Alan STOKES', 'Alasdair MACLENNAN', 'Alastair MAXWELL', 'Alastair WAUGH', 'Alayn MARTINEZ', 'Albert ICART', 'Albert RIERA ARCARONS', 'Albert VILA MAESTRE', 'Alberto FERRERAS BARRERA', 'Alberto FRANCO', 'Alberto FURLANI', 'Alberto LUNGHI', 'Alberto MOTTA', 'Alberto RADICE', 'Alberto ROGINA CHECA', 'Alberto SANCHEZ CARMONA', 'Alberto SANCHEZ-ORO GOMEZ', 'Aled GRIFFITHS', 'Alejandro Amigo KLAASSEN', 'Alejandro LOPEZ SANCHEZ', 'Alessandro BAGNOLI', 'Alessandro BASSO', 'Alessandro BONAROTTI', 'Alessandro CAPRA', 'Alessandro COLOMBO', 'Alessandro GENNESI', 'Alessandro LEVRA', 'Alessandro MISINO', 'Alessandro PICCOLI', 'Alessandro SCUNDI', 'Alessandro SEPP', 'Alessio GUIDOLIN', 'Alessio VERCELLI', 'Alex ANDALUZ', 'Alex BALFOUR', 'Alex BODAY', 'Alex CASTILLO', 'Alex LUPATO', 'Alex NOWOTYNSKI', 'Alex PETITDEMANGE', 'Alex STOCK', 'Alexander BAMBERGER', 'Alexander KANGAS', 'Alexander MCGUINNIS', 'Alexander RUDIGIER', 'Alexander SIMPSON', 'Alexandre BALAUD', 'Alexandre CLAVERIE', 'Alexandre CURE', 'Alexandre JANIN', 'Alexandre PONSIN', 'Alexandre SICARD', 'Alexandre TISSIER', 'Alexey SHCHERBINA', 'Alexis LEBERT', 'Alexis ROCHE', 'Ali FABB', 'Alistair JAMIESON', 'Alistair ROGERS', 'Allan BOUWSTRA', 'Allan CLARK', 'Allen MONGEY', 'Alois VON WURSTEMBERGER', 'Alvaro GRAGLIA', 'Alvaro HIDALGO VASQUEZ', 'Alvaro QUINTANILLA', 'Alvaro VAZQUEZ LOPEZ', 'Amedeo GIOFRE', 'Amedeo GIOFRO', 'Amedeo PESENTI', 'Andre Luiz Ramos BRETAS', 'Andre WAGENKNECHT', 'Andrea ANDREINI', 'Andrea BARBIERI', 'Andrea BORIN', 'Andrea BRUNO', 'Andrea GAMENARA', 'Andrea GARDELLA', 'Andrea MORI', 'Andrea NENCETTI', 'Andrea PEDINI', 'Andrea PELAZZA', 'Andrea PIRAZZOLI', 'Andrea POGGETTI', 'Andrea POLLIOT', 'Andrea RIGHETTINI', 'Andrea RODOLFI', 'Andrea ROSSET', 'Andrea SABBIA', 'Andrea SCAPPINI', 'Andrea TONIATI', 'Andrea VIGNONE', 'Andrea ZILIANI', 'Andreas Constantino KUKULIS BLAJTRACH', 'Andreas HEIMERDINGER', 'Andreas HESTLER', 'Andreas TSCHANZ', 'Andreas ZIEGLER', 'Andres AMARAL', 'Andres CASTRO', 'Andres CASTRO DURAN', 'Andres FERNANDEZ', 'Andres FERNANDEZ LATORRE', 'Andres JARAMILLO BOTERO', 'Andres WIDOYCOVICH', 'Andreu SOLDEVILLA FABREGA', 'Andrew BENT', 'Andrew CORCORAN', 'Andrew CUNNINGHAM (1)', 'Andrew DAPRE', 'Andrew DEVINE', 'Andrew FITZPATRICK', 'Andrew HEATON', 'Andrew MACPHERSON', 'Andrew MORRISON', 'Andrew NEETHLING', 'Andrew SHANDRO', 'Andrew TEMPLIN', 'Andrew WALKER', 'Andrey ALATORCEV', 'Andy BARLOW', 'Andy HYAM', 'Andy NELSON (1)', 'Andy SMITH', 'Andy WEAMES', 'Andy WHITE', 'Andy YOONG', 'Angel GUTIERREZ DIAZ DEL CAMPO', 'Angelo LEONE', 'Angelo PANTALEONE', 'Anthony ANDRE', 'Anthony ANDREOLETTI', 'Anthony BALESTER', 'Anthony DIAZ', 'Anthony ELLIOTT', 'Anthony MARRO', 'Antoine BAYLOT', 'Antoine BEZZOLA', 'Antoine CARON', 'Antoine MACHIN', 'Anton CHIKOV', 'Anton COOPER', 'Antonin GOURGIN', 'Antonio DE SILVI', 'Antonio FERREIRO PAJUELO', 'Antonio GUIDI', 'Antonio Luigi GALGANO', 'Antonio OVALLE VERGARA', 'Antonio PEREZ DA COSTA', 'Antonio PEREZ MONTAVA', 'Antonio ROSSI', 'Antonio Ramon LEIVA FIGEROA', 'Antonio VALENTINI', 'Antonio VIDAURRE', 'Antti LAMPEN', 'Antti SEPPALA', 'Anze ZABJEK', 'Ari KURVINEN', 'Ariel LINDSLEY', 'Armin BEELI', 'Arnaldo REGESTRO', 'Arnaud BLONDEL', 'Arnaud BOGUD', 'Arnaud BUFFAT', 'Arnaud FERDINAND', 'Arne GRAMMER', 'Arno FAUCHER', 'Arran MOORE', 'Arthur ESSLINGER', 'Artur KUZIN', 'Aurele ARNAUD', 'Aurelien DEMAILLY', 'Aurelien FERRIERE', 'Aurelien GIORDANENGO', 'Aurelien GRIMAND', 'Aurelien GUCHAN', 'Austen BICKFORD', 'Aviad IZRAEL', 'Axier BERNARAS', 'Azat SHARIPOV', 'Balz WEBER', 'Baptiste BISBAU', 'Baptiste GAILLOT', 'Baptiste REMBLIER', 'Barry HAMILTON', 'Barry LANGRELL', 'Barry TRACEY', 'Barry TRAVERS', 'Bart DE VOCHT', 'Bart VAN DEN BIGGELAAR', 'Basilio MUZZUPAPPA', 'Bastien BALMET', 'Bastien DIEFFENTHALER', 'Baumgartner PETER', 'Ben CATHRO', 'Ben CLARKE (mas2)', 'Ben CLAYTON (sen)', 'Ben CRUZ', 'Ben FORBES', 'Ben FURBEE', 'Ben GRIFFIN', 'Ben HOBBS', 'Ben MARCHANT', 'Ben PASKE', 'Ben PLENGE', 'Ben PRICE (elt)', 'Ben RAITT', 'Ben RAYNOR', 'Ben SHAYLER', 'Ben THOMPSON', 'Ben THOMSON', 'Benat ORONOZ GORROCHATEGUI', 'Benedikt PURNER', 'Benito GIRALDEZ', 'Benito GIRALDEZ SOUSA', 'Benjamin ASSIE', 'Benjamin BERNARDI', 'Benjamin BREYTMANN', 'Benjamin DE', 'Benjamin HILL', 'Benjamin LORSON', 'Benjamin MEIER', 'Benjamin WERLING', 'Benny LAHAT', 'Benoit BELTRITTI', 'Benoit DEKEYSER', 'Benoit MARONNEAU', 'Benoit MONTEIL', 'Benoit PICON', 'Benoit WENDLING', 'Bernardo GUARITA', 'Bernat GUARDIA PASCUAL', 'Bernd DORRONG', 'Billy CAROLI', 'Bjorn PETTERSON', 'Blake MASTRANGELO', 'Bo MACARTHUR', 'Bob MILLAR', 'Bobby WRIGHT', 'Borja ANON MANTINAN', 'Borja ESPINOS MUT', 'Botsy PHILLIPS', 'Brad COLE', 'Brad HALE', 'Brad ILLINGWORTH', 'Braden KAPPIUS', 'Brandon SLOAN', "Brendan O'HANLON", 'Brendan SLUDDS', 'Brendon EDGAR', 'Brett STOKMAN', 'Brian BUELL', 'Brian HUTCHINSON', 'Brian LOPES', 'Brian MELIA', 'Brian MERRITT (pro)', 'Brice LIEBRECHTS', 'Brodie HOOD', 'Bruce MCCLEARY', 'Bruno BECCHI', 'Bruno DAO CASTES', 'Bruno ZANCHI', 'Bryan CONLON', 'Bryan REGNIER', 'Bryn ATKINSON', 'Byron SCOTT', 'Cal DEW', 'Callum CHAMBERLAIN', 'Callum MCCUBBING', 'Calum MCRITCHIE', 'Cameron CORNFORTH', 'Camille CHAFFRE', 'Camille SERVANT', 'Camillo GIAGNACOVO', 'Camilo ARANDA', 'Cardona ENRIQUE SANTONJA', 'Carl BACHMANN', 'Carl DECKER', 'Carl JONES', 'Carlo SABBIA', 'Carlo VANBRABANT', 'Carlos BEYER', 'Carlos CAMPOS', 'Carlos CONCHA', 'Carlos FERNANDEZ ALGOBIA', 'Casey COFFMAN', 'Casey SWANSON', 'Cedric CARREZ', 'Cedric GRACIA', 'Cedric LACASTE', 'Cedric RAVANEL', 'Celso VIEITEZ SEOANE', 'Cesar GAIRIN', 'Cesare ALBASI', 'Cesare RUBATTO', 'Charles JONES (sen1)', 'Charlie SPONSEL', 'Chay GRANBY', 'Chris ARCHER (mas)', 'Chris BOICE', 'Chris BREEZE', 'Chris BROWN', 'Chris BUCHAN', 'Chris DEL BOSCO', 'Chris DEWAR', 'Chris DOWNHAM', 'Chris DRAPER', 'Chris EDWARDS (sen)', 'Chris GASKELL', 'Chris HEATH', 'Chris HUTCHENS', 'Chris JACKSON', 'Chris JOHNSON', 'Chris JOHNSTON', 'Chris KEEBLE-SMITH', 'Chris KENWARD', 'Chris KILMURRAY', 'Chris KIMBERLEY', 'Chris LEVINE', 'Chris MCCARTHY', 'Chris MUNTZ', 'Chris PRICE (2)', 'Chris REID', 'Chris ROSS (mas)', 'Chris SCOTT', 'Christian GREUB', 'Christian SCHLEKER', 'Christian SOTO', 'Christoffer BROCHS', 'Christoph SAUSER', 'Christoph SCHNETTLER', 'Christophe MAZERES', 'Christophe RIZZETTO', 'Christophe TROGNON', 'Christopher BERTOTTO', 'Christopher EVENHUS', 'Christopher GALLAGHER', 'Christopher MCCARTHY', 'Christopher MCGLINCHEY', 'Christopher PANOZZO', 'Christopher TOLEDO', 'Christopher WOOLDRIDGE', 'Chun Ting Vincent CHAN', 'Chus SEGORBE', 'Ciaran BYRNE', 'Claudio BRAVO', 'Claudio FLOCCA', 'Claudio NEGRO', 'Claudio PERTILE', 'Claudio VIALE', 'Clay KIMSEY', 'Clement BENOIT', 'Clement COMTE', 'Clement HAUDRECHY', 'Cocchi GERMANO', 'Cody JOHNSON (pro)', 'Cody KAISER', 'Cody KELLEY', 'Cody PHILLIPS', 'Cole PICCHIOTTINO', 'Colin BELISLE', 'Colin MCGREGOR', 'Colin PICKETT', 'Colin ROSS', 'Colm BRADLEY', 'Colton ANDERSEN', 'Connor FEARON', 'Connor MCCORMICK', 'Conor CRAIG', 'Conor DUFFY (mas)', 'Conor MACFARLANE', 'Conor MCGINN', 'Conor SWAINE', 'Corentin ALTHUSSER', 'Corentin ROUILLON', 'Corrado DRAGO', 'Cory SULLIVAN', 'Craig CARLSON', 'Craig DAVIES', 'Craig EVANS', 'Craig HARVEY', 'Craig JOHNSON (mas)', 'Craig LETTON', 'Craig MILLER', 'Craig REA', 'Craig WILSON', 'Cristian LAVORE', 'Cristian PONCE', 'Cristobal PURCELL', 'Cristobal RAMIREZ DUPUY', 'Cristobal TORRES', 'Curtis BENNETT', 'Curtis KEENE', 'Cyril BEN SAID', 'Cyril MOUILLET', 'Cyril SCATA', 'Cyrille KURTZ', 'Dain ZAFFKE', 'Daisuke KUROSAWA', 'Dale MCMULLAN', 'Damian GREAVY', 'Damiano MAGNANI', 'Damiano SCALA', 'Damien DALY', 'Damien DELORME', 'Damien ESCALIER', 'Damien GUICHARD', 'Damien OTON', 'Damien PAGES', 'Damien SAINT PATRICE', 'Damien SCALLY', 'Damien SPAGNOLO', 'Dan ALBERT', 'Dan ATHERTON', 'Dan SHERIDAN', 'Dan SMITH (sen)', 'Daniel ALGARRA', 'Daniel COLLINS', 'Daniel CUBERO MARTINEZ', 'Daniel EIERMANN', 'Daniel GIBSON', 'Daniel GOTTSCHALL', 'Daniel GRAF', 'Daniel GREENWOOD', 'Daniel HALLAM', 'Daniel HASTERT', 'Daniel JAHN', 'Daniel KEDNEY', 'Daniel LECHADO', 'Daniel MACMUNN', 'Daniel MEILINK', 'Daniel MOLINA', 'Daniel NAFTALI', 'Daniel ORTIZ', 'Daniel PRIJKEL', 'Daniel SCOTT', 'Daniel TAYLOR (sen)', 'Daniel WOLFE', 'Daniel ZAMORA HIDALGO', 'Daniele AIROLDI', 'Daniele CRISCUOLO', 'Daniele GIUSTINI', 'Dario BERGAMIN', 'Darren EVANS (elt)', 'Darrin SEEDS', 'Darryl PIMPERTON', 'Darryn HENDERSON', 'Dave EGAN', 'Dave GRIFFITH', 'Dave HARDER', 'Dave HENDERSON', 'David AHERN', 'David ARTHUR', 'David AXELSSON', 'David CLYNCKEMAILLIE', 'David COWAN', 'David DANGEL', 'David DANTHON', 'David DUGGAN (exp)', 'David FERNANDEZ FERNANDEZ', 'David HEEMS', 'David LUDENIA', 'David MCLEAN (vet1)', 'David METCHE', 'David MISSUD', 'David NAVAS', 'David O CONNOR', 'David OGDEN (1)', 'David PLANELLA VUILA', 'David READ', 'David RIMAILHO', 'David SCHMIED', 'David WALSH (mas)', 'David WALSH (sen)', 'Davide BARRO', 'Davide BOZZA', 'Davide BRONDI', 'Davide DE BELLA', 'Davide FERRIGNO', 'Davide GILARDO', 'Davide PAPAGNI', 'Davide SOTTOCORNOLA', 'Davide TEMPINI', 'Davis ENGLISH', 'Dean LUCCHI', 'Declan COKER', 'Denis CHAUVIN', 'Denis GAGNEUR', 'Dennis BEARE', 'Dennis DERTELL', 'Dennis TONDIN', 'Dennis ZUIDMULDER', 'Denny LUPATO', 'Deon BAKER', 'Derek BISSETT', 'Derrick PASTUSZEK', 'Diarmuid MCNAMARA', 'Didier GIRARDIN', 'Diego CAPATAZ RUIZ DE ARBULO', 'Diego HERNANDEZ SERNANDEZ', 'Diego RAMIREZ GARMENDIA', 'Diego RANCHO FRANCISCO', 'Diego SADA', 'Diego SALAS', 'Diego TAGLE', 'Diego ZABALA', 'Dillon LEMARR', 'Dimitri MODESTI', 'Dimitri TORDO', 'Dmitri REPKIN', 'Dobromir DOBREV', 'Domenico SPIAGGI', 'Dominic LAND', 'Dominique CASAMATTA', 'Donald HOXHA', 'Dorian PASCAL', 'Dorian ZURETTI', 'Douglas CHALMERS', 'Douglas MARSHALL', 'Douglas SHEARER', 'Drew PAUTLER', 'Dru BERRYMAN', 'Duncan PORTER', 'Duncan RIFFLE', 'Dylan CALOW', 'Dylan CRANE', 'Dylan STUCKI', 'Dylan WOLSKY', "Eamonn O'REILLY", 'Earl MCCLENAGHAN', 'Ed KERLY', 'Ed RHATIGAN', 'Eddie MASTERS', 'Eddy BURESH', 'Edgar CARBALLO GONZALEZ', 'Edgar MARTINS', 'Edison CANO', 'Edmunds GROSTINS', 'Edoardo BONETTO', 'Eduardo BORQUE DEL CASTILLO', 'Eduardo GALLEGO SUAREZ', 'Eduardo Jose GARCIA OLIVAS', 'Eduardo MARTINEZ-CONDE', 'Edward ROBERTS', 'Elia BOZZOLA', 'Elio BEGNIS', 'Elliot LEES', 'Ely WOODY', 'Emanuel PEREIRA POMBO', 'Emanuele PRATICO', 'Emil LINDGREN', 'Emmanuel ABATE', 'Emmanuel ALLAZ', 'Emmanuel BONNE', 'Emmanuel MILLARD', 'Emmet STOKES', 'Enrico MARTELLO', 'Enrico PULITI', 'Enrique GENOVA ESPINOZA', 'Enrique SANTONJA CARDONA', 'Eoghan ODONOGHUE', 'Eoin ELLIOTT', 'Eoin THOMAS', 'Eric ALEXANDRE', 'Eric DROWER', 'Eric LANDIS', 'Eric REGALLET', 'Erwan BLANCHARD', 'Erwan ROLLES', 'Erwin MATTESICH', 'Espen JOHNSEN', 'Esteban DERONZIER', 'Esteban MEZA', 'Esteban REYES', 'Etienne SIGAUX', 'Etienne WARNERY', 'Eugen-Maxi DICKERHOFF', 'Evan GEANKOPLIS', 'Evan GUTHRIE', 'Evan TURPEN', 'Evan VOSS', 'Evandro SOLDATI', 'Even BRAATEN', 'Evgeny SHIPILOV', 'Ewan BELL', 'Ewen TURNER', 'Ezekiel HERSH', 'Fabian ANRIG', 'Fabian RABENSTEINER', 'Fabian SCHOLZ', 'Fabian WELFORD-TUITT', 'Fabien ABERT', 'Fabien BAREL', 'Fabien BOIS', 'Fabien COUSINIE', 'Fabien HEULOT', 'Fabien VOLET', 'Fabio ANGELI', 'Fabio BREUZA', 'Fabio CARRARA', 'Fabio DI RENZO', 'Fabio FINA', 'Fabio GORI', 'Fabio GOTTARDI', 'Fabio MAGISTRI', 'Fabio MALCONTENTI', 'Fabio MARACA', 'Fabrice TERRONES', 'Fabrizio RIVA', 'Fabrizio RIZZO', 'Federico CHERUBINI', 'Federico CORAGGI', 'Federico SCHEUCH', 'Fel SCHNETTLER CHRISTOPH', 'Felipe GONZALEZ', 'Felipe HENOTT', 'Felipe MARTINEZ', 'Felipe SANDOVAL', 'Felipe SANTANA', 'Felipe VIAL', 'Felix BERNHARD', 'Felix DOERING', 'Felix MADDISON', 'Fergal O MAHONY', 'Fergus LAMB', 'Fernando LARENAS', 'Fernando MARCOS CARLUS', 'Fernando MICHELLI', 'Fernando Simioni NEVES', 'Filip POLC', 'Florent BOIS', 'Florent ROLOS', 'Florian DESCH', 'Florian FINDEISEN', 'Florian GOLAY', 'Florian HUMAJ', 'Florian NICOLAI', 'Florian PEST', 'Flynn GEORGE', 'Fouad GOURIRANE', 'Fran PASTOR', 'Francesc BUSQUETS', 'Francesco BARONI', 'Francesco BUCCIANTINI', 'Francesco CASTIONI', 'Francesco COLOMBO', 'Francesco CRESPI', 'Francesco DE FELICI', 'Francesco FREGONA', 'Francesco GARGAGLIA', 'Francesco SAVONA', 'Francesco SPADEA', 'Francisco BORJA ATARES', 'Francisco MARTINEZ', 'Francisco NEIRA', 'Francisco PALOMINOS', 'Francisco UVALLES', 'Franck DALLA COSTA', 'Franco MANERA', 'Francois BAILLY MAITRE', 'Francois VOITEY', 'Frank DOERR', 'Fraser ANDREW', 'Fraser MCNEIL', 'Frederic MARCASSUS', 'Frederic PERI', 'Frederic ROLLAND', 'Frederick BRATSCHIE', 'Frederik Andersen LETH', 'Frederik KJELDSEN', 'Fulvio MUCELI', 'Gabriel KLOUDA', 'Gabriel Yeray VARGAS HERNANDEZ', 'Gabriele TARSIA INCURIA', 'Gael WIRZ', 'Gaetan DUPIN', 'Gaetan FALAIZE', 'Gaetan RITZ', 'Gareth BREWIN', 'Gareth MONTGOMERIE', 'Gareth O CALLAGHAN', 'Gareth SHEPPARD', 'Garreth DAVIS', 'Gary BISCHOFF', 'Gary BRITTON', 'Gary DRAKE', 'Gary FORREST', 'Gary HUNTER', 'Gary WALL', 'Gaston QUIROGA', 'Gavin BLACK (elt)', 'Gavin CARROLL', 'Gavin DORAN', "Gavin O'CONNELL", 'Gaylord DELAMARLIORE', 'Geoff ROCKHEY', 'George DAVIES', 'George GORE-BROWNE', 'Georgy GROGGER', 'Gerard WOLFE', 'Gerardo BOTTINELLI', 'Gerd SKANT', 'German MENSA', 'Germano COCCHI', 'Gerry SIGNORELLI', 'Gethin Owen EVANS', 'Ghyslain PUECH', 'Giacomo DODINO', 'Giacomo GROssEHAGENBROCK', 'Giampaolo GAMBELUNGHE', 'Gianandrea LECCO', 'Gianluca CARUSO', 'Gianluca ROMANO', 'Gilardo ALBERTO', 'Gilberto PAGNINI', 'Giofre AMEDEO', 'Gionata LIVORTI', 'Gionata LIVORTY', 'Giordano MORONI', 'Giorgio BATISTI', 'Giorgio BENEDETTI', 'Giorgio PICCININI', 'Giorgio RIGHI', 'Giovanni BARBOLINI', 'Giovanni BASSO', "Giovanni D'AROMA", 'Giovanni ROMANINI', 'Giovanni TONTINI', 'Giulio GUADALUPI', 'Giulio RAINERI', 'Giuseppe PROVENZANO', 'Glen HENDERSON', 'Glen RILEY', "Glyn O'BRIEN", 'Goncalo DA SILVA', 'Goncalo GASPAR', 'Gonzalo RODRIGUEZ LLEBANA', 'Grady JAMES', 'Graeme FORREST', 'Graham ALDREDGE', 'Graham PINKERTON', 'Graham RUSHWORTH', 'Greg CALLAGHAN', 'Greg GRANT', 'Greg MINNAAR', 'Greg POTTIER', 'Greg WILLIAMSON', 'Grega ZVAN', 'Gregor FERK', 'Gregor MURRAY', 'Gregory BRUNACHE', 'Gregory DEMESY', 'Gregory FRISON', 'Gregory TORRES', 'Grzegorz GOC', 'Guglielmo BEDELLO', 'Guilhem LAMOISE', 'Guilherme RENKE', 'Guillaume BEGUE', 'Guillaume BETTOLI', 'Guillaume BONNAFFOUS', 'Guillaume CAUVIN', 'Guillaume DECLERCQ', 'Guillaume FARIN', 'Guillaume GENCEL', 'Guillaume HEINRICH', 'Guillaume LADINE', 'Guillaume MEURA', 'Guillaume RACINE', 'Guillem CABALLE RIERA', 'Guillem JORBA PRATS', 'Gus MICHAELS', 'Gustav LARSSON', 'Gustav NORVIK', 'Gustavo ADOLFO', 'Gustavo Adolfo CISNEROS', 'Gusti WILDHABER', 'Guy BAR', 'Guy GIBBS', 'Harrison REIBELT', 'Harrison SMITH', 'Hayden LEE', 'Hebert AMBROSE', 'Henrik KARPPINEN', 'Henry EWALD', 'Henry FOGDEN', 'Herkko RYYNANEN', 'Herrero PATRICIO', 'Holger GOTTSTEIN', 'Howie MILLER', 'Hugo OLIVARES GARCIA', 'Huw OLIVER', 'Iago GARAY', 'Iago GARAY TAMAYO', 'Ian AUSTERMUHLE', 'Ian COATES', 'Ian HARWOOD', 'Ian JACKSON', 'Ibai BELAMENDIA MINGUEZ', 'Ignacio ESPINOZA', 'Ignacio Enrique BARBOSA PRIETO', 'Ignacio ROJO PICAND', 'Ignacio SUAREZ COLOMO', 'Igor LEPESANT', 'Ilya BIRYUKOV', 'Indy PAUWELS', 'Inigo HOYO', 'Inko IRIARTE', 'Inti ROSSI', 'Irenee MENJOU', 'Isaac DENNY*</span>', 'Isaia LAUDI', 'Ismael MULLER', 'Ivan CAVALLINO', 'Ivan DIAZ BUJ', 'Ivan FERRER CASTELLA', 'Ivan KOLEV', 'J.B. MADDALENA', 'Jack HUDSON', 'Jack MOIR', 'Jacky BOUGEARD', 'Jacobo SANTANA PASTOR', 'Jacopo ORBASSANO', 'Jaka TANCIK', 'Jake HOOD', 'Jake IRELAND', 'Jake PADDON', 'Jakob BREITWIESER', 'Jakub HNIDAK', 'Jakub SLOWINSKI', 'James CARRINGTON', 'James CONDON', 'James COOP', 'James DAVIDSON', 'James DICKENS', 'James FLEMING', 'James FLINDERS', 'James GODDARD', 'James GREEN', 'James HALL', 'James HAMPTON', 'James HARRIS (mas)', 'James HOLLIBAUGH', 'James HUGHES (elt)', 'James KNOWLES', 'James LAMB', 'James MACFERRAN', 'James MACKINTOSH', 'James MCKNIGHT', "James O'CARROLL", 'James OLLIVIER', 'James PERKINS', 'James PRETTY', 'James RENNIE', 'James RICHARDS', 'James SCOTT (mas1)', 'James SEVERN', 'James SHIRLEY', 'James SORRIE', 'James STOCK', 'James STRACHAN', 'James SWINDEN', 'James TILBURY', 'James WEAMES', 'James WEST', 'Jamie BILUK', 'Jamie HEATHCOTE', 'Jamie NICOLL', 'Jamie NISBET', 'Jamie VOSPER', 'Jamie WHELAN', 'Jan GUZMAN KACHER', 'Jan HANSMANN', 'Jan VANER', 'Jani AHOLAAKKO', 'Jani KAYHTY', 'Jank TANCIK', 'Jannik SCHLICKEL', 'Jared GRAVES', 'Jarno VEERHOEK', 'Jarrod MCLAUCHLAN', 'Jason FAGAN', 'Jason MEMMELAAR', 'Jason MOESCHLER', 'Jason MORGAN', 'Jason SCHEIDING', 'Jason THOMSEN', 'Javier HASHIMOTO', 'Javier MELERO', 'Javier SANTIAGO', 'Jean Francois KRIER', 'Jean Nicolas GILLMANN', 'Jean Pascal GOLFI', 'Jean Pascal SORROCHE', 'Jean Yves MARTINEZ', 'Jean-Baptiste FERRARI', 'Jean-Baptiste GALI', 'Jean-Francois SERRAT', 'Jean-Louis DESERAUD', 'Jeff CARTER', 'Jeff KENDALL-WEED', 'Jeff LENOSKY', 'Jeff MCDOWELL', 'Jeffry GOETHALS', 'Jeremiah NEWMAN', 'Jeremias GABRIEL', 'Jeremias Gabriel MAIO', 'Jeremie TEUMA', 'Jeremy ARNOULD', 'Jeremy COLE', 'Jeremy DESROUSSEAUX', 'Jeremy HAMILTON', 'Jeremy HORGAN-KOBELSKI', 'Jeremy ORCHARD', 'Jeremy VASSEUR', 'Jeremy VOET', 'Jerome CLEMENTZ', 'Jerome CONREAUX', 'Jerome GALLOIS', 'Jerome GILLOUX', 'Jerome KESSLER', 'Jerome LEROUX', 'Jerome NOUISER', 'Jerome REVIRON', 'Jerome RICHARD', 'Jerome ROLLAND', 'Jerome SCHANDENE', 'Jess PEDERSEN', 'Jesse COSWAY', 'Jesse James CERUSO', 'Jesse MELAMED', 'Jesus BLASCO ARAGON', 'Jez WESTGARTH', 'Jimmy GUIGONNET', 'Jimmy POLLARD', 'Jimmy PRITCHARD', 'Joan BERENGUER', 'Joan COROMINAS VILARRASA', 'Joao RODRIGUES', 'Joao ZUZARTE REIS', 'Joaquin CARRASCO', 'Joaquin GAETE', 'Joaquin RODRIGUEZ', 'Joe BARNES', 'Joe BOWMAN', 'Joe BUCK', 'Joe BUCKLEY', 'Joe FINNEY', 'Joe FLANAGAN (elt)', 'Joe LAWWILL', 'Joe MCEWAN', 'Joe SCHNEIDER', 'Joe SMITH (elt)', 'Joe SWANN', 'Joe TAYLOR (sen)', 'Joe WINSTON', 'Joe YOUNG', 'Joel CHIDLEY', 'Joey SCHUSLER', 'Joey STEWART', 'Johann GROGNUX', 'Johannes RIEBL', 'Johannes SCHILDER', 'John DEAN', 'John FLATLEY', 'John FREY', 'John GYSLING', 'John OWEN (elt)', 'John Ola BUOY', 'John PLAZA', 'John WARDLAW', 'Johnny MAGIS', 'Jon BUCKELL', 'Jon RIDLEY', 'Jon STEVENS', 'Jonas BAHLER', 'Jonas BERNET', 'Jonas MEIER', 'Jonas MUNIZ SANTOVENA', 'Jonatan GARCIA BLANCO', 'Jonathan ADAMS-MARTIN', 'Jonathan ADILLE', 'Jonathan BERTETTO', 'Jonathan BROSSARD', 'Jonathan MAUNSELL', 'Jonathan WATT', 'Joost WICHMAN', 'Jordan BAUMANN', 'Jordan HAMPTON-OSBORNE', 'Jordan HODDER', 'Jordan NAVARRO', 'Jordan PROCHYRA', 'Jordan REGNIER', 'Jordi VILA FLO', 'Jorge ACUNA QUINTANA', 'Jorge CARVAJAL', 'Jorge JIMENEZ MARTOS', 'Jorge MONZON PENAILILLO', 'Jorge NAVARRO', 'Jorge PONS MAHAUT', 'Jorge RODRIGO', 'Jorge VERDUGO', 'Joris GAUTIER', 'Jose ABARCA', 'Jose Antonio DIEZ ARRIOLA', 'Jose Antonio GISTAU DUESO', 'Jose Antonio MENDEZ PEREZ', 'Jose BORGES', 'Jose COFRE', 'Jose CORRAL', 'Jose FERREIRA', 'Jose LETELIER', 'Jose Maria GUERRA CASTRO', 'Jose Miguel BOSQUET RIOJA', 'Jose PEREZ', 'Joseba AGUIRRE', 'Josep BARNIOL', 'Josep BARNIOL TORRES', 'Josep Maria SANCHEZ', 'Joseph NATION', 'Joseph NICHOLSON', 'Josh BRYCELAND', 'Josh CONROY', 'Josh LEWIS', 'Josh LYONS', 'Joshua CARLSON', 'Juan Antonio PASCUAL HEREDIA', 'Juan EDUARDO', 'Juan FIGUEROA', 'Juan HERRERO MAZUELAS', 'Juan OTERO', 'Juan Pablo VAZQUEZ PUJALES', 'Jubal DAVIS', 'Juha VAINIKKA', 'Juhani KETTUNEN', 'Jules GRANET', 'Julian GUERRERO PEREZ CEJUELA', 'Julien BARTHELEMY', 'Julien BERENGER', 'Julien BOLOTA', 'Julien BROSSE', 'Julien CAMELLINI', 'Julien CHARGE', 'Julien CHAUDET', 'Julien COQUELET', 'Julien CORFU', 'Julien GAUDET', 'Julien KNUCHEL', 'Julien MAIROT', 'Julien PETIT', 'Julien PRENEZ', 'Julien ROEHRIG', 'Julien ROISSARD', 'Julien ROSSE', 'Julien THOMAS', 'Julien VENDRIES', 'Juliet VINCENT', 'Julio HOCHSCHILD', 'Junya NAGATA', 'Jurgen DOLD', 'Jussi RAJALA', 'Justin FERNANDES', 'Justin LEOV', 'Juuso PIHLAJA', 'Kai WENDSCHUH', 'Kal FARMER', 'Kamil TATARKOVIC', 'Kane CHANDLER', 'Karim AMOUR', 'Karl CONNOLLY', "Karl O'SULLIVAN", 'Kashi LEUCHS', 'Keegan WRIGHT', 'Keelim RYAN', 'Keith BROCK', 'Keith BUCHAN', 'Keith PRAWALSKY', 'Kelan GRANT', 'Ken PERRAS', 'Kenny BELAEY', 'Kenny MCLEAN', 'Kev DUCKWORTH', 'Kevin BOYER', 'Kevin BRU', 'Kevin DUGGAN', 'Kevin LORENZATO', 'Kevin MIQUEL', 'Kevin MORAN', 'Kevin SIMARD', 'Kevin SMALLMAN', 'Kevin SOLLER', 'Kieran BENNETT', 'Kieran MCCARTHY', 'Kilian BRON', 'Kirt VOREIS', 'Klas OBERG', 'Klemen MARKUS', 'Kolben PREBLE', 'Konstantin MAKSIMOV', 'Kristijan MEDVESCEK', 'Kristjan MEDVESCEK', 'Kristof SCHREITER', 'Kyle LOFSTEDT', 'Kyle MALEE', 'Kyle MEARS', 'Kyle WARNER', 'Lachlan BLAIR', 'Lander FERNANDEZ', 'Larry DOUGLAS', 'Lars STERNBERG', 'Latorre Andres FERNANDEZ', 'Laurent CORSO', 'Laurent FUMAROLI', 'Laurent PRAZ', 'Laurent REVIRON', 'Laurent SOLLIET', 'Laurent TANGUY', 'Lawrence FARRINGTON', 'Lawrence JONES', 'Lee BAINES', 'Lee HAWDEN', 'Lee JORDAN', 'Lee KERMODE', 'Leif WINSTEAD', 'Leighton KIRK', 'Leith MCLEOD', 'Leland TURNER', 'Leo KOKKONEN', 'Leoluca SCURRIA', 'Leonardo SANTANA', 'Leonhard PUTZENLECHNER', 'Lester PERRY', 'Lewis BUCHANAN (elt)', 'Lewis KIRKWOOD', 'Liam DAWSON', 'Liam LITTLE (elt)', 'Liam LONG', 'Liam MOYNIHAN', 'Liam TYRRELL', 'Lief CHRISTENSEN', 'Lindsay KLEIN', 'Lionel FERNANDES', 'Lluis SEGURA CURTO', 'Loic BRUNI', 'Loic GUERIN', 'Loic LACASTE', 'Loic PIAZZON', 'Lorenzo AMADORI', 'Lorenzo CESARETTI', 'Lorenzo SORMANI', 'Lorenzo SUDING', 'Lorenzo VANNUCCI', 'Loui HARVEY', 'Louis PARALITICI', 'Luca AMILICIA', 'Luca ANGELONE', 'Luca BERTOCCHI', 'Luca BIWER', 'Luca FONTANA', 'Luca FORTESCHI', 'Luca GIANNECCHINI', 'Luca GUGLIELMUCCI', 'Luca MARINO', 'Luca MARTINI', 'Luca MELLANA', 'Luca NOTARIO', 'Luca TERZAROLI', 'Luca ZANETTE', 'Luca ZENONE', 'Lucas FRIGOUT', 'Lucas REDOIS', 'Luciano CARCHERI', 'Ludovic MAY', 'Ludovic OGET', 'Ludwig DOHL', 'Luigi CANALI', 'Luigi DE SANTI', 'Luigi PAVONE', 'Luigi SVANOSIO', 'Luis ALTENFELDER', 'Lukas ANRIG', 'Lukas FLUCKIGER', 'Lukas HOCKER', 'Lukas LEITSBERGER', 'Lukas SCHMITZ', 'Lukasz KOZLOWSKI', 'Luke DONALDSON', 'Luke GARSIDE', 'Luke GERRETT', 'Luke STROBEL', 'Macky FRANKLIN', 'Maicol CECCHI', 'Mandil PRADHAN', 'Manex BALERDI', 'Manuel BENGOLEA', 'Manuel BERTHOMIER', 'Manuel DUCCI', 'Manuel FUMIC', 'Manuel LOCATELLI', 'Manuel MARTINEZ', 'Marc BOSCA', 'Marc CERDAN', 'Marc LAMMENS', 'Marc LLAGOSTERA CARLES', 'Marcel LAUXTERMANN', 'Marcello PESENTI', 'Marcello PIZZI', 'Marcello SCOTTI', 'Marco Aurelio FONTANA', 'Marco Aurelio Silva FIDALGO', 'Marco BOLOGNA', 'Marco BONELLA', 'Marco BOTTICCHIO', 'Marco BUHLER', 'Marco CANTARUTTI', 'Marco CENNI', 'Marco COLOMBO', 'Marco DA COL', 'Marco DE COL', 'Marco DURASTANTI', 'Marco FULLONE', 'Marco FUMAGALLI', 'Marco MARCON', 'Marco MILIVINTI', 'Marco MOGNI', 'Marco OSBORNE', 'Marco PEGORARO', 'Marco PERLETTI', 'Marco RODOLICO', 'Marco TANI', 'Marco TIBERI', 'Marco VINCENZI', 'Marcos COBOS', 'Marcos Walter MALLMANN', 'Marcus KLAUSMANN', 'Mariano CISTERNA', 'Mariano NAJLES', 'Mario BORRAJA NUNEZ', 'Mario KRANZ', 'Mark BROOKS', 'Mark CHEETHAM', 'Mark DUNLOP', 'Mark FERNIHOUGH', 'Mark GREGORY', 'Mark HESTER', 'Mark JESSUP', 'Mark KELLY', 'Mark MCCOURT', 'Mark MILWARD', 'Mark NUGENT', 'Mark RAVILIOUS', 'Mark SCOTT', 'Mark TAYLOR', 'Mark WALLACE', 'Mark WEIR', 'Mark WEST', 'Markel URIARTE URRUTIA', 'Markus GREITZKE', 'Markus PEKOLL', 'Markus REISER', 'Martial COPIN', 'Martin ASTLEY', 'Martin BAYER', 'Martin BIRKHOFER', 'Martin BUTTERLY', 'Martin CAMPOY', 'Martin CONCHA', 'Martin DONAT', 'Martin Daniel RAFFO', 'Martin EGUIGUREN RODRIGUEZ', 'Martin FLANO', 'Martin GREBING', 'Martin KAEGI', 'Martin KEYS', 'Martin LARSSON', 'Martin LISLE', 'Martin MAES', 'Martin MCGUIRE', 'Martin MILLAUD', 'Martin PLANCKART', 'Martin ZIETSMAN', 'Martino DI PIERDOMENICO', 'Martino FRUET', 'Martxel ORONOZ', 'Marty LAZARSKI', 'Martyn BROOKES', 'Martyn FOUBISTER', 'Marvin Ray GAMBERI', 'Mason BOND', 'Massimiliano BACCOLINI', 'Massimiliano CAROLI', "Massimiliano D'INGILLO", 'Massimiliano MANGANELLI', 'Massimo ARTUDI', 'Massimo BRUNATTI', 'Massimo MAZZOLENI', 'Massimo PARENZI', 'Mat TERRELL', 'Matej CHARVAT', 'Matej VITKO', 'Mateos FACUNDO', 'Mathew PRICHARD', 'Mathew WOODALL', 'Mathias BOYER', 'Mathias FLUCKIGER', 'Mathias HAVAUX', 'Mathieu BALLION', 'Mathieu BUATOIS', 'Mathieu LADEUICH', 'Mathieu LORNAC', 'Matias DEL SOLAR', 'Matt BIRKBY', 'Matt BOUGHTON', 'Matt FINBOW', 'Matt MILLER', 'Matt RYAN', 'Matt SNELLING', 'Matt WALKER', 'Matteo BERNARDI', 'Matteo BERTA', 'Matteo BERTOS', 'Matteo CARRUBBA', 'Matteo GUGGER', 'Matteo Giulio POLO', 'Matteo MERLO', 'Matteo MEZZARI', 'Matteo MOLINARI', 'Matteo PALAZZI', 'Matteo PLANCHON', 'Matteo RAIMONDI', 'Matteo ROSSI NINCHI', 'Matteo SALARI', 'Matteo SALVI', 'Matthew ATKINSON', 'Matthew BEER', 'Matthew CORK', 'Matthew FRETWELL', 'Matthew HUNT', 'Matthew INESON', 'Matthew LOVE', 'Matthew MANSELL', 'Matthew MCMILLAN', 'Matthew SLAVEN', 'Matthias BORCIER', 'Matthias MENZL', 'Matthias SCHMID', 'Matthias STONIG', 'Matthieu FAURY', 'Matthieu MENGEL', 'Matthieu SEGUY', 'Matti LEHIKOINEN', 'Mattia ARDUINO', 'Mattia FOLCHI', 'Mattia MORASCHI', 'Mattia SETTI', 'Matty STUTTARD', 'Maurian MARNAY', 'Maurice VERCELLINO', 'Mauricio Andres ACUNA QUINTANA', 'Mauricio CARRASCO ZANZANI', 'Maurin TROCELLO', 'Maurizio BISTERZO', 'Maurizio LAZZARINI', 'Maurizio MARIANI', 'Maurizio MONTALDO', 'Mauro ARDIZIO', 'Mauro BARSI', 'Mauro RIVELLINI', 'Mauro SALVI', 'Max FRANKE', 'Max HORNER', 'Max LEITSBERGER', 'Max SCHUMANN', 'Max VAN DER LEE', 'Maxence BOUET', 'Maxi DICKERHOFF', 'Maxime CHAPUIS', 'Maxime DEKEYSER', 'Maxime DI NARDO', 'Maxime LEVERT', 'Maxime MAUVAIS', 'Maximilian HARNISCHFEGER', 'Maximilian MITTELBACH', 'Maximiliano GALLO', 'Maximov KONSTANTIN', 'Mckay VEZINA', 'Mehdi GABRILLARGUES', 'Michael BATEMAN', 'Michael BORNER', 'Michael BUELL', 'Michael BURTON', 'Michael CLYNE', 'Michael COWAN', 'Michael EASTON', 'Michael GRAY', 'Michael HANNAH', 'Michael HAYWARD', 'Michael HEIN', 'Michael HERLETH', 'Michael JANNEY', 'Michael JOHNSTONE', 'Michael KULL', "Michael L'HOTE", 'Michael LARSEN', 'Michael LOZACHMEUR', 'Michael RONNING', 'Michael SCHARER', 'Michael VIERSET', 'Michael WATT', 'Michal PROKOP', 'Michel ANGELINI', 'Michel BEAUDENOM', 'Michel VASSEUR', 'Michele DESTEFANIS', 'Michele GAETA', 'Michele MIANI', 'Michele PASQUALI', 'Michele TARDINI', 'Michiel HOGERZEIL', 'Mickael FREYCENON', 'Miguel Angel GALAN GARCIA', 'Miguel Marques PARDAL', 'Miguel RAMOS', 'Mika KANGAS', 'Mikael KERANEN', 'Mike COWLIN', 'Mike HALL', 'Mike HOLME', 'Mike HORNER', 'Mike JONES (elt)', 'Mike Mihai MOGA', 'Mike ROBERTSON', 'Mike SCHULER', 'Mike WEST', 'Mikhail VASILENKO', 'Mikko JAAKONSAARI', 'Milan MYSIK', 'Milciades JAQUE', 'Milton Sebastian CONTRERAS BARRERA', 'Mint HENK', 'Miquel CARRASCO SANCLIMENT', 'Mirco WIDMER', 'Mitch CHUBEY', 'Mitch ROPELATO', 'Mitchell CURRIE', 'Montava ANTONIO PEREZ', 'Moray GOODFELLOW', 'Moritz STROEER', 'Morris GOODING', 'Morten KROGH HANSEN', 'Nace KRIVONOG', 'Nash MASSON', 'Nathan ADAMS', 'Nathan CORRIGAN', 'Nathan MCCOMB', 'Nathan RIDDLE', 'Nathan TUCKER', 'Nathaniel HILLS', 'Nector VEAS', 'Neil ALLISON', 'Neil DONOGHUE', 'Neil HALCROW', 'Neil IRVING', 'Neil KENNEDY (sen)', 'Neil LACEY', 'Neil MARTIN', 'Neil MCCONVILLE', 'Neil MCLEAN', 'Nejc CERNILOGAR', 'Nejc RUTAR', 'Niall DAVIS', 'Niall EGAN', "Niall O'FLAHERTY", 'Nic Bennett KASCHUB', 'Nicholas WARN', 'Nick BARBER', 'Nick BURTON-LEGGE', 'Nick ETTER', 'Nick GEDDES', 'Nick GIBSON', 'Nick HANLEY', 'Nick HARDIN', 'Nick MAHER', 'Nick TEEBOON', 'Nick TRUITT', 'Nicola CASADEI', 'Nicola FISTOLERA', 'Nicola ROHRBACH', 'Nicola VILLA', 'Nicolas BAISIN', 'Nicolas CASTEELS', 'Nicolas DELVAUX', 'Nicolas GUY-CARON', 'Nicolas IDELON', 'Nicolas LAU', 'Nicolas LEGRAND', 'Nicolas MAVIT', 'Nicolas PALACIOS', 'Nicolas PILLET', 'Nicolas PRUDENCIO FLANO', 'Nicolas QUERE', 'Nicolas ROISSARD', 'Nicolas SIMMEN', 'Nicolas VOUILLOZ', 'Nicolas WALSER', 'Nicolas ZORTEA', 'Niels VAN DE VORST', 'Nigel JARVIS', 'Nigel MCDOWELL', 'Nikki WHILES', 'Niklas WALLNER', 'Niklaus MOSLE', 'Nikodem BYRKA', 'Ninchi Matteo ROSSI', 'Nino SCHURTER', 'Noah SEARS', 'Oisin BOYDELL', 'Ola ALSTERHOLM', 'Ola BUOY JOHN', 'Ole Christian FAGERLI', 'Olimpio SPINI', 'Oliver CARTER (1)', 'Oliver HUW', 'Oliver MCKENNA', 'Oliver MUNNIK', 'Oliver PATON (jun)', 'Oliver RUSHTON', 'Oliver WINDLER', 'Oliver YOUNG', 'Oliveri MASSIMO', 'Olivier BRUWIERE', 'Olivier DESMAISON', 'Olivier GIORDANENGO', 'Olivier PASCAL', 'Olivier VANDENBROUCKE', 'Oliwer KANGAS', 'Olle WEDIN', 'Oriol BRUNET GARCIA', 'Oriol MORGADES', 'Oscar FAYET SAENZ', 'Oscar HARNSTROM', 'Oscar IBANEZ ALONSO', 'Oscar SAIZ CASTANE', 'Ottavio RUGGIERO', 'Ove GRONDAL', 'Owain JAMES', 'Pablo BIANCHI', 'Pablo CASTRO DURAN', 'Pablo GONZALEZ', 'Pablo HORTA', 'Pablo Ignacio FLORES GOMEZ', 'Pablo MALDONADO', 'Pablo SOTO', 'Paddy LYNCH', 'Paolo Antonio FEDELI', 'Paolo CASTEGNARO', 'Paolo CIANCI', 'Paolo FENOCCHIO', 'Paolo GRASSINI', 'Paolo GUERRIERI', 'Paolo MENTI', 'Paolo TONLORENZI', 'Pascal KNUCHEL', 'Pascal WIDMER', 'Patric TINNER', 'Patrice BUISSAN', 'Patricio GOYCOLEA', 'Patrick BONIFAY', 'Patrick BONTEMPS', 'Patrick BUTLER', 'Patrick LYNCH', 'Patrick PIEPENSTOCK', 'Patrick SOUSA', 'Pau REIXACHS FERRER', 'Paul ANGUS', 'Paul ASTON', 'Paul CAFFIN', 'Paul CALDWELL', 'Paul COMMIN', 'Paul CUMMINS', 'Paul DOTSENKO', 'Paul GAYRAL', 'Paul HAYSOM', 'Paul HEATHCOTE', 'Paul JEPPSON', 'Paul LENIHAN', 'Paul MALISSARD', 'Paul NEWNHAM', "Paul O'BRIEN", 'Paul PICKUP', 'Paul SMAIL', 'Paul STEVENS', 'Paul VAN DER PLOEG', 'Paul WARREN', 'Paul WILSON (end)', 'Pearse GRIFFIN', 'Pedro BARROS', 'Pedro BARROSO L.', 'Pedro DAPENA CASTROMAN', 'Pedro FERREIRA', 'Pedro RIVAS', 'Peter BOADEN', 'Peter LOSCHER', 'Peter MCDONAGH', 'Peter MCELROY', 'Peter MLINAR', 'Peter OAKLEY', 'Peter OSTROSKI', 'Peter ROBINSON', 'Peter ROBSON', 'Petr FRANO', 'Petrik BRUCKNER', 'Phil OTT', 'Philip ATWILL', 'Philip BYRNE', 'Philip SHUCKSMITH', 'Philip WALDER', 'Philipp GERKEN', 'Philipp MEYER-KRENTLER', 'Philipp SCHERZINGER', 'Philippe MARTINEZ', 'Philippe PROVOST', 'Philippe RICARD', 'Philippe WIDMER', 'Phillip MCLAREN', 'Pierre Charles GEORGES', 'Pierre HENNI', 'Pierre LEHRY', 'Pierre MASOYE', 'Pierre MOMMESSIN', 'Pierre ROUX', 'Pierre Yves LIVERNEAUX', 'Pierre Yves LONGUETEAU', 'Pierre-Luc VAXELAIRE', 'Pierrick HUET', 'Pierrick SAUZEAT', 'Pieter GELUYKENS', 'Pietro CHINUCCI', 'Pietro LAMIANI', 'Pirmin KUss', 'Pol GUIXE JOVE', 'Pol ROMERO PERICH', 'Premek TEJCHMAN', 'Primoz GAMS', 'Primoz STRANCAR', 'Przemyslaw WIERZBICKI', 'Quentin ARNAUD', 'Quentin CHAMPION', 'Quentin CHENEVAL', 'Quentin DE CARVALHO', 'Quentin EMERIAU', 'Quentin LEPINE', 'Quentin STEPIEN', 'Rab WARDELL', 'Radek SZEREMETA', 'Rafael CASETTI', 'Rafael MOLINA CASTILLO', 'Rafal BELZOWSKI', 'Rafal ORTYNSKI', 'Ramun TSCHENETT', 'Raphael HEULE', 'Raphael LEISTNER', 'Raul FATTORI', 'Ravera BRUNO', 'Ray SYRON', 'Regan MCCORQUINDALE', 'Remi AUBERT', 'Remi CAPELLE', 'Remi GAUVIN', 'Remi SUPPER', 'Remi TROMEL', 'Remy ABSALON', 'Remy DURAND', 'Renaud DUPONT', 'Renaud HAVAUX', 'Rene WILDHABER', 'Rhys TELFORD', 'Ricardo PARREIRINHA', 'Riccardo PERSICO', 'Rich NORGATE', 'Richard CUNYNGHAME', 'Richard GASPEROTTI', 'Richard HAMILTON', 'Richard KAWECKI', 'Richard LANE', 'Richard PAYNE (elt)', 'Richard PAYNE (exp)', 'Richard SELBY', 'Richard THORNHILL', 'Richie RUDE Jr.', 'Rick MINSHULL', 'Riley TAYLOR', 'Rino FLOTTA', 'Rob JAMES', 'Rob QUINN', 'Rob RINGLE', 'Rob SCULLION', 'Rob SHERRATT', 'Rob SPRAGG', 'Robb RAND', 'Robert ELLISON', 'Robert HAMILTON-SMITH', 'Robert HAUSLER', 'Robert KORDEZ', 'Robert NICHOLS', 'Robert SLANEY', 'Robert WILLIAMS (elt)', 'Roberti TIZIANO', 'Roberto ANTALI', 'Roberto CIAMBRONE', 'Roberto DORDONI', 'Roberto MASCIADRI', 'Roberto MIERES', 'Roberto MORETTO', 'Roberto RODRIGUEZ MARTINEZ', 'Robin BROWN', 'Robin CHAUVIN', 'Robin LECHEVALLIER', 'Robin MAGNIN', 'Robin SARRAZIN', 'Robin SEYMOUR', 'Robin WALLNER', 'Robinson ALMONACID', 'Rocco SAVANI', 'Rod ELLIOT', 'Rodrigo CABELLO', 'Rodrigo GARCIA', 'Rodrigo GUARITA', 'Rodrigo NUNO', 'Rodrigo PARDO', 'Rodrigo SILVA', 'Roel VAN DER SLUIS', 'Roger CAMPBELL-CRAWFORD', 'Roger GONZALEZ SALVADOR', 'Rok MARKUS', 'Roland CZUDAY', 'Roland Jan SPAARWATER', 'Romain DAMONT', 'Romain LOPEZ', 'Romain SGARD', 'Roman BALAEV', 'Roman CZAJKOWSKI', 'Ronan DUGAN', 'Ronni ROSSI', 'Ronny SEIFERT', "Rory O'DONNELL", "Rory O'KEEFFE", 'Ross GREEN', 'Ross GRIMMETT', 'Ross LAMBIE', 'Ross MILAN', 'Ross PEARSON', 'Ross SCHNELL', 'Rouillon CORENTIN', 'Rouwen HENSS', 'Roy BENGE', 'Ruaridh CUNNINGHAM', 'Ruben JIMENEZ GOMEZ', 'Ruben MARTINS', 'Ruben SALZGEBER', 'Ruben VAZQUEZ LOPEZ', 'Rudolf BIEDERMANN', 'Rudy CABIROU', 'Rudy SAMUELLI', 'Rupert CHAPMAN', 'Russel TURNER', 'Ryan CAMPO', 'Ryan CONNELL', 'Ryan DE LA RUE', 'Ryan GAGNON', 'Ryan GARDNER', 'Ryan GEIGER', 'Ryan HELMUTH', 'Ryan LUSE', 'Ryan STIMAC', 'Saben ROSSI', 'Sam BENEDICT', 'Sam BLENKINSOP', 'Sam DALE (elt)', 'Sam FARRAR', 'Sam FLANAGAN', 'Sam FLOCKHART', 'Sam GERRETT', 'Sam GLADMAN', 'Sam HILL (elt)', 'Sam PANTLING', 'Sam RODDA (sen)', 'Sam SHARP', 'Sam SHUCKSMITH', 'Sami WUTHRICH', 'Samuel BUWERT', 'Samuel DIAZ ZORRILLA', 'Samuel PERIDY', 'Samuel POUGNET', 'Samuel SHAW', 'Samuel STEVENS', 'Samuele AICARDI', 'Samuli LOUKO', 'Sandro ALFEO', 'Sante PELOT', 'Santiago LOMBO', 'Santiago PEREZ', 'Sauli HJERPPE', 'Scott CHAPIN', 'Scott CLARKE', 'Scott COUNTRYMAN', 'Scott EVANS', 'Scott LAUGHLAND', 'Scott LINDSAY', 'Scott MARSHALL', 'Scott NELSON (mas)', 'Scott TAYLOR', 'Seamus CASH', 'Seamus POWELL', 'Sean CURTIN', 'Sean GLYNN', 'Sean HERLIHY', 'Sean LEADER', 'Sean MACKESSY', 'Sean MEIGHAN', 'Sean SHUMAN', 'Seb LLOYD', 'Seb RAMSAY', 'Sebastian ESSWEIN', 'Sebastian GEFREJTER', 'Sebastian RAMIREZ', 'Sebastian STOTT', 'Sebastien CLAQUIN', 'Sebastien GRISENDE', 'Sebastien GUILLAUME', 'Sebastien LE MARECHAL', 'Sebastien MIRAS', 'Sebastien PETIT', 'Sebastien PEYSSONNEAUX', 'Sebastien PHILIPPE', 'Sebastien POESY', 'Sebastien THEROND', 'Serge DEMICHELIS', 'Sergi BRUGAT COSTA', 'Sergio AGOSTO', 'Sergio ANTECAO', 'Sergio BELOTTI', 'Sergio CAMPO RULLAN', "Sergio D'AMICO", 'Sergio DIEZ TAPIA', 'Sergio FALLA MARTOS', 'Sergio PEREZ', 'Sergio TSCHENETT', 'Seth AANDEWIEL', 'Shane GAYTON', 'Shane KROEGER', 'Shane NORTON', 'Shaun FRY', 'Shawn ARTERBURN', 'Si WARD', 'Silas HESTERBERG', 'Silvan MARFURT', 'Silvio BUNDI', 'Simo KALATIE', 'Simon ANDRE', 'Simon BARRAL', 'Simon BUZACOTT', 'Simon CHARVAT', 'Simon DOYLE', 'Simon EVERITT', 'Simon GEGENHEIMER', 'Simon GOODWIN', 'Simon HARTLEY', 'Simon HEINZEMANN', 'Simon HUMPHRIES', 'Simon LEROUX', 'Simon MARSHALL', 'Simon METCALFE', 'Simon PRICE', 'Simon TRUELOVE', 'Simon VALENTI', 'Simone BONETTI', 'Simone BRESCIA', 'Simone CAPPELLINI', 'Simone FABBRI', 'Simone INVERNIZZI', 'Simone SERI', 'Simone TABARRANI', 'Simone ZANELLATO', 'Simone ZANIBONI', 'Slawomir LUKASIK', 'Spencer PAXSON', 'Spencer POWLISON', 'Spencer WIGHT', 'Stan JORGENSEN', 'Stanislav SEHNAL', 'Stefan OBERBICHLER', 'Stefan PETER', 'Stefano BALESTRACCI', 'Stefano DE PAOLA', 'Stefano GENNAIOLI', 'Stefano MIGLIORINI', 'Stefano POLETTI', 'Stefano POLETTO', 'Stefano ROTA', 'Stefano SEMERIA', 'Stefano TOFFOLETTI', 'Stefano VARNERIN', 'Stephan HEIN', 'Stephan SPROLL', 'Stephan WOHRLE', 'Stephane BESACIER', 'Stephane CHICO', 'Stephane PAUPERT', 'Stephane PIERRE', 'Stephane VALVERDE', 'Stephen BOYLE', 'Stephen FAGAN', 'Stephen HARDCASTLE', 'Stephen NOLAN', 'Stephen SCRIVENER', 'Stephen TIMMONS', 'Stepien QUENTIN', 'Steve DEMPSEY', 'Steve LECOURT', 'Steve MILNE', 'Steve PEAT', 'Steve PECHET', 'Steven BALDOCK', 'Steven COX', 'Steven DALY', 'Steven LARKING', 'Stevie CULLINAN', 'Stuart DICKSON', 'Stuart HIBBERT', 'Stuart NICHOLSON', 'Stuart VILLIS', 'Stuart WILCOX', 'Sven ALBAN', 'Sven Ivar JOHNSEN', 'Sven KLEIN', 'Sylvain BAUD', 'Sylvain MARONNEAU', 'T.J. WALKER', 'Tadhg SHEEHAN', 'Tamir ZINGER', 'Taylor LIDEEN', 'Teodoro NASS', 'Teodoro ROFRANO', 'Theo GALY', 'Thiago VELARDI', 'Thibaud DAVID', 'Thibault CORREARD', 'Thibault VIALA', 'Thibaut LEGASTELOIS', 'Thibaut MONTAGNONI', 'Thibaut PONCET', 'Thibaut SARAZIN', 'Thierry GASPARINI', 'Thomas ADAMS', 'Thomas Andrew DADDI', 'Thomas BAILLY', 'Thomas BLONDEAU', 'Thomas BOCH', 'Thomas BOSCHETTO', 'Thomas CHAZOTTES', 'Thomas DECUGIS', 'Thomas DELECRAY', 'Thomas DI LITTA', 'Thomas ESCUDIER', 'Thomas GERING', 'Thomas HARTSTERN', 'Thomas HENDRIKSEN', 'Thomas HUMMEL', 'Thomas JOUET PASTRE', 'Thomas KERN', 'Thomas LAPEYRIE', 'Thomas MITCHELL', 'Thomas SCHUSTER', 'Thomas SOUCHEYRE', 'Thomas WARBURTON', 'Tim BREEZE', 'Tim GARRECHT', 'Tim MCCULLOUGH', 'Tim MILLS', 'Tim MORRISON', 'Tim PRICE', 'Tim WALTERS', 'Tim WILLIAMS (mas1)', 'Timothe NEYTARD', 'Timothee OPPLIGER', 'Timothy CARSON', 'Timothy CROSBY', 'Tiziano DAVINI', 'Tiziano INTERNO', 'Tiziano ROBERTI', 'Tobia POLONI', 'Tobias MULLER', 'Tobias PANTLING', 'Tobias REISER', 'Tobias WOGGON', 'Todd MADSEN', 'Tom BRADSHAW', 'Tom CAMPBELL (mas)', 'Tom COOMBES', 'Tom COSGROVE', "Tom DORAN (O'BRIEN)", 'Tom DOWIE', 'Tom GARCIA', 'Tom GIBSON', 'Tom HICKEY', 'Tom HORN', 'Tom JENNINGS', 'Tom MAES', 'Tom MAURY', 'Tom MOORE (sen)', 'Tom SKILLICORN', 'Tom WILSON (mas)', 'Tomas BAEZA', 'Tomas BARRETT', 'Tomas FONTANA', 'Tommy LACOUR', 'Tommy UMBREIT*</span>', 'Tony LENNON', 'Tony RAMPON', 'Trevor BURKE', 'Trevor PRATT', 'Trevor WORSEY', 'Trevyn NEWPHER', 'Tristan MERRICK', 'Tristan MONNIER', 'Tristan RAWLENCE', 'Troy BROSNAN', 'Troydon MURISON', 'Truan WILLIS', 'Ty HATHAWAY', 'Ty HORTON', 'Tyler FRASCA', 'Tyler MORLAND', 'Ugo CATTANEO', 'Ulrich KASCHUB', 'Ulrich THEOBALD', 'Ulysse FRANCOGLIO', 'Umberto ANDREOLI', 'Umberto PARO', 'Unknown RIDER', 'Urs PARGMANN', 'Urs STADELMANN', 'Valentin FOSSE', 'Valentin GUIZARD BRES', 'Valentino FARINOLA', 'Vicente DIAZ', 'Victor BRUGUERA', 'Victor GALVEZ', 'Victor Manuel AQUILUE ESCARTIN', 'Vid PERSAK', 'Ville TUPPURAINEN', 'Vincent CHICO', 'Vincent COLANGE', 'Vincent DELAMOTTE', 'Vincent FUMAROLI', 'Vincent GRIME', 'Vincent HAULET', 'Vincent PIQUET', 'Vincent TSOI', 'Vincente Diaz SIMONETTI', 'Vincenz THOMA', 'Vincenzo CAMPLANI', 'Vinicio CRIGHTON-POLI', 'Vito TSCHENETT', 'Vittorio GAMBIRASIO', 'Walker SHAW', 'Walter IANNONE', 'Wanier PALMERINI', 'Waylon SMITH', 'Wayne MORRIS', 'Wesley LAMBERSON', 'Will CURRY', 'Will MARKS', 'Will MCDONALD', 'Willem COOPER', 'William CADHAM', 'William MATHIESON', 'Wouter SMITS', 'Wyn MASTERS', 'Xavier MAROVELLI', 'Xavier MURIGNEUX', 'Xavier RIGOL LOPEZ', 'Xavier THEATE', 'Yann BADIER', 'Yann GADOIN', 'Yann GUIGOZ', 'Yann QUERE', 'Yannick OFFREDI', 'Yannick PONTAL', 'Yannick SENECHAL', 'Yoan PESENTI', 'Yoann BARELLI', 'Yoann PACCARD', 'Yohann DEBURGGRAEVE', 'Yohann VACHETTE', 'Yuri PEREIRA', 'Yuri VERSURARO', 'Yuuki KUSHIMA', 'Zac WILLIAMS', 'Zakarias JOHANSEN', 'Zdenek NASINEC', 'Ziga PANDUR']

def whistler_name_match():
    names = [x[0] for x in whistler_list]
    for name_idx, name in enumerate(names):
        a, b = process.extractOne(name, full_names, scorer=fuzz.ratio)
        _, b2 = process.extractOne(name, full_names, scorer=fuzz.partial_ratio)
        _, b3 = process.extractOne(name, full_names, scorer=fuzz.token_set_ratio)
        _, b4 = process.extractOne(name, full_names, scorer=fuzz.token_sort_ratio)
        c = (b + b2 + b3 + b4) / 4

        if c > 80:
            whistler_list[name_idx][0] = a

        columns = ["name", "stage1_time", "stage1_position", "stage2_time",
                       "stage2_position", "stage3_time", "stage3_position",
                       "stage4_time", "stage4_position", "stage5_time", "stage5_position",  "finish_time",
                       "finish_position"]

        whistler_df = pd.DataFrame(whistler_list, columns=columns)
        whistler_df['year'] = 2016
        whistler_df['round_num'] = 6
        whistler_df['round_loc'] = 'Whistler, BC, Canada'
        whistler_df["stage8_time"] = 'Not Raced'
        whistler_df["stage8_position"] = 'Not Raced'
        whistler_df["overall_position"] = ''
        whistler_df["country"] = ''
        whistler_df["stage6_time"] = 'Not Raced'
        whistler_df["stage6_position"] = 'Not Raced'
        whistler_df["stage7_time"] = 'Not Raced'
        whistler_df["stage7_position"] = 'Not Raced'
        whistler_df["time_behind"] = ''
        whistler_df["dnf"] = False
        whistler_df["dns"] = False
        whistler_df["dsq"] = False
        whistler_df["out_at_stage"] = 0

        whistler_df['finish_time'] = whistler_df['finish_time'].apply(lambda x: '0:' + x if x.count(':') < 2 else x)

        whistler_df['time_behind'] = pd.to_datetime(whistler_df['finish_time'])
        whistler_df['time_behind'] = whistler_df['time_behind']\
            .apply(lambda x: pd.Timedelta(x - whistler_df.loc[0, 'time_behind']))
        whistler_df['time_behind'] = whistler_df['time_behind'].apply(lambda x: str(x)[10:-4])
        whistler_df['time_behind'] = whistler_df['time_behind'].apply(lambda x: x[3:] if x[:3] == '00:' else x)
        whistler_df['time_behind'] = whistler_df['time_behind'].apply(lambda x: x[1:]\
            if x[:1] == '0' and len(x) > 1 else x)
        print(whistler_df['time_behind'])

        os.makedirs(r'C:\EWSData\Whistler, BC 2016', exist_ok=True)
        whistler_df.to_csv(r'C:\EWSData\Whistler, BC 2016\Results.csv', encoding='utf-8')

        return whistler_list


def rotorua_name_match():
    names = [x[1] for x in rotorua_list]
    for name_idx, name in enumerate(names):
        a, b = process.extractOne(name, full_names, scorer=fuzz.ratio)
        _, b2 = process.extractOne(name, full_names, scorer=fuzz.partial_ratio)
        _, b3 = process.extractOne(name, full_names, scorer=fuzz.token_set_ratio)
        _, b4 = process.extractOne(name, full_names, scorer=fuzz.token_sort_ratio)
        c = (b + b2 + b3 + b4) / 4

        if c > 80 and name != 'James PRITCHARD':
            rotorua_list[name_idx][1] = a

        columns = ["overall_position", "name", "country", "stage1_time", "stage1_position", "stage2_time", "stage2_position", "stage3_time", "stage3_position",
                   "stage4_time", "stage4_position", "stage5_time", "stage5_position", "stage6_time", "stage6_position",
                   "stage7_time", "stage7_position", "finish_time", 'finish_position',"time_behind", "dnf", "dns", "dsq", "out_at_stage"]


        rotorua_df = pd.DataFrame(rotorua_list, columns=columns)
        rotorua_df['round_num'] = 1
        rotorua_df['year'] = 2015
        rotorua_df['round_loc'] = 'Rotorua, New Zealand'
        rotorua_df["stage8_time"] = 'Not Raced'
        rotorua_df["stage8_position"] = 'Not Raced'
        rotorua_df["penalties"] = ''
        rotorua_df.replace('6969', '', inplace=True)
        print(rotorua_df.head())

        os.makedirs(r'C:\EWSData\Rotorua 2015', exist_ok=True)
        rotorua_df.to_csv(r'C:\EWSData\Rotorua 2015\Results.csv', encoding='utf-8')
        return rotorua_list
whistler_name_match()
rotorua_name_match()


#print(process.extractOne('Josh CARLSON', full_names)[0])

#if its above the threshhold change the current name, otherwise keep it the same because its a new rider