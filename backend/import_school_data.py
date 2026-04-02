"""
Import school data from file 9 (各学院毕业去向与落实情况合并表)
degree_level: 本科/硕士/博士
graduation_type: 毕业/结业
"""
import csv
import sqlite3
import os
import uuid
from datetime import datetime

DB_PATH = 'backend/employment.db'
DATA_FILE = 'dataset/学校数据/9.各学院毕业去向与落实情况合并表.csv'
DEFAULT_UNIVERSITY_ID = 'UNI001'

def get_connection():
    return sqlite3.connect(DB_PATH)

def clean_int(val):
    if val is None:
        return None
    val = str(val).strip()
    if val == '' or val == '-' or val == '\\N':
        return None
    try:
        return int(float(val))
    except:
        return None

def ensure_university(conn):
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM universities WHERE university_id = ?', (DEFAULT_UNIVERSITY_ID,))
    if not cursor.fetchone():
        now = datetime.now().isoformat()
        cursor.execute('''
            INSERT INTO universities (university_id, name, province, city, type, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (DEFAULT_UNIVERSITY_ID, '默认大学', '未知', '未知', '综合', now, now))
        conn.commit()

def create_table(conn):
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS college_employment')
    cursor.execute('''
        CREATE TABLE college_employment (
            record_id TEXT PRIMARY KEY,
            university_id TEXT NOT NULL,
            college_name TEXT NOT NULL,
            graduation_year INTEGER,
            degree_level TEXT,
            graduation_type TEXT,
            graduate_nums INTEGER,
            employed_nums INTEGER,
            contract_nums INTEGER,
            total_graduate_school_nums INTEGER,
            domestic_graduate_school_nums INTEGER,
            overseas_graduate_school_nums INTEGER,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    ''')
    conn.commit()

def parse_degree(degree_level):
    """Parse '本科生毕业' -> ('本科生', '毕业'), '博士生结业' -> ('博士生', '结业')"""
    if not degree_level:
        return None, None
    degree_level = degree_level.strip()
    if degree_level == '小计':
        return None, None
    if degree_level.endswith('毕业'):
        return degree_level[:-2], '毕业'
    elif degree_level.endswith('结业'):
        return degree_level[:-2], '结业'
    return None, None

def import_file9(conn, csv_path):
    cursor = conn.cursor()
    count = 0

    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            college_name = row.get('院系名称', '').strip()
            if not college_name:
                continue

            degree_level_raw = row.get('学历层次', '').strip()
            if degree_level_raw == '小计':
                continue

            year = clean_int(row.get('年份'))
            if not year:
                continue

            degree_level, graduation_type = parse_degree(degree_level_raw)
            if not degree_level:
                continue

            now = datetime.now().isoformat()
            record_id = str(uuid.uuid4())

            cursor.execute('''
                INSERT INTO college_employment (
                    record_id, university_id, college_name, graduation_year,
                    degree_level, graduation_type,
                    graduate_nums, employed_nums, contract_nums,
                    total_graduate_school_nums, domestic_graduate_school_nums, overseas_graduate_school_nums,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                record_id, DEFAULT_UNIVERSITY_ID, college_name, year,
                degree_level, graduation_type,
                clean_int(row.get('毕业人数')),
                clean_int(row.get('就业数')),
                clean_int(row.get('签约人数')),
                clean_int(row.get('总升学人数')),
                clean_int(row.get('境内升学人数')),
                clean_int(row.get('境外升学人数')),
                now, now
            ))
            count += 1

    conn.commit()
    return count

def main():
    print("=" * 60)
    print("Importing school data (college + year + degree_level + graduation_type)")
    print("=" * 60)

    conn = get_connection()
    create_table(conn)
    ensure_university(conn)

    filepath = DATA_FILE
    if os.path.exists(filepath):
        print(f"\nImporting: {os.path.basename(filepath)}")
        count = import_file9(conn, filepath)
        print(f"  -> Inserted {count} records")
    else:
        print(f"File not found: {filepath}")

    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM college_employment')
    print(f"\nTotal records: {cursor.fetchone()[0]}")

    print("\nBy degree_level:")
    cursor.execute('SELECT degree_level, COUNT(*) FROM college_employment GROUP BY degree_level ORDER BY degree_level')
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]}")

    print("\nBy graduation_type:")
    cursor.execute('SELECT graduation_type, COUNT(*) FROM college_employment GROUP BY graduation_type')
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]}")

    print("\nSample:")
    cursor.execute('SELECT college_name, graduation_year, degree_level, graduation_type, graduate_nums FROM college_employment LIMIT 5')
    for row in cursor.fetchall():
        print(f"  {row}")

    conn.close()

if __name__ == '__main__':
    main()
