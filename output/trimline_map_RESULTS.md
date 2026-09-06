# trimline_map.py results

DEM: HMA 8 m (GLO-30 fill). Stations every 100 m; sections +/-600 m (+/-1,500 m below km 70).
| reach | km | layer | stations | both banks | one bank | cloud-truncated | open/no-bare | clean stage pts |
|---|---|---|---|---|---|---|---|---|
| Lhende gorge | 8.0-21.5 | s2 | 135 | 109 | 19 | 19 | 10 | 121 |
| Lhende gorge | 8.0-21.5 | s2chg | 135 | 109 | 23 | 19 | 9 | 122 |
| Lhende gorge | 8.0-21.5 | pelican0827 | 135 | 0 | 1 | 15 | 1 | 0 |
| Lhende gorge | 8.0-21.5 | pelican0901 | 135 | 2 | 13 | 13 | 0 | 6 |
| border junction | 21.5-22.8 | s2 | 13 | 11 | 2 | 0 | 2 | 0 |
| border junction | 21.5-22.8 | s2chg | 13 | 11 | 2 | 0 | 2 | 0 |
| border junction | 21.5-22.8 | pelican0827 | 13 | 8 | 5 | 5 | 0 | 0 |
| border junction | 21.5-22.8 | pelican0901 | 13 | 11 | 2 | 0 | 2 | 0 |
| Bhote Koshi gorge | 22.8-35.6 | s2 | 128 | 127 | 0 | 1 | 0 | 164 |
| Bhote Koshi gorge | 22.8-35.6 | s2chg | 128 | 127 | 0 | 1 | 0 | 167 |
| Bhote Koshi gorge | 22.8-35.6 | pelican0827 | 128 | 94 | 13 | 33 | 1 | 64 |
| Bhote Koshi gorge | 22.8-35.6 | pelican0901 | 128 | 127 | 1 | 1 | 0 | 111 |
| Syabrubesi opening | 35.6-40.0 | s2 | 44 | 41 | 3 | 1 | 2 | 70 |
| Syabrubesi opening | 35.6-40.0 | s2chg | 44 | 41 | 3 | 1 | 2 | 71 |
| Syabrubesi opening | 35.6-40.0 | pelican0827 | 44 | 24 | 10 | 18 | 3 | 35 |
| Syabrubesi opening | 35.6-40.0 | pelican0901 | 44 | 44 | 0 | 0 | 0 | 43 |
| Hakubesi deposit + gorge | 40.0-46.0 | s2 | 60 | 25 | 20 | 32 | 2 | 47 |
| Hakubesi deposit + gorge | 40.0-46.0 | s2chg | 60 | 26 | 20 | 31 | 2 | 51 |
| Hakubesi deposit + gorge | 40.0-46.0 | pelican0827 | 60 | 44 | 4 | 14 | 1 | 23 |
| Hakubesi deposit + gorge | 40.0-46.0 | pelican0901 | 60 | 12 | 6 | 33 | 4 | 0 |
| to Betrawati | 46.0-70.0 | s2 | 236 | 153 | 33 | 76 | 7 | 303 |
| to Betrawati | 46.0-70.0 | s2chg | 236 | 156 | 31 | 75 | 5 | 311 |
| to Betrawati | 46.0-70.0 | pelican0827 | 236 | 0 | 0 | 2 | 0 | 0 |
| to Betrawati | 46.0-70.0 | pelican0901 | 236 | 0 | 0 | 2 | 0 | 0 |
| Betrawati to Galchhi | 70.0-108.0 | s2 | 380 | 340 | 24 | 35 | 8 | 459 |
| Betrawati to Galchhi | 70.0-108.0 | s2chg | 380 | 343 | 21 | 33 | 7 | 493 |
| Galchhi to Mugling | 108.0-150.0 | s2 | 243 | 61 | 25 | 163 | 22 | 43 |
| Galchhi to Mugling | 108.0-150.0 | s2chg | 243 | 62 | 24 | 162 | 22 | 49 |
| Mugling to Devghat | 150.0-200.0 | s2 | 494 | 322 | 26 | 162 | 10 | 55 |
| Mugling to Devghat | 150.0-200.0 | s2chg | 494 | 317 | 31 | 166 | 11 | 56 |

Robust running fit (Pelican 1 Sept where both banks, else the Sentinel-2 change layer; window +/-1 km, outliers = beyond max(2.5 MAD, 10 m), 3 passes): 1228 points, 80 outliers (7 %). Fit stage by reach, median of the station fits [median p10 - p90 of the windows]:
| reach | fit stage m | stations with a fit / total |
|---|---|---|
| Lhende gorge 8-22 | 136 [96-176] | 102 / 135 |
| border junction 22-23 | 95 [81-110] | 9 / 13 |
| Bhote Koshi gorge 23-36 | 73 [59-99] | 123 / 128 |
| Syabrubesi opening 36-40 | 71 [59-82] | 44 / 44 |
| Hakubesi deposit + gorge 40-46 | 68 [42-85] | 53 / 60 |
| to Betrawati 46-70 | 29 [20-41] | 213 / 240 |
| Betrawati to Galchhi 70-108 | 15 [9-21] | 370 / 380 |
| Galchhi to Mugling 108-150 | 7 [3-13] | 81 / 420 |
| Mugling to Devghat 150-200 | 11 [9-12] | 90 / 500 |

Stage above bed by reach, clean stations only (both banks ok, no flags), median [10-90 %] (n):
| reach | s2 | s2chg | pelican0827 | pelican0901 |
|---|---|---|---|---|
| Lhende gorge 8-22 | 143 [107-170] (35) | 137 [105-170] (35) | - | 183 [183-183] (1) |
| border junction 22-23 | - | - | - | - |
| Bhote Koshi gorge 23-36 | 63 [52-84] (58) | 62 [51-84] (60) | 89 [64-109] (15) | 72 [56-89] (29) |
| Syabrubesi opening 36-40 | 65 [54-75] (27) | 64 [53-74] (28) | 73 [58-87] (9) | 69 [65-86] (11) |
| Hakubesi deposit + gorge 40-46 | 70 [59-87] (11) | 70 [53-86] (14) | 85 [78-92] (2) | - |
| to Betrawati 46-70 | 34 [23-67] (125) | 32 [21-66] (134) | - | - |
| Betrawati to Galchhi 70-108 | 19 [10-30] (173) | 18 [9-29] (200) | - | - |
| Galchhi to Mugling 108-150 | 7 [5-11] (8) | 7 [5-10] (11) | - | - |
| Mugling to Devghat 150-200 | 10 [10-11] (3) | 10 [10-11] (3) | - | - |

### Border junction km 21.5-22.8 (Dave: bed 1,815; lee 1,875; impact cliff 1,920-1,930)
| km | layer | bed(raw/loc) | L: z, d, status, flags | R: z, d, status, flags |
|---|---|---|---|---|
Main path: L = left bank looking downstream (east / Nepal side at the junction), R = right (west / China side). Kyirong arm: km up the arm from the junction, L = left looking UP the arm (south-west wall, the one facing the Lhende mouth).
| mai 21.0 | s2 | 1893/1859 | truncated | 1925±15 m at 175 m (28.28527,85.38463) [side-valley] |
| mai 21.0 | s2chg | 1893/1859 | truncated | 1925±15 m at 175 m (28.28527,85.38463) [side-valley] |
| mai 21.0 | pelican0827 | 1893/1859 | truncated [uncapped-s2-truncated] | truncated [side-valley;capped-by-s2chg] |
| mai 21.0 | pelican0901 | 1893/1859 | truncated [uncapped-s2-truncated] | 1929±4 m at 175 m (28.28530,85.38460) [side-valley] |
| mai 21.1 | s2 | 1877/1859 | truncated | 1927±29 m at 145 m (28.28474,85.38402) [side-valley] |
| mai 21.1 | s2chg | 1877/1859 | truncated | 1927±29 m at 145 m (28.28474,85.38402) [side-valley] |
| mai 21.1 | pelican0827 | 1877/1859 | truncated [uncapped-s2-truncated] | truncated [side-valley;capped-by-s2chg] |
| mai 21.1 | pelican0901 | 1877/1859 | truncated [uncapped-s2-truncated] | 1936±5 m at 146 m (28.28478,85.38398) [side-valley] |
| mai 21.2 | s2 | 1861/1861 | truncated | 1933±20 m at 135 m (28.28411,85.38324) [side-valley] |
| mai 21.2 | s2chg | 1861/1861 | truncated | 1933±20 m at 135 m (28.28411,85.38324) [side-valley] |
| mai 21.2 | pelican0827 | 1861/1861 | truncated [uncapped-s2-truncated] | truncated [side-valley;capped-by-s2chg] |
| mai 21.2 | pelican0901 | 1861/1861 | truncated [uncapped-s2-truncated] | 1860±3 m at 77 m (28.28372,85.38356) [side-valley;capped-by-s2chg] |
| mai 21.3 | s2 | 1846/1846 | truncated [manual:cloud-shadow] | 1938±21 m at 125 m (28.28353,85.38248) |
| mai 21.3 | s2chg | 1846/1846 | truncated [manual:cloud-shadow] | 1938±21 m at 125 m (28.28353,85.38248) |
| mai 21.3 | pelican0827 | 1846/1846 | truncated [uncapped-s2-truncated;manual:cloud-shadow] | 1971±5 m at 145 m (28.28370,85.38234) [capped-by-s2chg] |
| mai 21.3 | pelican0901 | 1846/1846 | truncated [uncapped-s2-truncated;manual:cloud-shadow] | 1945±5 m at 125 m (28.28356,85.38245) |
| mai 21.4 | s2 | 1829/1829 | 1999±32 m at 135 m (28.28107,85.38323) [manual:cloud-shadow] | 1949±20 m at 135 m (28.28300,85.38172) |
| mai 21.4 | s2chg | 1829/1829 | 1999±32 m at 135 m (28.28107,85.38323) [manual:cloud-shadow] | 1949±20 m at 135 m (28.28300,85.38172) |
| mai 21.4 | pelican0827 | 1829/1829 | truncated [capped-by-s2chg;manual:cloud-shadow] | truncated [capped-by-s2chg] |
| mai 21.4 | pelican0901 | 1829/1829 | truncated [capped-by-s2chg;manual:cloud-shadow] | 1969±5 m at 148 m (28.28313,85.38163) [capped-by-s2chg] |
| mai 21.5 | s2 | 1825/1825 | 2005±35 m at 185 m (28.28063,85.38284) [junction;manual:cloud-shadow] | 1925±16 m at 115 m (28.28244,85.38072) [junction] |
| mai 21.5 | s2chg | 1825/1825 | 2005±35 m at 185 m (28.28063,85.38284) [junction;manual:cloud-shadow] | 1925±16 m at 115 m (28.28244,85.38072) [junction] |
| mai 21.5 | pelican0827 | 1825/1825 | truncated [junction;capped-by-s2chg;manual:cloud-shadow] | 1959±5 m at 133 m (28.28258,85.38055) [junction;capped-by-s2chg] |
| mai 21.5 | pelican0901 | 1825/1825 | 2036±17 m at 196 m (28.28053,85.38295) [junction;capped-by-s2chg;manual:cloud-shadow] | 1958±6 m at 131 m (28.28257,85.38057) [junction;capped-by-s2chg] |
| mai 21.6 | s2 | 1821/1821 | 1991±29 m at 155 m (28.28011,85.38224) [junction;manual:cloud-shadow] | 1923±30 m at 155 m (28.28183,85.37989) [junction] |
| mai 21.6 | s2chg | 1821/1821 | 1991±29 m at 155 m (28.28011,85.38224) [junction;manual:cloud-shadow] | 1923±30 m at 155 m (28.28183,85.37989) [junction] |
| mai 21.6 | pelican0827 | 1821/1821 | 1916±7 m at 170 m (28.28000,85.38240) [junction;capped-by-s2chg;manual:cloud-shadow] | 1961±11 m at 166 m (28.28192,85.37977) [junction;capped-by-s2chg] |
| mai 21.6 | pelican0901 | 1821/1821 | 1916±7 m at 170 m (28.28000,85.38240) [junction;capped-by-s2chg;manual:cloud-shadow] | 1953±10 m at 163 m (28.28190,85.37979) [junction] |
| mai 21.7 | s2 | 1820/1820 | 1899±17 m at 95 m (28.27961,85.38123) [junction;manual:cloud-shadow] | 1903±31 m at 165 m (28.28121,85.37944) [junction] |
| mai 21.7 | s2chg | 1820/1820 | 1899±17 m at 95 m (28.27961,85.38123) [junction;manual:cloud-shadow] | 1903±31 m at 165 m (28.28121,85.37944) [junction] |
| mai 21.7 | pelican0827 | 1820/1820 | 1920±5 m at 106 m (28.27951,85.38134) [junction;capped-by-s2chg;manual:cloud-shadow] | 1922±5 m at 176 m (28.28131,85.37933) [junction;capped-by-s2chg] |
| mai 21.7 | pelican0901 | 1820/1820 | 1918±5 m at 104 m (28.27952,85.38133) [junction;capped-by-s2chg;manual:cloud-shadow] | 1899±7 m at 158 m (28.28120,85.37946) [junction] |
| mai 21.8 | s2 | 1816/1816 | 1918±22 m at 85 m (28.27918,85.38019) [junction] | 1865±15 m at 155 m (28.28085,85.37880) [junction] |
| mai 21.8 | s2chg | 1816/1816 | 1918±22 m at 85 m (28.27918,85.38019) [junction] | 1829±13 m at 55 m (28.28013,85.37941) [junction] |
| mai 21.8 | pelican0827 | 1816/1816 | 1930±12 m at 100 m (28.27904,85.38031) [junction;capped-by-s2chg] | 1833±2 m at 67 m (28.28024,85.37931) [junction;capped-by-s2chg;prebare-at-trim] |
| mai 21.8 | pelican0901 | 1816/1816 | 1930±12 m at 100 m (28.27904,85.38031) [junction;capped-by-s2chg] | 1833±2 m at 67 m (28.28024,85.37931) [junction;capped-by-s2chg;prebare-at-trim] |
| mai 21.9 | s2 | 1814/1814 | 1932±25 m at 105 m (28.27857,85.37939) [junction] | open [junction] |
| mai 21.9 | s2chg | 1814/1814 | 1932±25 m at 105 m (28.27857,85.37939) [junction] | open [junction] |
| mai 21.9 | pelican0827 | 1814/1814 | 1959±11 m at 124 m (28.27840,85.37952) [junction;capped-by-s2chg] | truncated [junction;uncapped-s2-open] |
| mai 21.9 | pelican0901 | 1814/1814 | 1959±11 m at 124 m (28.27840,85.37952) [junction;capped-by-s2chg] | open [junction;uncapped-s2-open] |
| mai 22.0 | s2 | 1818/1814 | 1919±25 m at 105 m (28.27800,85.37873) [junction] | open [junction] |
| mai 22.0 | s2chg | 1818/1814 | 1919±25 m at 105 m (28.27800,85.37873) [junction] | open [junction] |
| mai 22.0 | pelican0827 | 1818/1814 | 1943±12 m at 121 m (28.27786,85.37886) [junction;capped-by-s2chg] | truncated [junction;uncapped-s2-open] |
| mai 22.0 | pelican0901 | 1818/1814 | 1943±12 m at 121 m (28.27786,85.37886) [junction;capped-by-s2chg] | open [junction;uncapped-s2-open] |
| mai 22.1 | s2 | 1801/1801 | 1935±20 m at 165 m (28.27727,85.37848) [junction;side-valley;no-change-in-run] | 1910±18 m at 165 m (28.27915,85.37601) [junction] |
| mai 22.1 | s2chg | 1801/1801 | 1935±20 m at 165 m (28.27727,85.37848) [junction;side-valley;no-change-in-run] | 1910±18 m at 165 m (28.27915,85.37601) [junction] |
| mai 22.1 | pelican0827 | 1801/1801 | 1822±8 m at 73 m (28.27779,85.37780) [junction;side-valley;capped-by-s2chg;prebare-at-trim;no-change-in-run] | truncated [junction;capped-by-s2chg] |
| mai 22.1 | pelican0901 | 1801/1801 | 1822±8 m at 73 m (28.27779,85.37780) [junction;side-valley;capped-by-s2chg;prebare-at-trim;no-change-in-run] | 1939±4 m at 182 m (28.27928,85.37584) [junction;capped-by-s2chg] |
| mai 22.2 | s2 | 1797/1797 | 1933±18 m at 175 m (28.27710,85.37843) [junction] | 1947±14 m at 105 m (28.27775,85.37578) [junction;side-valley] |
| mai 22.2 | s2chg | 1797/1797 | 1933±18 m at 175 m (28.27710,85.37843) [junction] | 1947±14 m at 105 m (28.27775,85.37578) [junction;side-valley] |
| mai 22.2 | pelican0827 | 1797/1797 | 1949±8 m at 194 m (28.27705,85.37866) [junction;capped-by-s2chg] | 1962±5 m at 116 m (28.27778,85.37562) [junction;side-valley;capped-by-s2chg] |
| mai 22.2 | pelican0901 | 1797/1797 | 1949±8 m at 194 m (28.27705,85.37866) [junction;capped-by-s2chg] | 1950±4 m at 104 m (28.27775,85.37574) [junction;side-valley] |
| mai 22.3 | s2 | 1794/1794 | 1943±12 m at 185 m (28.27692,85.37859) [junction] | 1882±11 m at 145 m (28.27646,85.37537) [junction;side-valley] |
| mai 22.3 | s2chg | 1794/1794 | 1814±4 m at 75 m (28.27677,85.37749) [junction] | 1882±11 m at 145 m (28.27646,85.37537) [junction;side-valley] |
| mai 22.3 | pelican0827 | 1794/1794 | 1822±4 m at 88 m (28.27679,85.37766) [junction;capped-by-s2chg;prebare-at-trim] | 1891±4 m at 155 m (28.27644,85.37523) [junction;side-valley;capped-by-s2chg] |
| mai 22.3 | pelican0901 | 1794/1794 | 1822±4 m at 88 m (28.27679,85.37766) [junction;capped-by-s2chg;prebare-at-trim] | 1890±4 m at 154 m (28.27644,85.37524) [junction;side-valley] |
| mai 22.4 | s2 | 1794/1794 | 1872±19 m at 125 m (28.27619,85.37834) [junction] | 1870±15 m at 175 m (28.27535,85.37555) [junction;side-valley] |
| mai 22.4 | s2chg | 1794/1794 | 1872±19 m at 125 m (28.27619,85.37834) [junction] | 1870±15 m at 175 m (28.27535,85.37555) [junction;side-valley] |
| mai 22.4 | pelican0827 | 1794/1794 | 1919±11 m at 145 m (28.27625,85.37858) [junction;capped-by-s2chg] | 1903±6 m at 202 m (28.27526,85.37525) [junction;side-valley;capped-by-s2chg] |
| mai 22.4 | pelican0901 | 1794/1794 | 1919±11 m at 145 m (28.27625,85.37858) [junction;capped-by-s2chg] | 1903±6 m at 202 m (28.27526,85.37525) [junction;side-valley;capped-by-s2chg] |
| mai 22.5 | s2 | 1787/1787 | 1871±10 m at 125 m (28.27522,85.37864) [junction] | 1862±21 m at 185 m (28.27459,85.37567) [junction;no-change-in-run] |
| mai 22.5 | s2chg | 1787/1787 | 1871±10 m at 125 m (28.27522,85.37864) [junction] | 1862±21 m at 185 m (28.27459,85.37567) [junction;no-change-in-run] |
| mai 22.5 | pelican0827 | 1787/1787 | 1881±3 m at 136 m (28.27526,85.37879) [junction;capped-by-s2chg] | 1886±5 m at 202 m (28.27454,85.37546) [junction;capped-by-s2chg] |
| mai 22.5 | pelican0901 | 1787/1787 | 1880±3 m at 134 m (28.27525,85.37877) [junction;capped-by-s2chg] | 1885±5 m at 200 m (28.27454,85.37547) [junction;capped-by-s2chg] |
| mai 22.6 | s2 | 1780/1780 | 1865±10 m at 135 m (28.27421,85.37897) [junction] | 1868±14 m at 175 m (28.27393,85.37593) [junction;side-valley] |
| mai 22.6 | s2chg | 1780/1780 | 1865±10 m at 135 m (28.27421,85.37897) [junction] | 1868±14 m at 175 m (28.27393,85.37593) [junction;side-valley] |
| mai 22.6 | pelican0827 | 1780/1780 | 1874±3 m at 145 m (28.27423,85.37911) [junction;capped-by-s2chg] | 1880±4 m at 187 m (28.27391,85.37577) [junction;side-valley;capped-by-s2chg] |
| mai 22.6 | pelican0901 | 1780/1780 | 1865±3 m at 131 m (28.27422,85.37897) [junction] | 1880±4 m at 187 m (28.27391,85.37577) [junction;side-valley;capped-by-s2chg] |
| mai 22.7 | s2 | 1777/1777 | 1837±14 m at 145 m (28.27318,85.37912) [junction] | 1842±6 m at 155 m (28.27322,85.37617) [junction;side-valley] |
| mai 22.7 | s2chg | 1777/1777 | 1837±14 m at 145 m (28.27318,85.37912) [junction] | 1842±6 m at 155 m (28.27322,85.37617) [junction;side-valley] |
| mai 22.7 | pelican0827 | 1777/1777 | truncated [junction;capped-by-s2chg] | 1794±8 m at 169 m (28.27322,85.37599) [junction;side-valley;capped-by-s2chg] |
| mai 22.7 | pelican0901 | 1777/1777 | 1846±4 m at 151 m (28.27317,85.37923) [junction] | 1794±8 m at 169 m (28.27322,85.37599) [junction;side-valley;capped-by-s2chg] |
| mai 22.8 | s2 | 1773/1773 | 1845±13 m at 185 m (28.27225,85.37940) [junction;side-valley] | 1814±18 m at 125 m (28.27234,85.37634) [junction] |
| mai 22.8 | s2chg | 1773/1773 | 1845±13 m at 185 m (28.27225,85.37940) [junction;side-valley] | 1814±18 m at 125 m (28.27234,85.37634) [junction] |
| mai 22.8 | pelican0827 | 1773/1773 | 1857±4 m at 196 m (28.27225,85.37955) [junction;side-valley;capped-by-s2chg] | 1839±5 m at 140 m (28.27235,85.37615) [junction] |
| mai 22.8 | pelican0901 | 1773/1773 | 1849±4 m at 185 m (28.27225,85.37945) [junction;side-valley] | 1845±5 m at 145 m (28.27235,85.37610) [junction;capped-by-s2chg] |
| mai 22.9 | s2 | 1769/1769 | 1841±8 m at 195 m (28.27133,85.37953) | 1824±13 m at 155 m (28.27147,85.37606) [side-valley] |
| mai 22.9 | s2chg | 1769/1769 | 1841±8 m at 195 m (28.27133,85.37953) | 1782±3 m at 85 m (28.27144,85.37678) [side-valley] |
| mai 22.9 | pelican0827 | 1769/1769 | 1845±3 m at 215 m (28.27132,85.37978) [capped-by-s2chg] | 1784±2 m at 95 m (28.27145,85.37663) [side-valley;capped-by-s2chg;prebare-at-trim] |
| mai 22.9 | pelican0901 | 1769/1769 | 1843±3 m at 205 m (28.27133,85.37967) | 1784±2 m at 95 m (28.27145,85.37663) [side-valley;capped-by-s2chg;prebare-at-trim] |
| mai 23.0 | s2 | 1766/1766 | 1847±23 m at 155 m (28.27021,85.37909) | 1821±31 m at 175 m (28.27086,85.37591) |
| mai 23.0 | s2chg | 1766/1766 | 1793±6 m at 85 m (28.27035,85.37839) | 1774±4 m at 85 m (28.27067,85.37680) |
| mai 23.0 | pelican0827 | 1766/1766 | 1799±2 m at 98 m (28.27032,85.37856) [capped-by-s2chg;prebare-at-trim] | 1774±2 m at 97 m (28.27071,85.37664) [capped-by-s2chg;prebare-at-trim] |
| mai 23.0 | pelican0901 | 1766/1766 | 1799±2 m at 98 m (28.27032,85.37856) [capped-by-s2chg;prebare-at-trim] | 1774±2 m at 97 m (28.27071,85.37664) [capped-by-s2chg;prebare-at-trim] |
| mai 23.1 | s2 | 1760/1760 | 1856±15 m at 125 m (28.26922,85.37832) | 1829±15 m at 175 m (28.27039,85.37568) |
| mai 23.1 | s2chg | 1760/1760 | 1856±15 m at 125 m (28.26922,85.37832) | 1778±3 m at 45 m (28.26986,85.37686) |
| mai 23.1 | pelican0827 | 1760/1760 | 1872±4 m at 139 m (28.26915,85.37849) [capped-by-s2chg] | 1777±2 m at 62 m (28.26995,85.37667) [capped-by-s2chg;prebare-at-trim] |
| mai 23.1 | pelican0901 | 1760/1760 | 1858±4 m at 124 m (28.26921,85.37835) | 1777±2 m at 62 m (28.26995,85.37667) [capped-by-s2chg;prebare-at-trim] |
| mai 23.2 | s2 | 1754/1754 | 1856±14 m at 185 m (28.26825,85.37815) [side-valley] | 1824±13 m at 85 m (28.26939,85.37583) |
| mai 23.2 | s2chg | 1754/1754 | 1821±3 m at 125 m (28.26851,85.37761) [side-valley] | 1824±13 m at 85 m (28.26939,85.37583) |
| mai 23.2 | pelican0827 | 1754/1754 | 1831±3 m at 143 m (28.26841,85.37781) [side-valley;capped-by-s2chg;prebare-at-trim] | 1834±3 m at 100 m (28.26947,85.37566) [capped-by-s2chg] |
| mai 23.2 | pelican0901 | 1754/1754 | 1831±3 m at 143 m (28.26841,85.37781) [side-valley;capped-by-s2chg;prebare-at-trim] | 1833±3 m at 97 m (28.26946,85.37569) |
| mai 23.3 | s2 | 1751/1751 | 1828±18 m at 145 m (28.26776,85.37755) [side-valley] | 1820±17 m at 95 m (28.26853,85.37537) |
| mai 23.3 | s2chg | 1751/1751 | 1828±18 m at 145 m (28.26776,85.37755) [side-valley] | 1820±17 m at 95 m (28.26853,85.37537) |
| mai 23.3 | pelican0827 | 1751/1751 | 1877±12 m at 157 m (28.26770,85.37770) [side-valley;capped-by-s2chg] | truncated [capped-by-s2chg] |
| mai 23.3 | pelican0901 | 1751/1751 | 1877±12 m at 157 m (28.26770,85.37770) [side-valley;capped-by-s2chg] | 1834±10 m at 104 m (28.26857,85.37524) |
| kyi 0.0 | s2 | 1799/1791 | 1945±17 m at 125 m (28.27805,85.37576) [side-valley] | 1912±20 m at 195 m (28.27806,85.37892) |
| kyi 0.0 | s2chg | 1799/1791 | 1945±17 m at 125 m (28.27805,85.37576) [side-valley] | 1912±20 m at 195 m (28.27806,85.37892) |
| kyi 0.0 | pelican0827 | 1799/1791 | 1963±5 m at 136 m (28.27805,85.37560) [side-valley;capped-by-s2chg] | 1936±4 m at 215 m (28.27806,85.37917) [capped-by-s2chg] |
| kyi 0.0 | pelican0901 | 1799/1791 | 1963±5 m at 136 m (28.27805,85.37560) [side-valley;capped-by-s2chg] | 1936±4 m at 215 m (28.27806,85.37917) [capped-by-s2chg] |
| kyi 0.1 | s2 | 1791/1791 | 1911±18 m at 135 m (28.27879,85.37583) | 1913±22 m at 335 m (28.27929,85.38048) |
| kyi 0.1 | s2chg | 1791/1791 | 1911±18 m at 135 m (28.27879,85.37583) | 1816±7 m at 55 m (28.27898,85.37765) |
| kyi 0.1 | pelican0827 | 1791/1791 | truncated [capped-by-s2chg] | 1822±2 m at 68 m (28.27900,85.37783) [capped-by-s2chg;prebare-at-trim] |
| kyi 0.1 | pelican0901 | 1791/1791 | 1941±5 m at 154 m (28.27876,85.37559) [capped-by-s2chg] | 1822±2 m at 68 m (28.27900,85.37783) [capped-by-s2chg;prebare-at-trim] |
| kyi 0.2 | s2 | 1806/1806 | 1901±20 m at 125 m (28.27954,85.37560) | open |
| kyi 0.2 | s2chg | 1806/1806 | 1901±20 m at 125 m (28.27954,85.37560) | open |
| kyi 0.2 | pelican0827 | 1806/1806 | 1918±9 m at 139 m (28.27951,85.37542) | open [uncapped-s2-open] |
| kyi 0.2 | pelican0901 | 1806/1806 | 1917±10 m at 137 m (28.27951,85.37543) | open [uncapped-s2-open] |
| kyi 0.3 | s2 | 1806/1806 | 1904±25 m at 145 m (28.28029,85.37524) | 1860±9 m at 145 m (28.28103,85.37797) |
| kyi 0.3 | s2chg | 1806/1806 | 1904±25 m at 145 m (28.28029,85.37524) | 1860±9 m at 145 m (28.28103,85.37797) |
| kyi 0.3 | pelican0827 | 1806/1806 | 1923±5 m at 154 m (28.28026,85.37511) | 1874±4 m at 164 m (28.28109,85.37820) [capped-by-s2chg] |
| kyi 0.3 | pelican0901 | 1806/1806 | 1917±5 m at 149 m (28.28027,85.37515) | 1871±5 m at 160 m (28.28108,85.37815) |
| kyi 0.4 | s2 | 1807/1807 | 1892±14 m at 155 m (28.28099,85.37487) | 1866±17 m at 115 m (28.28189,85.37732) |
| kyi 0.4 | s2chg | 1807/1807 | 1892±14 m at 155 m (28.28099,85.37487) | 1866±17 m at 115 m (28.28189,85.37732) |
| kyi 0.4 | pelican0827 | 1807/1807 | 1907±4 m at 173 m (28.28091,85.37466) [capped-by-s2chg] | 1880±4 m at 125 m (28.28194,85.37746) [capped-by-s2chg] |
| kyi 0.4 | pelican0901 | 1807/1807 | 1904±4 m at 167 m (28.28093,85.37472) | 1865±4 m at 110 m (28.28189,85.37731) |
| kyi 0.5 | s2 | 1807/1807 | 1882±15 m at 135 m (28.28166,85.37481) | 1867±24 m at 95 m (28.28282,85.37663) |
| kyi 0.5 | s2chg | 1807/1807 | 1882±15 m at 135 m (28.28166,85.37481) | 1867±24 m at 95 m (28.28282,85.37663) |
| kyi 0.5 | pelican0827 | 1807/1807 | 1905±4 m at 152 m (28.28155,85.37464) | 1887±4 m at 113 m (28.28293,85.37682) [capped-by-s2chg] |
| kyi 0.5 | pelican0901 | 1807/1807 | 1906±4 m at 154 m (28.28154,85.37462) [capped-by-s2chg] | 1875±4 m at 101 m (28.28287,85.37672) |
| kyi 0.6 | s2 | 1807/1807 | 1875±11 m at 115 m (28.28224,85.37440) | 1867±16 m at 105 m (28.28363,85.37585) |
| kyi 0.6 | s2chg | 1807/1807 | 1875±11 m at 115 m (28.28224,85.37440) | 1867±16 m at 105 m (28.28363,85.37585) |
| kyi 0.6 | pelican0827 | 1807/1807 | truncated [capped-by-s2chg] | truncated [capped-by-s2chg] |
| kyi 0.6 | pelican0901 | 1807/1807 | 1881±3 m at 119 m (28.28219,85.37434) | 1868±10 m at 103 m (28.28365,85.37587) |
| kyi 0.7 | s2 | 1810/1810 | 1872±10 m at 95 m (28.28282,85.37379) | 1861±12 m at 105 m (28.28422,85.37491) |
| kyi 0.7 | s2chg | 1810/1810 | 1872±10 m at 95 m (28.28282,85.37379) | 1861±12 m at 105 m (28.28422,85.37491) |
| kyi 0.7 | pelican0827 | 1810/1810 | truncated [capped-by-s2chg] | truncated [capped-by-s2chg] |
| kyi 0.7 | pelican0901 | 1810/1810 | 1877±3 m at 98 m (28.28276,85.37374) | 1869±3 m at 112 m (28.28430,85.37498) |
| kyi 0.8 | s2 | 1811/1811 | 1844±14 m at 95 m (28.28326,85.37303) | 1851±19 m at 95 m (28.28469,85.37390) |
| kyi 0.8 | s2chg | 1811/1811 | 1844±14 m at 95 m (28.28326,85.37303) | 1851±19 m at 95 m (28.28469,85.37390) |
| kyi 0.8 | pelican0827 | 1811/1811 | truncated [capped-by-s2chg] | 1881±12 m at 115 m (28.28488,85.37402) [capped-by-s2chg] |
| kyi 0.8 | pelican0901 | 1811/1811 | 1851±10 m at 100 m (28.28319,85.37299) | 1881±12 m at 115 m (28.28488,85.37402) [capped-by-s2chg] |
| kyi 0.9 | s2 | 1813/1813 | 1899±37 m at 105 m (28.28361,85.37210) [side-valley] | 1857±18 m at 95 m (28.28513,85.37301) |
| kyi 0.9 | s2chg | 1813/1813 | 1899±37 m at 105 m (28.28361,85.37210) [side-valley] | 1857±18 m at 95 m (28.28513,85.37301) |
| kyi 0.9 | pelican0827 | 1813/1813 | 1929±17 m at 115 m (28.28350,85.37204) [side-valley;capped-by-s2chg] | truncated [capped-by-s2chg] |
| kyi 0.9 | pelican0901 | 1813/1813 | 1870±16 m at 88 m (28.28372,85.37216) [side-valley] | 1872±12 m at 104 m (28.28524,85.37307) |
| kyi 1.0 | s2 | 1815/1815 | 1857±27 m at 55 m (28.28430,85.37141) | 1865±15 m at 125 m (28.28568,85.37216) [side-valley] |
| kyi 1.0 | s2chg | 1815/1815 | 1857±27 m at 55 m (28.28430,85.37141) | 1865±15 m at 125 m (28.28568,85.37216) [side-valley] |
| kyi 1.0 | pelican0827 | 1815/1815 | truncated [capped-by-s2chg] | truncated [side-valley;capped-by-s2chg] |
| kyi 1.0 | pelican0901 | 1815/1815 | 1859±14 m at 52 m (28.28429,85.37140) | 1873±10 m at 130 m (28.28575,85.37220) [side-valley] |

### Kyirong arm, km up the arm from the junction (L = south-west wall facing the Lhende)
| km | layer | bed raw | L: z at d [flags] | R: z at d [flags] |
|---|---|---|---|---|
| 0.0 | s2 | 1799 | 1945±17 at 125 [side-valley] | 1912±20 at 195 |
| 0.0 | s2chg | 1799 | 1945±17 at 125 [side-valley] | 1912±20 at 195 |
| 0.0 | pelican0827 | 1799 | 1963±5 at 136 [side-valley;capped-by-s2chg] | 1936±4 at 215 [capped-by-s2chg] |
| 0.0 | pelican0901 | 1799 | 1963±5 at 136 [side-valley;capped-by-s2chg] | 1936±4 at 215 [capped-by-s2chg] |
| 0.5 | s2 | 1807 | 1882±15 at 135 | 1867±24 at 95 |
| 0.5 | s2chg | 1807 | 1882±15 at 135 | 1867±24 at 95 |
| 0.5 | pelican0827 | 1807 | 1905±4 at 152 | 1887±4 at 113 [capped-by-s2chg] |
| 0.5 | pelican0901 | 1807 | 1906±4 at 154 [capped-by-s2chg] | 1875±4 at 101 |
| 1.0 | s2 | 1815 | 1857±27 at 55 | 1865±15 at 125 [side-valley] |
| 1.0 | s2chg | 1815 | 1857±27 at 55 | 1865±15 at 125 [side-valley] |
| 1.0 | pelican0827 | 1815 | truncated [capped-by-s2chg] | truncated [side-valley;capped-by-s2chg] |
| 1.0 | pelican0901 | 1815 | 1859±14 at 52 | 1873±10 at 130 [side-valley] |
| 1.5 | s2 | 1826 | 1860±15 at 55 | 1874±20 at 85 |
| 1.5 | s2chg | 1826 | 1860±15 at 55 | 1874±20 at 85 |
| 1.5 | pelican0827 | 1826 | 1872±11 at 70 [capped-by-s2chg] | 1897±12 at 100 [capped-by-s2chg] |
| 1.5 | pelican0901 | 1826 | 1860±9 at 50 | 1878±11 at 85 |
| 2.0 | s2 | 1841 | 1860±16 at 5 | 1863±18 at 85 [side-valley] |
| 2.0 | s2chg | 1841 | 1860±16 at 5 | 1863±18 at 85 [side-valley] |
| 2.0 | pelican0827 | 1841 | 1872±11 at 13 | 1867±11 at 85 [side-valley] |
| 2.0 | pelican0901 | 1841 | 1867±10 at 8 | 1870±11 at 88 [side-valley] |
| 2.5 | s2 | 1849 | 1874±12 at 35 [side-valley] | 1854±10 at 45 [side-valley;prebare-at-trim;no-change-in-run] |
| 2.5 | s2chg | 1849 | 1874±12 at 35 [side-valley] | 1854±10 at 45 [side-valley;prebare-at-trim;no-change-in-run] |
| 2.5 | pelican0827 | 1849 | 1877±4 at 35 [side-valley] | 1871±5 at 56 [side-valley] |
| 2.5 | pelican0901 | 1849 | 1876±4 at 34 [side-valley] | 1875±5 at 59 [side-valley] |
| 3.0 | s2 | 1856 | truncated | truncated |
| 3.0 | s2chg | 1856 | truncated | truncated |
| 3.0 | pelican0827 | 1856 | truncated [uncapped-s2-truncated] | truncated [uncapped-s2-truncated] |
| 3.0 | pelican0901 | 1856 | 1896±9 at 44 [uncapped-s2-truncated] | truncated [uncapped-s2-truncated] |
| 3.5 | s2 | 1871 | 1895±12 at 25 [side-valley;prebare-at-trim;no-change-in-run] | 1900±34 at 55 |
| 3.5 | s2chg | 1871 | 1895±12 at 25 [side-valley;prebare-at-trim;no-change-in-run] | 1900±34 at 55 |
| 3.5 | pelican0827 | 1871 | truncated [side-valley] | truncated [capped-by-s2chg] |
| 3.5 | pelican0901 | 1871 | 1897±3 at 23 [side-valley] | 1922±3 at 71 [capped-by-s2chg] |
| 4.0 | s2 | 1897 | 1975±16 at 135 | 1943±30 at 45 |
| 4.0 | s2chg | 1897 | 1975±16 at 135 | 1943±30 at 45 |
| 4.0 | pelican0827 | 1897 | truncated [capped-by-s2chg] | truncated [capped-by-s2chg] |
| 4.0 | pelican0901 | 1897 | 1911±5 at 25 [prebare-at-trim;no-change-in-run] | 1982±17 at 58 [capped-by-s2chg] |
| 4.5 | s2 | 1899 | 1906±18 at 15 [prebare-at-trim;no-change-in-run] | truncated |
| 4.5 | s2chg | 1899 | 1906±18 at 15 [prebare-at-trim;no-change-in-run] | truncated |
| 4.5 | pelican0827 | 1899 | truncated | truncated [uncapped-s2-truncated] |
| 4.5 | pelican0901 | 1899 | 1932±5 at 28 [capped-by-s2chg] | open [uncapped-s2-truncated] |
| 5.0 | s2 | 1922 | 1933±2 at 35 [side-valley;prebare-at-trim;no-change-in-run] | 1930±9 at 35 [prebare-at-trim;no-change-in-run] |
| 5.0 | s2chg | 1922 | 1933±2 at 35 [side-valley;prebare-at-trim;no-change-in-run] | 1930±9 at 35 [prebare-at-trim;no-change-in-run] |
| 5.0 | pelican0827 | 1922 | 1936±2 at 53 [side-valley;capped-by-s2chg] | 1929±3 at 29 [prebare-at-trim;no-change-in-run] |
| 5.0 | pelican0901 | 1922 | 1936±2 at 53 [side-valley] | 1943±5 at 47 [capped-by-s2chg] |
| 5.5 | s2 | 1935 | 1935±5 at 5 [prebare-at-trim;no-change-in-run] | 1935±5 at 5 [prebare-at-trim;no-change-in-run] |
| 5.5 | s2chg | 1935 | 1935±5 at 5 [prebare-at-trim;no-change-in-run] | 1935±5 at 5 [prebare-at-trim;no-change-in-run] |
| 5.5 | pelican0827 | 1935 | 1936±2 at 13 | 1940±3 at 10 |
| 5.5 | pelican0901 | 1935 | 1935±2 at 5 [prebare-at-trim;no-change-in-run] | 1944±2 at 20 |

### Hakubesi km 42.5-45.5 — stills: ~45-70 m above the pre-event bed
| layer | stations | L stage min/med/max (n) | R stage min/med/max (n) | clean-station stage med | v_super (km: v) |
|---|---|---|---|---|---|
| s2 | 30 | 62/80/109 (14) | 49/54/87 (5) | 80 (16) | - |
| s2chg | 30 | 55/77/109 (15) | 49/60/87 (6) | 77 (17) | 45.3: 77 |
| pelican0827 | 31 | 65/93/109 (5) | 96/106/116 (2) | 96 (7) | 42.6: 53, 42.8: 25, 43.1: 45, 43.2: 53, 43.6: 55, 43.8: 94, 44.0: 50, 44.5: 46 |
| pelican0901 | 21 | - | - | - | - |

### Syabrubesi opening km 35.6-40.0 — geopera: velocity collapse to ~11 m/s at the opening
| layer | stations | L stage min/med/max (n) | R stage min/med/max (n) | clean-station stage med | v_super (km: v) |
|---|---|---|---|---|---|
| s2 | 45 | 43/71/100 (35) | 27/62/130 (37) | 65 (44) | 36.4: 12, 36.5: 45, 36.7: 22, 37.4: 45, 38.6: 34, 39.9: 31 |
| s2chg | 45 | 21/70/100 (36) | 27/60/130 (37) | 64 (44) | 36.5: 45, 36.7: 22, 39.9: 31 |
| pelican0827 | 45 | 47/77/118 (21) | 22/73/113 (15) | 73 (27) | 36.7: 12, 37.1: 48, 37.2: 24, 37.4: 30, 37.6: 41, 38.1: 50, 38.6: 28, 38.8: 45 |
| pelican0901 | 45 | 58/74/90 (18) | 27/66/111 (25) | 69 (32) | 36.2: 15, 36.5: 38, 36.7: 21, 37.1: 43, 37.2: 26, 37.4: 28, 37.6: 42, 38.6: 30, 38.8: 45, 39.6: 75, 39.9: 31 |
geopera superelevation velocities in km 35-46 (our chainage): 36.3: 11 (3-31), 38.7: 47 (24-78) *, 44.5: 42 (17-74) *, 45.5: 23 (3-49) *, 45.7: 77 (39-128) *

### geopera v1.1 trimlines projected onto our chainage — ABSOLUTE elevations, same bank
(theirs: HMA 8 m + GLO fill, their thalweg; ours: this run's DEM. 'd' = metres from the centreline. Height above bed follows in brackets.)

km 19-26: geopera n=46, heights above their thalweg min/median/max 1/44/134 m
  ours s2: clean stations n=44 38/97/177 m; all ok banks n=136 0/86/224 m
  ours s2chg: clean stations n=46 17/93/177 m; all ok banks n=136 0/83/224 m
  ours pelican0827: clean stations n=7 55/70/98 m; all ok banks n=84 1/83/169 m
  ours pelican0901: clean stations n=21 53/91/187 m; all ok banks n=106 -1/88/211 m
  s2 minus geopera, same bank, unflagged stations: n=18, median +9 m, 10-90 % -27..+46 m
  s2chg minus geopera, same bank, unflagged stations: n=18, median +2 m, 10-90 % -27..+46 m
  pelican0827 minus geopera, same bank, unflagged stations: n=4, median +17 m, 10-90 % +2..+25 m
  pelican0901 minus geopera, same bank, unflagged stations: n=9, median +11 m, 10-90 % -16..+28 m

| our km | bank | geopera z at d (h above thalweg) | ours: s2 / s2chg / pelican0827 / pelican0901: z at d (stage) [flags] |
|---|---|---|---|
| 21.2 | L | 1861 at 32 (3) | truncated / truncated / truncated / truncated |
| 21.2 | R | 1897 at 32 (40) | 1933±20 at 135 (72) [side-valley] / 1933±20 at 135 (72) [side-valley] / truncated / 1860±3 at 77 (-1) [side-valley;capped-by-s2chg] |
| 21.4 | L | 1849 at 16 (1)* | 1999±32 at 135 (171) [manual:cloud-shadow] / 1999±32 at 135 (171) [manual:cloud-shadow] / truncated / truncated |
| 21.4 | R | 1933 at 88 (84) | 1949±20 at 135 (120) / 1949±20 at 135 (120) / truncated / 1969±5 at 148 (141) [capped-by-s2chg] |
| 21.5 | L | 1825 at 24 (7) | 2005±35 at 185 (180) [junction;manual:cloud-shadow] / 2005±35 at 185 (180) [junction;manual:cloud-shadow] / truncated / 2036±17 at 196 (211) [junction;capped-by-s2chg;manual:cloud-shadow] |
| 21.5 | R | 1898 at 128 (80) | 1925±16 at 115 (100) [junction] / 1925±16 at 115 (100) [junction] / 1959±5 at 133 (134) [junction;capped-by-s2chg] / 1958±6 at 131 (133) [junction;capped-by-s2chg] |
| 21.8 | L | 1834 at 64 (22) | 1918±22 at 85 (102) [junction] / 1918±22 at 85 (102) [junction] / 1930±12 at 100 (115) [junction;capped-by-s2chg] / 1930±12 at 100 (115) [junction;capped-by-s2chg] |
| 21.8 | R | 1835 at 88 (22) | 1865±15 at 155 (49) [junction] / 1829±13 at 55 (14) [junction] / 1833±2 at 67 (17) [junction;capped-by-s2chg;prebare-at-trim] / 1833±2 at 67 (17) [junction;capped-by-s2chg;prebare-at-trim] |
| 22.0 | L | 1895 at 120 (87)* | 1919±25 at 105 (105) [junction] / 1919±25 at 105 (105) [junction] / 1943±12 at 121 (129) [junction;capped-by-s2chg] / 1943±12 at 121 (129) [junction;capped-by-s2chg] |
| 22.0 | R | 1817 at 280 (8) | open / open / truncated / open |
| 22.2 | L | 1810 at 64 (15) | 1933±18 at 175 (136) [junction] / 1933±18 at 175 (136) [junction] / 1949±8 at 194 (152) [junction;capped-by-s2chg] / 1949±8 at 194 (152) [junction;capped-by-s2chg] |
| 22.2 | R | 1929 at 88 (134) | 1947±14 at 105 (149) [junction;side-valley] / 1947±14 at 105 (149) [junction;side-valley] / 1962±5 at 116 (165) [junction;side-valley;capped-by-s2chg] / 1950±4 at 104 (152) [junction;side-valley] |
| 22.4 | L | 1798 at 32 (9) | 1872±19 at 125 (78) [junction] / 1872±19 at 125 (78) [junction] / 1919±11 at 145 (125) [junction;capped-by-s2chg] / 1919±11 at 145 (125) [junction;capped-by-s2chg] |
| 22.4 | R | 1890 at 112 (101) | 1870±15 at 175 (77) [junction;side-valley] / 1870±15 at 175 (77) [junction;side-valley] / 1903±6 at 202 (110) [junction;side-valley;capped-by-s2chg] / 1903±6 at 202 (110) [junction;side-valley;capped-by-s2chg] |
| 22.6 | L | 1850 at 176 (71) | 1865±10 at 135 (85) [junction] / 1865±10 at 135 (85) [junction] / 1874±3 at 145 (94) [junction;capped-by-s2chg] / 1865±3 at 131 (85) [junction] |
| 22.8 | L | 1834 at 264 (61) | 1845±13 at 185 (72) [junction;side-valley] / 1845±13 at 185 (72) [junction;side-valley] / 1857±4 at 196 (83) [junction;side-valley;capped-by-s2chg] / 1849±4 at 185 (75) [junction;side-valley] |
| 22.8 | R | 1805 at 16 (32) | 1814±18 at 125 (40) [junction] / 1814±18 at 125 (40) [junction] / 1839±5 at 140 (66) [junction] / 1845±5 at 145 (72) [junction;capped-by-s2chg] |
| 22.9 | L | 1800 at 8 (25) | 1841±8 at 195 (72) / 1841±8 at 195 (72) / 1845±3 at 215 (77) [capped-by-s2chg] / 1843±3 at 205 (74) |
| 22.9 | R | 1849 at 56 (74) | 1824±13 at 155 (55) [side-valley] / 1782±3 at 85 (14) [side-valley] / 1784±2 at 95 (15) [side-valley;capped-by-s2chg;prebare-at-trim] / 1784±2 at 95 (15) [side-valley;capped-by-s2chg;prebare-at-trim] |
| 23.2 | L | 1795 at 24 (40) | 1856±14 at 185 (103) [side-valley] / 1821±3 at 125 (67) [side-valley] / 1831±3 at 143 (77) [side-valley;capped-by-s2chg;prebare-at-trim] / 1831±3 at 143 (77) [side-valley;capped-by-s2chg;prebare-at-trim] |
| 23.2 | R | 1830 at 40 (75) | 1824±13 at 85 (71) / 1824±13 at 85 (71) / 1834±3 at 100 (81) [capped-by-s2chg] / 1833±3 at 97 (79) |
| 23.3 | L | 1823 at 152 (76) | 1828±18 at 145 (77) [side-valley] / 1828±18 at 145 (77) [side-valley] / 1877±12 at 157 (126) [side-valley;capped-by-s2chg] / 1877±12 at 157 (126) [side-valley;capped-by-s2chg] |
| 23.3 | R | 1849 at 80 (102) | 1820±17 at 95 (69) / 1820±17 at 95 (69) / truncated / 1834±10 at 104 (82) |
| 23.5 | L | 1751 at 0 (13) | 1824±11 at 305 (82) [side-valley] / 1824±11 at 305 (82) [side-valley] / 1776±2 at 91 (34) [side-valley;capped-by-s2chg] / truncated |
| 23.5 | R | 1794 at 48 (56) | 1818±22 at 85 (76) [side-valley] / 1818±22 at 85 (76) [side-valley] / 1824±2 at 97 (82) [side-valley;capped-by-s2chg] / 1824±2 at 97 (82) [side-valley;capped-by-s2chg] |
| 23.7 | L | 1742 at 24 (11) | 1838±12 at 225 (103) [side-valley] / 1778±3 at 95 (43) [side-valley] / 1779±2 at 107 (44) [side-valley;capped-by-s2chg;prebare-at-trim] / 1779±2 at 107 (44) [side-valley;capped-by-s2chg;prebare-at-trim] |
| 23.7 | R | 1846 at 136 (114) | 1820±36 at 105 (85) / 1820±36 at 105 (85) / 1850±5 at 119 (115) [capped-by-s2chg] / 1829±6 at 104 (94) |
| 24.0 | L | 1766 at 136 (42) | 1805±17 at 185 (80) / 1765±9 at 85 (39) / 1772±2 at 98 (46) [capped-by-s2chg;prebare-at-trim] / 1772±2 at 98 (46) [capped-by-s2chg;prebare-at-trim] |
| 24.0 | R | 1816 at 104 (93)* | 1801±23 at 105 (75) / 1801±23 at 105 (75) / 1825±5 at 118 (99) [capped-by-s2chg] / 1830±4 at 122 (104) |
| 24.2 | L | 1731 at 24 (13) | 1830±24 at 125 (112) / 1830±24 at 125 (112) / 1853±13 at 140 (134) [capped-by-s2chg] / 1853±13 at 140 (134) [capped-by-s2chg] |
| 24.2 | R | 1815 at 72 (97) | 1797±23 at 115 (78) / 1797±23 at 115 (78) / 1782±9 at 128 (63) [capped-by-s2chg] / 1782±9 at 128 (63) [capped-by-s2chg] |
| 24.4 | L | 1735 at 0 (28)* | 1794±21 at 145 (85) / 1794±21 at 145 (85) / 1763±9 at 64 (53) [capped-by-s2chg;prebare-at-trim;no-change-in-run] / 1763±9 at 64 (53) [capped-by-s2chg;prebare-at-trim;no-change-in-run] |
| 24.4 | R | 1788 at 16 (82)* | 1736±7 at 35 (26) / 1736±7 at 35 (26) / 1800±4 at 52 (91) [capped-by-s2chg] / 1800±4 at 52 (91) |
| 24.6 | L | 1720 at 40 (13) | 1796±20 at 115 (87) [side-valley] / 1796±20 at 115 (87) [side-valley] / 1803±5 at 116 (94) [side-valley] / 1801±5 at 115 (92) [side-valley] |
| 24.6 | R | 1719 at 16 (12)* | 1709±10 at 115 (0) [side-valley] / 1709±10 at 115 (0) [side-valley] / 1710±7 at 112 (1) [side-valley] / 1714±8 at 122 (5) [side-valley] |
| 24.8 | L | 1731 at 136 (30) | 1753±13 at 115 (49) / 1753±13 at 115 (49) / 1758±4 at 119 (55) / 1756±4 at 116 (53) |
| 24.9 | L | 1739 at 120 (45) | 1737±8 at 175 (38) / 1737±8 at 175 (38) / 1726±2 at 145 (27) [capped-by-s2chg] / 1726±2 at 145 (27) [capped-by-s2chg] |
| 25.2 | L | 1734 at 112 (44) | 1749±12 at 165 (56) / 1749±12 at 165 (56) / 1748±4 at 160 (55) / 1751±4 at 163 (58) |
| 25.4 | L | 1734 at 128 (49) | 1745±5 at 205 (58) / 1739±3 at 145 (52) / 1740±2 at 157 (54) [capped-by-s2chg;prebare-at-trim] / 1740±2 at 157 (54) [capped-by-s2chg;prebare-at-trim] |
| 25.4 | R | 1767 at 120 (82) | 1750±12 at 115 (64) / 1750±12 at 115 (64) / 1763±4 at 130 (77) / 1762±4 at 128 (76) |
| 25.6 | L | 1707 at 104 (29) | 1747±8 at 205 (68) / 1723±4 at 95 (45) / 1727±2 at 115 (48) [capped-by-s2chg;prebare-at-trim] / 1727±2 at 115 (48) [capped-by-s2chg;prebare-at-trim] |
| 25.6 | R | 1752 at 64 (74) | 1748±18 at 125 (69) [side-valley] / 1748±18 at 125 (69) [side-valley] / 1763±4 at 137 (85) [side-valley;capped-by-s2chg] / 1763±4 at 137 (85) [side-valley;capped-by-s2chg] |
| 25.7 | L | 1681 at 56 (9) | 1751±12 at 225 (76) [side-valley] / 1708±6 at 115 (33) [side-valley] / 1713±2 at 128 (38) [side-valley;capped-by-s2chg;prebare-at-trim] / 1713±2 at 128 (38) [side-valley;capped-by-s2chg;prebare-at-trim] |
| 25.7 | R | 1745 at 120 (74)* | 1745±22 at 125 (70) [side-valley] / 1745±22 at 125 (70) [side-valley] / 1764±11 at 142 (89) [side-valley;capped-by-s2chg] / 1764±11 at 142 (89) [side-valley;capped-by-s2chg] |
| 25.8 | L | 1724 at 48 (58) | 1746±14 at 225 (75) [side-valley] / 1680±3 at 75 (9) [side-valley] / 1684±2 at 91 (14) [side-valley;capped-by-s2chg;prebare-at-trim] / 1684±2 at 91 (14) [side-valley;capped-by-s2chg;prebare-at-trim] |
| 25.8 | R | 1747 at 24 (81) | 1755±15 at 75 (84) / 1755±15 at 75 (84) / 1768±5 at 86 (98) / 1772±5 at 89 (101) [capped-by-s2chg] |

km 35-46: geopera n=65, heights above their thalweg min/median/max 4/71/168 m
  ours s2: clean stations n=86 7/67/109 m; all ok banks n=169 4/66/130 m
  ours s2chg: clean stations n=87 7/65/109 m; all ok banks n=171 4/64/130 m
  ours pelican0827: clean stations n=49 31/78/118 m; all ok banks n=158 13/81/553 m
  ours pelican0901: clean stations n=37 27/70/103 m; all ok banks n=130 12/76/240 m
  s2 minus geopera, same bank, unflagged stations: n=43, median -5 m, 10-90 % -26..+28 m
  s2chg minus geopera, same bank, unflagged stations: n=43, median -5 m, 10-90 % -26..+25 m
  pelican0827 minus geopera, same bank, unflagged stations: n=22, median +2 m, 10-90 % -15..+35 m
  pelican0901 minus geopera, same bank, unflagged stations: n=20, median -6 m, 10-90 % -31..+39 m

| our km | bank | geopera z at d (h above thalweg) | ours: s2 / s2chg / pelican0827 / pelican0901: z at d (stage) [flags] |
|---|---|---|---|
| 35.2 | L | 1602 at 256 (168) | 1499±13 at 65 (69) / 1499±13 at 65 (69) / 1515±3 at 82 (84) [capped-by-s2chg] / 1509±3 at 74 (78) |
| 35.4 | L | 1478 at 88 (43) | 1498±16 at 75 (68) / 1498±16 at 75 (68) / 1513±4 at 86 (82) / 1516±5 at 89 (85) |
| 36.1 | R | 1511 at 200 (92) | 1483±5 at 125 (62) / 1483±5 at 125 (62) / no-bare / 1485±2 at 131 (65) |
| 36.3 | L | 1444 at 64 (28) | 1484±9 at 115 (68) [sharp-bend] / 1484±9 at 115 (68) [sharp-bend] / truncated / 1491±3 at 124 (74) [sharp-bend] |
| 36.3 | R | 1439 at 24 (24) | 1481±2 at 195 (65) [sharp-bend;side-valley;prebare-at-trim] / 1479±6 at 155 (63) [sharp-bend;side-valley] / truncated / 1478±2 at 134 (61) [sharp-bend;side-valley] |
| 36.5 | R | 1468 at 112 (56) | 1447±7 at 85 (34) / 1447±7 at 85 (34) / truncated / 1463±4 at 101 (50) |
| 36.7 | L | 1481 at 136 (74) | 1462±6 at 95 (54) / 1462±6 at 95 (54) / 1476±3 at 115 (68) [capped-by-s2chg] / 1466±3 at 100 (58) |
| 36.9 | L | 1454 at 88 (53) | 1476±10 at 145 (73) / 1476±10 at 145 (73) / 1480±3 at 148 (78) / 1477±3 at 143 (75) |
| 36.9 | R | 1449 at 88 (47) | 1477±5 at 135 (75) / 1477±5 at 135 (75) / 1469±3 at 112 (67) [capped-by-s2chg] / 1469±3 at 112 (67) [capped-by-s2chg] |
| 37.1 | R | 1430 at 24 (32) | 1469±4 at 235 (70) / 1444±8 at 105 (45) / 1453±2 at 122 (54) [capped-by-s2chg;prebare-at-trim] / 1453±2 at 122 (54) [capped-by-s2chg;prebare-at-trim] |
| 37.3 | L | 1464 at 72 (70) | truncated / truncated / 1467±4 at 59 (75) [uncapped-s2-truncated] / 1460±4 at 50 (67) [uncapped-s2-truncated] |
| 37.3 | R | 1465 at 176 (71) | 1467±4 at 195 (74) / 1467±4 at 195 (74) / 1471±3 at 206 (78) [capped-by-s2chg] / 1468±2 at 199 (76) |
| 37.5 | L | 1457 at 112 (67) | 1479±28 at 125 (88) / 1479±28 at 125 (88) / 1482±6 at 122 (90) / 1482±6 at 122 (90) |
| 37.7 | L | 1454 at 120 (70) | 1455±11 at 85 (71) / 1455±11 at 85 (71) / 1458±3 at 85 (73) / 1464±4 at 92 (79) |
| 37.9 | L | 1487 at 128 (109)* | 1478±26 at 105 (100) / 1478±26 at 105 (100) / 1496±14 at 113 (118) / 1498±14 at 115 (121) [capped-by-s2chg] |
| 38.0 | L | 1453 at 104 (80) | 1455±11 at 95 (79) / 1455±11 at 95 (79) / 1463±3 at 101 (86) / 1467±4 at 107 (91) [capped-by-s2chg] |
| 38.2 | L | 1413 at 80 (44) | 1414±10 at 55 (43) / 1414±10 at 55 (43) / 1419±3 at 58 (47) / 1425±3 at 73 (53) [capped-by-s2chg] |
| 38.2 | R | 1397 at 40 (27) | 1426±23 at 85 (55) / 1426±23 at 85 (55) / 1445±4 at 97 (73) / 1442±4 at 94 (71) |
| 38.5 | L | 1429 at 104 (62) | 1424±9 at 85 (57) / 1424±9 at 85 (57) / 1434±3 at 97 (67) [capped-by-s2chg] / 1434±3 at 97 (67) [capped-by-s2chg] |
| 38.5 | R | 1439 at 80 (71) | 1419±14 at 75 (52) / 1419±14 at 75 (52) / 1430±4 at 83 (63) / 1426±4 at 79 (59) |
| 38.7 | L | 1448 at 120 (85) | 1421±12 at 75 (61) / 1421±12 at 75 (61) / 1431±3 at 85 (71) / 1434±3 at 89 (73) |
| 38.7 | R | 1404 at 64 (41)* | 1430±12 at 105 (70) / 1430±12 at 105 (70) / 1436±4 at 103 (75) / 1448±4 at 113 (88) |
| 38.9 | L | 1440 at 152 (83) | 1428±7 at 105 (76) / 1428±7 at 105 (76) / 1432±3 at 110 (80) / 1437±3 at 122 (85) |
| 38.9 | R | 1461 at 80 (104)* | 1366±12 at 45 (14) [no-change-in-run] / 1366±12 at 45 (14) [no-change-in-run] / truncated / 1387±12 at 58 (35) |
| 39.0 | L | 1443 at 120 (95) | 1432±16 at 105 (83) / 1432±16 at 105 (83) / 1442±3 at 115 (93) / 1442±3 at 115 (93) [capped-by-s2chg] |
| 39.2 | L | 1424 at 88 (80) | 1411±21 at 35 (66) / 1411±21 at 35 (66) / 1421±4 at 50 (76) / 1413±4 at 35 (68) |
| 39.2 | R | 1425 at 88 (80)* | 1406±15 at 95 (61) / 1406±15 at 95 (61) / truncated / 1416±10 at 103 (71) |
| 39.4 | L | 1418 at 128 (76) | 1401±10 at 75 (56) / 1401±10 at 75 (56) / 1409±3 at 85 (65) / 1411±3 at 88 (66) |
| 39.4 | R | 1421 at 88 (79) | 1406±10 at 115 (62) / 1406±10 at 115 (62) / truncated / 1412±2 at 127 (67) |
| 39.6 | L | 1401 at 112 (65) | 1412±6 at 145 (74) / 1412±6 at 145 (74) / 1421±3 at 158 (83) [capped-by-s2chg] / 1415±3 at 148 (77) |
| 39.8 | L | 1359 at 0 (26) | 1407±7 at 85 (73) / 1407±7 at 85 (73) / 1411±2 at 95 (77) / 1411±2 at 95 (77) [capped-by-s2chg] |
| 39.8 | R | 1370 at 24 (37) | 1408±18 at 115 (74) / 1408±18 at 115 (74) / 1431±7 at 131 (97) [capped-by-s2chg] / 1431±7 at 131 (97) [capped-by-s2chg] |
| 40.0 | L | 1407 at 160 (78)* | 1422±37 at 155 (92) / 1422±37 at 155 (92) / 1460±7 at 167 (130) [capped-by-s2chg] / 1460±7 at 167 (130) [capped-by-s2chg] |
| 40.2 | L | 1430 at 104 (104)* | 1431±12 at 145 (103) [sharp-bend] / 1431±12 at 145 (103) [sharp-bend] / 1430±9 at 160 (103) [sharp-bend;capped-by-s2chg] / 1430±9 at 160 (103) [sharp-bend;capped-by-s2chg] |
| 40.4 | R | 1430 at 96 (74)* | 1399±15 at 125 (75) / 1399±15 at 125 (75) / 1414±4 at 139 (90) / 1417±4 at 142 (92) [capped-by-s2chg] |
| 40.9 | R | 1385 at 64 (50) | 1378±16 at 115 (57) / 1378±16 at 115 (57) / 1397±10 at 130 (76) [capped-by-s2chg] / 1397±10 at 130 (76) [capped-by-s2chg] |
| 41.0 | L | 1414 at 200 (96) | 1416±10 at 135 (100) [sharp-bend] / 1416±10 at 135 (100) [sharp-bend] / 1423±3 at 146 (107) [sharp-bend] / 1425±3 at 149 (109) [sharp-bend;capped-by-s2chg] |
| 41.2 | L | 1426 at 136 (109)* | 1423±12 at 175 (107) / 1423±12 at 175 (107) / 1414±3 at 139 (98) [capped-by-s2chg] / 1414±3 at 139 (98) [capped-by-s2chg] |
| 41.2 | R | 1370 at 80 (53) | truncated / truncated / 1444±10 at 130 (128) [side-valley;uncapped-s2-truncated] / truncated |
| 41.4 | L | 1414 at 72 (82)* | 1394±20 at 35 (77) [side-valley] / 1394±20 at 35 (77) [side-valley] / 1399±5 at 38 (82) [side-valley] / 1394±12 at 53 (77) [side-valley;capped-by-s2chg] |
| 41.4 | L | 1408 at 168 (93)* | 1394±20 at 35 (77) [side-valley] / 1394±20 at 35 (77) [side-valley] / 1399±5 at 38 (82) [side-valley] / 1394±12 at 53 (77) [side-valley;capped-by-s2chg] |
| 41.4 | R | 1346 at 72 (14)* | truncated / truncated / 1445±7 at 106 (128) [uncapped-s2-truncated] / 1410±7 at 95 (93) [uncapped-s2-truncated] |
| 41.4 | R | 1341 at 48 (26) | truncated / truncated / 1445±7 at 106 (128) [uncapped-s2-truncated] / 1410±7 at 95 (93) [uncapped-s2-truncated] |
| 41.7 | L | 1378 at 72 (42)* | 1379±10 at 105 (64) / 1379±10 at 105 (64) / 1382±7 at 107 (67) / 1387±6 at 121 (72) [capped-by-s2chg] |
| 41.7 | R | 1399 at 80 (63)* | truncated / truncated / 1383±5 at 58 (68) [uncapped-s2-truncated] / truncated |
| 42.0 | L | 1389 at 120 (74)* | 1380±21 at 85 (67) / 1380±21 at 85 (67) / 1372±5 at 74 (58) / truncated |
| 42.1 | R | 1357 at 80 (45) | 1320±16 at 15 (7) / 1320±16 at 15 (7) / 1343±5 at 31 (31) / truncated |
| 42.4 | L | 1316 at 80 (4) | 1364±23 at 125 (54) [side-valley] / 1364±23 at 125 (54) [side-valley] / 1366±12 at 122 (56) [side-valley;uncapped-s2-truncated] / truncated |
| 42.7 | L | 1330 at 8 (57)* | truncated / truncated / 1349±6 at 74 (73) [uncapped-s2-truncated] / - |
| 42.7 | R | 1358 at 88 (85) | truncated / truncated / 1365±3 at 145 (89) [side-valley;uncapped-s2-truncated] / - |
| 42.9 | R | 1357 at 136 (100)* | truncated / truncated / truncated / - |
| 43.9 | L | 1344 at 160 (92) | truncated / truncated / 1325±4 at 86 (97) [uncapped-s2-truncated] / - |
| 44.3 | L | 1321 at 96 (107)* | 1321±2 at 95 (109) / 1321±2 at 95 (109) / 1321±2 at 92 (109) / truncated |
| 44.5 | L | 1318 at 96 (99)* | 1307±17 at 75 (95) / 1307±17 at 75 (95) / 1341±10 at 85 (129) [capped-by-s2chg] / truncated |
| 44.5 | R | 1286 at 40 (67) | truncated / truncated / 1301±4 at 83 (89) [uncapped-s2-truncated] / truncated |
| 44.7 | L | 1294 at 96 (87) | 1281±11 at 85 (62) / 1281±11 at 85 (62) / 1284±3 at 86 (65) / truncated |
| 44.7 | R | 1261 at 56 (54) | 1268±12 at 65 (49) / 1268±12 at 65 (49) / no-bare / truncated |
| 44.9 | L | 1247 at 32 (15)* | truncated / truncated / truncated / truncated |
| 45.1 | L | 1260 at 96 (60) | 1275±8 at 155 (75) / 1275±8 at 155 (75) / truncated / truncated |
| 45.3 | L | 1303 at 112 (109)* | 1284±21 at 95 (90) / 1284±21 at 95 (90) / truncated / truncated |
| 45.5 | L | 1288 at 96 (80)* | truncated / truncated / truncated / truncated |
| 45.5 | R | 1270 at 88 (62)* | 1247±14 at 55 (54) / 1247±14 at 55 (54) / truncated / truncated |
| 45.7 | L | 1271 at 112 (75) | truncated / truncated / truncated / truncated |
| 45.7 | R | 1228 at 40 (32)* | truncated / truncated / truncated / truncated |
| 45.9 | L | 1268 at 160 (74)* | 1269±18 at 165 (79) / 1269±18 at 165 (79) / truncated / truncated |
