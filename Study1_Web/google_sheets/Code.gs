/**
 * Study 1 - receives the data rows from the task (web version: data.js;
 * PsychoPy version: sheets_sync.py) and appends them to the sheet "data".
 * Both versions can use the same sheet. For the web version, doGet also
 * tells the page which counterbalancing lists completed sessions used
 * (all devices).
 *
 * Setup (once):
 *  1. Make a new Google Sheet (e.g. in the lab's Google Drive).
 *  2. In the sheet: Extensions > Apps Script. Replace the code there with this
 *     file and change TOKEN below to a password of your own.
 *  3. Deploy > New deployment > type "Web app".
 *       Execute as: Me
 *       Who has access: Anyone
 *     Deploy, allow access, and copy the web app URL.
 *  4. In data.js (web) and/or sheets_sync.py (PsychoPy), set SHEETS_URL to
 *     that URL and SHEETS_TOKEN to the same password as TOKEN.
 *  5. Check: open <URL>?action=sessions&token=<TOKEN> in a browser; it should
 *     show {"ok":true,"sessions":[...]}.
 *  After changing this code later: Deploy > Manage deployments > edit >
 *  Version: New version (the URL stays the same).
 *
 * The first row of the sheet holds the column names; new columns are added
 * at the right when the task sends a field the sheet does not have yet.
 * A row whose row_id is already in the sheet is updated, not added again
 * (no duplicates when a row is sent twice; at the end of a session the task
 * sends its rows again with session_duration_min filled in).
 */
const TOKEN = 'change-me';  // same as SHEETS_TOKEN in data.js / sheets_sync.py
const SHEET_NAME = 'data';

function doPost(e) {
  const lock = LockService.getScriptLock();
  lock.waitLock(30000);  // one request at a time
  try {
    const data = JSON.parse(e.postData.contents);
    if (data.token !== TOKEN) return reply({ok: false, error: 'wrong token'});

    const book = SpreadsheetApp.getActiveSpreadsheet();
    const sheet = book.getSheetByName(SHEET_NAME) || book.insertSheet(SHEET_NAME);

    const header = sheet.getLastColumn() > 0
        ? sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0] : [];
    data.rows.forEach(row => Object.keys(row).forEach(key => {
      if (!header.includes(key)) header.push(key);
    }));
    sheet.getRange(1, 1, 1, header.length).setValues([header]);
    sheet.setFrozenRows(1);

    const idColumn = header.indexOf('row_id') + 1;
    const lastRow = sheet.getLastRow();
    const ids = lastRow > 1
        ? sheet.getRange(2, idColumn, lastRow - 1, 1).getValues().map(r => String(r[0]))
        : [];
    const fresh = [];
    let updated = 0;
    data.rows.forEach(row => {
      const values = header.map(key =>
          row[key] === undefined || row[key] === null ? '' : row[key]);
      const i = ids.indexOf(String(row.row_id));
      if (i >= 0) {  // known row: update it
        sheet.getRange(i + 2, 1, 1, header.length).setValues([values]);
        updated++;
      } else {
        fresh.push(values);
      }
    });
    if (fresh.length) {
      sheet.getRange(sheet.getLastRow() + 1, 1, fresh.length, header.length)
           .setValues(fresh);
    }
    return reply({ok: true, added: fresh.length, updated: updated});
  } catch (err) {
    return reply({ok: false, error: String(err)});
  } finally {
    lock.releaseLock();
  }
}

function reply(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
      .setMimeType(ContentService.MimeType.JSON);
}

// Completed sessions per participant and date (age, cb_list, number of
// trials), for the counterbalancing of the web version.
function doGet(e) {
  const p = e.parameter || {};
  if (p.token !== TOKEN) return reply({ok: false, error: 'wrong token'});
  if (p.action !== 'sessions') return reply({ok: false, error: 'unknown action'});
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAME);
  if (!sheet || sheet.getLastRow() < 2) return reply({ok: true, sessions: []});
  const values = sheet.getDataRange().getValues();
  const header = values[0];
  const col = name => header.indexOf(name);
  const sessions = {};
  values.slice(1).forEach(row => {
    const key = row[col('participant')] + '_' + row[col('date')];
    if (!sessions[key]) {
      const age = col('age') >= 0 ? row[col('age')] : row[col('age_group')];
      sessions[key] = {participant: String(row[col('participant')]), age: String(age),
                       cb_list: row[col('cb_list')], n: 0};
    }
    sessions[key].n++;
  });
  return reply({ok: true, sessions: Object.values(sessions)});
}
