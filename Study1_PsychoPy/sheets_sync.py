#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Upload of the data rows to a Google Sheet, with a local outbox
================================================================

The task always saves every trial locally first (data/<participant>_<date>.csv).
Each row is also put in data/outbox/ as a small JSON file. The outbox is sent
to the Google Apps Script web app in google_sheets/Code.gs, which appends the
rows to the sheet. A file is only deleted after the sheet has confirmed it,
so without internet the rows simply wait in the outbox:
  - while the task runs, it tries again every RETRY_SECONDS;
  - when the task starts, it sends whatever is left from earlier sessions;
  - running this file on its own sends the outbox by hand:
        python sheets_sync.py          send the outbox
        python sheets_sync.py --test   send one test row (checks the connection)

The sheet updates a row whose row_id it already has, so a row that is sent
twice (e.g. the connection dropped before the confirmation arrived) appears
once; at the end of a session the rows are sent again with
session_duration_min filled in.

Setup: see google_sheets/Code.gs. With SHEETS_URL empty, data are only saved
locally.
"""

from pathlib import Path
import json
import sys
import threading
import time
import urllib.request

SHEETS_URL = ''  # web app URL of google_sheets/Code.gs ('' = save locally only)
SHEETS_TOKEN = 'change-me'  # must be the same as TOKEN in Code.gs
RETRY_SECONDS = 30

OUTBOX = Path(__file__).resolve().parent / 'data' / 'outbox'
_sending = threading.Lock()


def queue_row(row, row_id):
    """Put one data row in the outbox."""
    OUTBOX.mkdir(parents=True, exist_ok=True)
    path = OUTBOX / f'{row_id}.json'
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps({'row_id': row_id, **row}, default=str), encoding='utf-8')
    tmp.replace(path)  # so the outbox only ever holds complete files


def pending():
    """Rows (files) still waiting in the outbox."""
    return sorted(OUTBOX.glob('*.json')) if OUTBOX.exists() else []


def send_pending(timeout=10):
    """Send everything in the outbox in one request. Returns the number of
    rows still waiting (0 = all in the sheet)."""
    if not SHEETS_URL:
        return len(pending())
    if not _sending.acquire(blocking=False):  # another send is running
        return len(pending())
    try:
        files = pending()
        if not files:
            return 0
        try:
            rows = [json.loads(f.read_text(encoding='utf-8')) for f in files]
            body = json.dumps({'token': SHEETS_TOKEN, 'rows': rows}).encode('utf-8')
            request = urllib.request.Request(
                SHEETS_URL, data=body, headers={'Content-Type': 'text/plain;charset=utf-8'})
            with urllib.request.urlopen(request, timeout=timeout) as response:
                answer = json.loads(response.read().decode('utf-8'))
        except (OSError, ValueError):  # no internet, timeout, or no JSON answer
            return len(files)
        if not answer.get('ok'):
            print(f"Google Sheets refused the data: {answer.get('error')}", file=sys.stderr)
            return len(files)
        for f in files:
            f.unlink(missing_ok=True)
        return len(pending())
    finally:
        _sending.release()


def send_in_background():
    """Start one send without making the task wait for it."""
    threading.Thread(target=send_pending, daemon=True).start()


def start_retrying():
    """Send what is left from earlier sessions now, then try again every
    RETRY_SECONDS while the task runs."""
    def loop():
        while True:
            send_pending()
            time.sleep(RETRY_SECONDS)
    threading.Thread(target=loop, daemon=True).start()


if __name__ == '__main__':
    if not SHEETS_URL:
        sys.exit('SHEETS_URL is empty - fill it in first (see google_sheets/Code.gs).')
    if '--test' in sys.argv:
        stamp = time.strftime('%Y-%m-%d_%H%M%S')
        queue_row({'participant': 'connection_test', 'date': stamp}, f'connection_test_{stamp}')
    n = len(pending())
    left = send_pending(timeout=30)
    print(f'{n - left} row(s) sent, {left} still waiting'
          + (' (no internet, or check SHEETS_URL / SHEETS_TOKEN)' if left else '.'))
