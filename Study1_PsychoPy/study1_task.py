#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Study 1 - Belief revision tablet task (PsychoPy Coder script)
==============================================================

Procedure per session

  0. Start dialog: language (Dutch/English), reasons (numeric/quality video
     version), participant, age (3-10), gender.
  1. Group choice: the child picks the Moon or the Sun team (the chosen
     picture blinks with a happy sound). Right away both teams are shown
     (stimuli/teams/, order random: teams_pic_top) while the child gets the
     team's sticker and hat. On the same screen the child then taps their
     own team: it blinks
     with the happy sound; a tap on the other team plays a 'wrong' sound and
     the child can try again (team_tap_first own/other, team_tap_n_wrong,
     team_tap_rt).
  1b. Sticker distribution: one member of each team (same gender as the
     child; random if gender is not female/male) is shown; the child gives
     5 stickers to them and the experimenter records the numbers by tapping
     the 5 dots under each photo (stickers_to_sun_member,
     stickers_to_moon_member, 0-5 each).
  2. Four trials. Each trial:
       a. Experimenter set-up screens (box colour + animal pair; open the
          first box). In round 1 only, the child first practises the scale:
          the experimenter demonstrates it ("Let me show you!"; a thinking
          child's bubble shows the animal the marker points to, larger and
          more solid the closer it is to that end, "?" in the middle), then the
          child shows where the marker goes for "really more <left animal>",
          "really more <right animal>" and "don't know" (a thinking child with
          that animal or "?" in a thought bubble). Right answers (outer half
          of that side / within PRACTICE_MIDDLE of the middle) get a chime;
          wrong ones an 'oops' sound and the child tries again (skip button
          for the experimenter after PRACTICE_SKIP_AFTER wrong answers).
          Data: practice_<item> (final position), _first (first answer),
          _attempts, _correct for really_left, really_right, dont_know
       b. Initial belief: first a binary choice ("Which animal do you think
          there are more of?" - the child taps one of the two animals), then
          the scale appears below the same animals ("How sure are you?").
          With BUBBLE_IN_TEST the thinking child (as in the demo) is shown on
          both test sliders.
          The video team claims the animal the child did NOT choose.
       c. Experimenter screen (place the team logo), then the
          video: ingroup/outgroup team states the OPPOSITE belief with a
          strong/weak reason (tap the video to start it; afterwards
          Replay or Continue)
       c2. Check questions, on one screen with the team from the video:
          what does the team believe (tap one of the two animals) and why
          (numeric version: boxes with 2 or 4 open; quality version: eyes =
          they looked, speaking head = someone told them); "doesn't know"
          for both; and whether the child said the reason themselves or
          after asking. If belief or reason is wrong, the video is shown
          again and the questions are repeated (up to MAX_CHECKS attempts).
          Per attempt k the data has check<k>_belief, _belief_correct,
          _reason (2_boxes / 4_boxes / looked / told / dont_know),
          _reason_correct, _reason_prompted (self / prompted / empty),
          _passed, _rt.
       d. Second belief rating; the handle starts at the first answer (a grey
          line and "your first answer" mark it; the text disappears as soon
          as the child moves the handle)
  3. Solution: a row of boxes for each round with the child's final animal
     (second rating; first choice if it was exactly in the middle). Tapping
     a row opens the boxes: SOLUTION_MAJORITY of the 10 hold the child's
     animal, so the child is always right (chime and a green tick; the happy
     jingle when all are open). Data: solution_animal per trial.
  On both scales the exact middle (50) is marked by a "?" under the handle;
  positions within MIDDLE_SNAP of the middle snap to it.

Counterbalancing (assigned automatically, separately for each age)
  - Order of the 4 conditions (IS/IW = ingroup strong/weak,
    OS/OW = outgroup strong/weak; balanced Latin square):
        A: IS IW OW OS    B: IW OS IS OW    C: OS OW IW IS    D: OW IS OS IW
  - Order of the 4 box colours (balanced 4x4 Latin square, crossed with the
    condition order, so each condition is paired with each colour equally often)
  - Which animal of a pair appears on the left of the scale
  Together these make 32 lists. Each new child gets the condition order (A-D)
  that is least used among the completed sessions of their age in data/,
  and within that order the least used list (ties broken at random). Sessions
  with fewer than 4 trials and participant IDs starting with "test" are not
  counted.
  - Side of the Moon/Sun pictures on the choice screen is randomised and logged

Language and video version
  The language chosen in the start dialog sets the language of the videos and
  of all text, including the experimenter's. "reasons" chooses the numeric
  (videos x.1 / x.2) or quality (x.3 / x.4) video set.

Experimenter text
  Instructions for the experimenter are light grey. What to say (from the
  procedure scripts in procedure/) is hidden and shown with the (i) icon in
  the top-left corner; it stays on or off until tapped again (SHOW_HELP sets
  the start).

Expected folder structure (next to this script)
  stimuli/groups/moon.png, sun.png
  stimuli/sounds/team_chosen.m4a  (happy sound when the child picks / finds their team)
  stimuli/sounds/wrong.m4a        (child taps the other team / wrong practice answer)
  stimuli/sounds/correct.m4a      (right practice answer)
  stimuli/members/<team>_<female|male>.png  (stills from the videos)
  stimuli/thinking/child.png, bubble.png  (thinking child on the scale screens)
  stimuli/reasons/looked.png, told.png    (check question, quality version)
  stimuli/animals/elephant.png, lion.png, dog.png, cat.png,
                  rhino.png, turtle.png, cow.png, pig.png
  video_stimuli/<row>.<version>-<colour>-<team>-<animal>-<reason>.mp4
                 named as in video_stimuli/Study_1&2_video_labels.xlsx, e.g.
                 2.1-Blue-Moon-Elephant-Weak.mp4  (numeric reasons, English)
                 2.2-Blauw-Maan-Olifant-Zwak.mp4  (numeric reasons, Dutch)
                 (2 teams x 2 reason strengths x 8 animals = 32 videos per version)
  Missing files are replaced by text placeholders so the script can be tested
  before all media are ready.

Data
  data/<participant>_<date>.csv  - one row per trial, written after every trial.
  Each row is also sent to a Google Sheet (see sheets_sync.py and
  google_sheets/Code.gs). Without internet the rows wait in data/outbox/ and
  are sent as soon as there is a connection (the task retries while it runs
  and when it is started again).
  minutes_since_start: time from the first screen until that trial was saved;
  session_duration_min: from the first screen to the end screen (filled into
  all rows at the end; empty if the session was stopped early).
  Ratings are stored from -100 to +100. "rating*_raw" is screen-based
  (-100 = far left, +100 = far right); "rating*_toward_claim" is positive when
  the marker is on the side of the animal the team claimed.

Press ESC at any time to quit (data of finished trials are already saved).
Press M to show/hide the mouse cursor (hidden by default, see SHOW_CURSOR).
Videos are played with ffpyplayer (installed together with PsychoPy).
"""

from pathlib import Path
import csv
import math
import random
import sys

import numpy as np
from ffpyplayer.player import MediaPlayer
from psychopy import visual, core, event, gui, data, logging

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sheets_sync  # Google Sheets upload with local outbox (next to this script)

logging.console.setLevel(logging.WARNING)

# --------------------------------------------------------------------------
# Settings
# --------------------------------------------------------------------------
HERE = Path(__file__).resolve().parent
STIM = HERE / 'stimuli'
VIDEO_DIR = HERE / 'video_stimuli'
DATA_DIR = HERE / 'data'

BG_COLOR = 'white'
FULLSCREEN = True
SHOW_CURSOR = True  # laptop testing; set to False for the tablet. Key 'm' toggles it

AGES = [str(a) for a in range(3, 11)]  # choices in the start dialog
TEAMS = ['moon', 'sun']
QUALITIES = ['strong', 'weak']
CONDITIONS = ['ingroup_strong', 'ingroup_weak', 'outgroup_strong', 'outgroup_weak']
BOXES = {  # box colour -> animal pair, in the order of the video label list
    'blue': ('elephant', 'lion'),
    'red': ('dog', 'cat'),
    'green': ('rhino', 'turtle'),
    'yellow': ('cow', 'pig'),
}
BOX_ORDER = list(BOXES)
N_BOXES = 10  # boxes of one colour per trial
BOX_DISPLAY = {'blue': '#2b2f8c', 'red': '#e2462c',  # as the boxes in the videos
               'green': '#4f97a3', 'yellow': '#f3c623'}
N_STICKERS = 5  # stickers the child distributes between the two team members
SOUND_TEAM = STIM / 'sounds' / 'team_chosen.m4a'  # stereo AAC (mono WAV does not play)
SOUND_WRONG = STIM / 'sounds' / 'wrong.m4a'  # other team tapped / wrong practice answer
SOUND_CORRECT = STIM / 'sounds' / 'correct.m4a'  # right practice answer
PRACTICE_MIDDLE = 0.1  # practice "don't know": right if this close to the middle (-1..1)
PRACTICE_SKIP_AFTER = 3  # wrong practice answers before the experimenter can skip
BUBBLE_IN_TEST = False  # True: thinking child (as in the practice) also on the test sliders
MIDDLE_SNAP = 0.02  # scale positions this close to the middle (-1..1) snap to it
CHECK_FADED_OPACITY = 0.25  # check screen: the questions not being asked right now
SOLUTION_MAJORITY = 6  # end screen: boxes (of N_BOXES) that hold the child's animal
UNCHOSEN_OPACITY = 0.25  # first rating: the animal not chosen and its half of the scale
# Colour of each animal's end of the rating scale
ANIMAL_COLORS = {'dog': '#9a6500', 'cat': '#8f1d14',
                 'elephant': '#777777', 'lion': '#d78320',
                 'cow': '#333333', 'pig': '#d78378',
                 'turtle': '#287a3e', 'rhino': '#777777'}

DUTCH = {'blue': 'blauw', 'red': 'rood', 'green': 'groen', 'yellow': 'geel',
         'moon': 'maan', 'sun': 'zon', 'strong': 'sterk', 'weak': 'zwak',
         'elephant': 'olifant', 'lion': 'leeuw', 'dog': 'hond', 'cat': 'kat',
         'rhino': 'neushoorn', 'turtle': 'schildpad', 'cow': 'koe',
         'pig': 'varken'}
TEXT = {  # text the child sees
    'en': {'question': 'Which animal do you think there are more of?',
           'sure': 'How sure are you?',
           'first_answer': 'your first answer', 'continue': 'Continue',
           'next': 'Next pair', 'finish': 'Finish',
           'watch': 'Watch the video', 'replay': 'Replay',
           'stickers': 'You have 5 stickers. How many do you want to give '
                       'to each of them?',
           'teams': 'This is the {first} team and this is the {second} team.',
           'practice_show': 'Let me show you!',
           'solution': "Let's see what was in the boxes!",
           # check questions, read aloud by the experimenter
           'check_belief': 'Okay, does {whose} think there are more {a} or '
                           'more {b}?',
           'check_reason': 'And why do they think that?',
           'check_reason_numeric': 'And why do they think that? How many boxes '
                                   'did they open?'},
    'nl': {'question': 'Van welk dier denk je dat er meer zijn?',
           'sure': 'Hoe zeker ben je?',
           'first_answer': 'je eerste antwoord', 'continue': 'Verder',
           'next': 'Volgende', 'finish': 'Klaar',
           'watch': 'Kijk naar het filmpje', 'replay': 'Opnieuw',
           'stickers': 'Je hebt 5 stickers. Hoeveel wil je aan ieder van '
                       'hen geven?',
           'teams': 'Dit is het {first}-team en dit is het {second}-team.',
           'practice_show': 'Ik laat het je zien!',
           'solution': 'Laten we kijken wat er in de doosjes zat!',
           'check_belief': 'Oké, denkt {whose} dat er meer {a} of meer {b} zijn?',
           'check_reason': 'En waarom denken ze dat?',
           'check_reason_numeric': 'En waarom denken ze dat? Hoeveel doosjes '
                                   'hebben ze opengemaakt?'},
}

# Instructions for the experimenter, in light grey italics (so they don't draw
# the child's attention), in the language chosen in the start dialog.
# Each screen has a short instruction (always shown) and, under the key
# '<name>_say', what to say (wording from procedure/STUDY 1 - Script.docx and
# STUDIE 1 - Script Nederlands.docx). The "say" text is shown or hidden with
# the (i) icon in the top-left corner; [brackets] inside quotes are actions.
EXP_COLOR = '#a3a3a3'
EXP_BUTTON_COLOR = '#8f8f8f'  # answer buttons on the check screens
SELECTED_COLOR = '#e09b00'  # chosen answer / number on the check screens
SHOW_HELP = False  # show the "say" text from the start (the (i) icon toggles it)
EXP_TEXT = {
    'en': {
        'tap': '(tap to continue)',
        'missing': 'WARNING: {n} media files missing (placeholders will be used):',
        'online_only': ' (only online in Google Drive)',
        'more': '... and {n} more',
        'start': 'Participant {p} - order {o}\n\nGroup choice: let the child '
                 "choose a team, then tap the picture of the child's team.",
        'start_say': '"The game we will play has two teams, the Moon team and the '
                     'Sun team." [show the team pictures]\n'
                     '"What team do you want to be on today?"',
        'chosen': 'The child chose the {TEAM} team. Give the child the sticker and '
                  'hat of this team and show both teams. Then let the child tap '
                  'their own team (Continue = skip).',
        'tap_team_say': '"Can you show me your team? Tap on your team!"',
        'chosen_say': '"Okay! So I have a couple of things for you. First, I have a '
                      'special {team} team sticker for you." [give the sticker]\n'
                      '"I also have a special {team} team hat for you." [give the hat]\n'
                      '"Great, now you are part of the {team} team!"',
        'show_teams_say': '[point to the {own} team] "Here are some people who play '
                          'on your team, the {own} team."\n[point to the {other} '
                          'team] "And here are some people who play on the other '
                          'team, the {other} team."',
        'sticker_intro': 'Sticker task\n\nPut {n} stickers on the table. On the next '
                         'screen the child gives them to the two team members; tap '
                         'the dots under each person to record how many each gets.',
        'sticker_intro_say': '"Now I will ask you some questions about the two '
                             'teams. I have some stickers here, let\'s see how many I '
                             'have. I have 1, 2, 3, 4, 5 stickers. And now you can '
                             'tell me how many stickers to give each of these two '
                             '{pl}."\n[next screen, point to each person]\n'
                             '"So out of these 5 stickers, how many stickers should I '
                             'give to {this_sg} from your team?"\n'
                             '"Okay, and how many stickers should I give to {this_sg} '
                             'from the other team?"',
        'setup_first': 'Round 1 of {n} - game introduction\n\nPut the {k} {color} '
                       'boxes in front of the child and introduce the two animals '
                       '({pl_l} / {pl_r}).',
        'setup_first_say': '"Now we can play the game! The game today involves a '
                           'zoo. See, here is the zoo! Many animals are part of the '
                           'zoo, including some {pl_l} [hold up the {l}] and {pl_r} '
                           '[hold up the {r}]." [let the child name both animals]\n'
                           '"Your job will be to figure out whether there are more '
                           '{pl_l} or more {pl_r} in the boxes. Each one of these '
                           'boxes has an animal in it, either {a_l} or {a_r}."',
        'setup': 'Round {t} of {n}\n\nClear away the boxes, logo and toy animals of '
                 'the last round. Put the {k} {color} boxes in front of the child and '
                 'introduce the two animals ({pl_l} / {pl_r}).',
        'setup_say': '"Great job! Now we will play again. These boxes have {pl_l} '
                     '[hold up the {l}] and {pl_r} [hold up the {r}] in them." [let the '
                     'child name both animals]\n'
                     '"Each box has either {a_l} or {a_r} in it. Your job is to figure '
                     'out whether there are more {pl_l} or more {pl_r}."',
        'train_demo': 'Practice with the scale (first round only): show the child how '
                      'the scale works, then give them the tablet and tap Continue.',
        'train_demo_say': '"Later, I will ask you what you think about the boxes, and '
                          'we\'ll use this picture for you to tell me." [move the '
                          'marker yourself]\n"If you really think there are more '
                          '{pl_l}, you can place your marker here [far {l} side]. If '
                          'you kind of think there are more {pl_l}, somewhere in here '
                          '[middle of the {l} side]." [the same for the {pl_r}]\n'
                          '"And if you don\'t know, you can place your marker here." '
                          '[the middle, where the ? appears]',
        'train_left': 'Practice 1 of 3: the child shows where the marker goes if they '
                      'really think there are more {pl_l}. Continue checks the answer; '
                      'if it is wrong, the child tries again.',
        'train_left_say': '"Okay, so later when I ask you, if you really thought there '
                          'were more {pl_l}, where would you place your marker?"',
        'train_right': 'Practice 2 of 3: ... if they really think there are more '
                       '{pl_r}.',
        'train_right_say': '"Good, and if you really thought there were more {pl_r}, '
                           'where would you place your marker?"',
        'train_middle': "Practice 3 of 3: ... if they don't know.",
        'train_middle_say': '"Good, and if you didn\'t know, where would you place '
                            'your marker?"',
        'train_end_say': '"Okay great, I will bring the tablet back in a moment."',
        'open_box': 'Put the tablet aside. Open the leftmost box, show the child the '
                    'animal and close the box again.\nThen put the tablet in front of '
                    'the child.',
        'open_box_say': '"I am going to open one box for you. Let\'s see what is in '
                        'it!" [open the box]\n"Look, there is a ... in this box!"',
        'ask_binary_say': '"Okay, so what do you think? Do you think there are more '
                          '{pl_l} or more {pl_r} in the boxes?"',
        'ask_sure_say': '"And now you can tell me how sure you are that there are more '
                        '{pl}. Do you really think there are more {pl}, do you kind of '
                        'think there are more {pl}, or do you not really know?" '
                        '[point to each part of the scale]\nIf the child doesn\'t move '
                        'the marker: "So where do you want to place your marker?"',
        'ask_final_say': '"Earlier you said that you {how} there are more {pl} in the '
                         'boxes. So now what do you think? Do you want to move your '
                         'marker or leave it where it is?"',
        'how': {'really': 'really thought', 'kind_of': 'kind of thought',
                'dont_know': "didn't know whether"},
        'before_video': 'Place the {team} logo on the table ({whose}).\n'
                        'On the next screen, tap the video to start it.',
        'before_video_say': '"Earlier, the Moon team and the Sun team played this game '
                            'with these boxes, and each team opened some of the boxes. '
                            'Now we are going to watch a video from one of the teams '
                            'and see what they think: whether they think there are '
                            'more {pl_l} or more {pl_r}."\n'
                            '"Remember, you are part of the {own} team." [place the '
                            'logo]\n"Look, it\'s {whose}, the {team} team! And those '
                            'are the same boxes we have right here." [point to the '
                            'boxes]\n"Let\'s see what {whose} thinks."',
        'your_team': 'your team', 'other_team': 'the other team',
        'header': 'Round {t} of {n} · {color} · Step {s} of 2',
        'practice': 'Practice',
        'solution': "Let the child tap each row of boxes to open it. The child's "
                    "animal is always in most boxes; then tap Continue.",
        'solution_say': '"Let\'s see what was in the boxes! Tap on the boxes." [after '
                        'each row] "Look, there were more of your animal. You were '
                        'right!"',
        'skip': 'Skip',
        'video_missing': 'VIDEO MISSING',
        'check_head': 'Check question - attempt {k} of {m}',
        'ask': 'Ask: "{q}"',
        'correct': '(correct: {c})',
        'n_boxes': '{n} boxes',
        'if_right_belief_say': 'If right: "That\'s right, {whose} thinks there are '
                               'more {c}."',
        'if_right_number_say': 'If right: "That\'s right, they opened {n} boxes and '
                               'they were all {c}."',
        'dont_know': "Doesn't know",
        'said_self': 'Said it themselves', 'said_prompted': 'After asking',
        'reason_looked': 'looked in the boxes', 'reason_told': 'someone told them',
        'if_right_reason_say': 'If right: "That\'s right!"',
        'repeat': 'The answer was not correct. The video is shown again.',
        'repeat_say': '"Hm, let\'s watch the video one more time!"',
        'give_up': 'Still not correct after {m} attempts.\n\n',
        'summary': 'Place the extra toy {animal} on the {team} logo.\nThen put the '
                   'tablet in front of the child for the second rating.',
        'summary_say': '"So {whose} thinks there are more {c}, because {why}."',
        'why_numeric': 'they opened {n} boxes and they were all {c}',
        'why_strong': 'they looked in the boxes and saw more {c}',
        'why_weak': 'someone told them there are more {c}',
        'end': 'All {n} rounds done. Let the child choose a sticker to take home.'
               '\n\nData saved to:\n{file}',
        'sheets_ok': 'Google Sheets: all data sent.',
        'sheets_waiting': 'Google Sheets: {n} row(s) not sent yet (no internet?). '
                          'They are sent automatically the next time the task '
                          'runs with internet.',
        'end_say': '"Awesome! Now we are all done with our game today. You did such '
                   'a great job! For all of your hard work, you can choose any '
                   'sticker in here you want to take home!" [show the sticker box]',
    },
    'nl': {
        'tap': '(tik om verder te gaan)',
        'missing': 'LET OP: {n} mediabestanden ontbreken (er wordt een '
                   'vervangende tekst getoond):',
        'online_only': ' (alleen online in Google Drive)',
        'more': '... en nog {n}',
        'start': 'Deelnemer {p} - volgorde {o}\n\nTeamkeuze: laat het kind een '
                 'team kiezen en tik dan op het plaatje van het team van het kind.',
        'start_say': '"Bij het spelletje dat we gaan spelen zijn er twee teams: het '
                     'Maan-team en het Zon-team." [laat de teamplaatjes zien]\n'
                     '"Bij welk team wil jij vandaag horen?"',
        'chosen': 'Het kind heeft het {TEAM}-team gekozen. Geef het kind de sticker '
                  'en de pet van dit team en laat beide teams zien. Laat het kind dan '
                  'op het eigen team tikken (Verder = overslaan).',
        'tap_team_say': '"Kun je mij jouw team laten zien? Tik op jouw team!"',
        'chosen_say': '"Oké! Ik heb een paar dingen voor jou. Eerst heb ik een '
                      'speciale {team}-team sticker voor jou." [geef de sticker]\n'
                      '"Ik heb ook een speciale {team}-team pet voor jou." [geef de '
                      'pet]\n"Top, nu hoor jij bij het {team}-team!"',
        'show_teams_say': '[wijs naar het {own}-team] "Hier zijn een paar mensen die '
                          'in jouw team spelen, het {own}-team."\n[wijs naar het '
                          '{other}-team] "En hier zijn een paar mensen die in het '
                          'andere team spelen, het {other}-team."',
        'sticker_intro': 'Stickertaak\n\nLeg {n} stickers op tafel. Op het volgende '
                         'scherm verdeelt het kind ze over de twee teamleden; tik op '
                         'de bolletjes onder elke persoon om te noteren hoeveel '
                         'ieder krijgt.',
        'sticker_intro_say': '"Nu ga ik je een paar vragen stellen over de twee '
                             'teams. Ik heb hier wat stickers, laten we eens kijken '
                             'hoeveel ik er heb. Ik heb 1, 2, 3, 4, 5 stickers. Nu mag '
                             'jij mij vertellen hoeveel stickers ik aan elk van deze '
                             'twee {pl} moet geven."\n[volgend scherm, wijs naar elke '
                             'persoon]\n"Hoeveel van deze 5 stickers moet ik geven aan '
                             '{this_sg} van jouw team?"\n"Oké, en hoeveel stickers moet '
                             'ik geven aan {this_sg} van het andere team?"',
        'setup_first': 'Ronde 1 van {n} - introductie van het spel\n\nZet de {k} '
                       '{color} doosjes voor het kind neer en introduceer de twee '
                       'dieren ({pl_l} / {pl_r}).',
        'setup_first_say': '"Nu kunnen we het spelletje gaan spelen! Het spelletje '
                           'van vandaag gaat over een dierentuin. Kijk, hier is de '
                           'dierentuin! In de dierentuin wonen veel dieren, zoals '
                           '{pl_l} [houd {the_l} omhoog] en {pl_r} [houd {the_r} '
                           'omhoog]." [laat het kind beide dieren benoemen]\n'
                           '"Jouw taak is om uit te zoeken of er meer {pl_l} of meer '
                           '{pl_r} in de doosjes zitten. In elk van deze doosjes zit '
                           'één dier, {a_l} of {a_r}."',
        'setup': 'Ronde {t} van {n}\n\nRuim de doosjes, het logo en de '
                 'speelgoeddieren van de vorige ronde op. Zet de {k} {color} doosjes '
                 'voor het kind neer en introduceer de twee dieren ({pl_l} / {pl_r}).',
        'setup_say': '"Goed gedaan! Nu gaan we nog een keer spelen, met nieuwe '
                     'doosjes en nieuwe dieren. In deze doosjes zitten {pl_l} [houd '
                     '{the_l} omhoog] en {pl_r} [houd {the_r} omhoog]." [laat het kind '
                     'beide dieren benoemen]\n"In elk doosje zit {a_l} of {a_r}. Jouw '
                     'taak is om uit te zoeken of er meer {pl_l} of meer {pl_r} in '
                     'zitten."',
        'train_demo': 'Oefenen met de schaal (alleen in de eerste ronde): laat het '
                      'kind zien hoe de schaal werkt, geef dan de tablet aan het kind '
                      'en tik op Verder.',
        'train_demo_say': '"Straks vraag ik je wat jij denkt over de doosjes, en dan '
                          'kun je het mij vertellen met dit plaatje." [schuif zelf het '
                          'pijltje]\n"Als je straks echt denkt dat er meer {pl_l} in '
                          'de doosjes zitten, dan zet je je pijltje hier [helemaal aan '
                          'de {l}-kant]. Als je een beetje denkt dat er meer {pl_l} '
                          'zijn, dan zet je je pijltje ergens hier [midden van de '
                          '{l}-kant]." [hetzelfde voor de {pl_r}]\n"En als je het niet '
                          'weet, dan zet je je pijltje hier." [het midden, waar het ? '
                          'verschijnt]',
        'train_left': 'Oefening 1 van 3: het kind laat zien waar het pijltje komt als '
                      'het echt denkt dat er meer {pl_l} zijn. Verder controleert het '
                      'antwoord; is het fout, dan probeert het kind het opnieuw.',
        'train_left_say': '"Oké, als je straks echt zou denken dat er meer {pl_l} '
                          'zijn, waar zou je je pijltje dan zetten?"',
        'train_right': 'Oefening 2 van 3: ... als het echt denkt dat er meer {pl_r} '
                       'zijn.',
        'train_right_say': '"Goed zo, en als je echt zou denken dat er meer {pl_r} '
                           'zijn, waar zou je je pijltje dan zetten?"',
        'train_middle': 'Oefening 3 van 3: ... als het het niet weet.',
        'train_middle_say': '"Goed zo, en als je het niet zou weten, waar zou je je '
                            'pijltje dan zetten?"',
        'train_end_say': '"Super, ik pak de tablet zo weer terug."',
        'open_box': 'Leg de tablet aan de kant. Maak het meest linkse doosje open, '
                    'laat het dier zien en doe het doosje weer dicht.\nLeg dan de '
                    'tablet voor het kind neer.',
        'open_box_say': '"Ik ga één doosje voor je openmaken. Eens kijken wat erin '
                        'zit!" [maak het doosje open]\n"Kijk, in dit doosje zit een '
                        '...!"',
        'ask_binary_say': '"Oké, wat denk jij? Denk je dat er meer {pl_l} of meer '
                          '{pl_r} in de doosjes zitten?"',
        'ask_sure_say': '"Oké. En nu mag je mij vertellen hoe zeker je ervan bent dat '
                        'er meer {pl} zijn. Denk je echt dat er meer {pl} zijn, denk je '
                        'een beetje dat er meer {pl} zijn, of weet je niet zo goed of '
                        'er meer {pl} zijn?" [wijs de delen van de schaal aan]\nAls het '
                        'kind het pijltje niet verplaatst: "Waar wil je je pijltje '
                        'neerzetten?"',
        'ask_final_say': '"Net zei je dat je {how} er meer {pl} in de doosjes zitten. '
                         'Wat denk je nu? Wil je je pijltje verplaatsen of laat je het '
                         'staan waar het staat?"',
        'how': {'really': 'echt dacht dat', 'kind_of': 'een beetje dacht dat',
                'dont_know': 'niet wist of'},
        'before_video': 'Leg het logo van het {team}-team op tafel ({whose}).\n'
                        'Tik op het volgende scherm op het filmpje om het te starten.',
        'before_video_say': '"Eerder hebben het Maan-team en het Zon-team dit '
                            'spelletje met deze doosjes gespeeld, en elk team heeft '
                            'een paar doosjes opengemaakt. Nu gaan we een filmpje van '
                            'één van de teams bekijken en zien wat zij denken: of zij '
                            'denken dat er meer {pl_l} of meer {pl_r} in zitten."\n'
                            '"Weet je nog, jij hoort bij het {own}-team." [leg het '
                            'logo neer]\n"Kijk, het is {whose}, het {team}-team! En dat '
                            'zijn dezelfde doosjes als die hier op tafel staan." [wijs '
                            'naar de doosjes]\n"Eens kijken wat {whose} denkt."',
        'your_team': 'jouw team', 'other_team': 'het andere team',
        'header': 'Ronde {t} van {n} · {color} · Stap {s} van 2',
        'practice': 'Oefenen',
        'solution': 'Laat het kind op elke rij doosjes tikken om ze te openen. Het '
                    'dier van het kind zit altijd in de meeste doosjes; tik dan op '
                    'Verder.',
        'solution_say': '"Laten we kijken wat er in de doosjes zat! Tik op de '
                        'doosjes." [na elke rij] "Kijk, er waren meer van jouw dier. '
                        'Je had gelijk!"',
        'skip': 'Overslaan',
        'video_missing': 'FILMPJE ONTBREEKT',
        'check_head': 'Controlevraag - poging {k} van {m}',
        'ask': 'Vraag: "{q}"',
        'correct': '(juist: {c})',
        'n_boxes': '{n} doosjes',
        'if_right_belief_say': 'Als goed: "Dat klopt, {whose} denkt dat er meer {c} '
                               'zijn."',
        'if_right_number_say': 'Als goed: "Dat klopt, ze hebben {n} doosjes '
                               'opengemaakt en daar zaten allemaal {c} in."',
        'dont_know': 'Weet het niet',
        'said_self': 'Zelf gezegd', 'said_prompted': 'Na doorvragen',
        'reason_looked': 'in de doosjes gekeken', 'reason_told': 'iemand heeft het verteld',
        'if_right_reason_say': 'Als goed: "Dat klopt!"',
        'repeat': 'Het antwoord was niet juist. Het filmpje wordt nog een keer '
                  'getoond.',
        'repeat_say': '"Hm, laten we het filmpje nog een keer bekijken!"',
        'give_up': 'Na {m} pogingen nog steeds niet juist.\n\n',
        'summary': 'Zet het extra speelgoeddier ({animal}) op het logo van het '
                   '{team}-team.\nLeg dan de tablet voor het kind neer voor de tweede '
                   'beoordeling.',
        'summary_say': '"Dus {whose} denkt dat er meer {c} zijn, omdat {why}."',
        'why_numeric': 'ze {n} doosjes hebben opengemaakt en daar allemaal {c} in '
                       'zaten',
        'why_strong': 'ze in de doosjes hebben gekeken en meer {c} hebben gezien',
        'why_weak': 'iemand hun heeft verteld dat er meer {c} in zitten',
        'end': 'Alle {n} rondes zijn klaar. Laat het kind een sticker uitkiezen om '
               'mee naar huis te nemen.\n\nData opgeslagen in:\n{file}',
        'sheets_ok': 'Google Sheets: alle data verstuurd.',
        'sheets_waiting': 'Google Sheets: {n} rij(en) nog niet verstuurd (geen '
                          'internet?). Ze worden automatisch verstuurd zodra de '
                          'taak weer met internet draait.',
        'end_say': '"Super! We zijn klaar met het spelletje. Wat heb je het goed '
                   'gedaan! Omdat je zo goed je best hebt gedaan, mag je een sticker '
                   'uitkiezen om mee naar huis te nemen!" [laat de stickerdoos zien]',
    },
}
COLOR_NAMES = {'en': {'blue': 'blue', 'red': 'red', 'green': 'green', 'yellow': 'yellow'},
               'nl': {'blue': 'blauw', 'red': 'rood', 'green': 'groen', 'yellow': 'geel'}}
NEUTER_NL = {'pig'}  # 'het varken'; all other animals take 'de'
COLOR_ADJ_NL = {'blue': 'blauwe', 'red': 'rode', 'green': 'groene', 'yellow': 'gele'}

TEAM_NAMES = {'en': {'moon': 'Moon', 'sun': 'Sun'},
              'nl': {'moon': 'Maan', 'sun': 'Zon'}}
PLURALS = {'en': {'elephant': 'elephants', 'lion': 'lions', 'dog': 'dogs',
                  'cat': 'cats', 'rhino': 'rhinos', 'turtle': 'turtles',
                  'cow': 'cows', 'pig': 'pigs'},
           'nl': {'elephant': 'olifanten', 'lion': 'leeuwen', 'dog': 'honden',
                  'cat': 'katten', 'rhino': 'neushoorns', 'turtle': 'schildpadden',
                  'cow': 'koeien', 'pig': 'varkens'}}
MAX_CHECKS = 3  # check-question attempts per trial: the video is shown at most 3 times (2 replays)
CHECK_FIELDS = ['belief', 'belief_correct', 'reason', 'reason_correct',
                'reason_prompted', 'passed', 'rt']
BOXES_OPENED = {'strong': 4, 'weak': 2}  # boxes the team opened in the numeric videos
NUMBER_WORDS = {'en': {2: 'two', 4: 'four'}, 'nl': {2: 'twee', 4: 'vier'}}
MEMBER_WORDS = {'en': {'female': ('this girl', 'girls'), 'male': ('this boy', 'boys')},
                'nl': {'female': ('dit meisje', 'meisjes'), 'male': ('deze jongen', 'jongens')}}
REALLY = 0.5  # first answers this far from the middle are read back as "really"

# Layout of the scale and video screens follows the HTML versions in
# code_caro/. Their sizes in CSS pixels are converted for a 1366 x 1024
# (iPad, landscape) screen: 1 px = 1/1024 of the screen height.
PX = 1 / 1024
FONT = 'Arial'

# Balanced Latin square for 4 items (each item once per position and
# each item directly follows every other item once). For the conditions the
# rows are orders A-D.
LATIN = [[0, 1, 3, 2],
         [1, 2, 0, 3],
         [2, 3, 1, 0],
         [3, 0, 2, 1]]
ORDER_NAMES = 'ABCD'
N_LISTS = 32


VIDEO_PIXELS = (1280, 720)  # frames are scaled to this before drawing (speed)


def video_path(box, team, quality, claimed_animal, lang, reason_set):
    """Video file named as in video_stimuli/Study_1&2_video_labels.xlsx.
    reason_set 'numeric' -> videos x.1 (en) / x.2 (nl),
               'quality' -> videos x.3 (en) / x.4 (nl)."""
    row = (BOX_ORDER.index(box) * 8 + TEAMS.index(team) * 4
           + BOXES[box].index(claimed_animal) * 2 + QUALITIES.index(quality) + 1)
    version = {'numeric': 1, 'quality': 3}[reason_set] + (lang == 'nl')
    words = [DUTCH[w] if lang == 'nl' else w
             for w in (box, team, claimed_animal, quality)]
    return VIDEO_DIR / f"{row}.{version}-{'-'.join(w.capitalize() for w in words)}.mp4"


# --------------------------------------------------------------------------
# Session info and counterbalancing
# --------------------------------------------------------------------------
def session_dialog():
    """Start dialog. Returns the info dict, or None if cancelled."""
    from PyQt6 import QtWidgets
    from psychopy.gui import qtgui
    qtgui.ensureQtApp()

    dlg = QtWidgets.QDialog()
    dlg.setWindowTitle('Study 1')
    dlg.setMinimumWidth(420)
    form = QtWidgets.QFormLayout(dlg)

    language = QtWidgets.QComboBox()
    language.addItems(['Nederlands', 'English'])
    reason_set = QtWidgets.QComboBox()
    reason_set.addItems(['numeric', 'quality'])
    participant = QtWidgets.QLineEdit()
    age = QtWidgets.QComboBox()
    age.addItems(AGES)
    age.setPlaceholderText('choose')
    age.setCurrentIndex(-1)  # no default, so the age is never left at a wrong value
    gender = QtWidgets.QComboBox()
    gender.addItems(['', 'female', 'male', 'other'])

    form.addRow('language', language)
    form.addRow('reasons (video version)', reason_set)
    form.addRow('participant', participant)
    form.addRow('age', age)
    form.addRow('gender', gender)

    buttons = QtWidgets.QDialogButtonBox(
        QtWidgets.QDialogButtonBox.StandardButton.Ok
        | QtWidgets.QDialogButtonBox.StandardButton.Cancel)
    form.addRow(buttons)
    buttons.accepted.connect(dlg.accept)
    buttons.rejected.connect(dlg.reject)
    ok = buttons.button(QtWidgets.QDialogButtonBox.StandardButton.Ok)
    ok.setEnabled(False)  # until an age is chosen
    age.currentIndexChanged.connect(lambda i: ok.setEnabled(i >= 0))

    dlg.raise_()
    dlg.activateWindow()
    if not dlg.exec():
        return None
    return {'language': ['nl', 'en'][language.currentIndex()],
            'reason_set': reason_set.currentText(),
            'participant': participant.text().strip(),
            'age': age.currentText(),
            'gender': gender.currentText()}


def completed_lists(age):
    """cb_list of every completed session (all trials) of this age in data/.
    Participant IDs starting with 'test' are ignored."""
    lists = []
    for path in DATA_DIR.glob('*.csv'):
        try:
            with open(path, newline='', encoding='utf-8') as f:
                rows = list(csv.DictReader(f))
            first = rows[0]
            row_age = first['age'] if 'age' in first else first['age_group']  # older files
            if (len(rows) == len(CONDITIONS) and row_age == age
                    and not first['participant'].lower().startswith('test')):
                lists.append(int(first['cb_list']))
        except (OSError, IndexError, KeyError, ValueError):
            continue
    return lists


def assign_list(age):
    """Least used condition order (A-D) at this age and, within that order,
    the least used list (box order x animal sides); ties at random."""
    done = completed_lists(age)

    def usage(cb):
        n_order = sum((d - 1) % 4 == (cb - 1) % 4 for d in done)
        return n_order, done.count(cb), random.random()

    return min(range(1, N_LISTS + 1), key=usage)


info = session_dialog()
if info is None:
    core.quit()

cb_list = assign_list(info['age'])
idx = cb_list - 1
info['order'] = ORDER_NAMES[idx % 4]
info['cb_list'] = cb_list
info['date'] = data.getDateStr()
lang = info['language']
reason_set = info['reason_set']
TXT = TEXT[lang]
EXP = EXP_TEXT[lang]

condition_order = [CONDITIONS[i] for i in LATIN[idx % 4]]
box_order = [BOX_ORDER[i] for i in LATIN[(idx // 4) % 4]]
swap_sides = idx >= 16

trials = []
for n, (cond, box) in enumerate(zip(condition_order, box_order), start=1):
    pair = BOXES[box]
    left, right = (pair[1], pair[0]) if swap_sides else pair
    group, quality = cond.split('_')
    trials.append({'trial': n, 'condition': cond, 'group_type': group,
                   'reason_quality': quality, 'box_color': box,
                   'animal_left': left, 'animal_right': right})

DATA_DIR.mkdir(exist_ok=True)
data_file = DATA_DIR / f"{info['participant']}_{info['date']}.csv"
sheets_sync.start_retrying()  # also sends rows left over from earlier sessions

# --------------------------------------------------------------------------
# Window, input and helpers
# --------------------------------------------------------------------------
win = visual.Window(fullscr=FULLSCREEN, units='height', color=BG_COLOR,
                    allowGUI=False)
mouse = event.Mouse(win=win, visible=SHOW_CURSOR)  # touches arrive as mouse clicks
HALF_W = win.size[0] / win.size[1] / 2  # half screen width in 'height' units


def quit_experiment():
    mouse.setVisible(True)
    win.close()
    core.quit()


def check_quit():
    """ESC quits; 'm' shows/hides the mouse cursor."""
    keys = event.getKeys(['escape', 'm'])
    if 'escape' in keys:
        quit_experiment()
    if 'm' in keys:
        mouse.setVisible(not mouse.visible)


def wait_release():
    """Wait until the finger is lifted, so one tap is not counted twice."""
    while mouse.getPressed()[0]:
        check_quit()
        core.wait(0.01)


# (i) icon in the top-left corner: shows/hides what the experimenter can say.
# The setting is kept for the following screens.
help_shown = {'on': SHOW_HELP}
HELP_POS = (-HALF_W + 0.04, 0.46)
help_ring = visual.Circle(win, radius=0.022, pos=HELP_POS, lineColor=EXP_COLOR,
                          lineWidth=2)
help_label = visual.TextStim(win, text='i', pos=HELP_POS, height=0.03, bold=True,
                             font=FONT)


def say_text(text, pos, height=0.026, anchor='top'):
    """Experimenter's script text (only drawn while help is on), or None."""
    if not text:
        return None
    return visual.TextStim(win, text=text, pos=pos, height=height, color=EXP_COLOR,
                           italic=True, font=FONT, anchorVert=anchor,
                           wrapWidth=2 * HALF_W * 0.9)


def help_tapped(xy):
    """If the tap is on the (i) icon, switch the script text on/off."""
    if math.dist(xy, HELP_POS) < 0.05:  # a bit larger than the icon, for fingers
        help_shown['on'] = not help_shown['on']
        wait_release()
        return True
    return False


def draw_help(say=None):
    """The (i) icon (filled while help is on) and, if on, the script text."""
    on = help_shown['on']
    help_ring.fillColor = EXP_COLOR if on else BG_COLOR
    help_label.color = BG_COLOR if on else EXP_COLOR
    help_ring.draw()
    help_label.draw()
    if on and say is not None:
        say.draw()


def load_image(path, pos, max_size):
    """Image scaled to fit max_size, or a text placeholder if the file is missing."""
    if path.exists():
        img = visual.ImageStim(win, image=str(path), pos=pos)
        w, h = img.size
        scale = max_size / max(w, h)
        img.size = (w * scale, h * scale)
        return img
    return visual.TextStim(win, text=f'[{path.stem}]', pos=pos,
                           height=max_size * 0.2, color='black')


def animal_name(animal):
    return (DUTCH[animal] if lang == 'nl' else animal).capitalize()


def the_animal(animal):
    """'the elephant' / 'de olifant', 'het varken'."""
    name = animal_name(animal).lower()
    if lang == 'nl':
        return ('het ' if animal in NEUTER_NL else 'de ') + name
    return 'the ' + name


def with_article(animal):
    """'an elephant' / 'een olifant'."""
    name = animal_name(animal).lower()
    if lang == 'nl':
        return 'een ' + name
    return ('an ' if name[0] in 'aeiou' else 'a ') + name


def rounded_rect(size, pos, color, radius):
    """Filled rectangle with rounded corners."""
    w, h = size
    r = min(radius, w / 2, h / 2)
    verts = []
    for cx, cy, start in ((w / 2 - r, h / 2 - r, 0), (-w / 2 + r, h / 2 - r, 90),
                          (-w / 2 + r, -h / 2 + r, 180), (w / 2 - r, -h / 2 + r, 270)):
        for a in range(start, start + 91, 15):
            verts.append((cx + r * math.cos(math.radians(a)),
                          cy + r * math.sin(math.radians(a))))
    return visual.ShapeStim(win, vertices=verts, pos=pos, fillColor=color,
                            lineColor=None)


def corner_masks(size, pos, radius, color):
    """Four shapes that cover the corners outside a rounded rectangle, used to
    round the corners of the video."""
    w, h = size
    masks = []
    for sx, sy in ((1, 1), (-1, 1), (-1, -1), (1, -1)):
        cx, cy = sx * (w / 2 - radius), sy * (h / 2 - radius)
        verts = [(sx * w / 2, sy * h / 2)]
        for a in range(0, 91, 10):
            verts.append((cx + sx * radius * math.cos(math.radians(a)),
                          cy + sy * radius * math.sin(math.radians(a))))
        masks.append(visual.ShapeStim(win, vertices=verts, pos=pos,
                                      fillColor=color, lineColor=None))
    return masks


class Button:
    """Rounded button as in code_caro: black with white 21 px text, 16/34 px
    padding, grey and not clickable while `enabled` is False."""

    def __init__(self, text, pos, color='#111111', width=None):
        self.color = color
        self.enabled = True
        if width is None:
            width = (len(text) * 0.5 * 21 + 68) * PX  # Arial: ~0.5 em per letter
        self.box = rounded_rect((width, 56 * PX), pos, color, radius=14 * PX)
        self.label = visual.TextStim(win, text=text, pos=pos, height=21 * PX,
                                     color='white', font=FONT)

    def draw(self):
        self.box.fillColor = self.color if self.enabled else '#aaaaaa'
        self.box.draw()
        self.label.draw()

    def contains(self, xy):
        return self.enabled and self.box.contains(xy)


def box_row(color, n=N_BOXES, y=-0.2, n_open=1, arrow=True, width=None, x0=0.0):
    """A row of n boxes (lid, body and two clasps) in the box colour, centred
    at (x0, y). The first n_open boxes (from the left) are drawn open; with
    `arrow` an arrow points at the first one (the box the experimenter
    opens). `width` is the width of the whole row (default: up to the screen
    width, boxes at most 0.1 wide)."""
    if width is None:
        width = min(n * 0.1 + (n - 1) * 0.02, 2 * HALF_W * 0.92)
    w = width / (n + (n - 1) * 0.2)
    gap = 0.2 * w
    h = w * 0.62
    line = 1.5 if w > 0.06 else 1
    stims = []
    for i in range(n):
        x = x0 + (i - (n - 1) / 2) * (w + gap)
        stims.append(visual.Rect(win, width=w, height=h, pos=(x, y - h * 0.1),
                                 fillColor=color, lineColor='#333333', lineWidth=line))
        if i < n_open:
            # open: dark opening, lid swung up around its right back corner
            stims.append(visual.Rect(win, width=w * 0.94, height=h * 0.1,
                                     pos=(x, y + h * 0.33), fillColor='#1a1a1a',
                                     lineColor=None))
            angle = math.radians(-40)  # clockwise: the lid's free end goes up
            hinge = (x + w * 0.52, y + h * 0.4)
            dx, dy = -w * 0.52, h * 0.125  # lid centre seen from the hinge
            stims.append(visual.Rect(
                win, width=w * 1.04, height=h * 0.25, ori=40, fillColor=color,
                lineColor='#333333', lineWidth=line,
                pos=(hinge[0] + dx * math.cos(angle) - dy * math.sin(angle),
                     hinge[1] + dx * math.sin(angle) + dy * math.cos(angle))))
        if i == 0 and arrow:  # arrow pointing down at the open box
            top, tip = y + h * 3.1, y + h * 2.0  # above the open lid
            stims.append(visual.ShapeStim(
                win, fillColor='#555555', lineColor=None,
                vertices=[(x - w * 0.08, top), (x + w * 0.08, top),
                          (x + w * 0.08, tip + w * 0.18), (x + w * 0.22, tip + w * 0.18),
                          (x, tip), (x - w * 0.22, tip + w * 0.18),
                          (x - w * 0.08, tip + w * 0.18)]))
        if i >= n_open:
            stims.append(visual.Rect(win, width=w * 1.04, height=h * 0.25,
                                     pos=(x, y + h * 0.4), fillColor=color,
                                     lineColor='#333333', lineWidth=line))
        for side in (-1, 1):
            stims.append(visual.Rect(win, width=w * 0.12, height=h * 0.14,
                                     pos=(x + side * w * 0.3, y + h * 0.2),
                                     fillColor='#c9a227', lineColor=None))
    return stims


def experimenter_screen(text, color=None, say=None):
    """Instruction screen for the experimenter; tap anywhere (except the (i)
    icon) to continue. `say` is the script text shown below the instruction
    while help is on. With `color`, a row of boxes in that colour is shown."""
    msg = visual.TextStim(win, text=text, height=0.034, color=EXP_COLOR,
                          italic=True, font=FONT, wrapWidth=2 * HALF_W * 0.85,
                          pos=(0, 0.4), anchorVert='top')
    script = say_text(say, (0, 0.16))
    hint = visual.TextStim(win, text=EXP['tap'], height=0.026, color=EXP_COLOR,
                           italic=True, font=FONT, pos=(0, -0.44))
    boxes = box_row(color, y=-0.33) if color else []
    wait_release()
    while True:
        check_quit()
        msg.draw()
        hint.draw()
        for stim in boxes:
            stim.draw()
        draw_help(script)
        win.flip()
        if mouse.getPressed()[0]:
            if help_tapped(mouse.getPos()):
                continue
            wait_release()
            return


# --------------------------------------------------------------------------
# Group choice
# --------------------------------------------------------------------------
def play_sound(path):
    """Start a sound; returns the player (close it when the sound is over)."""
    return MediaPlayer(str(path), ff_opts={'vn': True}) if path.exists() else None


def celebrate(keep, fade, pos, size, pulse=None, glow=True, dur=1.8):
    """Happy sound while the area at pos/size blinks (gold/green frame, with
    `glow` a gold glow behind it) and the image `pulse` grows and shrinks;
    the stims in `fade` are dimmed. `keep` are drawn normally."""
    glow_rect = rounded_rect((size[0] + 0.12, size[1] + 0.12), pos, '#ffd54f',
                             radius=0.04) if glow else None
    frame = visual.Rect(win, width=size[0] + 0.04, height=size[1] + 0.04, pos=pos,
                        lineWidth=12, fillColor=None)
    base_size = pulse.size.copy() if isinstance(pulse, visual.ImageStim) else None
    for stim in fade:
        stim.opacity = 0.25
    player = play_sound(SOUND_TEAM)
    try:
        clock = core.Clock()
        while clock.getTime() < dur:
            check_quit()
            t = clock.getTime()
            on = int(t / 0.15) % 2 == 0
            for stim in fade:
                stim.draw()
            if glow_rect:
                glow_rect.opacity = 0.7 if on else 0.15
                glow_rect.draw()
            if base_size is not None:
                pulse.size = base_size * (1 + 0.08 * abs(math.sin(t * math.pi / 0.3)))
            for stim in keep:
                stim.draw()
            frame.lineColor = '#f5b700' if on else '#2e7d32'
            frame.draw()
            win.flip()
    finally:
        if player:
            player.close_player()
        for stim in fade:
            stim.opacity = 1
        if base_size is not None:
            pulse.size = base_size


def choose_group():
    sides = TEAMS[:] if random.random() < 0.5 else TEAMS[::-1]
    x = HALF_W * 0.5
    options = {}
    for team, xpos in zip(sides, (-x, x)):
        frame = visual.Rect(win, width=0.5, height=0.5, pos=(xpos, 0),
                            lineColor='grey', lineWidth=4, fillColor=None)
        pic = load_image(STIM / 'groups' / f'{team}.png', (xpos, 0), 0.45)
        options[team] = (frame, pic)

    wait_release()
    clock = core.Clock()
    while True:
        check_quit()
        for frame, pic in options.values():
            pic.draw()
            frame.draw()
        win.flip()
        if mouse.getPressed()[0]:
            for team, (frame, pic) in options.items():
                if frame.contains(mouse):
                    rt = clock.getTime()
                    other = [stim for t, pair in options.items() if t != team for stim in pair]
                    celebrate([pic], other, frame.pos, (0.5, 0.5), pulse=pic)
                    wait_release()
                    return team, sides[0], rt


def show_teams(own):
    """Both teams (stills from the videos, stimuli/teams/), each with its
    team picture, one above the other in random order, right after the team
    choice. On this one screen the experimenter gives the child the sticker
    and hat of their team and points to both teams; then the child taps their
    own team: it blinks with the happy sound and the task goes on. A tap on
    the other team plays the 'wrong' sound and shakes that team; the child
    can try again (the experimenter can skip with Continue, grey, bottom
    right). Returns (team shown on top, data of the team tap; team_tap_rt is
    counted from the start of the screen)."""
    order = TEAMS[:] if random.random() < 0.5 else TEAMS[::-1]
    other = [team for team in TEAMS if team != own][0]
    names = {'own': TEAM_NAMES[lang][own], 'other': TEAM_NAMES[lang][other]}
    icon = 0.13
    w = min(0.72, 2 * HALF_W - icon - 0.2)
    h = w / 2.6
    row_w = icon + 0.03 + w
    left_edge = -row_w / 2
    title = visual.TextStim(
        win, text=TXT['teams'].format(first=TEAM_NAMES[lang][order[0]],
                                      second=TEAM_NAMES[lang][order[1]]),
        pos=(0, 0.45), height=34 * PX, color='#111111', bold=True, font=FONT,
        wrapWidth=2 * HALF_W * 0.9)
    instruction = visual.TextStim(
        win, text=EXP['chosen'].format(TEAM=names['own'].upper()), pos=(0, 0.385),
        height=0.024, color=EXP_COLOR, italic=True, font=FONT,
        wrapWidth=2 * HALF_W * 0.85)
    say_pos = (-0.08, -0.3)
    script = say_text(EXP['chosen_say'].format(team=names['own']) + '\n'
                      + EXP['show_teams_say'].format(**names) + '\n'
                      + EXP['tap_team_say'], say_pos, height=0.021)
    rows = {}
    for team, y in zip(order, (0.19, -0.13)):
        photo_pos = (left_edge + icon + 0.03 + w / 2, y)
        stims = [load_image(STIM / 'groups' / f'{team}.png', (left_edge + icon / 2, y), icon),
                 load_image(STIM / 'teams' / f'{team}.png', photo_pos, w)]
        stims += corner_masks((w, h), photo_pos, 12 * PX, BG_COLOR)
        rows[team] = {'stims': stims, 'pos': (0, y), 'icon': stims[0]}
    done = Button(TXT['continue'], (HALF_W - 0.13, -0.45), color=EXP_BUTTON_COLOR)

    def draw_rows(shaking=None, dx=0.0):
        for team, row in rows.items():
            shift = dx if team == shaking else 0
            for stim in row['stims']:
                stim.pos = (stim.pos[0] + shift, stim.pos[1])
                stim.draw()
                stim.pos = (stim.pos[0] - shift, stim.pos[1])

    result = {'team_tap_first': '', 'team_tap_n_wrong': 0, 'team_tap_rt': ''}
    wait_release()
    clock = core.Clock()
    while True:
        check_quit()
        if mouse.getPressed()[0]:
            xy = mouse.getPos()
            if help_tapped(xy):
                continue
            if done.contains(xy):  # skipped by the experimenter
                wait_release()
                return order[0], result
            tapped = [team for team, row in rows.items()
                      if abs(xy[0]) < row_w / 2 + 0.02 and abs(xy[1] - row['pos'][1]) < h / 2 + 0.02]
            if tapped:
                team = tapped[0]
                if not result['team_tap_first']:
                    result['team_tap_first'] = 'own' if team == own else 'other'
                if team == own:
                    result['team_tap_rt'] = round(clock.getTime(), 3)
                    celebrate(rows[own]['stims'], rows[other]['stims'], rows[own]['pos'],
                              (row_w, h), pulse=rows[own]['icon'], glow=False)
                    wait_release()
                    return order[0], result
                # wrong team: 'oops' sound and a little shake
                result['team_tap_n_wrong'] += 1
                player = play_sound(SOUND_WRONG)
                shake = core.Clock()
                while shake.getTime() < 0.6:
                    title.draw()
                    instruction.draw()
                    draw_rows(team, 0.015 * math.sin(shake.getTime() * 40))
                    done.draw()
                    win.flip()
                if player:
                    player.close_player()
                wait_release()
        title.draw()
        instruction.draw()
        draw_rows()
        done.draw()
        draw_help(script)
        win.flip()


# --------------------------------------------------------------------------
# Sticker distribution
# --------------------------------------------------------------------------
def sticker_task(member_gender):
    """One member of each team (photos in stimuli/members/, same gender as
    the child) with N_STICKERS dots under each photo. The experimenter taps
    the dots to record how many stickers the child gave to each person:
    tapping dot k sets the count to k, tapping the highest filled dot again
    lowers it by one (so 0 is possible). Both together can't exceed
    N_STICKERS. Returns ({team: n stickers}, team shown left, rt)."""
    sides = TEAMS[:] if random.random() < 0.5 else TEAMS[::-1]
    photo = min(0.42, HALF_W * 0.62)
    x = min(0.3, HALF_W * 0.45)
    y_photo, y_dots = 0.07, 0.07 - photo / 2 - 0.06
    spacing, radius = 0.075, 0.026
    question = visual.TextStim(win, text=TXT['stickers'], pos=(0, 0.4),
                               height=42 * PX, color='#111111', bold=True,
                               font=FONT, wrapWidth=2 * HALF_W * 0.9)
    total_text = visual.TextStim(win, text='', pos=(0, y_dots - 0.07),
                                 height=18 * PX, color='#777777', font=FONT)
    done = Button(TXT['continue'], (0, -0.38))
    people, dots = {}, {}
    for team, xpos in zip(sides, (-x, x)):
        people[team] = [load_image(STIM / 'members' / f'{team}_{member_gender}.png',
                                   (xpos, y_photo), photo)]
        people[team] += corner_masks((photo, photo), (xpos, y_photo), 12 * PX, BG_COLOR)
        dots[team] = [visual.Circle(win, radius=radius, lineWidth=3,
                                    pos=(xpos + (k - (N_STICKERS - 1) / 2) * spacing, y_dots),
                                    lineColor='#777777', fillColor='white')
                      for k in range(N_STICKERS)]
    count = {team: 0 for team in TEAMS}

    wait_release()
    clock = core.Clock()
    while True:
        check_quit()
        if mouse.getPressed()[0]:
            xy = mouse.getPos()
            if done.contains(xy):
                rt = clock.getTime()
                wait_release()
                return count, sides[0], rt
            for team in TEAMS:
                for k, dot in enumerate(dots[team], start=1):
                    if dot.contains(xy):
                        new = k - 1 if count[team] == k else k
                        if new + sum(count.values()) - count[team] <= N_STICKERS:
                            count[team] = new
            wait_release()

        question.draw()
        for team in TEAMS:
            for stim in people[team]:
                stim.draw()
            for k, dot in enumerate(dots[team], start=1):
                dot.fillColor = '#f5b800' if k <= count[team] else 'white'
                dot.lineColor = '#111111' if k <= count[team] else '#777777'
                dot.draw()
        total_text.text = f'{sum(count.values())} / {N_STICKERS}'
        total_text.draw()
        done.draw()
        win.flip()


# --------------------------------------------------------------------------
# Belief scale (design taken from code_caro/confidence_scale_*.txt)
# --------------------------------------------------------------------------
def hex_rgb(color):
    return np.array([int(color[i:i + 2], 16) for i in (1, 3, 5)]) / 255


def scale_texture(color_left, color_right, w, h):
    """w x h pixel image of the scale bar: left colour -> white -> right colour,
    rounded #555 border; pixels outside the rounded corners are white."""
    x = (np.arange(w) + 0.5) / w
    t = np.abs(x - 0.5) * 2  # 0 in the middle, 1 at the ends
    end = np.where((x < 0.5)[:, None], hex_rgb(color_left), hex_rgb(color_right))
    img = np.repeat((1 - t[:, None] * (1 - end))[None], h, axis=0)

    # signed distance (pixels) to the rounded outline: < 0 inside, > 0 outside
    r = h * 0.3  # corner radius (12 px of a 40 px bar)
    qx = np.abs(np.arange(w) + 0.5 - w / 2)[None, :] - w / 2 + r
    qy = np.abs(np.arange(h) + 0.5 - h / 2)[:, None] - h / 2 + r
    dist = (np.hypot(np.maximum(qx, 0), np.maximum(qy, 0))
            + np.minimum(np.maximum(qx, qy), 0) - r)
    border = np.clip(dist + h * 0.05 + 0.5, 0, 1)[..., None]  # 2 px of 40 px
    img = img * (1 - border) + hex_rgb('#555555') * border
    outside = np.clip(dist + 0.5, 0, 1)[..., None]
    return img * (1 - outside) + outside


def rating_scale(animal_left, animal_right, header, button_text, first=None,
                 binary=False, question=None, say=None, thought=None, check=None,
                 follow=False):
    """Scale screen as in code_caro/confidence_scale_GOEDE_KLEUREN... (with
    the question from trial1_test_text and larger animals): a small header,
    the question, an animal (with its name) above each end, and a bar shading
    from the left animal's colour through white to the right animal's colour.
    The handle appears where the child touches and can be dragged; the button
    is grey until then.

    With `binary`, the screen first shows only the question and the two
    animals; when the child taps one, the bar appears (animals stay in place)
    and the question changes to "How sure are you?". Only the chosen half of
    the bar (up to the middle) can then be used; the other animal and its
    half are faded (UNCHOSEN_OPACITY).

    `first` (-1..1) is the first answer: on the second rating the handle
    starts there, on a grey line labelled "your first answer"; the label
    disappears once the child moves the handle. A "?" under the handle marks
    the exact middle. Returns a dict: pos (-1..1), rt (button), first_touch_rt,
    n_touches, and with `binary` also choice (animal) and choice_rt.

    `question` replaces the child's question ('' = none, for the practice);
    `thought` (an animal, or 'dont_know') shows a thinking child in the
    middle with that animal (or a "?") in the thought bubble (practice);
    with `follow` the bubble shows the animal the marker points to, larger
    the closer it is to that end (see ThoughtBubble);
    `check` (practice): a function pos -> right?; Continue then gives
    feedback (chime / 'oops') and only goes on once the answer is right
    (the experimenter can skip after PRACTICE_SKIP_AFTER wrong answers); the
    result then also has attempts, correct and first_pos;
    `say` is the experimenter's script text, shown under the button while
    help is on (with `binary` it changes to the "how sure" text after the
    choice).
    """
    task_w = min(1100 * PX, 0.92 * 2 * HALF_W)
    half_len = 1.05 * task_w / 2  # the bar is 105 % of the animal row
    bar_h = 40 * PX
    img_size = 0.16  # animals
    # vertical layout: header, question, animals, names, bar, button
    y_head, y_question, y_animal, y_name, y = 0.44, 0.35, 0.14, 0.035, -0.07
    y_button = -0.25
    animal_x = task_w / 2 - img_size / 2
    px = win.size[1]  # pixels per 'height' unit, for the bar texture

    head = visual.TextStim(win, text=header, pos=(0, y_head), height=16 * PX,
                           color=EXP_COLOR, italic=True, font=FONT,
                           wrapWidth=2 * HALF_W * 0.8)
    script = say_text(say, (0, y_button - 0.06))
    bubble = ThoughtBubble(animal_left, animal_right) if thought or follow else None
    question = visual.TextStim(win, text=TXT['question'] if question is None else question,
                               pos=(0, y_question),
                               height=42 * PX, color='#111111', bold=True,
                               font=FONT, wrapWidth=2 * HALF_W * 0.9)
    pid = visual.TextStim(win, text=info['participant'], height=12 * PX,
                          pos=(HALF_W - 16 * PX, 0.5 - 18 * PX),
                          anchorHoriz='right', alignText='right',
                          color=EXP_COLOR, italic=True, font=FONT)
    img_l = load_image(STIM / 'animals' / f'{animal_left}.png', (-animal_x, y_animal), img_size)
    img_r = load_image(STIM / 'animals' / f'{animal_right}.png', (animal_x, y_animal), img_size)
    name_l = visual.TextStim(win, text=animal_name(animal_left), pos=(-animal_x, y_name),
                             height=24 * PX, color='#333333', font=FONT)
    name_r = visual.TextStim(win, text=animal_name(animal_right), pos=(animal_x, y_name),
                             height=24 * PX, color='#333333', font=FONT)
    bar = visual.ImageStim(
        win, image=scale_texture(ANIMAL_COLORS[animal_left], ANIMAL_COLORS[animal_right],
                                 int(2 * half_len * px), int(bar_h * px)),
        size=(2 * half_len, bar_h), pos=(0, y))
    first_marker = first_label = None
    if first is not None:
        first_marker = visual.Rect(win, width=3 * PX, height=52 * PX,
                                   pos=(first * half_len, y),
                                   fillColor='#777777', lineColor=None)
        label_y = y - (95 if first == 0 else 40) * PX  # below the "?" if in the middle
        first_label = visual.TextStim(win, text=TXT['first_answer'],
                                      pos=(first * half_len, label_y),
                                      height=14 * PX, color='#777777', font=FONT)
    middle_mark = visual.TextStim(win, text='?', pos=(0, y - 58 * PX), height=36 * PX,
                                  color=EXP_COLOR, bold=True, font=FONT)
    radius = 22.5 * PX  # 45 px handle with a 5 px black ring
    handle_shadow = visual.Circle(win, radius=radius + 2 * PX, fillColor='black',
                                  lineColor=None, opacity=0.12)
    handle_ring = visual.Circle(win, radius=radius, fillColor='#111111', lineColor=None)
    handle_fill = visual.Circle(win, radius=radius - 5 * PX,
                                fillColor='white', lineColor=None)
    done = Button(button_text, (0, y_button))

    result = {}
    if binary:
        # Binary belief: tap an animal (picture or name)
        def tapped_animal(mx, my):
            if not y_name - 0.04 < my < y_animal + img_size / 2:
                return None
            for animal, x in ((animal_left, -animal_x), (animal_right, animal_x)):
                if abs(mx - x) < img_size / 2 + 0.02:
                    return animal
            return None

        wait_release()
        clock = core.Clock()
        while result.get('choice') is None:
            check_quit()
            if mouse.getPressed()[0] and not help_tapped(mouse.getPos()):
                result['choice'] = tapped_animal(*mouse.getPos())
            for stim in (head, pid, question, img_l, img_r, name_l, name_r):
                stim.draw()
            draw_help(script)
            win.flip()
        result['choice_rt'] = clock.getTime()
        question.text = TXT['sure']
        script = say_text(EXP['ask_sure_say'].format(pl=PLURALS[lang][result['choice']]),
                          (0, y_button - 0.06))
        # only the chosen half of the scale (up to the middle) can be used;
        # the other animal and that half of the bar are faded
        side = -1 if result['choice'] == animal_left else 1
        for stim in ((img_r, name_r) if side < 0 else (img_l, name_l)):
            stim.opacity = UNCHOSEN_OPACITY
        veil = visual.Rect(win, width=half_len + 4 * PX, height=bar_h + 4 * PX,
                           pos=(-side * (half_len + 4 * PX) / 2, y), fillColor=BG_COLOR,
                           lineColor=None, opacity=1 - UNCHOSEN_OPACITY)

    if not binary:
        side, veil = 0, None  # whole scale usable
    placed = first is not None  # the second rating starts at the first answer
    pos = first if placed else 0.0
    dragging = False
    n_touches = 0
    first_touch_rt = None
    attempts = 0  # with `check`: answers given (Continue taps)
    skip = Button(EXP['skip'], (HALF_W - 0.12, -0.45), color=EXP_BUTTON_COLOR)

    def draw_screen(ring='#111111', shift=0.0):
        head.draw()
        pid.draw()
        question.draw()
        if bubble and follow:
            bubble.follow(pos, placed)
        elif bubble:
            bubble.draw(thought)
        img_l.draw()
        img_r.draw()
        name_l.draw()
        name_r.draw()
        bar.draw()
        if veil:
            veil.draw()
        if first_marker:
            first_marker.draw()
            if n_touches == 0:
                first_label.draw()
        if placed and pos == 0:
            middle_mark.draw()
        if placed:
            hx = pos * half_len + shift
            handle_shadow.pos = (hx, y - 2 * PX)
            handle_ring.pos = handle_fill.pos = (hx, y)
            handle_ring.fillColor = ring
            handle_shadow.draw()
            handle_ring.draw()
            handle_fill.draw()
        done.draw()
        if check and attempts >= PRACTICE_SKIP_AFTER:
            skip.draw()
        draw_help(script)

    def feedback(right):
        """Practice: chime and green marker, or 'oops' and a red shaking marker."""
        player = play_sound(SOUND_CORRECT if right else SOUND_WRONG)
        shown = core.Clock()
        while shown.getTime() < 0.8:
            check_quit()
            t = shown.getTime()
            draw_screen('#2e9d4a' if right else '#d93025',
                        0 if right else 0.012 * math.sin(t * 40) * (t < 0.5))
            win.flip()
        if player:
            player.close_player()

    wait_release()
    clock = core.Clock()
    while True:
        check_quit()
        mx, my = mouse.getPos()
        if mouse.getPressed()[0]:
            if not dragging and help_tapped((mx, my)):
                continue
            if (not dragging and check and attempts >= PRACTICE_SKIP_AFTER
                    and skip.contains((mx, my))):
                result.update(pos=pos, rt=clock.getTime(), first_touch_rt=first_touch_rt,
                              n_touches=n_touches, attempts=attempts, correct=False)
                wait_release()
                return result
            if not dragging and done.contains((mx, my)):
                rt = clock.getTime()
                wait_release()
                if check:
                    attempts += 1
                    if attempts == 1:
                        result['first_pos'] = pos
                    right = check(pos)
                    feedback(right)
                    if not right:  # try again
                        placed = False
                        continue
                    result.update(attempts=attempts, correct=True)
                result.update(pos=pos, rt=rt, first_touch_rt=first_touch_rt,
                              n_touches=n_touches)
                return result
            on_scale = abs(my - y) < 75 * PX and abs(mx) <= half_len  # 150 px tall
            if side and mx * side < -MIDDLE_SNAP * half_len:
                on_scale = False  # touch on the faded half
            if dragging or on_scale:
                if not dragging:
                    n_touches += 1
                    if first_touch_rt is None:
                        first_touch_rt = clock.getTime()
                dragging = True
                placed = True
                pos = max(-1.0, min(1.0, mx / half_len))
                if abs(pos) < MIDDLE_SNAP or pos * side < 0:
                    pos = 0.0  # middle; a drag into the faded half stops there
        else:
            dragging = False
        done.enabled = placed

        draw_screen()
        win.flip()


class ThoughtBubble:
    """A child (stimuli/thinking/child.png) with a thought bubble
    (bubble.png) in the middle of the scale screen, under the question. In
    the bubble: a fixed thought (an animal, or a big "?" for 'dont_know'), or
    with follow() the animal toward which the marker points, larger and
    more solid the closer the marker is to that end, smaller and fainter
    toward the middle ("?" in the middle, empty before the marker is placed)."""

    def __init__(self, animal_left, animal_right):
        width = 0.25
        pos = (0.05, 0.185)
        self.inside = (pos[0] + 0.03 * width, pos[1] + 0.07 * width)  # cloud centre
        self.max_size = 0.1
        self.frame = [load_image(STIM / 'thinking' / 'bubble.png', pos, width),
                      load_image(STIM / 'thinking' / 'child.png', (-0.105, 0.065), 0.11)]
        self.animals = {a: load_image(STIM / 'animals' / f'{a}.png', self.inside,
                                      self.max_size)
                        for a in (animal_left, animal_right)}
        self.full_size = {a: img.size.copy() for a, img in self.animals.items()
                          if isinstance(img, visual.ImageStim)}
        self.left, self.right = animal_left, animal_right
        self.unsure = visual.TextStim(win, text='?', pos=self.inside, height=self.max_size,
                                      color='#555555', bold=True, font=FONT)

    def draw(self, thought=None, strength=1.0):
        """thought: an animal, 'dont_know' or None (empty); strength 0..1
        scales and fades the animal (0 = smallest and faintest, 1 = full)."""
        for stim in self.frame:
            stim.draw()
        if thought == 'dont_know':
            self.unsure.draw()
        elif thought:
            img = self.animals[thought]
            if thought in self.full_size:
                img.size = self.full_size[thought] * (0.25 + 0.75 * strength)
            img.opacity = 0.15 + 0.85 * strength  # fades toward the middle
            img.draw()

    def follow(self, pos, placed=True):
        """Show what the marker at pos (-1..1) says."""
        if not placed:
            self.draw(None)
        elif pos == 0:
            self.draw('dont_know')
        else:
            self.draw(self.left if pos < 0 else self.right, abs(pos))


def slider_training(left, right, names):
    """Practice with the scale (first round only, as in the procedure script):
    the experimenter shows how the scale works ("Let me show you!"), then the
    child shows where the marker goes if they really thought there were more
    of the left animal, more of the right animal, and if they didn't know (a
    thinking child with that animal, or "?", in a thought bubble). Returns
    the practice positions (-100..100)."""
    rating_scale(left, right, EXP['train_demo'], TXT['continue'],
                 question=TXT['practice_show'], say=EXP['train_demo_say'].format(**names),
                 follow=True)
    result = {}
    for key, column, thought, check in (
            ('train_left', 'practice_really_left', left, lambda p: p <= -REALLY),
            ('train_right', 'practice_really_right', right, lambda p: p >= REALLY),
            ('train_middle', 'practice_dont_know', 'dont_know',
             lambda p: abs(p) <= PRACTICE_MIDDLE)):
        answer = rating_scale(left, right, EXP[key].format(**names), TXT['continue'],
                              question='', say=EXP[key + '_say'].format(**names),
                              thought=thought, check=check)
        result[column] = round(answer['pos'] * 100, 1)
        result[column + '_first'] = round(answer['first_pos'] * 100, 1)
        result[column + '_attempts'] = answer['attempts']
        result[column + '_correct'] = answer['correct']
    return result


# --------------------------------------------------------------------------
# Video (screen design after code_caro/trial1_test_text.txt)
# --------------------------------------------------------------------------
def frame_to_array(img):
    """ffpyplayer frame -> float array (0..1) for an ImageStim."""
    w, h = img.get_size()
    return (np.frombuffer(img.to_memoryview()[0], np.uint8)
            .reshape(h, w, 3) / np.float32(255))


def first_frame(path):
    """First frame of a video (shown before it starts), or None."""
    player = MediaPlayer(str(path), ff_opts={'out_fmt': 'rgb24', 'an': True})
    player.set_size(*VIDEO_PIXELS)
    try:
        t0 = core.getTime()
        while core.getTime() - t0 < 3:
            frame, val = player.get_frame()
            if frame is not None:
                return frame_to_array(frame[0])
            if val == 'eof':
                break
            core.wait(0.005)
    finally:
        player.close_player()
    return None


def play_video(path):
    """Video screen: title, the video in a rounded dark frame, and a play
    symbol; tapping the video starts it. Afterwards 'Replay' plays it again
    and 'Continue' goes on. Returns the number of times the video was played.

    Videos are decoded with ffpyplayer directly (PsychoPy's MovieStim stays
    blank with these files); the sound sets the pace, so picture and sound
    stay in sync. Key 's' skips the rest of the video.
    """
    vid_w = min(1.15, 0.92 * 2 * HALF_W)
    vid_h = vid_w * 9 / 16
    vid_pos = (0, 0.02)
    title = visual.TextStim(win, text=TXT['watch'], pos=(0, 0.42),
                            height=42 * PX, color='#111111', bold=True, font=FONT)
    backdrop = rounded_rect((vid_w, vid_h), vid_pos, '#111111', radius=12 * PX)
    screen = visual.ImageStim(win, size=(vid_w, vid_h), pos=vid_pos,
                              flipVert=True, interpolate=True)
    corners = corner_masks((vid_w, vid_h), vid_pos, 12 * PX, BG_COLOR)
    play_circle = visual.Circle(win, radius=0.06, pos=vid_pos, fillColor='black',
                                lineColor=None, opacity=0.55)
    play_icon = visual.ShapeStim(win, pos=vid_pos, fillColor='white', lineColor=None,
                                 vertices=[(-0.018, -0.03), (-0.018, 0.03), (0.034, 0)])
    missing = visual.TextStim(win, text=f"{EXP['video_missing']}\n{path.name}",
                              pos=vid_pos, height=0.035, color='red', font=FONT)
    y_buttons = vid_pos[1] - vid_h / 2 - 66 * PX
    replay = Button(TXT['replay'], (-0.11, y_buttons), color='#616161')
    cont = Button(TXT['continue'], (0.11, y_buttons))

    shown = {'frame': False}
    if path.exists():
        poster = first_frame(path)
        if poster is not None:
            screen.image = poster
            shown['frame'] = True

    def draw(*extra):
        title.draw()
        backdrop.draw()
        if shown['frame']:
            screen.draw()
        elif not path.exists():
            missing.draw()
        for c in corners:
            c.draw()
        for stim in extra:
            stim.draw()

    # wait for a tap on the video
    wait_release()
    while not (mouse.getPressed()[0] and backdrop.contains(mouse.getPos())):
        check_quit()
        draw(play_circle, play_icon)
        win.flip()
    wait_release()

    n_plays = 0
    while True:
        n_plays += 1
        if path.exists():
            # the picture sets the pace (sound follows), so no frames are
            # skipped or rushed at the start
            player = MediaPlayer(str(path), ff_opts={'out_fmt': 'rgb24',
                                                     'sync': 'video'})
            player.set_size(*VIDEO_PIXELS)
            next_frame = 0.0
            try:
                event.getKeys(['s'])
                while not event.getKeys(['s']):
                    check_quit()
                    if core.getTime() >= next_frame:
                        frame, val = player.get_frame()
                        if val == 'eof':
                            break
                        if frame is not None:
                            screen.image = frame_to_array(frame[0])
                            shown['frame'] = True
                            # val = seconds until the next frame is due
                            next_frame = core.getTime() + val
                    draw()
                    win.flip()
            finally:
                player.close_player()

        # last frame stays visible; replay or continue
        wait_release()
        while True:
            check_quit()
            draw(replay, cont)
            win.flip()
            if mouse.getPressed()[0]:
                xy = mouse.getPos()
                if cont.contains(xy):
                    wait_release()
                    return n_plays
                if replay.contains(xy):
                    wait_release()
                    break


# --------------------------------------------------------------------------
# Check questions after the video
# --------------------------------------------------------------------------
def check_screen(team, whose, left, right, claimed, box, quality, attempt):
    """Check questions after the video, on one screen: the team from the video
    at the top; "What does the team think?" with both animals; "Why?" with
    two pictures (numeric version: the row of boxes with 2 and with 4 boxes
    open; quality version: eyes = they looked in the boxes, speaking head =
    someone told them); a "doesn't know" button for each question; and a
    toggle whether the child gave the reason themselves or after asking.
    The child points (or taps) and the experimenter taps; a second tap
    changes the answer. One step at a time: the question being asked is
    fully visible and the rest faded (CHECK_FADED_OPACITY); after the
    belief the reason question becomes active, then the toggle and
    Continue.
    Returns the answers (keys as in CHECK_FIELDS)."""
    c = PLURALS[lang][claimed]
    if reason_set == 'numeric':
        n_open = BOXES_OPENED[quality]
        right_reason = f'{n_open}_boxes'
        reason_label = EXP['n_boxes'].format(n=n_open)
        if_right = EXP['if_right_number_say'].format(n=NUMBER_WORDS[lang][n_open], c=c)
        question_reason = TXT['check_reason_numeric']
    else:
        right_reason = 'looked' if quality == 'strong' else 'told'
        reason_label = EXP['reason_' + right_reason]
        if_right = EXP['if_right_reason_say']
        question_reason = TXT['check_reason']

    def text(t, y, height=0.024, color=EXP_COLOR):
        return visual.TextStim(win, text=t, pos=(0, y), height=height, color=color,
                               italic=True, font=FONT, wrapWidth=2 * HALF_W * 0.92)

    head = text(EXP['check_head'].format(k=attempt, m=MAX_CHECKS) + '   '
                + EXP['correct'].format(c=f'{c} · {reason_label}'), 0.465, 0.021)
    # the team from the video
    photo_w = 0.42
    photo_pos = (0.06, 0.35)
    team_stims = [load_image(STIM / 'groups' / f'{team}.png', (-0.25, 0.35), 0.1),
                  load_image(STIM / 'teams' / f'{team}.png', photo_pos, photo_w)]
    team_stims += corner_masks((photo_w, photo_w / 2.6), photo_pos, 8 * PX, BG_COLOR)
    ask_belief = text(EXP['ask'].format(q=TXT['check_belief'].format(
        whose=whose, a=PLURALS[lang][left], b=PLURALS[lang][right])), 0.235)
    ask_reason = text(EXP['ask'].format(q=question_reason), 0.0)

    # answer options: value -> (pictures, hit box (x, y, half width, half height))
    y_b, y_r = 0.12, -0.12
    options = {'belief': {}, 'reason': {}}
    for animal, x in ((left, -0.22), (right, 0.22)):
        options['belief'][animal] = (
            [load_image(STIM / 'animals' / f'{animal}.png', (x, y_b), 0.14)], (x, y_b, 0.1, 0.09))
    if reason_set == 'numeric':
        for n, x in ((2, -0.25), (4, 0.25)):
            options['reason'][f'{n}_boxes'] = (
                box_row(BOX_DISPLAY[box], y=y_r - 0.01, n_open=n, arrow=False,
                        width=0.42, x0=x), (x, y_r, 0.23, 0.07))
    else:
        for value, x in (('looked', -0.22), ('told', 0.22)):
            options['reason'][value] = (
                [load_image(STIM / 'reasons' / f'{value}.png', (x, y_r), 0.12)],
                (x, y_r, 0.1, 0.08))
    buttons = {'belief': Button(EXP['dont_know'], (0, y_b), color=EXP_BUTTON_COLOR),
               'reason': Button(EXP['dont_know'], (0, y_r - 0.105), color=EXP_BUTTON_COLOR)}
    prompted_buttons = {'self': Button(EXP['said_self'], (-0.17, -0.31), color=EXP_BUTTON_COLOR),
                        'prompted': Button(EXP['said_prompted'], (0.17, -0.31),
                                           color=EXP_BUTTON_COLOR)}
    highlight = {(q, v): rounded_rect((2 * hb[2] + 0.02, 2 * hb[3] + 0.02), hb[:2],
                                      SELECTED_COLOR, radius=0.02)
                 for q in options for v, (_, hb) in options[q].items()}
    for h in highlight.values():
        h.opacity = 0.35
    done = Button(TXT['continue'], (0, -0.42))
    script = say_text(EXP['if_right_belief_say'].format(whose=whose, c=c) + '\n' + if_right,
                      (0, -0.455), height=0.019)
    answer = {'belief': None, 'reason': None, 'prompted': ''}
    # One step at a time: the question being asked is fully visible, the
    # rest is faded. Questions not reached yet can't be tapped; an answered
    # one can be tapped again to change the answer.
    sections = {q: [ask_belief if q == 'belief' else ask_reason, buttons[q]]
                   + [highlight[q, v] for v in options[q]]
                   + [stim for stims, _ in options[q].values() for stim in stims]
                for q in options}
    sections['end'] = list(prompted_buttons.values())

    def current_step():
        return next((q for q in ('belief', 'reason') if answer[q] is None), 'end')

    def set_opacity(items, opacity):
        for item in items:
            if isinstance(item, Button):
                item.box.opacity = item.label.opacity = opacity
            else:
                item.opacity = opacity

    step = current_step()
    wait_release()
    clock = core.Clock()
    while True:
        check_quit()
        if mouse.getPressed()[0]:
            mx, my = mouse.getPos()
            if help_tapped((mx, my)):
                continue
            if done.contains((mx, my)):
                rt = clock.getTime()
                wait_release()
                break
            for q in options:
                if q != step and answer[q] is None:
                    continue  # not asked yet
                for value, (_, (x, y, hw, hh)) in options[q].items():
                    if abs(mx - x) < hw and abs(my - y) < hh:
                        answer[q] = value
                if buttons[q].contains((mx, my)):
                    answer[q] = 'dont_know'
            if step == 'end':
                for value, button in prompted_buttons.items():
                    if button.contains((mx, my)):
                        answer['prompted'] = '' if answer['prompted'] == value else value
            step = current_step()
            wait_release()

        for name, items in sections.items():
            set_opacity(items, 1 if name == step else CHECK_FADED_OPACITY)
        head.draw()
        for stim in team_stims:
            stim.draw()
        ask_belief.draw()
        ask_reason.draw()
        for q in options:
            for value, (stims, _) in options[q].items():
                if answer[q] == value:
                    highlight[q, value].draw()
                for stim in stims:
                    stim.draw()
            buttons[q].color = SELECTED_COLOR if answer[q] == 'dont_know' else EXP_BUTTON_COLOR
            buttons[q].draw()
        for value, button in prompted_buttons.items():
            button.color = SELECTED_COLOR if answer['prompted'] == value else EXP_BUTTON_COLOR
            button.draw()
        done.enabled = step == 'end'
        done.draw()
        draw_help(script)
        win.flip()

    belief_correct = answer['belief'] == claimed
    reason_correct = answer['reason'] == right_reason
    return {'belief': answer['belief'], 'belief_correct': belief_correct,
            'reason': answer['reason'], 'reason_correct': reason_correct,
            'reason_prompted': answer['prompted'],
            'passed': belief_correct and reason_correct, 'rt': round(rt, 3)}


# --------------------------------------------------------------------------
# Solution at the end
# --------------------------------------------------------------------------
def tick_mark(pos, radius=0.028):
    """Green circle with a white tick."""
    x, y = pos
    r = radius
    return [visual.Circle(win, radius=r, pos=pos, fillColor='#2e9d4a', lineColor=None),
            visual.ShapeStim(win, closeShape=False, lineColor='white', lineWidth=5,
                             fillColor=None,
                             vertices=[(x - 0.45 * r, y), (x - 0.1 * r, y - 0.35 * r),
                                       (x + 0.5 * r, y + 0.4 * r)])]


def solution_screen(rounds):
    """At the end: for each round (box colour, left animal, right animal, the
    child's animal) a row of closed boxes with the child's animal next to it.
    Tapping a row opens its boxes: SOLUTION_MAJORITY of them hold the child's
    animal (the child is always right), with the 'correct' chime and a green
    tick. When all rows are open the happy jingle plays and Continue
    appears."""
    title = visual.TextStim(win, text=TXT['solution'], pos=(0, 0.45), height=34 * PX,
                            color='#111111', bold=True, font=FONT,
                            wrapWidth=2 * HALF_W * 0.9)
    instruction = visual.TextStim(win, text=EXP['solution'], pos=(0, 0.395), height=0.022,
                                  color=EXP_COLOR, italic=True, font=FONT,
                                  wrapWidth=2 * HALF_W * 0.9)
    script = say_text(EXP['solution_say'], (0, -0.465), height=0.019)
    row_w, row_x = 0.8, -0.13
    n = N_BOXES
    box_w = row_w / (n + (n - 1) * 0.2)  # as in box_row
    ys = [0.27 - i * 0.17 for i in range(len(rounds))]
    rows = []
    for (box, left, right, animal), y in zip(rounds, ys):
        other = right if animal == left else left
        contents = [animal] * SOLUTION_MAJORITY + [other] * (n - SOLUTION_MAJORITY)
        random.shuffle(contents)
        icons = []
        for i, a in enumerate(contents):
            x = row_x + (i - (n - 1) / 2) * 1.2 * box_w
            icons.append(load_image(STIM / 'animals' / f'{a}.png', (x, y + 0.012), box_w * 0.95))
        rows.append({
            'y': y, 'open': False,
            'closed': box_row(BOX_DISPLAY[box], y=y - 0.02, n_open=0, arrow=False,
                              width=row_w, x0=row_x),
            'opened': box_row(BOX_DISPLAY[box], y=y - 0.02, n_open=n, arrow=False,
                              width=row_w, x0=row_x) + icons,
            'answer': [load_image(STIM / 'animals' / f'{animal}.png', (0.43, y), 0.11)],
            'tick': tick_mark((0.54, y + 0.04))})
    done = Button(TXT['continue'], (0, -0.4))
    player = None

    wait_release()
    while True:
        check_quit()
        all_open = all(row['open'] for row in rows)
        if mouse.getPressed()[0]:
            mx, my = mouse.getPos()
            if help_tapped((mx, my)):
                continue
            if all_open and done.contains((mx, my)):
                wait_release()
                break
            for row in rows:
                if not row['open'] and abs(my - row['y']) < 0.08 and -0.62 < mx < 0.6:
                    row['open'] = True
                    if player:
                        player.close_player()
                    last = all(r['open'] for r in rows)
                    player = play_sound(SOUND_TEAM if last else SOUND_CORRECT)
            wait_release()
        title.draw()
        instruction.draw()
        for row in rows:
            for stim in row['opened' if row['open'] else 'closed'] + row['answer']:
                stim.draw()
            if row['open']:
                for stim in row['tick']:
                    stim.draw()
        if all_open:
            done.draw()
        draw_help(script)
        win.flip()
    if player:
        player.close_player()


# --------------------------------------------------------------------------
# Data
# --------------------------------------------------------------------------
def row_id(row):
    return f"{info['participant']}_{info['date']}_trial{row['trial']}"


def save_row(row):
    new_file = not data_file.exists()
    with open(data_file, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(row.keys()))
        if new_file:
            writer.writeheader()
        writer.writerow(row)
    if sheets_sync.SHEETS_URL:  # empty = local copy only
        sheets_sync.queue_row(row, row_id(row))
        sheets_sync.send_in_background()


def add_session_duration(minutes):
    """Fill session_duration_min into all rows of this session (local file;
    the rows are sent to the sheet again, which updates them)."""
    with open(data_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fields, rows = reader.fieldnames, list(reader)
    for row in rows:
        row['session_duration_min'] = minutes
    with open(data_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    if sheets_sync.SHEETS_URL:
        for row in rows:
            sheets_sync.queue_row(row, row_id(row))


def check_media():
    files = [STIM / 'groups' / f'{t}.png' for t in TEAMS]
    for box, pair in BOXES.items():
        for animal in pair:
            files.append(STIM / 'animals' / f'{animal}.png')
            for team in TEAMS:
                for quality in QUALITIES:
                    files.append(video_path(box, team, quality, animal, lang,
                                            reason_set))
    return [f.relative_to(HERE) for f in files if not f.exists()]


# --------------------------------------------------------------------------
# Run
# --------------------------------------------------------------------------
missing = check_media()
if missing:
    shown = '\n'.join(
        str(m) + (EXP['online_only']
                  if (HERE / m).with_suffix('.gvid').exists() else '')
        for m in missing[:12])
    more = '\n' + EXP['more'].format(n=len(missing) - 12) if len(missing) > 12 else ''
    experimenter_screen(EXP['missing'].format(n=len(missing)) + f'\n\n{shown}{more}')

session_clock = core.Clock()  # duration of the session: first to last screen
experimenter_screen(EXP['start'].format(p=info['participant'], o=info['order']),
                    say=EXP['start_say'])
child_team, team_left, team_rt = choose_group()
other_team = [t for t in TEAMS if t != child_team][0]
own_name = TEAM_NAMES[lang][child_team]

# Both teams right away (while the child gets the sticker and hat); then
# the child taps their own team
teams_top, team_tap = show_teams(child_team)

# Sticker distribution: one member of each team, same gender as the child
if info['gender'] in ('female', 'male'):
    member_gender = info['gender']
else:
    member_gender = random.choice(['female', 'male'])
this_sg, pl = MEMBER_WORDS[lang][member_gender]
experimenter_screen(EXP['sticker_intro'].format(n=N_STICKERS),
                    say=EXP['sticker_intro_say'].format(pl=pl, this_sg=this_sg))
stickers, sticker_left, sticker_rt = sticker_task(member_gender)
session = {'child_team': child_team, 'team_pic_left': team_left,
           'team_choice_rt': round(team_rt, 3), 'teams_pic_top': teams_top,
           **team_tap,
           'sticker_member_gender': member_gender,
           'sticker_pic_left': sticker_left,
           'stickers_to_sun_member': stickers['sun'],
           'stickers_to_moon_member': stickers['moon'],
           'sticker_rt': round(sticker_rt, 3),
           **{f'practice_{item}{suffix}': '' for item in ('really_left', 'really_right', 'dont_know')
              for suffix in ('', '_first', '_attempts', '_correct')}}

solutions = []  # (box, left, right, the child's final animal) per round, for the end
for t in trials:
    left, right = t['animal_left'], t['animal_right']
    box = t['box_color']
    names = {'pl_l': PLURALS[lang][left], 'pl_r': PLURALS[lang][right],
             'a_l': with_article(left), 'a_r': with_article(right),
             'l': animal_name(left).lower(), 'r': animal_name(right).lower(),
             'the_l': the_animal(left), 'the_r': the_animal(right)}
    first_round = t['trial'] == 1
    setup = 'setup_first' if first_round else 'setup'
    experimenter_screen(
        EXP[setup].format(t=t['trial'], n=len(trials), k=N_BOXES,
                          color=COLOR_ADJ_NL[box] if lang == 'nl' else box, **names),
        color=BOX_DISPLAY[box], say=EXP[setup + '_say'].format(**names))

    # Practice with the scale (first round only), then open the first box
    open_say = EXP['open_box_say']
    if first_round:
        session.update(slider_training(left, right, names))
        open_say = EXP['train_end_say'] + '\n' + open_say
    experimenter_screen(EXP['open_box'], color=BOX_DISPLAY[box], say=open_say)

    def header(step):
        return EXP['header'].format(t=t['trial'], n=len(trials), s=step,
                                    color=COLOR_NAMES[lang][box].capitalize())

    # Initial belief: binary choice, then how sure on the scale
    rating1 = rating_scale(left, right, header(1), TXT['continue'], binary=True,
                           say=EXP['ask_binary_say'].format(**names),
                           follow=BUBBLE_IN_TEST)
    r1 = rating1['pos']
    choice = rating1['choice']

    # Video: the team states the belief opposite to the child's choice
    claimed = right if choice == left else left
    video_team = child_team if t['group_type'] == 'ingroup' else other_team
    whose = EXP['your_team' if video_team == child_team else 'other_team']
    team_name = TEAM_NAMES[lang][video_team]
    vid = video_path(t['box_color'], video_team, t['reason_quality'], claimed,
                     lang, reason_set)
    experimenter_screen(
        EXP['before_video'].format(team=team_name, whose=whose),
        say=EXP['before_video_say'].format(team=team_name, whose=whose,
                                           own=own_name, **names))
    n_plays = play_video(vid)

    # Check questions; if the answer is wrong the video is shown again
    n_boxes = BOXES_OPENED[t['reason_quality']] if reason_set == 'numeric' else None
    c = PLURALS[lang][claimed]
    why = (EXP['why_numeric'].format(n=NUMBER_WORDS[lang][n_boxes], c=c) if n_boxes
           else EXP['why_' + t['reason_quality']].format(c=c))
    checks = {f'check{k}_{f}': '' for k in range(1, MAX_CHECKS + 1)
              for f in CHECK_FIELDS}
    for attempt in range(1, MAX_CHECKS + 1):
        if attempt > 1:
            experimenter_screen(EXP['repeat'], say=EXP['repeat_say'])
            n_plays += play_video(vid)
        result = check_screen(video_team, whose, left, right, claimed, box,
                              t['reason_quality'], attempt)
        checks.update({f'check{attempt}_{f}': result[f] for f in CHECK_FIELDS})
        if result['passed']:
            break

    # Summary of the team's belief; the toy animal goes on the team logo
    experimenter_screen(
        ('' if result['passed'] else EXP['give_up'].format(m=MAX_CHECKS))
        + EXP['summary'].format(animal=animal_name(claimed).lower(), team=team_name),
        say=EXP['summary_say'].format(whose=whose, c=c, why=why))

    # Second belief; the handle starts at the first answer
    if r1 == 0:
        how, said = 'dont_know', choice
    else:
        how = 'really' if abs(r1) >= REALLY else 'kind_of'
        said = left if r1 < 0 else right
    last = t['trial'] == len(trials)
    rating2 = rating_scale(left, right, header(2),
                           TXT['finish'] if last else TXT['next'], first=r1,
                           follow=BUBBLE_IN_TEST,
                           say=EXP['ask_final_say'].format(how=EXP['how'][how],
                                                           pl=PLURALS[lang][said]))
    r2 = rating2['pos']
    final_animal = choice if r2 == 0 else (left if r2 < 0 else right)  # middle: first choice
    solutions.append((box, left, right, final_animal))

    def rounded(value):
        return None if value is None else round(value, 3)

    sign = 1 if claimed == right else -1  # positive = toward claimed animal
    row = dict(info)
    row.update({
        **session, 'swap_sides': swap_sides,
        **t,
        'belief1_choice': choice,
        'belief1_choice_side': 'left' if choice == left else 'right',
        'belief1_choice_rt': round(rating1['choice_rt'], 3),
        'video_team': video_team, 'claimed_animal': claimed,
        'video_file': vid.name,
        'video_missing': not vid.exists(), 'video_n_plays': n_plays,
        'check_n_attempts': attempt, 'check_passed': result['passed'],
        **checks,
        'rating1_raw': round(r1 * 100, 1),
        'rating1_toward_claim': round(sign * r1 * 100, 1),
        'rating1_on_chosen_side': sign * r1 < 0,
        'rating1_rt': round(rating1['rt'], 3),
        'rating1_first_touch_rt': rounded(rating1['first_touch_rt']),
        'rating1_n_touches': rating1['n_touches'],
        'rating2_raw': round(r2 * 100, 1),
        'rating2_toward_claim': round(sign * r2 * 100, 1),
        'rating2_rt': round(rating2['rt'], 3),
        'rating2_first_touch_rt': rounded(rating2['first_touch_rt']),
        'rating2_n_touches': rating2['n_touches'],
        'change_toward_claim': round(sign * (r2 - r1) * 100, 1),
        'solution_animal': final_animal,
        'minutes_since_start': round(session_clock.getTime() / 60, 2),
        'session_duration_min': '',  # filled in at the end (add_session_duration)
    })
    save_row(row)

# Solution: the child's animal was always right
solution_screen(solutions)

# Duration from the first screen to the last (the end screen)
add_session_duration(round(session_clock.getTime() / 60, 2))

if sheets_sync.SHEETS_URL:
    waiting = sheets_sync.send_pending(timeout=5)
    sheets = '\n\n' + (EXP['sheets_waiting'].format(n=waiting) if waiting
                         else EXP['sheets_ok'])
else:
    sheets = ''
experimenter_screen(EXP['end'].format(n=len(trials), file=data_file.name) + sheets,
                    say=EXP['end_say'])
quit_experiment()
