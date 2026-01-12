import mysql.connector
from datetime import datetime

# Convert date to SQL acceptable date format

def parse_date(date_str):
    # Try multiple known formats
    for fmt in ("%d-%b-%Y", "%d %b %Y", "%d-%B-%Y", "%d %B %Y"):
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Unsupported date format: {date_str}")

def get_all_events():
    try:
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="Helloworld1$",
            database="Neighbourly_Database"
        )
        cursor = db.cursor()

        events = {
            "1": {
                "title": "(Cheng San-Seletar AAC) Project 100 Seniors",
                "organiser": "Cheng San CC SCEC",
                "ref_code": "20028085",
                "start_date": "01 Jan 2025",
                "end_date": "31 Dec 2025",
                "time": "9:00 AM - 5:00 PM",
                "location": "Cheng San CC",
                "price": "Free",
                "region": "North",
                "latitude": 1.3721945138181022,
                "longitude": 103.84933222355224
            },
            "2": {
                "title": "(Cheng San AAC) Breakfast Club - Engagement at Blk 446 Coffeeshop",
                "organiser": "Cheng San ASC 1",
                "ref_code": "25489058",
                "start_date": "16 Aug 2025",
                "end_date": "16 Aug 2025",
                "time": "9:00 AM - 11:00 AM",
                "location": "Cheng San CC",
                "price": "Free",
                "region": "North",
                "latitude": 1.3721945138181022,
                "longitude": 103.84933222355224
            },
            "3": {
                "title": "Bedok CSN FairPrice Walk For Health @ South East",
                "organiser": "Bedok CSN",
                "ref_code": "36740918",
                "start_date": "30 Aug 2025",
                "end_date": "30 Aug 2025",
                "time": "2:00 PM - 5:00 PM",
                "location": "Bedok CC",
                "price": "Free",
                "region": "Southeast",
                "latitude": 1.3245168661164641,
                "longitude": 103.9359174228699
            },

            "4": {
                "title": "HEALTHIER U WALK @HORT PARK WITH BOTTLE TREE",
                "organiser": "Cheng San Bottle Tree RN",
                "ref_code": "26198234",
                "start_date": "30 Aug 2025",
                "end_date": "30 Aug 2025",
                "time": "8:00 AM - 12:30 PM",
                "location": "Cheng San Bottle Tree RN",
                "price": "$3.00",
                "region": "Central",
                "latitude": 1.3675728299765795,
                "longitude": 103.85369683986299
            },
            



            "5": {
                "title": "Fengshan CC IAEC - Dandiya Night",
                "organiser": "Fengshan CC IAEC",
                "ref_code": "53262267",
                "start_date": "20 Sep 2025",
                "end_date": "20 Sep 2025",
                "time": "6:30 PM - 9:30 PM",
                "location": "Fengshan CC",
                "price": "$12.00",
                "region": "Southeast",
                "latitude":1.3308269212835684,
                "longitude":103.93630610716767
            },
            "6": {
                "title": "RN3 Karaoke",
                "organiser": "Potong Pasir Zone 3 RN",
                "ref_code": "31784705",
                "start_date": "01 Aug 2025",
                "end_date": "30 Aug 2025",
                "time": "9:00 AM - 10:00 PM",
                "location": "Potong Pasir Avenue 1",
                "price": "$4.00",
                "region": "Central",
                "latitude": 1.3380392858645396,
                "longitude": 103.8656426267668
            },

            "7": {
                "title": "Table Tennis",
                "organiser": "Teck Ghee CSN",
                "ref_code": "88234522",
                "start_date": "07 Aug 2025",
                "end_date": "31 Aug 2025",
                "time": "9:00 AM - 5:00 PM",
                "location": "Ang Mo Kio CC",
                "price": "$3.00",
                "region": "Central",
                "latitude": 1.367265164626977,
                "longitude": 103.84057490449639
            },

            "8": {
                "title": "BE Z3 Ukulele IG",
                "organiser": "Bishan East Zone 3 RN",
                "ref_code": "99707858",
                "start_date": "02 Jul 2025",
                "end_date": "31 Dec 2025",
                "time": "1:00 PM - 5:00 PM",
                "location": "Bishan East Zone 3 RN",
                "price": "$12.00",
                "region": "Central",
                "latitude": 1.3502626335998098,
                "longitude": 103.8514865801373
            },


            "9": {
                "title": "Bedok Flea Market",
                "organiser": "Bedok CC",
                "ref_code": "70962015",
                "start_date": "07 Sep 2025",
                "end_date": "07 Sep 2025",
                "time": "8:00 AM - 12:00 PM",
                "location": "Bedok CC",
                "price": "$5.00",
                "region": "Southeast",
                "latitude":1.3245919479473565,
                "longitude":103.93594960907336 
            },


            "10": {
                "title": "Bishan Wellness Hub - Dance Fitness Workout with Crystal",
                "organiser": "Bishan CC SCEC",
                "ref_code": "56468970",
                "start_date": "13 Aug 2025",
                "end_date": "01 Oct 2025",
                "time": "10:00 AM - 11:00 AM",
                "location": "Bishan Wellness Hub",
                "price": "$5.00",
                "region": "Central",
                "latitude": 1.3459743210254465,
                "longitude": 103.85309259480995
            },


            "11": {
                "title": "Cheng San Acacia RN (Mental Health) - Kkardio",
                "organiser": "Cheng San Acacia RN",
                "ref_code": "13145845",
                "start_date": "14 Sep 2025",
                "end_date": "14 Sep 2025",
                "time": "9:30 AM - 12:30 PM",
                "location": "Acacia RN Calm Corner",
                "price": "Free",
                "region": "Central",
                "latitude": 1.36788025337523,
                "longitude": 103.84969342384657
            },


            "12": {
                "title": "[WEC] A trip to Sembawang Hot Spring Park",
                "organiser": "Siglap South CC WEC",
                "ref_code": "24252907",
                "start_date": "06 Sep 2025",
                "end_date": "06 Sep 2025",
                "time": "8:00 AM - 1:00 PM",
                "location": "Siglap South CC",
                "price": "$5.00",
                "region": "Southeast",
                "latitude":1.313717869875838,
                "longitude":103.93065796945126
            },

            "13": {
                "title": "Bishan Wellness Hub - 2025 Baking Demo",
                "organiser": "Bishan CC SCEC",
                "ref_code": "67340035",
                "start_date": "23 Aug 2025",
                "end_date": "23 Aug 2025",
                "time": "10:00 AM - 11:00 AM",
                "location": "Bishan Wellness Hub",
                "price": "$2.00",
                "region": "Central",
                "latitude": 1.3459743210254465,
                "longitude": 103.85309259480995
            },


            "14": {
                "title": "Parenting Gen-Alpha Building Relationship Talk",
                "organiser": "Cheng San Diamond RN",
                "ref_code": "99737222",
                "start_date": "28 Sep 2025",
                "end_date": "28 Sep 2025",
                "time": "9:30 AM - 12:30 PM",
                "location": "Blk 511 Ang Mo Kio Ave 8 Void Deck",
                "price": "Free",
                "region": "Central",
                "latitude": 1.3738456939383352,
                "longitude": 103.85009113704578
            },


            "15": {
                "title": "Bishan RN-LOFT-WEC Kite Flying Day",
                "organiser": " Bishan RN, Bishan Loft RN, Bishan CC",
                "ref_code": "54765001",
                "start_date": "23 Aug 2025",
                "end_date": "23 Aug 2025",
                "time": "3:15 PM - 6:30 PM",
                "location": "Marina Barrage",
                "price": "$6.00",
                "region": "South",
                "latitude": 1.2813480769938332,
                "longitude": 103.87051721998381
            },


            "16": {
                "title": "Folk Dance Night",
                "organiser": "Kebun Baru CC SCEC",
                "ref_code": "30114285",
                "start_date": "06 Sep 2025",
                "end_date": "06 Sep 2025",
                "time": "5:00 PM - 9:30 PM",
                "location": "Kebun Baru Community Club",
                "price": "Free",
                "region": "Central",
                "latitude": 1.3732743253648643,
                "longitude": 103.837425984551
            },


            "17": {
                "title": "Wine and sake appreciation workshops",
                "organiser": "Kampong Chai Chee CC",
                "ref_code": "50183673",
                "start_date": "27 Jun 2025",
                "end_date": "08 Nov 2025",
                "time": "7:00 PM - 9:30 PM",
                "location": "Kampong Chai Chee CC",
                "price": "$12.00",
                "region": "Southeast",
                "latitude":1.3274215464122074,
                "longitude":103.9320103370993
            },


            "18": {
                "title": "YOGA for seniors",
                "organiser": "Boon Lay Zone F RN",
                "ref_code": "15168925",
                "start_date": "05 Sep 2025",
                "end_date": "05 Sep 2025",
                "time": "9:30 AM - 10:30 AM",
                "location": "Boon Lay Zone F RN",
                "price": "Free",
                "region": "West",
                "latitude": 1.3447623252781828,
                "longitude": 103.70221058625616
            },


            "19": {
                "title": "SG60 Melodies of Home by Impression of Nanyang Arts Association",
                "organiser": "Potong Pasir CCC",
                "ref_code": "13224387",
                "start_date": "22 Aug 2025",
                "end_date": "22 Aug 2025",
                "time": "6:30 PM - 10:00 PM",
                "location": "Potong Pasir CC",
                "price": "Free",
                "region": "Central",
                "latitude": 1.33282261360184,
                "longitude": 103.86740638686717
            },

            "20": {
                "title": "Dandiya Night 2025",
                "organiser": "Keat Hong CC IAEC",
                "ref_code": "60099637",
                "start_date": "28 Sep 2025",
                "end_date": "28 Sep 2025",
                "time": "6:00 PM - 10:00 PM",
                "location": "Keat Hong CC",
                "price": "$12.00",
                "region": "Northwest",
                "latitude":1.3844447183417912 ,
                "longitude":103.7448249955252
            },

            "21": {
                "title": "Bukit Purmei Zone A BBQ Pit 2025",
                "organiser": "Bukit Purmei Zone A RN",
                "ref_code": "69717894",
                "start_date": "01 Aug 2025",
                "end_date": "31 Dec 2025",
                "time": "6:00 PM - 9:30 PM",
                "location": "Block 108 Bukit Purmei Road",
                "price": "$10.00",
                "region": "South",
                "latitude": 1.2738130953420992,
                "longitude": 103.82547920102662
            },

            "22": {
                "title": "Healthy Fiesta 2025",
                "organiser": "Boon Lay CC IAEC",
                "ref_code": "82803305",
                "start_date": "07 Sep 2025",
                "end_date": "07 Sep 2025",
                "time": "9:30 AM - 1:00 PM",
                "location": "Boon Lay CC",
                "price": "$3.00",
                "region": "West",
                "latitude": 1.3487751249421833,
                "longitude": 103.71137253269335
            },

            "23": {
                "title": "Naval base deck RN: Chinese Calligraphy with Seniors",
                "organiser": "Canberra Zone 5 RN",
                "ref_code": "35964645",
                "start_date": "26 Aug 2025",
                "end_date": "26 Aug 2025",
                "time": "10:00 AM - 11:30 AM",
                "location": "Naval base deck RN",
                "price": "Free",
                "region": "North",
                "latitude": 1.452641760202271,
                "longitude": 103.81806901015263
            },

            "24": {
                "title": "[Yew Tee CC IAEC] Onam @ Yew Tee 2025",
                "organiser": "Yew Tee CC IAEC",
                "ref_code": "16612409",
                "start_date": "21 Sep 2025",
                "end_date": "21 Sep 2025",
                "time": "12:00 PM - 6:00 PM",
                "location": "Yew Tee CC",
                "price": "$10.00",
                "region": "Northwest",
                "latitude":1.3951102143477117,
                "longitude":103.74475371086824
            },

            "25": {
                "title": "Adventure with Canberra Community Sports Network - Coast to Coast Trail - 4 Part Series - Act 3",
                "organiser": "Canberra CSN",
                "ref_code": "42271138",
                "start_date": "24 Aug 2025",
                "end_date": "24 Aug 2025",
                "time": "7:00 AM - 12:00 PM",
                "location": "Canberra Community Club",
                "price": "$4.00",
                "region": "North",
                "latitude": 1.4450848544875667,
                "longitude": 103.81972917946695
            },


            "26": {
                "title": "GRACE EXERCISE AUG 2025 (Every Sat)",
                "organiser": "Bukit Batok East Jurong East View RN",
                "ref_code": "81698450",
                "start_date": "02 Aug 2025",
                "end_date": "30 Aug 2025",
                "time": "8:00 AM - 9:00 AM",
                "location": "MPH @ blk 204 Jurong East St 21",
                "price": "Free",
                "region": "West",
                "latitude": 1.3505521941052314,
                "longitude": 103.7446347696943
            },


            "27": {
                "title": "LTRN Mahjong Session",
                "organiser": "Lengkong Tiga RN",
                "ref_code": "90198710",
                "start_date": "04 Jul 2025",
                "end_date": "26 Sep 2025",
                "time": "1:00 PM - 4:00 PM",
                "location": "Blk 109 Lengkong Tiga RC Centre",
                "price": "Free",
                "region": "East",
                "latitude": 1.3248164102918254,
                "longitude": 103.91077849666006
            },


            "28": {
                "title": "Briskwalk (Healthier SG)",
                "organiser": "Bukit Batok East Zone 3 RN",
                "ref_code": "50442280",
                "start_date": "03 Aug 2025",
                "end_date": "31 Aug 2025",
                "time": "7:00 AM - 8:30 AM",
                "location": "Blk 268 Bukit Batok East Ave 4",
                "price": "Free",
                "region": "West",
                "latitude": 1.3518357046752822,
                "longitude": 103.75935273726503
            },

            "29": {
                "title": "Crafted Tea Party 2025",
                "organiser": "Kallang CC WEC",
                "ref_code": "36819480",
                "start_date": "23 Aug 2025",
                "end_date": "23 Aug 2025",
                "time": "2:30 PM - 5:00 PM",
                "location": "Kallang CC Multi Purpose Hall",
                "price": "$10.00",
                "region": "East",
                "latitude": 1.3189078342873144,
                "longitude": 103.86171929165282
            },

            "30": {
                "title": "Outing to Singapore Botanic Garden",
                "organiser": "Bukit Batok East CC",
                "ref_code": "63415186",
                "start_date": "28 Sep 2025",
                "end_date": "28 Sep 2025",
                "time": "8:30 AM - 1:30 PM",
                "location": "Botanical Garden",
                "price": "$6.00",
                "region": "South",
                "latitude": 1.31929671750821,
                "longitude": 103.81512590987883
            },

            "31": {
                "title": "Hougang CC WEC - Crochet Workshop",
                "organiser": "Hougang CC WEC",
                "ref_code": "71212329",
                "start_date": "16 Sep 2025",
                "end_date": "16 Sep 2025",
                "time": "10:00 AM - 12:00 PM",
                "location": "Hougang CC",
                "price": "$5.00",
                "region": "Northeast",
                "latitude":1.3648273371039572,
                "longitude":103.89235665319684 
            },


            "32": {
                "title": "Seize Your Youth 2025 - Call of Duty",
                "organiser": "Taman Jurong YN",
                "ref_code": "40864029",
                "start_date": "30 Aug 2025",
                "end_date": "30 Aug 2025",
                "time": "1:00 PM - 4:00 PM",
                "location": "Taman Jurong Community Club",
                "price": "$3.00",
                "region": "West",
                "latitude": 1.3440393459886992,
                "longitude": 103.72117639165282
            },


            "33": {
                "title": "Qigong Interest Group",
                "organiser": "Admiralty Zone 7 RN",
                "ref_code": "99622163",
                "start_date": "06 Nov 2024",
                "end_date": "05 Nov 2025",
                "time": "8:00 AM - 9:30 AM",
                "location": "Blk 622 Woodlands Drive 52 Link Hall",
                "price": "Free",
                "region": "North",
                "latitude": 1.4357887900810782,
                "longitude": 103.79765363289657
            },

            "34": {
                "title": "Paya Lebar Mid-Autumn Festival 2025",
                "organiser": "Paya Lebar CCC",
                "ref_code": "27193423",
                "start_date": "27 Sep 2025",
                "end_date": "27 Sep 2025",
                "time": "6:00 PM - 9:00 PM",
                "location": "Aljunied CC",
                "price": "$3.00",
                "region": "Northeast",
                "latitude":1.3581587780942161,
                "longitude":103.88944972561308 
            },

            "35": {
                "title": "Digital Wellness - Cybersecurity Workshop (Nanyang Youth Network)",
                "organiser": "Nanyang YN",
                "ref_code": "69063722",
                "start_date": "23 Aug 2025",
                "end_date": "23 Aug 2025",
                "time": "10:00 AM - 11:00 AM",
                "location": "Nanyang CC",
                "price": "Free",
                "region": "West",
                "latitude": 1.3426654718146607,
                "longitude": 103.69228189481004
            },

            "36": {
                "title": "Sustainable Jurong Spring",
                "organiser": " Jurong Spring CCC, Jurong Spring CC",
                "ref_code": "55956798",
                "start_date": "30 Aug 2025",
                "end_date": "30 Aug 2025",
                "time": "7:30 AM - 11:00 AM",
                "location": "Singapore 640501",
                "price": "$10.00",
                "region": "West",
                "latitude": 1.351996201161442,
                "longitude": 103.71945348289276
            },

            "37": {
                "title": "Marine Parade Mid-Autumn Festival 2025",
                "organiser": "Marine Parade CCC,Marine Parade CC,Joo Chiat CC",
                "ref_code": "86957329",
                "start_date": "27 Sep 2025",
                "end_date": "27 Sep 2025",
                "time": "7:00 PM - 9:00 PM",
                "location": "Marine Parade CC",
                "price": "$5.00",
                "region": "South",
                "latitude":1.305197529526832,
                "longitude":103.90987694210607
            },

            "38": {
                "title": "PPPEA RN - Normanton Park Condo Family Day",
                "organiser": "Pasir Panjang Private Estate Association RN, Telok Blangah CC",
                "ref_code": "43150098",
                "start_date": "30 Aug 2025",
                "end_date": "30 Aug 2025",
                "time": "2:00 PM - 6:00 PM",
                "location": "55 Normanton Park, Normanton Park Condo, Singapore",
                "price": "$6.00",
                "region": "South",
                "latitude": 1.287290878438917,
                "longitude": 103.79100088185122
            },

            "39": {
                "title": "Foldable Tote Bag Making Workshop",
                "organiser": "Ayer Rajah CC WEC",
                "ref_code": "80717045",
                "start_date": "25 Aug 2025",
                "end_date": "26 Aug 2025",
                "time": "7:00 PM - 9:00 PM",
                "location": "Ayer Rajah Community Club",
                "price": "$3.00",
                "region": "West",
                "latitude": 1.3206991506490562,
                "longitude": 103.74757803713858
            },

            "40": {
                "title": "Yoga @ Esparis",
                "organiser": "Esparis RN",
                "ref_code": "58121060",
                "start_date": "05 Jul 2025",
                "end_date": "27 Sep 2025",
                "time": "8:00 AM - 9:00 AM",
                "location": "Esparis Function Room, Level 2",
                "price": "Free",
                "region": "East",
                "latitude": 1.3697034393491523,
                "longitude": 103.95974489815161
            },
            
            "41": {
                "title": "Sengkang East Youth Network - Climbing/Bouldering (The Playground Series)",
                "organiser": "Sengkang East YN,Rivervale Court RC",
                "ref_code": "34829150",
                "start_date": "13 Sep 2025",
                "end_date": "13 Sep 2025",
                "time": "10:30 AM - 1:30 PM",
                "location": "Rivervale CC",
                "price": "$15.00",
                "region": "Northeast",
                "latitude": 1.3852181098246166,
                "longitude": 103.9024485531967
            },
            "42": {
                "title": "Dance Jam Night",
                "organiser": "Pasir Ris Elias CC WEC",
                "ref_code": "36608960",
                "start_date": "06 Sep 2025",
                "end_date": "06 Sep 2025",
                "time": "5:00 PM - 9:30 PM",
                "location": "Pasir Ris Elias Community Club",
                "price": "5.00",
                "region": "Northeast",
                "latitude": 1.3793872731752428,
                "longitude": 103.94326223503509
            },
            "43": {
                "title": "Esparina Day",
                "organiser": "Esparina RN, Buangkok CC",
                "ref_code": "77505322",
                "start_date": "31 Aug 2025",
                "end_date": "31 Aug 2025",
                "time": "10:00 AM - 12:00 PM",
                "location": "Esparina West Foyer",
                "price": "$2.00",
                "region": "Northeast",
                "latitude": 1.3872332790329658,
                "longitude": 103.89086916899902
            },         
           
            "44": {
                "title": "Rivervale CC IAEC - Kuthu Fitness",
                "organiser": "Rivervale CC IAEC",
                "ref_code": "24092723",
                "start_date": "13 Sep 2025",
                "end_date": "13 Sep 2025",
                "time": "6:30 PM - 8:30 PM",
                "location": "Rivervale CC",
                "price": "$5.00",
                "region": "Northeast",
                "latitude": 1.3853789953259716,
                "longitude": 103.90242709552518
            },  

            "45": {
                "title": "Punggol Coast Community Sports Network (CSN) Sports Day 2025",
                "organiser": "Punggol Coast CSN",
                "ref_code": "28435859",
                "start_date": "06 Sep 2025",
                "end_date": "06 Sep 2025",
                "time": "9:00 AM - 1:00 PM",
                "location": "One Punggol CC",
                "price": "$5.00",
                "region": "Northeast",
                "latitude":1.4085040731809393,
                "longitude": 103.90501126401965
            },   
            "46": {
                "title": "Compassvale Cape - Sunrise Morning Walk",
                "organiser": "Compassvale Cape RN",
                "ref_code": "86921398",
                "start_date": "30 Aug 2025",
                "end_date": "30 Aug 2025",
                "time": "6:30 AM - 8:00 AM",
                "location": "Blk 286 Compassvale Crescent Multipurpose Hall",
                "price": "Free",
                "region": "Northeast",
                "latitude": 1.3977964601865076,
                "longitude": 103.89569339295994
            },  
            
            "47": {
                "title": "Karaoke Sessions",
                "organiser": "Tampines Parkview RN",
                "ref_code": "74812878",
                "start_date": "13 Aug 2025",
                "end_date": "27 Sep 2025",
                "time": "6:00 PM - 10:00 PM",
                "location": "Tampines Parkview RN",
                "price": "Free",
                "region": "East",
                "latitude": 1.37507309772342,
                "longitude": 103.92937633361187
            },   
            "48": {
                "title": "IAEC ONAM CELEBRATION 2025",
                "organiser": "Punggol 21 CC IAEC",
                "ref_code": "10647527",
                "start_date": "14 Sep 2025",
                "end_date": "14 Sep 2025",
                "time": "9:30 AM - 1:30 PM",
                "location": "Punggol 21 CC",
                "price": "$8.00",
                "region": "Northeast",
                "latitude": 1.393767340158758,
                "longitude": 103.91354352436092
            },    
            "49": {
                "title": "Jewel RN - Lasting Power of Attorney (LPA) & Will Talk",
                "organiser": "Sengkang Central CCC",
                "ref_code": "95859494",
                "start_date": "31 Aug 2025",
                "end_date": "31 Aug 2025",
                "time": "10:00 AM - 12:00 PM",
                "location": "Jewel Function Room",
                "price": "Free",
                "region": "Northwest",
                "latitude": 1.3773150544660926,
                "longitude": 103.98618289514712
            },      
            "50": {
                "title": "Fall Prevention Tips For Seniors & Caregivers",
                "organiser": "Thomson CC WEC",
                "ref_code": "60940793",
                "start_date": "28 Sep 2025",
                "end_date": "28 Sep 2025",
                "time": "2:00 PM - 4:00 PM",
                "location": "Thomson CC",
                "price": "Free",
                "region": "Central",
                "latitude":1.3603009412927225,
                "longitude": 103.83474552640861
            },      
            "51": {
                "title": "Digital For Life: Be Safe, Smart and Kind Online (Gen AI)",
                "organiser": "Keat Hong CC SCEC",
                "ref_code": "33451591",
                "start_date": "31 Aug 2025",
                "end_date": "31 Aug 2025",
                "time": "8:30 AM - 10:00 AM",
                "location": "Keat Hong Zone 7 RN Centre",
                "price": "Free",
                "region": "Northwest",
                "latitude": 1.3827647242102437,
                "longitude": 103.74135131755509
            },   
            "52": {
                "title": "ACRN BMW - Seletar Airport + Fernvale Hawker Centre",
                "organiser": "Axis Colours RN",
                "ref_code": "29303359",
                "start_date": "31 Aug 2025",
                "end_date": "31 Aug 2025",
                "time": "7:00 AM - 1:00 PM",
                "location": "807B Choa Chu Kang Avenue 1, Singapore",
                "price": "Free",
                "region": "Northwest",
                "latitude": 1.376212513453137,
                "longitude": 103.74526713528849
            },    
            "53": {
                "title": "Current Affairs Sharing Session",
                "organiser": "Tampines Changkat CC",
                "ref_code": "35757006",
                "start_date": "06 Sep 2025",
                "end_date": "06 Sep 2025",
                "time": "10:30 AM - 12:00 PM",
                "location": "Tampines Changkat CC Multi-Purpose Hall (Level 3)",
                "price": "Free",
                "region": "East",
                "latitude": 1.3467497906659582,
                "longitude": 103.94765510422725
            },                        
        }

        for event_data in events.values():
            sql = """
                INSERT INTO events (title, organiser, ref_code, start_date, end_date, time, location, price, region, latitude, longitude)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            # Parse to MySQL-friendly date
            start_date = parse_date(event_data['start_date'])
            end_date = parse_date(event_data['end_date'])

            values = (
                event_data['title'],
                event_data['organiser'],
                event_data['ref_code'],
                start_date,
                end_date,
                event_data['time'],
                event_data['location'],
                event_data['price'],
                event_data['region'],
                event_data['latitude'],
                event_data['longitude']
            )

            cursor.execute(sql, values)

        db.commit()
        print("Events data inserted successfully.")

    except Exception as e:
        print(f"[ERROR] {e}")

    finally:
        cursor.close()
        db.close()

#get_all_events()
