import sqlite3


class SchoolDatabase:
    def __init__(self, db_name='bd_rksi_schedule.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

    def create_tables(self):
        # Таблица преподавателей
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS teachers (
                id INTEGER PRIMARY KEY,
                fullname TEXT
            )
        ''')

        # Таблица групп
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS groups (
                id INTEGER PRIMARY KEY,
                name TEXT
            )
        ''')

        # Таблица предметов
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS subjects (
                id INTEGER PRIMARY KEY,
                name TEXT
            )
        ''')
        self.cursor.execute('''
                    CREATE TABLE IF NOT EXISTS cards (
                        id_card INTEGER PRIMARY KEY,
                        num_para TEXT,
                        room TEXT,
                        id_teacher INTEGER,
                        id_group INTEGER,
                        id_subject INTEGER,
                        FOREIGN KEY (id_teacher) REFERENCES teachers(id),
                        FOREIGN KEY (id_group) REFERENCES groups(id),
                        FOREIGN KEY (id_subject) REFERENCES subjects(id)
                    )
                ''')
        self.conn.commit()

    def get_teacher_id_by_name(self, teacher_name):
            self.cursor.execute('SELECT id FROM teachers WHERE fullname = ?', (teacher_name,))
            result = self.cursor.fetchone()
            if result:
                return result[0]
            else:
                return None

    def get_group_id_by_name(self, group_name):
            self.cursor.execute('SELECT id FROM groups WHERE name = ?', (group_name,))
            result = self.cursor.fetchone()
            if result:
                return result[0]
            else:
                return None

    def get_subject_id_by_name(self, subject_name):
            self.cursor.execute('SELECT id FROM subjects WHERE name = ?', (subject_name,))
            result = self.cursor.fetchone()
            if result:
                return result[0]
            else:
                return None


    def close_connection(self):
        self.conn.close()
