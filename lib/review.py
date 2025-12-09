from __init__ import CURSOR, CONN
from department import Department
from employee import Employee


class Review:

    all = {}

    def __init__(self, year, summary, employee_id, id=None):
        self.id = id
        self.year = year
        self.summary = summary
        self.employee_id = employee_id

    def __repr__(self):
        return (
            f"<Review {self.id}: {self.year}, {self.summary}, "
            + f"Employee: {self.employee_id}>"
        )

    @classmethod
    def create_table(cls):
        sql = """
            CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY,
            year INT,
            summary TEXT,
            employee_id INTEGER,
            FOREIGN KEY (employee_id) REFERENCES employees(id))
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        sql = """DROP TABLE IF EXISTS reviews;"""
        CURSOR.execute(sql)
        CONN.commit()

    # --------------------
    # ORM SAVE
    # --------------------
    def save(self):
        if self.id is None:
            sql = """
                INSERT INTO reviews (year, summary, employee_id)
                VALUES (?, ?, ?)
            """
            CURSOR.execute(sql, (self.year, self.summary, self.employee_id))
            CONN.commit()

            self.id = CURSOR.lastrowid
            Review.all[self.id] = self

    # --------------------
    # ORM CREATE
    # --------------------
    @classmethod
    def create(cls, year, summary, employee_id):
        review = cls(year, summary, employee_id)
        review.save()
        return review

    # --------------------
    # instance_from_db
    # --------------------
    @classmethod
    def instance_from_db(cls, row):
        id, year, summary, employee_id = row

        if id in cls.all:
            instance = cls.all[id]
            instance.year = year
            instance.summary = summary
            instance.employee_id = employee_id
        else:
            instance = cls(year, summary, employee_id, id=id)
            cls.all[id] = instance

        return instance

    # --------------------
    # FIND BY ID
    # --------------------
    @classmethod
    def find_by_id(cls, id):
        row = CURSOR.execute(
            "SELECT * FROM reviews WHERE id = ?",
            (id,)
        ).fetchone()

        if row:
            return cls.instance_from_db(row)
        return None

    # --------------------
    # UPDATE
    # --------------------
    def update(self):
        sql = """
            UPDATE reviews
            SET year = ?, summary = ?, employee_id = ?
            WHERE id = ?
        """
        CURSOR.execute(sql, (self.year, self.summary, self.employee_id, self.id))
        CONN.commit()

        Review.all[self.id] = self

    # --------------------
    # DELETE
    # --------------------
    def delete(self):
        CURSOR.execute("DELETE FROM reviews WHERE id = ?", (self.id,))
        CONN.commit()

        del Review.all[self.id]
        self.id = None

    # --------------------
    # GET ALL
    # --------------------
    @classmethod
    def get_all(cls):
        rows = CURSOR.execute("SELECT * FROM reviews").fetchall()
        return [cls.instance_from_db(row) for row in rows]

    # --------------------
    # PROPERTY METHODS
    # --------------------
    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, value):
        if type(value) is not int or value < 2000:
            raise ValueError("Year must be an integer >= 2000.")
        self._year = value

    @property
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, value):
        if type(value) is not str or value.strip() == "":
            raise ValueError("Summary must be a non-empty string.")
        self._summary = value

    @property
    def employee_id(self):
        return self._employee_id

    @employee_id.setter
    def employee_id(self, value):
        if type(value) is not int:
            raise ValueError("employee_id must be an integer.")

        # ensure employee exists in DB
        if not Employee.find_by_id(value):
            raise ValueError("Employee must exist in DB before assigning review.")

        self._employee_id = value

