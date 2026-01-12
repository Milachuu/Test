import mysql.connector


def populateBin():
    # Connect to MySQL
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="Helloworld1$",  # your password
        database="Neighbourly_Database"
    )

    cursor = db.cursor()


    bins = {
        '1': {'region': 'North', 'type': 'E-recycling Bin', 'name': 'Marsiling Industrial Estate Road 8', 'address': '30 Marsiling Industrial Estate Road 8, Singapore 739193', 'latitude': 1.4413303205691028, 'longitude': 103.7836765411749},
        '2': {'region': 'North', 'type': 'Recycling Bin', 'name': 'Giant Supermarket - Woodlands Mart','address': '768 Woodlands Avenue 6, #01-34 Woodlands Mart, Singapore 730768', 'latitude': 1.446691255052452, 'longitude': 103.79820185016169},
        '3': {'region': 'North', 'type': 'Recycling Bin', 'name': '876 Woodlands Street 83','address': '876 Woodlands Avenue 9, #01-256, Singapore 730876', 'latitude': 1.4461478789582505, 'longitude': 103.79066959619146},
        '4': {'region': 'North', 'type': 'E-recycling Bin', 'name': '336A Sembawang Crescent', 'address': '336A Sembawang Crescent, Singapore 751336', 'latitude': 1.4469694516136498, 'longitude': 103.81518159619151},
        '5': {'region': 'North', 'type': 'Recycling Bin', 'name': 'Giant Supermarket - Woodlands North Plaza', 'address': 'Blk 883 Woodlands Street 82, #01-498, Singapore 730883', 'latitude': 1.4439142733389227, 'longitude': 103.79087959619139},
        '6': {'region': 'North', 'type': 'E-recycling Bin', 'name': '20 Woodlands Link', 'address': '20 Woodlands Link, Singapore 738733', 'latitude': 1.4511941067185379, 'longitude': 103.81129693481856},
        '7': {'region': 'North', 'type': 'Recycling Bin', 'name': 'Block 406A HDB Sembawang (MSCP)', 'address': '406A Sembawang Drive, Singapore 751406', 'latitude': 1.4533626121231904, 'longitude': 103.81738210413205},
        '8': {'region': 'North', 'type': 'E-recycling Bin', 'name': 'Northpoint City Centre', 'address': 'Blk 930 Yishun Avenue 2, Northpoint City Centre, Singapore 769098', 'latitude': 1.430834722250474, 'longitude': 103.83589725756403},
        '9': {'region': 'North', 'type': 'E-recycling Bin', 'name': 'Tzu Chi Humanistic Youth Centre', 'address': '30A Yishun Central 1, Singapore 768796', 'latitude': 1.427858977652298, 'longitude': 103.8384464348179},
        '10': {'region': 'North', 'type': 'Recycling Bin', 'name': 'Challenger (Sun Plaza)', 'address': '30 Sembawang Drive, #02-06 Sun Plaza, Singapore 757713', 'latitude': 1.4495856719850477, 'longitude': 103.81914431947524},
        '11': {'region': 'North', 'type': 'Recycling Bin', 'name': 'Woodgrove Community Centre', 'address': '353 Woodlands Avenue 1, #01-753, Singapore 730353', 'latitude': 1.4326850159962372, 'longitude': 103.78517993565708},
        '12': {'region': 'North', 'type': 'Recycling Bin', 'name': 'Fuchun Community Club', 'address': '1 Woodlands Street 31, Singapore 738581', 'latitude': 1.4306535263024636, 'longitude': 103.77497727344486},
        '13': {'region': 'North', 'type': 'Recycling Bin', 'name': 'Sheng Siong Supermarket - Marsiling Admiralty Park', 'address': '202 Marsiling Drive, #01-138, Singapore 730202', 'latitude': 1.444132961099367, 'longitude': 103.77428201947507},
        '14': {'region': 'North', 'type': 'Recycling Bin', 'name': 'Popular Bookstore - Northpoint City', 'address': '930 Yishun Avenue 2, #03-12, Singapore 769098', 'latitude': 1.4306631143950619, 'longitude': 103.83538227344485},
        '15': {'region': 'North', 'type': 'Recycling Bin', 'name': 'Nee Soon East Community Club','address': '1 Yishun Ave 9, Singapore 768893', 'latitude': 1.431466408201187, 'longitude': 103.83860710413144},
        '16': {'region': 'North', 'type': 'Recycling Bin', 'name': 'Block 602 Yishun Street 61','address': 'Blk 602 Yishun Street 61, Singapore 760602', 'latitude': 1.4231991650397748, 'longitude': 103.8361872734447},

        '17': {'region': 'Northeast', 'type': 'E-recycling Bin', 'name': 'JTC Aviation Two','address': '690 West Camp Road, Singapore 797523', 'latitude': 1.4203643935701462, 'longitude': 103.86392273123725},
        '18': {'region': 'Northeast', 'type': 'E-recycling Bin', 'name': 'Sengkang General Hospital','address': '110 Sengkang East Way, Singapore 544886', 'latitude': 1.3959387944064647, 'longitude': 103.89310684138194},
        '19': {'region': 'Northeast', 'type': 'Recycling Bin', 'name': 'Punggol West Community Centre','address': 'Blk 259C Punggol Fld, Singapore 823259', 'latitude': 1.405554518508735, 'longitude': 103.89558684138072},
        '20': {'region': 'Northeast', 'type': 'Recycling Bin', 'name': '1 Sengkang Square','address': '1 Sengkang Square, #B1-52/53, Compass One, Singapore 545078', 'latitude': 1.3951892907414105, 'longitude': 103.89391636521079},
        '21': {'region': 'Northeast', 'type': 'Recycling Bin', 'name': 'Yio Chu Kang Community Club','address': 'Blk 633 Ang Mo Kio Avenue 6, #01-5135 8, Singapore 560633', 'latitude': 1.382004818803334, 'longitude': 103.8426249948123},
        '22': {'region': 'Northeast', 'type': 'E-recycling Bin', 'name': 'Ang Mo Kio Hub Singtel Store','address': '53 Ang Mo Kio Avenue 3, #B1-54/55/56/57 AMK Hub, Singapore 569933', 'latitude': 1.370046586254528, 'longitude': 103.84812167207104},
        '23': {'region': 'Northeast', 'type': 'Recycling Bin', 'name': 'Canopy Coffee Club','address': 'Blk 260 Ang Mo Kio Street 21, Singapore 560260', 'latitude': 1.3703625170424802, 'longitude': 103.83530631755681},
        '24': {'region': 'Northeast', 'type': 'E-recycling Bin', 'name': 'Highland Centre Condominium','address': '22 Yio Chu Kang Road, Singapore 545535', 'latitude': 1.3574998356808199, 'longitude': 103.87616436521569},
        '25': {'region': 'Northeast', 'type': 'Recycling Bin', 'name': 'Shell - Serangoon Garden','address': '49 Serangoon Garden Way, Singapore 555944', 'latitude': 1.3658880529418251, 'longitude': 103.86684068795748},
        '26': {'region': 'Northeast', 'type': 'Recycling Bin', 'name': 'Giant Supermarket - Buangkok Crescent','address': 'Blk 982 Buangkok Cres, #01-01, Singapore 530982', 'latitude': 1.3835626442925864, 'longitude': 103.87967299481234},
        '27': {'region': 'Northeast', 'type': 'E-recycling Bin', 'name': 'Block 326D Anchorvale Road','address': 'Blk 326D Anchorvale Rd, Singapore 544326', 'latitude': 1.3986670653228666, 'longitude': 103.88756585726745},
        '28': {'region': 'Northeast', 'type': 'Recycling Bin', 'name': 'Sheng Siong Supermarket - Waterway Sundew','address': 'Blk 660A , #01-01 Waterway Sundew, Singapore 821660', 'latitude': 1.4038888342629727, 'longitude': 103.91731614823813},
        '29': {'region': 'Northeast', 'type': 'Recycling Bin', 'name': 'Sengkang General Hospital','address': '110 Sengkang E Wy, Singapore 544886', 'latitude': 1.3955955735258272, 'longitude': 103.89250602658188},
        '30': {'region': 'Northeast', 'type': 'E-recycling Bin', 'name': 'Block 274C Compassvale Bow','address': 'Blk 274C Compassvale Bow, Singapore 543274', 'latitude': 1.383209335442932, 'longitude': 103.89099701069783},

        '31': {'region': 'East', 'type': 'Recycling Bin', 'name': 'Block 148 Pasir Ris','address': 'Blk 148 Pasir Ris Street 13, Singapore 510148', 'latitude': 1.3628753793461421, 'longitude': 103.9621537655026},
        '32': {'region': 'East', 'type': 'Recycling Bin', 'name': 'Tampines Ville RN','address': 'Blk 848 Tampines St 82, Singapore 520848', 'latitude': 1.3543135616701922, 'longitude': 103.93578107743699},
        '33': {'region': 'East', 'type': 'Recycling Bin', 'name': 'FairPrice Chai Chee Avenue','address': 'Blk 29B Chai Chee Ave, #01-62 Ansar Garden, Singapore 462029', 'latitude': 1.3262667239432768, 'longitude': 103.92336568538967},
        '34': {'region': 'East', 'type': 'E-recycling Bin', 'name': 'Block 738 Pasir Ris Drive 10','address': 'Blk 738 Pasir Ris Drive 10, Singapore 510738', 'latitude': 1.3813766177666662, 'longitude': 103.9359010240149},
        '35': {'region': 'East', 'type': 'Recycling Bin', 'name': 'Shell - Siglap','address': '40 Upper East Coast Rd, Singapore 455212', 'latitude': 1.3135925636589816, 'longitude': 103.92656266949348},
        '36': {'region': 'East', 'type': 'Recycling Bin', 'name': 'Bedok Industrial Park E','address': '3013 Bedok Industrial Park E, Pavilion, Bedok Industrial Park E 489978', 'latitude': 1.3385677175372337, 'longitude': 103.94928585470423},
        '37': {'region': 'East', 'type': 'Recycling Bin', 'name': 'Tampines Changkat Zone 8 Residents Network','address': 'Blk 364 Tampines Street 34, #01-133, Singapore 520364', 'latitude': 1.3581379619860696, 'longitude': 103.95946790812008},
        '38': {'region': 'East', 'type': 'E-recycling Bin', 'name': 'Shell - Tampines','address': '9 Tampines Avenue 2, Singapore 529731', 'latitude': 1.350604437162599, 'longitude': 103.94787350017229},
        '39': {'region': 'East', 'type': 'E-recycling Bin', 'name': 'Block 24 Bedok','address': 'Blk 24 Chai Chee Rd, Singapore 460024', 'latitude': 1.3263944539658974, 'longitude': 103.92279699222667},
        '40': {'region': 'East', 'type': 'Recycling Bin', 'name': 'Block 135 Pasir Ris','address': '135 Pasir Ris Street 11, Singapore 510135', 'latitude': 1.366588213979486, 'longitude': 103.95655753196567},

        '41': {'region': 'West', 'type': 'Recycling Bin', 'name': 'Yuhua Community Club','address': '90 Boon Lay Wy, Singapore 609958', 'latitude': 1.3417636222038514, 'longitude': 103.73656668538752},
        '42': {'region': 'West', 'type': 'Recycling Bin', 'name': 'FairPrice Supermarket - Taman Jurong Shopping Centre','address': 'Blk 399 Yung Sheng Rd, #01-35, Singapore 610399', 'latitude': 1.3364041044531667, 'longitude': 103.7212243308579},
        '43': {'region': 'West', 'type': 'E-recycling Bin', 'name': 'Block 318 Clementi','address': 'Blk 318 Clementi Ave 4, Singapore 120318', 'latitude': 1.3202858719270836, 'longitude': 103.76446885470673},
        '44': {'region': 'West', 'type': 'E-recycling Bin', 'name': 'National Library Board','address': '21 Jurong East Central 1, Singapore 609732', 'latitude': 1.3343505910044047, 'longitude': 103.73976716154185},
        '45': {'region': 'West', 'type': 'Recycling Bin', 'name': 'NTUC FairPrice - Bukit Batok MRT Station','address': '10 Bukit Batok Central, #01-08 MRT Station, Singapore 659958', 'latitude': 1.3506762440128357, 'longitude': 103.74905358538629},
        '46': {'region': 'West', 'type': 'E-recycling Bin', 'name': 'Pioneer Zone 9 RN','address': '602 Jurong West St 65, #01-175, Singapore 640602', 'latitude': 1.3409940083503602, 'longitude': 103.70034133085728},
        '47': {'region': 'West', 'type': 'Recycling Bin', 'name': 'Ng Teng Fong General Hospital Tower B','address': '1 Jurong East Street 21, Singapore 609606', 'latitude': 1.3357744718545743, 'longitude': 103.74530717743953},
        '48': {'region': 'West', 'type': 'Recycling Bin', 'name': 'Giant Hypermarket - Pioneer Mall','address': 'Blk 638 Jurong West Street 61, #03-01, Singapore 640638', 'latitude': 1.3433218137327476, 'longitude': 103.69724516154074},
        '49': {'region': 'West', 'type': 'E-recycling Bin', 'name': 'Nanyang Meadows - Block 98','address': 'Blk 98 Nanyang Cres, Nanyang Meadows Staff Housing, Singapore 637665', 'latitude': 1.3533320488686498, 'longitude': 103.6894189081208},
        '50': {'region': 'West', 'type': 'Recycling Bin', 'name': '2 Jurong East Central 1','address': '2 Jurong East Central 1, Rear Entrance, Capitaland JCube 609731', 'latitude': 1.335750856980327, 'longitude': 103.74010500812321},
        '51': {'region': 'West', 'type': 'E-recycling Bin', 'name': 'Block 297D Choa Chu Kang','address': 'Blk 297D Choa Chu Kang Ave 2, Singapore 684297', 'latitude': 1.3794966550116192, 'longitude': 103.7430895001684},
        '52': {'region': 'West', 'type': 'Recycling Bin', 'name': 'Sheng Siong Supermarket - Clementi Ave 2','address': 'Blk 352 Clementi Ave 2, #01-91/93/95 Shopping Centre, Singapore 120352', 'latitude': 1.316482643148272, 'longitude': 103.7706713626561},

        '53': {'region': 'Central', 'type': 'E-recycling Bin', 'name': 'Marymount Community Club','address': '191 Sin Ming Ave, Main Lobby, Singapore 575738', 'latitude': 1.3614711341320127, 'longitude': 103.84150039471682},
        '54': {'region': 'Central', 'type': 'E-recycling Bin', 'name': 'Toa Payoh West Community Club','address': '200 Lor 2 Toa Payoh, Side of Building, Singapore 319642', 'latitude': 1.3369463966760355, 'longitude': 103.8449578388067},
        '55': {'region': 'Central', 'type': 'Recycling Bin', 'name': 'Environment Building','address': '40 Scotts Rd, Singapore 228231', 'latitude': 1.312631262780027, 'longitude': 103.83609700812633},
        '56': {'region': 'Central', 'type': 'E-recycling Bin', 'name': "King's Centre",'address': '390 Havelock Rd, Singapore 169662', 'latitude': 1.2913038546856723, 'longitude': 103.8358803308641},
        '57': {'region': 'Central', 'type': 'Recycling Bin', 'name': 'Kitchener Complex','address': 'Blk 809 French Rd, Kitchener Complex, Main Lobby, Singapore 200809', 'latitude': 1.3100142734914308, 'longitude': 103.86185766949403},
        '58': {'region': 'Central', 'type': 'Recycling Bin', 'name': 'FairPrice Finest Funan Mall','address': '107 N Bridge Rd, #B1-10 Funan, Singapore 179105', 'latitude': 1.2935656151624633, 'longitude': 103.85070993086387},
        '59': {'region': 'Central', 'type': 'Recycling Bin', 'name': 'Guoco Tower B2 Atrium','address': '7 Wallich St, Guoco Tower, B2 Atrium Beside Escalator, Singapore 078884', 'latitude': 1.278853723642018, 'longitude': 103.84561565360066},
        '60': {'region': 'Central', 'type': 'E-recycling Bin', 'name': 'Revenue Centre','address': '55 Newton Rd, Level 2, Singapura 307987', 'latitude': 1.3210555997035396, 'longitude': 103.84234350017624},
        '61': {'region': 'Central', 'type': 'E-recycling Bin', 'name': 'Singtel Shop 313@somerset','address': '313 Orchard Rd, #03-31/32/33/34/35/36 313 Somerset, Singapore 238895', 'latitude': 1.3034825123229317, 'longitude': 103.83882272291356},
        '62': {'region': 'West', 'type': 'E-recycling Bin', 'name': 'ALBA E-WASTE SMART RECYCLING PTE LTD', 'address': '20 TUAS LOOP 637350', 'latitude': 1.320382282, 'longitude': 103.6364225},
        '63': {'region': 'West', 'type': 'E-recycling Bin', 'name': '223 CHOA CHU KANG CENTRAL', 'address': '223 CHOA CHU KANG CENTRAL 680223', 'latitude': 1.39154207667851, 'longitude': 103.69787132141693},
        '64': {'region': 'Central', 'type': 'E-recycling Bin', 'name': 'CHENG SAN COMMUNITY CENTRE', 'address': '6 ANG MO KIO STREET 53, CHENG SAN COMMUNITY CENTRE, LEVEL 1 569205', 'latitude': 1.3734060967427648, 'longitude':103.84887085727055},
        '65':  {'region': 'South', 'type': 'E-recycling Bin', 'name': '313@SOMERSET', 'address': ' 313 ORCHARD ROAD, LEVEL 1 DISCOVERY WALK, NEAR MONEY CHANGER 238895', 'latitude': 1.307909288322698, 'longitude': 103.79958988562055},
        '66': {'region': 'North', 'type': 'E-recycling Bin', 'name': 'Northpoint City', 'address': '930 YISHUN AVENUE 2, NORTHPOINT CITY, SOUTH WING, LEVEL 2 769098', 'latitude': 1.431478182993142, 'longitude': 103.83649780960612},
        '67': {'region': 'North', 'type': 'E-recycling Bin', 'name': '406A SEMBAWANG DRIVE MSCP','address': '55 Newton Rd, Level 2, Singapura 307987', 'latitude': 1.3210555997035396, 'longitude': 103.81798265617468},
        '68': {'region': 'North', 'type': 'E-recycling Bin', 'name': '336A SEMBAWANG CRESCENT MSCP','address': ' 336A SEMBAWANG CRESCENT 751336', 'latitude': 1.4468703845839972, 'longitude': 103.81500217829434},
        '69': {'region': 'South', 'type': 'E-recycling Bin', 'name': '54 CHIN SWEE RD','address': ' 54 CHIN SWEE ROAD 160054', 'latitude': 1.2960415552912634, 'longitude': 103.79825951254996},
        '70': {'region': 'South', 'type': 'E-recycling Bin', 'name': 'MARINA ONE','address': '5 STRAITS VIEW, MARINA ONE, #B2-79 18935', 'latitude': 1.2784027208672746, 'longitude': 103.85316023345499},
        '71': {'region': 'North', 'type': 'E-recycling Bin', 'name': 'TZU CHI HUMANISTIC YOUTH CENTRE','address': '30A YISHUN CENTRAL 1, TZU CHI HUMANISTIC YOUTH CENTRE 768796', 'latitude': 1.42694513834467, 'longitude': 103.83830978316702},
        '72': {'region': 'South', 'type': 'E-recycling Bin', 'name': 'SOUTH BEACH AVENUE ','address': '26 BEACH ROAD, SOUTH BEACH AVENUE 189768', 'latitude': 1.2956259577802005, 'longitude': 103.85478864400407},
        '73': {'region': 'South', 'type': 'E-recycling Bin', 'name': 'Singapore General Hospital ','address': '20 COLLEGE ROAD, ACADEMIA BUILDING 169856', 'latitude': 1.282880818929548, 'longitude': 103.83558034934006},
        '74': {'region': 'South', 'type': 'E-recycling Bin', 'name': '68 GEYLANG BAHRU','address': '68 GEYLANG BAHRU, MAIN ENTRANCE 330068', 'latitude': 1.328282724031856, 'longitude': 103.80042922638337},
        '75': {'region': 'Southeast', 'type': 'E-recycling Bin', 'name': 'Singpost Centre ','address': '10 EUNOS ROAD 8, SINGPOST CENTRE 408600', 'latitude': 1.3217792942926212, 'longitude': 103.89404619590623},
        '76': {'region': 'Northwest', 'type': 'E-recycling Bin', 'name': '888 PLAZA','address': ' 888 WOODLANDS DRIVE 50, 888 PLAZA, COMMON CORRIDOR 730888', 'latitude': 1.4393788360510313, 'longitude': 103.79538848180178},
        '77': {'region': 'South', 'type': 'E-recycling Bin', 'name': '23 GHIM MOH LINK','address': '23 GHIM MOH LINK 271023', 'latitude': 1.3132210375675755, 'longitude': 103.78511651174452},
        '78': {'region': 'Northwest', 'type': 'E-recycling Bin', 'name': 'ACE THE PLACE CC','address': '120 WOODLANDS AVENUE 1, ACE THE PLACE CC, BESIDE CC OFFICE ENTRANCE 739069', 'latitude': 1.4278297637302129, 'longitude': 103.79200557946693},
        '79': {'region': 'North', 'type': 'E-recycling Bin', 'name': 'Sembawang Shopping Centre','address': '604 SEMBAWANG ROAD, SEMBAWANG SHOPPING CENTRE, 2F 758459', 'latitude': 1.444102747697095, 'longitude': 103.8244803493188},
        '80': {'region': 'East', 'type': 'E-recycling Bin', 'name': 'ESR BIZPARK@CHANGI ','address': '8 CHANGI BUSINESS PARK AVENUE 1, ESR BIZPARK #01-51 486018 ', 'latitude': 1.3368174337252217, 'longitude': 103.96424999481842},
        '81': {'region': 'South', 'type': 'E-recycling Bin', 'name': 'ALEXANDRA HOSPITAL','address': '378 ALEXANDRA ROAD, BLK 21, LEVEL 1 159964', 'latitude': 1.2899017305330418, 'longitude': 103.79973255300274},
        '82': {'region': 'East', 'type': 'E-recycling Bin', 'name': 'CHANGI GENERAL HOSPITAL ','address': '2 SIMEI STREET 3, CHANGI GENERAL HOSPITAL 529889', 'latitude': 1.3419979715645487, 'longitude': 103.94926584138906},
        '83': {'region': 'Central', 'type': 'E-recycling Bin', 'name': 'ANCHORVALE CC','address': '59 ANCHORVALE ROAD, ANCHORVALE COMMUNITY CLUB, MAIN LOBBY 544965', 'latitude': 1.3999337166898354, 'longitude': 103.79933406400282},
        '84': {'region': 'Northeast', 'type': 'E-recycling Bin', 'name': 'SENGKANG GENERAL HOSPITAL ','address': ' 110 SENGKANG EAST WAY, SENGKANG GENERAL HOSPITAL, LEVEL 8 544886', 'latitude': 1.407424756625887, 'longitude': 103.89284230012797},
        '85': {'region': 'Central', 'type': 'E-recycling Bin', 'name': 'WISMA ATRIA','address': '435 ORCHARD ROAD, WISMA ATRIA, LEVEL 6 BESIDE CARPARK 238877', 'latitude': 1.3061340045371002, 'longitude': 103.83058711031889},
        '86': {'region': 'Central', 'type': 'E-recycling Bin', 'name': 'ANG MO KIO CC','address': 'ANG MO KIO AVENUE 1, MAIN LOBBY ENTRANCE 569976', 'latitude': 1.3722923675632144, 'longitude': 103.79950923623795},
        '87': {'region': 'West', 'type': 'E-recycling Bin', 'name': 'JURONG POINT','address': '1 JURONG WEST CENTRAL 2, JURONG POINT, BESIDES SKECHERS #01-16H/J 648886', 'latitude': 1.3415900078898062, 'longitude': 103.70526204247484},
        '88': {'region': 'South', 'type': 'E-recycling Bin', 'name': 'ONE MARINA','address': '1 MARINA BOULEVARD, ONE MARINA BOULEVARD, B1 18989', 'latitude': 1.285905092168645, 'longitude': 103.85260197741067},
        '89': {'region': 'East', 'type': 'E-recycling Bin', 'name': 'BEDOK INDUSTRIAL PARK E','address': '3013 BEDOK INDUSTRIAL PARK E, PAVILION 489978', 'latitude': 1.3392428849963993, 'longitude': 103.89935731628293},
        '90': {'region': 'Central', 'type': 'E-recycling Bin', 'name': 'ANG MO KIO HUB','address': '53 ANG MO KIO AVENUE 3, AMK HUB, #03-13 569933', 'latitude': 1.286765830420325, 'longitude': 103.85260197741067},
        '91': {'region': 'North', 'type': 'E-recycling Bin', 'name': 'SHELL YISHUN','address': ' 1 YISHUN STREET 11 768642', 'latitude': 1.4318209030848217, 'longitude': 103.8334806479851},
        '92': {'region': 'Southeast', 'type': 'E-recycling Bin', 'name': 'BEDOK IXORA RC','address': '51 NEW UPPER CHANGI ROAD, #01-1500 461051', 'latitude': 1.3273799370382893, 'longitude': 103.8989375209667},
        '93': {'region': 'North', 'type': 'E-recycling Bin', 'name': 'SHELL WOODLANDS','address': '20 WOODLANDS AVENUE 9 738954', 'latitude': 1.445479498083321, 'longitude': 103.78932902657563},
        '94': {'region': 'Central', 'type': 'E-recycling Bin', 'name': 'SHELL TOA PAYOH','address': ' 248 TOA PAYOH LORONG 1 319755', 'latitude': 1.3427410070082675, 'longitude': 103.84981480961768},
        '95': {'region': 'South', 'type': 'E-recycling Bin', 'name': 'SHELL TIONG BAHRU','address': '603 TIONG BAHRU ROAD 158788', 'latitude': 1.2929995356794106, 'longitude': 103.82173303932373},
        '96': {'region': 'Central', 'type': 'E-recycling Bin', 'name': 'SHELL THOMSON','address': '324 THOMSON ROAD 307672', 'latitude': 1.3329137047931552, 'longitude': 103.84241519974921},
        '97': {'region': 'East', 'type': 'E-recycling Bin', 'name': 'SHELL TAMPINES','address': '9 TAMPINES AVENUE 2 529731', 'latitude': 1.3499179823295622, 'longitude': 103.94778767207367},
        '98': {'region': 'East', 'type': 'E-recycling Bin', 'name': 'SHELL SIMPANG BEDOK','address': '331 BEDOK ROAD 469504', 'latitude': 1.3332735244526117, 'longitude': 103.94779150276183},
        '99': {'region': 'East', 'type': 'E-recycling Bin', 'name': 'SHELL SIGLAP','address': '40 UPPER EAST COAST ROAD 455212', 'latitude': 1.3154734973796138, 'longitude': 103.9258670979167},
        '100': {'region': 'Southeast', 'type': 'E-recycling Bin', 'name': 'SHELL PAYA LEBAR MACPHERSON','address': '255 PAYA LEBAR ROAD 409037', 'latitude': 1.3413699807153459, 'longitude': 103.88277112879744},
        '101': {'region': 'Southeast', 'type': 'E-recycling Bin', 'name': 'SHELL PAYA LEBAR','address': ' 98 PAYA LEBAR ROAD 409008', 'latitude': 1.3234880716626753, 'longitude': 103.89217031756311},
        



    }
    for bin_data in bins.values():
        sql = """
            INSERT INTO bins (region, type, name, address, latitude, longitude)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        values = (
            bin_data['region'],
            bin_data['type'],
            bin_data['name'],
            bin_data['address'],
            bin_data['latitude'],
            bin_data['longitude']
        )
        cursor.execute(sql, values)

    db.commit()
    print("Data inserted successfully.")
    cursor.close()
    db.close()

#  Populate Data

#populateBin()