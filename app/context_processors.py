# -*- coding: utf-8 -*-
from app import app
from random import choice

silent_songs = [
    (u'4\'33"', u'John Cage', 273),
    (u'Funeral March for the Obsequies of a Deaf Man', u'Alphonse Allais', 112),
    (u'In Futurum', u'Erwin Schulhoff', 161),
    (u"12:97:24:99", u'Mudvayne', 11),
    (u"18 sekúndur fyrir sólarupprás", u'Sigur Rós', 18),
    (u"23 Seconds of Silence", u'Wilco', 23),
    (u"42 Minutes of Silence", u'Milosh', 42),
    (u"9-11-01", u'Soulfly', 60),
    (u"Absolute Elsewhere", u'Coil', 4),
    (u"Anniversary Of World War III", u'The West Coast Pop Art Experimental Band', 97),
    (u"Are We Here? (Criminal Justice Bill? Mix)", 'uOrbital', 240),
    (u"The Ballad of Richard Nixon", u'John Denver', 11),
    (u"The Best of Marcel Marceau, Side 1", u'Michael Viner', 1140),
    (u"The Best of Marcel Marceau, Side 2", u'Michael Viner', 1140),
    (u"Beware! The Funk is Everywhere", u'Afrika Bambaataa', 21),
    (u"Birthdeath Experience", u'Whitehouse', 210),
    (u"Le chant des carpes", u'Ludwig von 88', 141),
    (u"In Remembrance", u'Pan.Thy.Monium', 60),
    (u"Intentionally Left Blank", u'James Holden', 165),
    (u"A Lot of Nothing I-XI", u'Coheed and Cambria', 93),
    (u"Magic Window", u'Boards of Canada', 108),
    (u"The Misinterpretation of Silence and its Disastrous Consequences", u'Type O Negative', 64),
    (u"The Most Important Track On the Album", u'Astronautalis', 164),
    (u"The Nutopian International Anthem", u'John Lennon', 3),
    (u"Two Minutes Silence", u'John Lennon and Yoko Ono', 120),
    (u"Omitted for Clarity", u'Karnivool', 21),
    (u"One Minute of Silence", u'Soundgarden', 60),
    (u"A One Minute Silence", u'Mike Batt', 60),
    (u"Path XII Inlustra Nigror", u'Vesania', 1559),
    (u"Pause", u'Rob Dougan', 34),
    (u"Pregnant Pause... Intermission", u'Leila Bela', 4),
    (u"Pending Silence extended Remix (extra silent)", u'Magnus "SoulEye" Pålsson', 60),
    (u"Rwanda", u'Radio Boy', 8),
    (u"Schweigenminute", u'VNV Nation', 60),
    (u'A suitable place for those with tired ears to pause and resume listening later', u'Robert Wyatt', 30),
    (u"Silence", u'Brian Eno', 57),
    (u"The Sound of Free speech", u'Crass', 426),
    (u"Štrajk", u'Hladno pivo', 5),
    (u"There's a Riot Goin' On", u'Sly Stone', 4),
    (u"Thirty-second Silence", u'Guster', 30),
    (u"Three Bagatelles for David Tudor", u'György Ligeti', 84),
    (u"The Ten Coolest Things About New Jersey", u'The Bloodhound Gang', 10),
    (u"Tunnel of Goats XVII", u'Coil', 25),
    (u"You Can Make Your Own Music", u'Covenant', 273)]

@app.context_processor
def silence():
    return {'silence':choice(silent_songs)}
