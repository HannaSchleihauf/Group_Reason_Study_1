# Study 1

Study 1 has two versions with the same procedure, texts and data columns. The
PsychoPy version is `Study1_PsychoPy/study1_task.py`. The web version
(`Study1_Web/`) is a port of it. The procedure follows
`procedure/STUDY 1 - Procedure.docx`. The texts follow the English and Dutch
scripts in `procedure/`.

| File | What it holds |
|---|---|
| `procedure/` | procedure and scripts (English, Dutch) |
| `Study1_PsychoPy/` | PsychoPy version: `study1_task.py`, `stimuli/`, original videos in `video_stimuli/`, data in `data/` (not in git) |
| `Study1_Web/index.html` | the page (any web host); `claude_page.html` is the same page for claude.ai |
| `Study1_Web/config.js` | settings and all texts (English / Dutch), made from the PsychoPy script by `tools/export_config.py` |
| `Study1_Web/app.js` | the task |
| `Study1_Web/data.js` | data storage on the device + Google Sheets (`SHEETS_URL`) |
| `Study1_Web/google_sheets/Code.gs` | Apps Script for the Study 1 Google Sheet (shared with the PsychoPy version) |
| `Study1_Web/media/videos/`, `media/posters/` | web videos (960×540) and first frames |
| `Study1_Web/tools/` | `run_local.sh` (test), `make_site_folder.sh` (GitHub Pages), `make_hostinger_zip.sh`, `export_config.py` |

All commands below are run from the `Study1_Web` folder.

## Session flow

1. **Start form**: language, video version (*numeric*: 4 vs 2 boxes opened;
   *quality*: looked vs someone told them), participant number (counted up
   automatically), age and gender.
2. **Introduction**: the child picks a team and taps their own team.
3. **Sticker task** (5 stickers) with one gender-matched member of each team,
   then the **play question** with the same two members: who would the child
   rather play with? The experimenter names them in the order of the pictures
   (left to right, random) and taps the picture the child chooses.
4. **4 trials**, one animal pair each:
   - setup; in the first trial, the game introduction and scale practice
     (really / kind of more of each animal, and don't know);
   - the experimenter opens the fifth box from the left and shows the animal;
   - **initial belief** (which animal, then how sure);
   - **one video**: the child's own team or the other team claims the animal
     the child did *not* choose, with a strong or a weak reason;
   - check questions (what does the team think, and why?); if an answer is
     wrong, the video is replayed, up to twice;
   - **final belief** (the marker starts at the initial belief).
5. **Solution screen**: the child taps each row of boxes; the child's final
   animal is always in most of them.
6. **End screen**: the child picks a sticker; the data can be downloaded as CSV.

The **(i)** button (top left) shows what to say on each screen. The **←**
button under it goes back one screen (web version): the answers given on the
screens since then are undone, and a trial done again replaces its data row.
On a video screen, the **s** key skips to the end of the video (for testing).

## Design and counterbalancing

Conditions (all within subjects, one trial each): IS / IW = ingroup strong /
weak reason, OS / OW = outgroup strong / weak. Each session gets a
counterbalancing list (`cb_list`, 1–32) that sets the condition order (Latin
square, orders A–D), the order of the animal pairs (Latin square), and the
sides of the scale (`swap_sides`). The app chooses the least used condition
order for this age, then the least used list within it.

## Data (one row per trial)

The main columns are listed below. The full list is in the docstring of
`study1_task.py`.

| Column(s) | Meaning |
|---|---|
| `cb_list`, `order`, `swap_sides`, `reason_set` | counterbalancing; numeric / quality videos |
| `child_team`, `team_tap_*` | the team chosen; tapping their own team |
| `sticker_member_gender`, `sticker_pic_left` | gender of the two members; the team shown left (sticker and play screens) |
| `play_choice` | the team member the child would rather play with: moon / sun (empty if skipped) |
| `play_team`, `play_rt` | own_team / other_team (empty if skipped); time to answer (s) |
| `stickers_to_moon_member`, `stickers_to_sun_member` | sticker allocation |
| `practice_*` | scale practice |
| `trial`, `condition`, `group_type`, `reason_quality` | 1–4; ingroup / outgroup; strong / weak |
| `belief1_choice`, `claimed_animal`, `video_team`, `video_file` | the child's initial animal; the team claims the other one |
| `check<k>_*`, `check_n_attempts`, `check_passed` | check answers per try |
| `rating1_raw`, `rating2_raw` | scale position, −100 (left) … 100 (right) |
| `rating*_toward_claim`, `change_toward_claim` | positive = toward the animal the team claimed |
| `solution_animal` | the animal shown as the majority on the solution screen |

## Setup

**Google Sheet.** This is already connected (`SHEETS_URL` in `data.js`). The
PsychoPy version sends to the same sheet.

**Testing on this computer.** Run `sh tools/run_local.sh`. It opens the task
in the browser and prints an address that an iPad on the same Wi-Fi can use.
Stop it with Ctrl+C. Tick "test run" on the start form, so the session is not
counted.

**Publishing (GitHub Pages).** This folder is the git repository
`HannaSchleihauf/Group_Reason_Study_1`. GitHub Pages serves its `docs/`
folder (Settings > Pages: branch `master`, folder `/docs`) at
https://hannaschleihauf.github.io/Group_Reason_Study_1/. After changing
anything in `Study1_Web`, run

    sh tools/make_site_folder.sh

and then commit and push. (`tools/make_hostinger_zip.sh` is still there for a
web host such as Hostinger.)

**Texts.** After changing texts or settings in the PsychoPy script, run
`python tools/export_config.py ../Study1_PsychoPy/study1_task.py config.js`
so that the web version uses the same wording.
