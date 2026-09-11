from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker


# =========================================================
# PROJECT PATH
# =========================================================

ROOT_PATH = Path(__file__).resolve().parent


# =========================================================
# MYSQL CONFIGURATION
# =========================================================

DB_USER = "root"
DB_PASSWORD = "root"
DB_HOST = "localhost"
DB_PORT = "3306"
DB_NAME = "student_db"


DATABASE_URL = (
    f"mysql+pymysql://"
    f"{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)


# =========================================================
# DATABASE CONNECTION
# =========================================================

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=False
)


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)


Base = declarative_base()


# =========================================================
# STUDENT TABLE
# =========================================================

class Student(Base):

    __tablename__ = "students"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    roll_no = Column(
        String(50),
        unique=True,
        nullable=False
    )

    name = Column(
        String(100),
        nullable=False
    )

    course = Column(
        String(100),
        nullable=False
    )


# =========================================================
# CREATE TABLE
# =========================================================

Base.metadata.create_all(bind=engine)


# =========================================================
# PYDANTIC MODELS
# =========================================================

class StudentCreate(BaseModel):

    roll_no: str
    name: str
    course: str


class StudentUpdate(BaseModel):

    roll_no: str
    name: str
    course: str


# =========================================================
# FASTAPI APP
# =========================================================

app = FastAPI(
    title="Student Management System",
    version="1.0.0"
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)


# =========================================================
# HOME PAGE
# =========================================================

@app.get("/")
def home():

    index_file = ROOT_PATH / "index.html"

    if not index_file.exists():

        raise HTTPException(
            status_code=404,
            detail=f"index.html not found: {index_file}"
        )

    return FileResponse(
        index_file,
        media_type="text/html"
    )


# =========================================================
# CSS
# =========================================================

@app.get("/style.css")
def get_css():

    css_file = ROOT_PATH / "style.css"

    if not css_file.exists():

        raise HTTPException(
            status_code=404,
            detail=f"style.css not found: {css_file}"
        )

    return FileResponse(
        css_file,
        media_type="text/css"
    )


# =========================================================
# GET ALL STUDENTS
# =========================================================

@app.get("/api/students")
def get_students():

    db = SessionLocal()

    try:

        students = (
            db.query(Student)
            .order_by(Student.id.desc())
            .all()
        )

        return [
            {
                "id": student.id,
                "roll_no": student.roll_no,
                "name": student.name,
                "course": student.course
            }
            for student in students
        ]

    finally:

        db.close()


# =========================================================
# GET STATISTICS
# =========================================================

@app.get("/api/students/stats")
def get_stats():

    db = SessionLocal()

    try:

        students = db.query(Student).all()

        python_count = 0
        java_count = 0
        web_count = 0

        for student in students:

            course = student.course.strip().lower()

            if course == "python":
                python_count += 1

            elif course == "java":
                java_count += 1

            elif course == "web development":
                web_count += 1

        return {
            "total": len(students),
            "python": python_count,
            "java": java_count,
            "web": web_count
        }

    finally:

        db.close()


# =========================================================
# ADD STUDENT
# =========================================================

@app.post("/api/students")
def add_student(student: StudentCreate):

    db = SessionLocal()

    try:

        roll_no = student.roll_no.strip()
        name = student.name.strip()
        course = student.course.strip()

        if not roll_no or not name or not course:

            raise HTTPException(
                status_code=400,
                detail="All fields are required"
            )

        existing_student = (
            db.query(Student)
            .filter(Student.roll_no == roll_no)
            .first()
        )

        if existing_student:

            raise HTTPException(
                status_code=400,
                detail="Roll number already exists"
            )

        new_student = Student(
            roll_no=roll_no,
            name=name,
            course=course
        )

        db.add(new_student)

        db.commit()

        db.refresh(new_student)

        return {
            "message": "Student added successfully",
            "student": {
                "id": new_student.id,
                "roll_no": new_student.roll_no,
                "name": new_student.name,
                "course": new_student.course
            }
        }

    except HTTPException:

        db.rollback()
        raise

    except Exception as error:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )

    finally:

        db.close()


# =========================================================
# UPDATE STUDENT
# =========================================================

@app.put("/api/students/{student_id}")
def update_student(
    student_id: int,
    student: StudentUpdate
):

    db = SessionLocal()

    try:

        roll_no = student.roll_no.strip()
        name = student.name.strip()
        course = student.course.strip()

        if not roll_no or not name or not course:

            raise HTTPException(
                status_code=400,
                detail="All fields are required"
            )

        existing_student = (
            db.query(Student)
            .filter(Student.id == student_id)
            .first()
        )

        if not existing_student:

            raise HTTPException(
                status_code=404,
                detail="Student not found"
            )

        duplicate_student = (
            db.query(Student)
            .filter(
                Student.roll_no == roll_no,
                Student.id != student_id
            )
            .first()
        )

        if duplicate_student:

            raise HTTPException(
                status_code=400,
                detail="Roll number already exists"
            )

        existing_student.roll_no = roll_no
        existing_student.name = name
        existing_student.course = course

        db.commit()

        db.refresh(existing_student)

        return {
            "message": "Student updated successfully",
            "student": {
                "id": existing_student.id,
                "roll_no": existing_student.roll_no,
                "name": existing_student.name,
                "course": existing_student.course
            }
        }

    except HTTPException:

        db.rollback()
        raise

    except Exception as error:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )

    finally:

        db.close()


# =========================================================
# DELETE STUDENT
# =========================================================

@app.delete("/api/students/{student_id}")
def delete_student(student_id: int):

    db = SessionLocal()

    try:

        student = (
            db.query(Student)
            .filter(Student.id == student_id)
            .first()
        )

        if not student:

            raise HTTPException(
                status_code=404,
                detail="Student not found"
            )

        db.delete(student)

        db.commit()

        return {
            "message": "Student deleted successfully"
        }

    except HTTPException:

        db.rollback()
        raise

    except Exception as error:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )

    finally:

        db.close()


# =========================================================
# RUN SERVER
# =========================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        reload=True
    )