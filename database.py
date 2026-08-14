import csv
import shutil
import sqlite3
from datetime import datetime

import settings
from paths import DATA_DIR

DB_PATH = DATA_DIR / "attendance.db"
BACKUP_DIR = DATA_DIR / "backups"


def _connect():
    DATA_DIR.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )"""
    )
    conn.execute(
        """CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            class_name TEXT DEFAULT '',
            section TEXT DEFAULT '',
            roll_no TEXT DEFAULT ''
        )"""
    )
    if settings.get_marking_mode() == "daily":
        conn.execute(
            "DELETE FROM attendance WHERE id NOT IN "
            "(SELECT MAX(id) FROM attendance GROUP BY name, substr(timestamp, 1, 10))"
        )
        conn.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_attendance_daily "
            "ON attendance(name, substr(timestamp, 1, 10))"
        )
    else:
        conn.execute("DROP INDEX IF EXISTS idx_attendance_daily")
    conn.commit()
    return conn


def mark_attendance(name):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = _connect()
    if settings.get_marking_mode() == "daily":
        cur = conn.execute(
            "INSERT OR IGNORE INTO attendance (name, timestamp) VALUES (?, ?)",
            (name, now),
        )
    else:
        cur = conn.execute(
            "INSERT INTO attendance (name, timestamp) VALUES (?, ?)",
            (name, now),
        )
    conn.commit()
    conn.close()
    return now, cur.rowcount > 0


def get_today_records():
    today = datetime.now().strftime("%Y-%m-%d")
    conn = _connect()
    rows = conn.execute(
        "SELECT name, timestamp FROM attendance WHERE timestamp LIKE ? ORDER BY id DESC",
        (today + "%",),
    ).fetchall()
    conn.close()
    return rows


def get_all_records():
    conn = _connect()
    rows = conn.execute(
        "SELECT name, timestamp FROM attendance ORDER BY timestamp DESC"
    ).fetchall()
    conn.close()
    return rows


def get_person_records(name):
    conn = _connect()
    rows = conn.execute(
        "SELECT name, timestamp FROM attendance WHERE name = ? ORDER BY timestamp DESC",
        (name,),
    ).fetchall()
    conn.close()
    return rows


def get_counts_for_days(days=7):
    conn = _connect()
    rows = conn.execute(
        "SELECT substr(timestamp, 1, 10) AS d, COUNT(*) AS c FROM attendance "
        "GROUP BY d ORDER BY d DESC LIMIT ?",
        (days,),
    ).fetchall()
    conn.close()
    return {d: c for d, c in rows}


def export_records_to_csv(path, rows):
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Timestamp"])
        writer.writerows(rows)


def get_records_for_date(date_str):
    conn = _connect()
    rows = conn.execute(
        "SELECT name, timestamp FROM attendance WHERE timestamp LIKE ? "
        "ORDER BY timestamp DESC",
        (date_str + "%",),
    ).fetchall()
    conn.close()
    return rows


def get_available_dates():
    conn = _connect()
    rows = conn.execute(
        "SELECT DISTINCT substr(timestamp, 1, 10) AS d FROM attendance ORDER BY d DESC"
    ).fetchall()
    conn.close()
    return [r[0] for r in rows]


def clear_records_for_date(date_str):
    conn = _connect()
    cur = conn.execute(
        "DELETE FROM attendance WHERE timestamp LIKE ?", (date_str + "%",)
    )
    conn.commit()
    count = cur.rowcount
    conn.close()
    return count


def clear_all_records():
    conn = _connect()
    cur = conn.execute("DELETE FROM attendance")
    conn.commit()
    count = cur.rowcount
    conn.close()
    return count


# ---------------------------------------------------------------- students


def add_student(name, class_name="", section="", roll_no=""):
    name = name.strip()
    if not name:
        return False
    conn = _connect()
    try:
        conn.execute(
            "INSERT INTO students (name, class_name, section, roll_no) VALUES (?, ?, ?, ?)",
            (name, class_name, section, roll_no),
        )
        conn.commit()
        ok = True
    except sqlite3.IntegrityError:
        ok = False
    conn.close()
    return ok


def update_student(name, class_name=None, section=None, roll_no=None):
    fields = {}
    if class_name is not None:
        fields["class_name"] = class_name
    if section is not None:
        fields["section"] = section
    if roll_no is not None:
        fields["roll_no"] = roll_no
    if not fields:
        return
    conn = _connect()
    set_clause = ", ".join(f"{key} = ?" for key in fields)
    conn.execute(
        f"UPDATE students SET {set_clause} WHERE name = ?",
        (*fields.values(), name),
    )
    conn.commit()
    conn.close()


def get_student(name):
    conn = _connect()
    row = conn.execute(
        "SELECT name, class_name, section, roll_no FROM students WHERE name = ?",
        (name,),
    ).fetchone()
    conn.close()
    return row


def list_students():
    conn = _connect()
    rows = conn.execute(
        "SELECT name, class_name, section, roll_no FROM students "
        "ORDER BY class_name, roll_no, name"
    ).fetchall()
    conn.close()
    return rows


def delete_student(name):
    conn = _connect()
    conn.execute("DELETE FROM students WHERE name = ?", (name,))
    conn.commit()
    conn.close()


def get_classes():
    conn = _connect()
    rows = conn.execute(
        "SELECT DISTINCT class_name FROM students "
        "WHERE class_name != '' ORDER BY class_name"
    ).fetchall()
    conn.close()
    return [r[0] for r in rows]


def import_students(rows):
    added = 0
    skipped = 0
    for name, class_name, section, roll_no in rows:
        if add_student(name, class_name, section, roll_no):
            added += 1
        else:
            skipped += 1
    return added, skipped


def get_unmarked_today():
    today = datetime.now().strftime("%Y-%m-%d")
    conn = _connect()
    present = {
        r[0]
        for r in conn.execute(
            "SELECT name FROM attendance WHERE timestamp LIKE ?", (today + "%",)
        ).fetchall()
    }
    students = conn.execute("SELECT name FROM students").fetchall()
    conn.close()
    return [s[0] for s in students if s[0] not in present]


# ------------------------------------------------------- class-aware logs


def get_all_records_by_class(class_name):
    conn = _connect()
    rows = conn.execute(
        "SELECT a.name, a.timestamp FROM attendance a "
        "JOIN students s ON s.name = a.name WHERE s.class_name = ? "
        "ORDER BY a.timestamp DESC",
        (class_name,),
    ).fetchall()
    conn.close()
    return rows


def get_today_records_by_class(class_name):
    today = datetime.now().strftime("%Y-%m-%d")
    conn = _connect()
    rows = conn.execute(
        "SELECT a.name, a.timestamp FROM attendance a "
        "JOIN students s ON s.name = a.name "
        "WHERE s.class_name = ? AND a.timestamp LIKE ? ORDER BY a.id DESC",
        (class_name, today + "%"),
    ).fetchall()
    conn.close()
    return rows


def get_person_records_in_class(name, class_name):
    conn = _connect()
    rows = conn.execute(
        "SELECT a.name, a.timestamp FROM attendance a "
        "JOIN students s ON s.name = a.name "
        "WHERE a.name = ? AND s.class_name = ? ORDER BY a.timestamp DESC",
        (name, class_name),
    ).fetchall()
    conn.close()
    return rows


# ---------------------------------------------------------------- reports


def get_daily_report(date_str, class_name=None):
    present = {name for name, _ in get_records_for_date(date_str)}
    conn = _connect()
    if class_name:
        rows = conn.execute(
            "SELECT name, class_name, section, roll_no FROM students "
            "WHERE class_name = ? ORDER BY roll_no, name",
            (class_name,),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT name, class_name, section, roll_no FROM students "
            "ORDER BY class_name, roll_no, name"
        ).fetchall()
    conn.close()
    return [
        (name, class_name, section, roll_no,
         "Present" if name in present else "Absent")
        for name, class_name, section, roll_no in rows
    ]


def get_monthly_summary(year_month, class_name=None):
    prefix = year_month + "%"
    conn = _connect()
    if class_name:
        rows = conn.execute(
            "SELECT s.name, s.class_name, s.roll_no, COUNT(a.id) "
            "FROM students s LEFT JOIN attendance a "
            "ON a.name = s.name AND a.timestamp LIKE ? "
            "WHERE s.class_name = ? GROUP BY s.name "
            "ORDER BY s.roll_no, s.name",
            (prefix, class_name),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT s.name, s.class_name, s.roll_no, COUNT(a.id) "
            "FROM students s LEFT JOIN attendance a "
            "ON a.name = s.name AND a.timestamp LIKE ? "
            "GROUP BY s.name ORDER BY s.class_name, s.roll_no, s.name",
            (prefix,),
        ).fetchall()
    conn.close()
    return rows


# ------------------------------------------------------------- backup


def backup_data():
    BACKUP_DIR.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    dest = BACKUP_DIR / stamp
    shutil.copytree(
        DATA_DIR,
        dest,
        ignore=shutil.ignore_patterns("backups", "__pycache__"),
    )
    return dest


def list_backups():
    if not BACKUP_DIR.exists():
        return []
    return sorted(
        (p.name for p in BACKUP_DIR.iterdir() if p.is_dir()), reverse=True
    )


def restore_database(db_file):
    shutil.copy2(db_file, DB_PATH)