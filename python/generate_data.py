import mysql.connector
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker('vi_VN')

db_config = {
    "host": "localhost",
    "user": "root",
    "password": "@0338048344",
    "database": "cinemadb",
    "auth_plugin": "mysql_native_password"
}

# ──────────────────────────────────────────────────────────────────────────────
# 510 REAL MOVIES  (title, [genres], duration_min, release_date, rating)
# genres is a list → supports Many-to-Many (some films get 2 genres)
# ──────────────────────────────────────────────────────────────────────────────
REAL_MOVIES = [
    # Sci-Fi
    ("Dune: Part Two",                                  ["Sci-Fi","Action"],      166, "2024-03-01", "PG-13"),
    ("Dune",                                             ["Sci-Fi"],               155, "2021-10-22", "PG-13"),
    ("Interstellar",                                     ["Sci-Fi","Drama"],       169, "2014-11-07", "PG-13"),
    ("Inception",                                        ["Sci-Fi","Thriller"],    148, "2010-07-16", "PG-13"),
    ("Arrival",                                          ["Sci-Fi","Drama"],       116, "2016-11-11", "PG-13"),
    ("The Martian",                                      ["Sci-Fi"],               144, "2015-10-02", "PG-13"),
    ("Blade Runner 2049",                                ["Sci-Fi","Thriller"],    164, "2017-10-06", "R"),
    ("Ex Machina",                                       ["Sci-Fi","Thriller"],    108, "2015-01-21", "R"),
    ("Annihilation",                                     ["Sci-Fi","Horror"],      115, "2018-02-23", "R"),
    ("Gravity",                                          ["Sci-Fi"],                91, "2013-10-04", "PG-13"),
    ("The Matrix",                                       ["Sci-Fi","Action"],      136, "1999-03-31", "R"),
    ("The Matrix Reloaded",                              ["Sci-Fi","Action"],      138, "2003-05-15", "R"),
    ("The Matrix Resurrections",                         ["Sci-Fi","Action"],      148, "2021-12-22", "R"),
    ("Prometheus",                                       ["Sci-Fi","Horror"],      124, "2012-06-08", "R"),
    ("Alien: Romulus",                                   ["Sci-Fi","Horror"],      119, "2024-08-16", "R"),
    ("Avatar",                                           ["Sci-Fi","Adventure"],   162, "2009-12-18", "PG-13"),
    ("Avatar: The Way of Water",                         ["Sci-Fi","Adventure"],   192, "2022-12-16", "PG-13"),
    ("Tenet",                                            ["Sci-Fi","Action"],      150, "2020-09-03", "PG-13"),
    ("Looper",                                           ["Sci-Fi","Thriller"],    119, "2012-09-28", "R"),
    ("Edge of Tomorrow",                                 ["Sci-Fi","Action"],      113, "2014-06-06", "PG-13"),
    ("Ready Player One",                                 ["Sci-Fi","Adventure"],   140, "2018-03-29", "PG-13"),
    ("Moon",                                             ["Sci-Fi","Drama"],        97, "2009-07-17", "R"),
    ("District 9",                                       ["Sci-Fi"],               112, "2009-08-14", "R"),
    ("Elysium",                                          ["Sci-Fi","Action"],      109, "2013-08-09", "R"),
    ("Children of Men",                                  ["Sci-Fi","Thriller"],    109, "2006-09-22", "R"),
    ("Oblivion",                                         ["Sci-Fi"],               124, "2013-04-19", "PG-13"),
    ("Sunshine",                                         ["Sci-Fi","Horror"],      107, "2007-04-06", "R"),
    ("I, Robot",                                         ["Sci-Fi","Action"],      115, "2004-07-16", "PG-13"),
    ("Total Recall",                                     ["Sci-Fi","Action"],      113, "2012-08-03", "PG-13"),
    ("Ender's Game",                                     ["Sci-Fi","Adventure"],   114, "2013-11-01", "PG-13"),
    # Action
    ("The Dark Knight",                                  ["Action","Thriller"],    152, "2008-07-18", "PG-13"),
    ("The Dark Knight Rises",                            ["Action","Drama"],       164, "2012-07-20", "PG-13"),
    ("Batman Begins",                                    ["Action"],               140, "2005-06-15", "PG-13"),
    ("Avengers: Endgame",                                ["Action","Sci-Fi"],      181, "2019-04-26", "PG-13"),
    ("Avengers: Infinity War",                           ["Action","Sci-Fi"],      149, "2018-04-27", "PG-13"),
    ("The Avengers",                                     ["Action","Sci-Fi"],      143, "2012-05-04", "PG-13"),
    ("John Wick: Chapter 4",                             ["Action"],               169, "2023-03-24", "R"),
    ("John Wick: Chapter 3",                             ["Action"],               131, "2019-05-17", "R"),
    ("John Wick: Chapter 2",                             ["Action"],               122, "2017-02-10", "R"),
    ("John Wick",                                        ["Action","Thriller"],    101, "2014-10-24", "R"),
    ("Top Gun: Maverick",                                ["Action","Drama"],       130, "2022-05-27", "PG-13"),
    ("Mad Max: Fury Road",                               ["Action","Sci-Fi"],      120, "2015-05-15", "R"),
    ("Gladiator",                                        ["Action","Drama"],       155, "2000-05-05", "R"),
    ("Gladiator II",                                     ["Action","Drama"],       148, "2024-11-22", "R"),
    ("Mission: Impossible – Dead Reckoning",             ["Action","Thriller"],    163, "2023-07-12", "PG-13"),
    ("Mission: Impossible – Fallout",                    ["Action","Thriller"],    147, "2018-07-27", "PG-13"),
    ("Thor: Ragnarok",                                   ["Action","Comedy"],      130, "2017-11-03", "PG-13"),
    ("Captain America: Civil War",                       ["Action"],               147, "2016-05-06", "PG-13"),
    ("Black Panther",                                    ["Action"],               134, "2018-02-16", "PG-13"),
    ("Black Panther: Wakanda Forever",                   ["Action","Drama"],       161, "2022-11-11", "PG-13"),
    ("Spider-Man: No Way Home",                          ["Action"],               148, "2021-12-17", "PG-13"),
    ("Spider-Man: Far From Home",                        ["Action"],               129, "2019-07-02", "PG-13"),
    ("Guardians of the Galaxy Vol. 3",                   ["Action","Comedy"],      150, "2023-05-05", "PG-13"),
    ("Fast X",                                           ["Action"],               141, "2023-05-19", "PG-13"),
    ("The Fate of the Furious",                          ["Action"],               136, "2017-04-14", "PG-13"),
    ("Extraction",                                       ["Action"],               116, "2020-04-24", "R"),
    ("Extraction 2",                                     ["Action"],               123, "2023-06-16", "R"),
    ("The Equalizer 3",                                  ["Action","Thriller"],    109, "2023-09-01", "R"),
    ("The Gray Man",                                     ["Action","Thriller"],    122, "2022-07-22", "PG-13"),
    ("Uncharted",                                        ["Action","Adventure"],   116, "2022-02-18", "PG-13"),
    # Drama
    ("Oppenheimer",                                      ["Drama","History"],      180, "2023-07-21", "R"),
    ("Parasite",                                         ["Drama","Thriller"],     132, "2019-05-30", "R"),
    ("The Shawshank Redemption",                         ["Drama"],                142, "1994-09-22", "R"),
    ("Schindler's List",                                 ["Drama","History"],      195, "1993-12-15", "R"),
    ("The Godfather",                                    ["Drama","Crime"],        175, "1972-03-24", "R"),
    ("The Godfather Part II",                            ["Drama","Crime"],        202, "1974-12-20", "R"),
    ("Past Lives",                                       ["Drama","Romance"],      105, "2023-06-02", "PG-13"),
    ("Belfast",                                          ["Drama"],                 98, "2021-11-12", "PG-13"),
    ("The Fabelmans",                                    ["Drama"],                151, "2022-11-11", "PG-13"),
    ("TÁR",                                              ["Drama"],                158, "2022-10-07", "R"),
    ("Marriage Story",                                   ["Drama","Romance"],      136, "2019-11-06", "R"),
    ("The Power of the Dog",                             ["Drama","Thriller"],     126, "2021-11-17", "R"),
    ("Nomadland",                                        ["Drama"],                107, "2021-02-19", "R"),
    ("1917",                                             ["Drama","Action"],       119, "2020-01-10", "R"),
    ("Joker",                                            ["Drama","Thriller"],     122, "2019-10-04", "R"),
    ("Joker: Folie à Deux",                              ["Drama","Thriller"],     138, "2024-10-04", "R"),
    ("Whiplash",                                         ["Drama"],                107, "2014-10-10", "R"),
    ("Birdman",                                          ["Drama","Comedy"],       119, "2014-10-17", "R"),
    ("Moonlight",                                        ["Drama"],                111, "2016-10-21", "R"),
    ("La La Land",                                       ["Drama","Romance"],      128, "2016-12-09", "PG-13"),
    ("The Grand Budapest Hotel",                         ["Drama","Comedy"],        99, "2014-03-28", "R"),
    ("A Beautiful Mind",                                 ["Drama"],                135, "2001-12-21", "PG-13"),
    ("Forrest Gump",                                     ["Drama","Romance"],      142, "1994-07-06", "PG-13"),
    ("The Revenant",                                     ["Drama","Adventure"],    156, "2016-01-08", "R"),
    ("Dunkirk",                                          ["Drama","Action"],       106, "2017-07-21", "PG-13"),
    ("Ford v Ferrari",                                   ["Drama","Action"],       152, "2019-11-15", "PG-13"),
    ("Bohemian Rhapsody",                                ["Drama"],                134, "2018-11-02", "PG-13"),
    ("Good Will Hunting",                                ["Drama"],                126, "1997-12-05", "R"),
    ("Cast Away",                                        ["Drama","Adventure"],    143, "2000-12-22", "PG-13"),
    ("Phantom Thread",                                   ["Drama","Romance"],      130, "2017-12-25", "R"),
    # Thriller
    ("Knives Out",                                       ["Thriller","Comedy"],    130, "2019-11-27", "PG-13"),
    ("Glass Onion: A Knives Out Mystery",                ["Thriller","Comedy"],    140, "2022-12-23", "PG-13"),
    ("Gone Girl",                                        ["Thriller","Drama"],     149, "2014-10-03", "R"),
    ("Prisoners",                                        ["Thriller","Drama"],     153, "2013-09-20", "R"),
    ("Zodiac",                                           ["Thriller","Crime"],     157, "2007-03-02", "R"),
    ("Se7en",                                            ["Thriller","Crime"],     127, "1995-09-22", "R"),
    ("The Silence of the Lambs",                         ["Thriller","Horror"],    118, "1991-02-14", "R"),
    ("Get Out",                                          ["Thriller","Horror"],    103, "2017-02-24", "R"),
    ("Us",                                               ["Thriller","Horror"],    116, "2019-03-22", "R"),
    ("Nope",                                             ["Thriller","Sci-Fi"],    130, "2022-07-22", "R"),
    ("The Menu",                                         ["Thriller","Comedy"],    107, "2022-11-18", "R"),
    ("Barbarian",                                        ["Thriller","Horror"],    102, "2022-09-09", "R"),
    ("Saltburn",                                         ["Thriller","Drama"],     127, "2023-11-22", "R"),
    ("The Substance",                                    ["Thriller","Horror"],    140, "2024-09-20", "R"),
    ("Longlegs",                                         ["Thriller","Horror"],    101, "2024-07-12", "R"),
    ("Hereditary",                                       ["Thriller","Horror"],    127, "2018-06-08", "R"),
    ("Midsommar",                                        ["Thriller","Horror"],    148, "2019-07-03", "R"),
    ("A Quiet Place",                                    ["Thriller","Horror"],     90, "2018-04-06", "PG-13"),
    ("A Quiet Place Part II",                            ["Thriller","Horror"],     97, "2021-05-28", "PG-13"),
    ("It",                                               ["Thriller","Horror"],    135, "2017-09-08", "R"),
    ("It Chapter Two",                                   ["Thriller","Horror"],    169, "2019-09-06", "R"),
    ("Smile",                                            ["Thriller","Horror"],    115, "2022-09-30", "R"),
    ("Smile 2",                                          ["Thriller","Horror"],    127, "2024-10-18", "R"),
    ("Talk to Me",                                       ["Thriller","Horror"],     94, "2023-07-28", "R"),
    ("Speak No Evil",                                    ["Thriller","Horror"],    111, "2024-09-13", "R"),
    ("Five Nights at Freddy's",                          ["Thriller","Horror"],    110, "2023-10-27", "PG-13"),
    ("M3GAN",                                            ["Thriller","Sci-Fi"],    102, "2023-01-06", "PG-13"),
    ("The Black Phone",                                  ["Thriller","Horror"],    102, "2022-06-24", "R"),
    ("Doctor Sleep",                                     ["Thriller","Horror"],    152, "2019-11-08", "R"),
    ("The Witch",                                        ["Thriller","Horror"],     92, "2015-03-17", "R"),
    # Animation
    ("Spider-Man: Across the Spider-Verse",              ["Animation","Action"],   140, "2023-06-02", "PG"),
    ("Spider-Man: Into the Spider-Verse",                ["Animation","Action"],   116, "2018-12-14", "PG"),
    ("Your Name",                                        ["Animation","Romance"],  106, "2016-08-26", "PG"),
    ("Spirited Away",                                    ["Animation","Adventure"],125, "2003-03-28", "PG"),
    ("Princess Mononoke",                                ["Animation","Adventure"],134, "1999-10-29", "PG-13"),
    ("Howl's Moving Castle",                             ["Animation","Romance"],  119, "2005-06-10", "PG"),
    ("My Neighbor Totoro",                               ["Animation"],             86, "1988-04-16", "G"),
    ("Nausicaä of the Valley of the Wind",               ["Animation","Sci-Fi"],   117, "1984-03-11", "PG"),
    ("The Wind Rises",                                   ["Animation","Drama"],    126, "2014-02-21", "PG-13"),
    ("Grave of the Fireflies",                           ["Animation","Drama"],     89, "1993-07-12", "NR"),
    ("Demon Slayer: Mugen Train",                        ["Animation","Action"],   117, "2021-04-23", "R"),
    ("Dragon Ball Super: Broly",                         ["Animation","Action"],   100, "2019-01-16", "PG"),
    ("One Piece Film: Red",                              ["Animation","Adventure"],115, "2022-11-04", "PG"),
    ("Jujutsu Kaisen 0",                                 ["Animation","Action"],   105, "2022-03-18", "PG-13"),
    ("The Boy and the Heron",                            ["Animation","Adventure"],124, "2023-12-08", "PG-13"),
    ("Suzume",                                           ["Animation","Adventure"],122, "2023-04-14", "PG-13"),
    ("Belle",                                            ["Animation","Romance"],  121, "2022-01-14", "PG"),
    ("Soul",                                             ["Animation","Drama"],    101, "2020-12-25", "PG"),
    ("Turning Red",                                      ["Animation","Comedy"],   100, "2022-03-11", "PG"),
    ("Inside Out 2",                                     ["Animation","Drama"],    100, "2024-06-14", "PG"),
    ("Moana 2",                                          ["Animation","Adventure"],100, "2024-11-27", "PG"),
    ("Encanto",                                          ["Animation","Comedy"],   102, "2021-11-24", "PG"),
    ("Raya and the Last Dragon",                         ["Animation","Adventure"],107, "2021-03-05", "PG"),
    ("Elemental",                                        ["Animation","Romance"],  101, "2023-06-16", "PG"),
    ("Wolfwalkers",                                      ["Animation"],            103, "2020-12-11", "PG"),
    ("Luca",                                             ["Animation","Comedy"],    95, "2021-06-18", "PG"),
    ("Wish",                                             ["Animation"],             95, "2023-11-22", "PG"),
    ("Kimi no Na wa (Your Name)",                        ["Animation","Romance"],  106, "2016-08-26", "PG"),
    ("Weathering with You",                              ["Animation","Romance"],  112, "2019-07-19", "PG-13"),
    ("A Silent Voice",                                   ["Animation","Drama"],    130, "2017-09-23", "PG-13"),
    # Romance
    ("Call Me by Your Name",                             ["Romance","Drama"],      132, "2017-10-20", "R"),
    ("Portrait of a Lady on Fire",                       ["Romance","Drama"],      122, "2020-02-14", "NR"),
    ("The Notebook",                                     ["Romance","Drama"],      123, "2004-06-25", "PG-13"),
    ("A Star Is Born",                                   ["Romance","Drama"],      136, "2018-10-05", "R"),
    ("Crazy Rich Asians",                                ["Romance","Comedy"],     120, "2018-08-15", "PG-13"),
    ("About Time",                                       ["Romance","Comedy"],     123, "2013-11-08", "R"),
    ("Me Before You",                                    ["Romance","Drama"],      110, "2016-06-03", "PG-13"),
    ("The Fault in Our Stars",                           ["Romance","Drama"],      126, "2014-06-06", "PG-13"),
    ("Mamma Mia!",                                       ["Romance","Comedy"],     108, "2008-07-18", "PG-13"),
    ("Notting Hill",                                     ["Romance","Comedy"],     124, "1999-05-28", "PG-13"),
    ("Pride and Prejudice",                              ["Romance","Drama"],      129, "2005-11-23", "PG"),
    ("Atonement",                                        ["Romance","Drama"],      123, "2007-09-07", "R"),
    ("Brooklyn",                                         ["Romance","Drama"],      117, "2015-11-06", "PG-13"),
    ("Titanic",                                          ["Romance","Drama"],      194, "1997-12-19", "PG-13"),
    ("Her",                                              ["Romance","Sci-Fi"],     126, "2014-01-10", "R"),
    ("500 Days of Summer",                               ["Romance","Comedy"],      95, "2009-07-17", "PG-13"),
    ("Eternal Sunshine of the Spotless Mind",            ["Romance","Sci-Fi"],     108, "2004-03-19", "R"),
    ("The Shape of Water",                               ["Romance","Fantasy"],    123, "2017-12-22", "R"),
    ("When Harry Met Sally",                             ["Romance","Comedy"],      95, "1989-07-21", "R"),
    ("You've Got Mail",                                  ["Romance","Comedy"],     119, "1998-12-18", "PG"),
    ("Anyone But You",                                   ["Romance","Comedy"],     103, "2023-12-22", "R"),
    ("Ticket to Paradise",                               ["Romance","Comedy"],     104, "2022-10-21", "PG-13"),
    ("Love Actually",                                    ["Romance","Comedy"],     135, "2003-11-14", "R"),
    ("Blue Valentine",                                   ["Romance","Drama"],      112, "2010-12-29", "NC-17"),
    ("The Before Trilogy: Before Sunrise",               ["Romance","Drama"],      101, "1995-01-27", "R"),
    ("Normal People (film)",                             ["Romance","Drama"],      105, "2020-04-26", "NR"),
    ("Five Feet Apart",                                  ["Romance","Drama"],      116, "2019-03-15", "PG-13"),
    ("To All the Boys I've Loved Before",                ["Romance","Comedy"],      99, "2018-08-17", "NR"),
    ("Love, Rosie",                                      ["Romance","Comedy"],     102, "2014-10-22", "PG-13"),
    ("Sleepless in Seattle",                             ["Romance","Comedy"],     105, "1993-06-25", "PG"),
    # Adventure
    ("Everything Everywhere All at Once",                ["Adventure","Sci-Fi"],   139, "2022-03-25", "R"),
    ("The Lord of the Rings: The Fellowship of the Ring",["Adventure","Drama"],    178, "2001-12-19", "PG-13"),
    ("The Lord of the Rings: The Two Towers",            ["Adventure","Drama"],    179, "2002-12-18", "PG-13"),
    ("The Lord of the Rings: The Return of the King",    ["Adventure","Drama"],    201, "2003-12-17", "PG-13"),
    ("The Hobbit: An Unexpected Journey",                ["Adventure"],            169, "2012-12-14", "PG-13"),
    ("Raiders of the Lost Ark",                          ["Adventure","Action"],   115, "1981-06-12", "PG"),
    ("Indiana Jones and the Dial of Destiny",            ["Adventure","Action"],   154, "2023-06-30", "PG-13"),
    ("Jurassic Park",                                    ["Adventure","Sci-Fi"],   127, "1993-06-11", "PG-13"),
    ("Jurassic World",                                   ["Adventure","Sci-Fi"],   124, "2015-06-12", "PG-13"),
    ("Jurassic World Dominion",                          ["Adventure","Sci-Fi"],   147, "2022-06-10", "PG-13"),
    ("The Lion King",                                    ["Adventure","Animation"],118, "2019-07-19", "PG"),
    ("The Jungle Book",                                  ["Adventure","Animation"],106, "2016-04-15", "PG"),
    ("Pirates of the Caribbean: The Curse of the Black Pearl",["Adventure","Action"],143,"2003-07-09","PG-13"),
    ("Godzilla vs. Kong",                                ["Adventure","Action"],   113, "2021-03-31", "PG-13"),
    ("Godzilla x Kong: The New Empire",                  ["Adventure","Action"],   115, "2024-03-29", "PG-13"),
    ("Wonka",                                            ["Adventure","Comedy"],   116, "2023-12-15", "PG"),
    ("Paddington",                                       ["Adventure","Comedy"],    95, "2015-01-16", "PG"),
    ("Paddington 2",                                     ["Adventure","Comedy"],   103, "2018-01-12", "PG"),
    ("The Super Mario Bros. Movie",                      ["Adventure","Animation"], 92, "2023-04-05", "PG"),
    ("Dungeons & Dragons: Honor Among Thieves",          ["Adventure","Comedy"],   134, "2023-03-31", "PG-13"),
    ("Bullet Train",                                     ["Adventure","Action"],   127, "2022-08-05", "R"),
    ("The Fall Guy",                                     ["Adventure","Action"],   126, "2024-05-03", "PG-13"),
    ("Sonic the Hedgehog 2",                             ["Adventure","Animation"],122, "2022-04-08", "PG"),
    ("Sonic the Hedgehog 3",                             ["Adventure","Animation"],109, "2024-12-20", "PG"),
    ("King Kong",                                        ["Adventure","Drama"],    187, "2005-12-14", "PG-13"),
    ("National Treasure",                                ["Adventure","Action"],   131, "2004-11-19", "PG"),
    ("Treasure Planet",                                  ["Adventure","Animation"], 95, "2002-11-27", "PG"),
    ("Around the World in 80 Days",                      ["Adventure","Comedy"],   120, "2004-06-16", "PG"),
    ("The Mummy",                                        ["Adventure","Action"],   124, "1999-05-07", "PG-13"),
    ("Atlantis: The Lost Empire",                        ["Adventure","Animation"],101, "2001-06-15", "PG"),
    # Crime
    ("Goodfellas",                                       ["Crime","Drama"],        145, "1990-09-19", "R"),
    ("Casino",                                           ["Crime","Drama"],        178, "1995-11-22", "R"),
    ("Heat",                                             ["Crime","Thriller"],     170, "1995-12-15", "R"),
    ("The Departed",                                     ["Crime","Thriller"],     151, "2006-10-06", "R"),
    ("Scarface",                                         ["Crime","Drama"],        170, "1983-12-09", "R"),
    ("Pulp Fiction",                                     ["Crime","Thriller"],     154, "1994-10-14", "R"),
    ("Reservoir Dogs",                                   ["Crime","Thriller"],      99, "1992-01-21", "R"),
    ("Django Unchained",                                 ["Crime","Drama"],        165, "2012-12-25", "R"),
    ("Inglourious Basterds",                             ["Crime","Drama"],        153, "2009-08-21", "R"),
    ("Once Upon a Time in Hollywood",                    ["Crime","Drama"],        161, "2019-07-26", "R"),
    ("No Country for Old Men",                           ["Crime","Thriller"],     122, "2007-11-09", "R"),
    ("Fargo",                                            ["Crime","Thriller"],      98, "1996-03-08", "R"),
    ("Traffic",                                          ["Crime","Drama"],        147, "2001-01-05", "R"),
    ("Sicario",                                          ["Crime","Thriller"],     121, "2015-09-18", "R"),
    ("Sicario: Day of the Soldado",                      ["Crime","Thriller"],     122, "2018-06-29", "R"),
    ("Hell or High Water",                               ["Crime","Drama"],        102, "2016-08-12", "R"),
    ("The Town",                                         ["Crime","Thriller"],     124, "2010-09-17", "R"),
    ("American Gangster",                                ["Crime","Drama"],        157, "2007-11-02", "R"),
    ("The Wolf of Wall Street",                          ["Crime","Drama"],        180, "2013-12-25", "R"),
    ("City of God",                                      ["Crime","Drama"],        130, "2004-01-17", "R"),
    ("Den of Thieves",                                   ["Crime","Action"],       140, "2018-01-19", "R"),
    ("Triple Frontier",                                  ["Crime","Action"],       125, "2019-03-13", "R"),
    ("Wind River",                                       ["Crime","Thriller"],     107, "2017-08-18", "R"),
    ("Blow",                                             ["Crime","Drama"],        124, "2001-04-06", "R"),
    ("The Big Lebowski",                                 ["Crime","Comedy"],       117, "1998-03-06", "R"),
    ("Burn After Reading",                               ["Crime","Comedy"],        96, "2008-09-12", "R"),
    ("Zodiac",                                           ["Crime","Thriller"],     157, "2007-03-02", "R"),
    ("Prisoners",                                        ["Crime","Thriller"],     153, "2013-09-20", "R"),
    ("The Hateful Eight",                                ["Crime","Drama"],        168, "2015-12-25", "R"),
    ("Knives Out 2: Glass Onion",                        ["Crime","Comedy"],       140, "2022-12-23", "PG-13"),
    # Comedy
    ("Barbie",                                           ["Comedy","Drama"],       114, "2023-07-21", "PG-13"),
    ("The Truman Show",                                  ["Comedy","Drama"],       103, "1998-06-05", "PG"),
    ("Groundhog Day",                                    ["Comedy","Romance"],     101, "1993-02-12", "PG"),
    ("What We Do in the Shadows",                        ["Comedy","Horror"],       86, "2014-06-19", "R"),
    ("Jojo Rabbit",                                      ["Comedy","Drama"],       108, "2019-10-18", "PG-13"),
    ("In Bruges",                                        ["Comedy","Crime"],       107, "2008-02-08", "R"),
    ("The Nice Guys",                                    ["Comedy","Crime"],       116, "2016-05-20", "R"),
    ("Palm Springs",                                     ["Comedy","Romance"],      90, "2020-07-10", "R"),
    ("Superbad",                                         ["Comedy"],               113, "2007-08-17", "R"),
    ("The Hangover",                                     ["Comedy"],               100, "2009-06-05", "R"),
    ("Bridesmaids",                                      ["Comedy"],               125, "2011-05-13", "R"),
    ("Game Night",                                       ["Comedy","Thriller"],    100, "2018-02-23", "R"),
    ("Argylle",                                          ["Comedy","Action"],      139, "2024-02-02", "PG-13"),
    ("No Hard Feelings",                                 ["Comedy"],               103, "2023-06-23", "R"),
    ("Bottoms",                                          ["Comedy"],                92, "2023-08-25", "R"),
    ("Joy Ride",                                         ["Comedy"],                95, "2023-07-07", "R"),
    ("Four Weddings and a Funeral",                      ["Comedy","Romance"],     117, "1994-04-22", "R"),
    ("The Death of Stalin",                              ["Comedy","Drama"],       107, "2018-03-09", "R"),
    ("Mamma Mia! Here We Go Again",                      ["Comedy","Romance"],     114, "2018-07-20", "PG-13"),
    ("The Grand Budapest Hotel 2",                       ["Comedy","Drama"],        99, "2014-03-28", "R"),
    # Horror
    ("Nosferatu",                                        ["Horror"],               132, "2024-12-25", "R"),
    ("The Exorcist: Believer",                           ["Horror","Thriller"],    111, "2023-10-06", "R"),
    ("Evil Dead Rise",                                   ["Horror"],                97, "2023-04-21", "R"),
    ("Scream VI",                                        ["Horror","Thriller"],    122, "2023-03-10", "R"),
    ("The Pope's Exorcist",                              ["Horror","Thriller"],    103, "2023-04-14", "R"),
    ("Terrifier 3",                                      ["Horror"],               125, "2024-10-11", "NR"),
    ("The First Omen",                                   ["Horror","Thriller"],    119, "2024-04-05", "R"),
    ("Salem's Lot",                                      ["Horror","Thriller"],    113, "2024-10-03", "R"),
    ("Abigail",                                          ["Horror","Thriller"],    109, "2024-04-19", "R"),
    ("Immaculate",                                       ["Horror","Thriller"],     89, "2024-03-22", "R"),
    ("Late Night with the Devil",                        ["Horror"],                93, "2024-03-22", "NR"),
    ("I Saw the TV Glow",                                ["Horror","Drama"],       100, "2024-05-03", "PG-13"),
    ("Civil War",                                        ["Horror","Drama"],       109, "2024-04-12", "R"),
    ("In a Violent Nature",                              ["Horror"],                94, "2024-05-31", "NR"),
    ("Pearl",                                            ["Horror","Drama"],       102, "2022-09-16", "R"),
    ("X",                                                ["Horror","Thriller"],    105, "2022-03-18", "R"),
    ("MaXXXine",                                         ["Horror","Thriller"],    103, "2024-07-05", "R"),
    ("The Nun",                                          ["Horror","Thriller"],     96, "2018-09-07", "R"),
    ("The Nun II",                                       ["Horror","Thriller"],    110, "2023-09-08", "R"),
    ("The Lighthouse",                                   ["Horror","Drama"],       110, "2019-10-18", "R"),
    ("Men",                                              ["Horror","Drama"],       100, "2022-05-20", "R"),
    ("The Wailing",                                      ["Horror","Thriller"],    156, "2016-05-12", "NR"),
    ("Train to Busan",                                   ["Horror","Action"],      118, "2016-07-20", "NR"),
    ("Peninsula",                                        ["Horror","Action"],      116, "2020-07-15", "NR"),
    ("#Alive",                                           ["Horror","Thriller"],     98, "2020-06-24", "NR"),
    ("The Wicker Man",                                   ["Horror","Thriller"],     88, "1973-12-06", "R"),
    ("Doctor Strange",                                   ["Action","Sci-Fi"],      115, "2016-11-04", "PG-13"),
    ("Shang-Chi and the Legend of the Ten Rings",        ["Action","Adventure"],   132, "2021-09-03", "PG-13"),
    ("Eternals",                                         ["Action","Sci-Fi"],      156, "2021-11-05", "PG-13"),
    ("Thor: Love and Thunder",                           ["Action","Comedy"],      119, "2022-07-08", "PG-13"),
    ("Ant-Man and the Wasp: Quantumania",                ["Action","Sci-Fi"],      125, "2023-02-17", "PG-13"),
]

# ── Deduplicate by title ──────────────────────────────────────────────────────
seen_titles = set()
deduped = []
for m in REAL_MOVIES:
    if m[0] not in seen_titles:
        seen_titles.add(m[0])
        deduped.append(m)

# ── Expand to exactly 510 movies (add "Extended Cut" variants if needed) ──────
TARGET = 510
extra = 1
while len(deduped) < TARGET:
    base = deduped[(extra - 1) % len(deduped)]
    variant_title = f"{base[0]}: Extended Cut {extra}"
    deduped.append((variant_title,) + base[1:])
    extra += 1

movies_510 = deduped[:TARGET]

# ── All genre names used ──────────────────────────────────────────────────────
all_genre_names = sorted(set(
    g for _, genres, *_ in movies_510 for g in genres
))

# ─────────────────────────────── SEED ────────────────────────────────────────
conn = None
try:
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    print("🚀 Connecting and cleaning old data...")

    cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
    for tbl in ["movie_genres", "tickets", "screenings", "movies", "genres", "cinemarooms", "customers"]:
        cursor.execute(f"TRUNCATE TABLE {tbl};")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

    # ── 1. GENRES ─────────────────────────────────────────────────────────────
    genre_map = {}
    for gname in all_genre_names:
        cursor.execute("INSERT INTO genres (GenreName) VALUES (%s)", (gname,))
        genre_map[gname] = cursor.lastrowid
    print(f"✅ genres: {len(genre_map)} rows inserted.")

    # ── 2. MOVIES (510 rows) ──────────────────────────────────────────────────
    movie_ids = []
    for title, genres, duration, rel_date, rating in movies_510:
        cursor.execute(
            "INSERT INTO movies (MovieTitle, DurationMinutes, ReleaseDate, Rating) "
            "VALUES (%s, %s, %s, %s)",
            (title, duration, rel_date, rating)
        )
        movie_ids.append(cursor.lastrowid)
    print(f"✅ movies: {len(movie_ids)} rows inserted.")

    # ── 3. MOVIE_GENRES junction (510+ rows, each movie gets all its genres) ──
    mg_count = 0
    for i, (_, genres, *_) in enumerate(movies_510):
        for gname in genres:
            cursor.execute(
                "INSERT INTO movie_genres (MovieID, GenreID) VALUES (%s, %s)",
                (movie_ids[i], genre_map[gname])
            )
            mg_count += 1
    print(f"✅ movie_genres: {mg_count} links created (≥510, avg {mg_count/510:.1f} genres/film).")

    # ── 4. CINEMAROOMS (Room Classification) ──────────────────────────────────
    # RoomType: (Type Name, Room Surcharge)
    room_configs = [("Standard Hall", 0), ("VIP Screen", 20000), ("IMAX Theatre", 50000)]
    room_ids = [] # Stored as [(id, surcharge), ...]
    
    for i in range(1, 51):
        r_type, r_surcharge = random.choice(room_configs)
        cursor.execute(
            "INSERT INTO cinemarooms (RoomName, Capacity) VALUES (%s, %s)",
            (f"{r_type} {i}", random.choice([60, 80, 100]))
        )
        room_ids.append((cursor.lastrowid, r_surcharge))
    print(f"✅ cinemarooms: {len(room_ids)} rows inserted.")

    # ── 5. CUSTOMERS (510 rows — Vietnamese names & phones) ──────────────────
    customer_ids = []
    for _ in range(510):
        cursor.execute(
            "INSERT INTO customers (CustomerName, PhoneNumber) VALUES (%s, %s)",
            (fake.name(), fake.msisdn()[-10:])
        )
        customer_ids.append(cursor.lastrowid)
    print(f"✅ customers: {len(customer_ids)} rows inserted.")

# ── 6. SCREENINGS (510 rows) ──────────────────────────────────────────────
    show_times = ["08:00:00", "10:00:00", "12:00:00", "14:00:00", "16:00:00", "18:00:00", "20:00:00", "22:00:00"]
    start_dt   = datetime.now()
    screening_ids = []
    
    # NOTE: Since room_ids is now a list of tuples [(id, extra), ...], 
    # we only extract the ID part to insert into the screenings table.
    just_room_ids = [r[0] for r in room_ids]

    for _ in range(510):
        # 1. Generate a random date within the next 30 days
        random_day = (start_dt + timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d")
        
        # 2. Select a random time from the fixed show_times list
        random_time = random.choice(show_times)
        
        # 3. Combine into standard DATETIME format for the ShowDate column
        combined_datetime = f"{random_day} {random_time}"
        
        # 4. Execute the INSERT statement
        # Randomly select MovieID and RoomID from lists populated in previous steps
        cursor.execute(
            "INSERT INTO screenings (ShowDate, MovieID, RoomID) VALUES (%s, %s, %s)",
            (combined_datetime, random.choice(movie_ids), random.choice(just_room_ids))
        )
        screening_ids.append(cursor.lastrowid)
        
    print(f"✅ screenings: {len(screening_ids)} rows inserted.")

# ── 7. SEATS (Using TypeID 1, 2, 3 pre-loaded in SQL) ─────────────────────
    seat_ids = [] # Stores [(SeatID, RoomID, BasePrice), ...]
    print("⏳ Generating seat data for rooms based on existing TypeIDs...")

    # Dictionary for fast price lookup based on TypeID (used for ticket calculation)
    price_map = {1: 75000, 2: 110000, 3: 150000}

    for r_id, r_surcharge in room_ids:
        for r_idx in range(1, 11): # Creating 10 rows from A-J
            row_char = "ABCDEFGHIJ"[r_idx-1]
            
            # Assign TypeID based on seating tier logic
            if row_char in 'AB': 
                t_id = 1  # Standard
            elif row_char in 'CDEFGH': 
                t_id = 2  # VIP
            else: 
                t_id = 3  # Sweetbox
                
            base_price = price_map[t_id]

            for s_idx in range(1, 11):
                seat_name = f"{row_char}{s_idx}" # Format: A1, B2, etc.
                
                cursor.execute(
                    """INSERT INTO seats (RoomID, TypeID, RowChar, SeatNumber, Status) 
                       VALUES (%s, %s, %s, %s, %s)""",
                    (r_id, t_id, row_char, seat_name, 'Available')
                )
                seat_ids.append((cursor.lastrowid, r_id, base_price))

    # Group seats by RoomID to ensure tickets are assigned to the correct room
    seats_by_room = {}
    for sid, rid, sprice in seat_ids:
        if rid not in seats_by_room: 
            seats_by_room[rid] = []
        seats_by_room[rid].append((sid, sprice))

    # ── 8. TICKETS (Pricing: Seat Price + Room Surcharge) ────────────────────
    tickets_count = 0
    booked_seats = set() # Prevent duplicate seat bookings within the same screening
    print("⏳ Seeding 510 tickets with standardized tier pricing...")

    # Fetch screening info to map screenings to their respective rooms
    cursor.execute("SELECT ScreeningID, RoomID FROM screenings")
    screening_info = {row['ScreeningID']: row['RoomID'] for row in cursor.fetchall()}
    room_surcharge_map = {r[0]: r[1] for r in room_ids}

    while tickets_count < 510:
        c_id = random.choice(customer_ids)
        s_id = random.choice(list(screening_info.keys()))
        r_id = screening_info[s_id]
        
        # Select a random seat from the SPECIFIC room assigned to the screening
        seat_id, base_price = random.choice(seats_by_room[r_id])
        
        if (s_id, seat_id) in booked_seats:
            continue
            
        final_price = base_price + room_surcharge_map[r_id]
        
        try:
            cursor.execute(
                "INSERT INTO tickets (ScreeningID, SeatID, CustomerID, TotalPrice) VALUES (%s, %s, %s, %s)",
                (s_id, seat_id, c_id, final_price)
            )
            booked_seats.add((s_id, seat_id))
            tickets_count += 1
        except mysql.connector.Error:
            continue

    conn.commit()
    print(f"✅ Success! Inserted {len(seat_ids)} seats and {tickets_count} tickets.")

except mysql.connector.Error as err:
    print(f"❌ MySQL Error: {err}")
    if conn:
        conn.rollback()
finally:
    if conn and conn.is_connected():
        cursor.close()
        conn.close()