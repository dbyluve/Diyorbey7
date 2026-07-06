"""
SQLite ma'lumotlar bazasi bilan ishlash.
"""
import aiosqlite
from datetime import datetime
from config import DB_PATH

CREATE_STUDENTS_TABLE = """
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER UNIQUE NOT NULL,
    full_name TEXT,
    phone TEXT,
    grade INTEGER,
    course_key TEXT,
    amount INTEGER,
    payment_status TEXT DEFAULT 'pending',
    created_at TEXT
)
"""

CREATE_PAYMENTS_TABLE = """
CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    click_trans_id TEXT,
    merchant_trans_id TEXT,
    amount INTEGER,
    status TEXT,
    created_at TEXT,
    FOREIGN KEY (student_id) REFERENCES students (id)
)
"""


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(CREATE_STUDENTS_TABLE)
        await db.execute(CREATE_PAYMENTS_TABLE)
        await db.commit()


async def upsert_student(telegram_id: int, full_name: str, phone: str,
                          grade: int, course_key: str, amount: int) -> int:
    """O'quvchini bazaga qo'shadi yoki yangilaydi. Student id qaytaradi."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO students (telegram_id, full_name, phone, grade, course_key, amount, payment_status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, 'pending', ?)
            ON CONFLICT(telegram_id) DO UPDATE SET
                full_name=excluded.full_name,
                phone=excluded.phone,
                grade=excluded.grade,
                course_key=excluded.course_key,
                amount=excluded.amount,
                payment_status='pending',
                created_at=excluded.created_at
            """,
            (telegram_id, full_name, phone, grade, course_key, amount, datetime.now().isoformat()),
        )
        await db.commit()
        cursor = await db.execute("SELECT id FROM students WHERE telegram_id = ?", (telegram_id,))
        row = await cursor.fetchone()
        return row[0]


async def get_student_by_telegram_id(telegram_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM students WHERE telegram_id = ?", (telegram_id,))
        return await cursor.fetchone()


async def get_student_by_id(student_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM students WHERE id = ?", (student_id,))
        return await cursor.fetchone()


async def mark_payment_created(student_id: int, click_trans_id: str, merchant_trans_id: str, amount: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT INTO payments (student_id, click_trans_id, merchant_trans_id, amount, status, created_at)
               VALUES (?, ?, ?, ?, 'created', ?)""",
            (student_id, click_trans_id, merchant_trans_id, amount, datetime.now().isoformat()),
        )
        await db.commit()


async def mark_payment_confirmed(merchant_trans_id: str, click_trans_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE payments SET status='confirmed', click_trans_id=? WHERE merchant_trans_id=?",
            (click_trans_id, merchant_trans_id),
        )
        await db.execute(
            "UPDATE students SET payment_status='paid' WHERE id=?",
            (int(merchant_trans_id),),
        )
        await db.commit()


async def mark_payment_cancelled(merchant_trans_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE payments SET status='cancelled' WHERE merchant_trans_id=?",
            (merchant_trans_id,),
        )
        await db.execute(
            "UPDATE students SET payment_status='cancelled' WHERE id=?",
            (int(merchant_trans_id),),
        )
        await db.commit()


async def get_all_students():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM students ORDER BY created_at DESC")
        return await cursor.fetchall()


async def get_stats():
    """Kurs bo'yicha va umumiy statistika."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        total = await (await db.execute("SELECT COUNT(*) as c FROM students")).fetchone()
        paid = await (await db.execute("SELECT COUNT(*) as c FROM students WHERE payment_status='paid'")).fetchone()
        revenue = await (await db.execute(
            "SELECT COALESCE(SUM(amount),0) as s FROM students WHERE payment_status='paid'"
        )).fetchone()
        by_course_cursor = await db.execute(
            """SELECT course_key, COUNT(*) as cnt,
                      SUM(CASE WHEN payment_status='paid' THEN 1 ELSE 0 END) as paid_cnt
               FROM students GROUP BY course_key"""
        )
        by_course = await by_course_cursor.fetchall()
        return {
            "total": total["c"],
            "paid": paid["c"],
            "revenue": revenue["s"],
            "by_course": by_course,
        }


async def get_all_telegram_ids():
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT telegram_id FROM students")
        rows = await cursor.fetchall()
        return [r[0] for r in rows]
