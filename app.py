from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker


# =====================================================
# PROJECT PATH
# =====================================================

ROOT_PATH = Path(__file__).resolve().parent


# =====================================================
# MYSQL CONFIGURATION
# =====================================================

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


# =====================================================
# DATABASE CONNECTION
# =====================================================

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)


Base = declarative_base()


# =====================================================
# STUDENT TABLE
# =====================================================

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


# Create table automatically
Base.metadata.create_all(
    bind=engine
)


# =====================================================
# PYDANTIC MODELS
# =====================================================

class StudentCreate(BaseModel):

    roll_no: str
    name: str
    course: str


class StudentUpdate(BaseModel):

    roll_no: str
    name: str
    course: str


# =====================================================
# FASTAPI APPLICATION
# =====================================================

app = FastAPI(
    title="Student Management System API"
)


# =====================================================
# CORS
# =====================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]
)


# =====================================================
# HOME PAGE
# =====================================================

@app.get("/")
def home():

    return FileResponse(
        ROOT_PATH / "index.html"
    )


# =====================================================
# CSS FILE
# IMPORTANT FIX
# =====================================================

@app.get("/style.css")
def get_css():

    return FileResponse(
        ROOT_PATH / "style.css",
        media_type="text/css"
    )


# =====================================================
# SHOW ALL STUDENTS
# =====================================================

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

                "roll_no":
                    student.roll_no,

                "name":
                    student.name,

                "course":
                    student.course
            }

            for student in students

        ]

    finally:

        db.close()


# =====================================================
# STUDENT STATISTICS
# =====================================================

@app.get("/api/students/stats")
def get_stats():

    db = SessionLocal()

    try:

        students = db.query(Student).all()


        return {

            "total":
                len(students),


            "python":
                sum(
                    student.course.lower()
                    == "python"
                    for student in students
                ),


            "java":
                sum(
                    student.course.lower()
                    == "java"
                    for student in students
                ),


            "web":
                sum(
                    student.course.lower()
                    == "web development"
                    for student in students
                )

        }

    finally:

        db.close()


# =====================================================
# ADD STUDENT
# =====================================================

@app.post("/api/students")
def add_student(
    student: StudentCreate
):

    db = SessionLocal()

    try:

        existing_student = (
            db.query(Student)
            .filter(
                Student.roll_no
                == student.roll_no
            )
            .first()
        )


        if existing_student:

            raise HTTPException(
                status_code=400,
                detail=
                    "Roll number already exists"
            )


        new_student = Student(

            roll_no=student.roll_no,

            name=student.name,

            course=student.course

        )


        db.add(new_student)

        db.commit()

        db.refresh(new_student)


        return {

            "message":
                "Student added successfully",

            "student": {

                "id":
                    new_student.id,

                "roll_no":
                    new_student.roll_no,

                "name":
                    new_student.name,

                "course":
                    new_student.course

            }

        }

    finally:

        db.close()


# =====================================================
# UPDATE STUDENT
# =====================================================

@app.put("/api/students/{student_id}")
def update_student(

    student_id: int,

    student: StudentUpdate

):

    db = SessionLocal()

    try:

        existing_student = (
            db.query(Student)
            .filter(
                Student.id
                == student_id
            )
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
                Student.roll_no
                == student.roll_no,

                Student.id
                != student_id
            )
            .first()
        )


        if duplicate_student:

            raise HTTPException(
                status_code=400,
                detail=
                    "Roll number already exists"
            )


        existing_student.roll_no = student.roll_no

        existing_student.name = student.name

        existing_student.course = student.course


        db.commit()

        db.refresh(
            existing_student
        )


        return {

            "message":
                "Student updated successfully",

            "student": {

                "id":
                    existing_student.id,

                "roll_no":
                    existing_student.roll_no,

                "name":
                    existing_student.name,

                "course":
                    existing_student.course

            }

        }

    finally:

        db.close()


# =====================================================
# DELETE STUDENT
# =====================================================

@app.delete("/api/students/{student_id}")
def delete_student(
    student_id: int
):

    db = SessionLocal()

    try:

        student = (
            db.query(Student)
            .filter(
                Student.id
                == student_id
            )
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

            "message":
                "Student deleted successfully"

        }

    finally:

        db.close()


# =====================================================
# RUN FASTAPI
# =====================================================

if __name__ == "__main__":

    import uvicorn


    uvicorn.run(

        "app:app",

        host="127.0.0.1",

        port=8000,

        reload=True

    )