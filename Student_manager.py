# student_manager.py
"""
Advanced Student Management System (CLI)
Features:
- Add student (name, roll, age, subjects->marks)
- View all students, view single student
- Update student fields and marks
- Delete student
- Search by name/roll or by mark range for a subject
- Save/load from JSON (auto-save)
- Export to CSV / import from JSON
"""

import json
from pathlib import Path
from typing import List, Dict, Optional
import csv

DATA_FILE = Path("students.json")


class Student:
    def __init__(self, sid: str, name: str, roll: str, age: int, subjects: Dict[str, float]):
        self.id = sid             # string id
        self.name = name.strip()
        self.roll = roll.strip()
        self.age = int(age)
        # subjects is dict: {"math": 90, "eng": 85}
        self.subjects = {k.strip(): float(v) for k, v in subjects.items()}

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "roll": self.roll,
            "age": self.age,
            "subjects": self.subjects
        }

    @staticmethod
    def from_dict(data: Dict):
        return Student(data["id"], data["name"], data["roll"], data["age"], data.get("subjects", {}))

    def total_marks(self) -> float:
        return sum(self.subjects.values())

    def average(self) -> float:
        return self.total_marks() / (len(self.subjects) or 1)

    def __str__(self):
        subj = ", ".join(f"{k}:{v}" for k, v in self.subjects.items())
        return f"{self.id} | {self.name} | Roll:{self.roll} | Age:{self.age} | Avg:{self.average():.2f} | {subj}"


class StudentManager:
    def __init__(self, path: Path = DATA_FILE):
        self.path = path
        self.students: List[Student] = []
        self.__load()

    def __load(self):
        if self.path.exists():
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.students = [Student.from_dict(d) for d in data]
            except Exception as e:
                print("Warning: failed to load data:", e)
                self.students = []
        else:
            self.students = []

    def __save(self):
        data = [s.to_dict() for s in self.students]
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def __next_id(self) -> str:
        if not self.students:
            return "1"
        return str(max(int(s.id) for s in self.students) + 1)

    def add_student(self, name: str, roll: str, age: int, subjects: Dict[str, float]) -> Student:
        sid = self.__next_id()
        s = Student(sid, name, roll, age, subjects)
        self.students.append(s)
        self.__save()
        return s

    def list_students(self, limit: Optional[int] = None) -> List[Student]:
        sorted_list = sorted(self.students, key=lambda x: x.name.lower())
        return sorted_list[:limit] if limit else sorted_list

    def find_by_id(self, sid: str) -> Optional[Student]:
        for s in self.students:
            if s.id == sid:
                return s
        return None

    def find_by_roll(self, roll: str) -> Optional[Student]:
        for s in self.students:
            if s.roll == roll:
                return s
        return None

    def delete_student(self, sid: str) -> bool:
        s = self.find_by_id(sid)
        if not s:
            return False
        self.students.remove(s)
        self.__save()
        return True

    def update_student(self, sid: str, name: Optional[str] = None, roll: Optional[str] = None,
                       age: Optional[int] = None, subjects: Optional[Dict[str, float]] = None) -> bool:
        s = self.find_by_id(sid)
        if not s:
            return False
        if name is not None:
            s.name = name.strip()
        if roll is not None:
            s.roll = roll.strip()
        if age is not None:
            s.age = int(age)
        if subjects is not None:
            # merge subjects: replace provided subjects keys, keep others
            for k, v in subjects.items():
                s.subjects[k.strip()] = float(v)
        self.__save()
        return True

    def search(self, term: str) -> List[Student]:
        t = term.lower()
        return [s for s in self.students if t in s.name.lower() or t in s.roll.lower() or t in s.id]

    def search_by_subject_range(self, subject: str, low: Optional[float] = None, high: Optional[float] = None) -> List[Student]:
        res = []
        sub = subject.strip().lower()
        for s in self.students:
            for k, v in s.subjects.items():
                if k.lower() == sub:
                    if low is not None and v < low:
                        break
                    if high is not None and v > high:
                        break
                    res.append(s)
                    break
        return res

    def export_csv(self, filename: str = "students_export.csv"):
        # gather all subjects to create columns
        subjects = set()
        for s in self.students:
            subjects.update(s.subjects.keys())
        subjects = sorted(subjects)
        keys = ["id", "name", "roll", "age"] + subjects
        with open(filename, "w", newline='', encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=keys)
            writer.writeheader()
            for s in self.students:
                row = {"id": s.id, "name": s.name, "roll": s.roll, "age": s.age}
                for sub in subjects:
                    row[sub] = s.subjects.get(sub, "")
                writer.writerow(row)
        return filename

    def import_json(self, filename: str):
        p = Path(filename)
        if not p.exists():
            raise FileNotFoundError(filename)
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
        # assume list of student dicts
        for d in data:
            try:
                # avoid id collisions: create new id
                subjects = d.get("subjects", {})
                self.add_student(d.get("name", "unknown"), d.get("roll", ""), d.get("age", 0), subjects)
            except Exception:
                continue


def pretty_print_students(students: List[Student]):
    if not students:
        print("No students found.")
        return
    print(f"{'ID':<4} {'NAME':<20} {'ROLL':<10} {'AGE':<5} {'AVG':<6} SUBJECTS")
    print("-" * 80)
    for s in students:
        subj = "; ".join(f"{k}:{v}" for k, v in s.subjects.items())
        print(f"{s.id:<4} {s.name:<20} {s.roll:<10} {s.age:<5} {s.average():<6.2f} {subj}")


def input_subjects_interactive() -> Dict[str, float]:
    print("Enter subjects and marks. Type empty subject name to stop.")
    subs = {}
    while True:
        name = input(" Subject name (e.g. math): ").strip()
        if not name:
            break
        val = input(f"  Marks for {name}: ").strip()
        try:
            v = float(val)
        except ValueError:
            print("  Invalid number, try again.")
            continue
        subs[name] = v
    return subs


def cli():
    mgr = StudentManager()
    print("Student Management CLI")
    while True:
        print("\nOptions:")
        print("1) Add student")
        print("2) List all students")
        print("3) View student by ID")
        print("4) Find by roll")
        print("5) Update student")
        print("6) Delete student")
        print("7) Search name/roll")
        print("8) Search by subject & mark range")
        print("9) Export CSV")
        print("10) Import JSON")
        print("0) Quit")
        ch = input("Choose: ").strip()

        if ch == "1":
            name = input("Name: ").strip()
            roll = input("Roll: ").strip()
            age = input("Age: ").strip()
            try:
                age_val = int(age)
            except ValueError:
                print("Invalid age. Using 0.")
                age_val = 0
            subjects = input_subjects_interactive()
            s = mgr.add_student(name, roll, age_val, subjects)
            print("Added:", s)

        elif ch == "2":
            pretty_print_students(mgr.list_students())

        elif ch == "3":
            sid = input("Student ID: ").strip()
            s = mgr.find_by_id(sid)
            if not s:
                print("Not found.")
            else:
                print(s)

        elif ch == "4":
            roll = input("Roll: ").strip()
            s = mgr.find_by_roll(roll)
            if not s:
                print("Not found.")
            else:
                print(s)

        elif ch == "5":
            sid = input("Student ID to update: ").strip()
            s = mgr.find_by_id(sid)
            if not s:
                print("Not found.")
                continue
            print("Current:", s)
            new_name = input(f"Name [{s.name}]: ").strip()
            new_roll = input(f"Roll [{s.roll}]: ").strip()
            new_age = input(f"Age [{s.age}]: ").strip()
            print("Update subjects? (y/n)")
            subjects_update = None
            if input().strip().lower().startswith("y"):
                subjects_update = input_subjects_interactive()
            try:
                age_val = int(new_age) if new_age else None
                ok = mgr.update_student(sid, name=new_name or None, roll=new_roll or None, age=age_val, subjects=subjects_update)
                print("Updated." if ok else "Failed.")
            except Exception as exc:
                print("Error:", exc)

        elif ch == "6":
            sid = input("Student ID to delete: ").strip()
            ok = mgr.delete_student(sid)
            print("Deleted." if ok else "Not found.")

        elif ch == "7":
            term = input("Search term (name or roll): ").strip()
            pretty_print_students(mgr.search(term))

        elif ch == "8":
            subject = input("Subject name: ").strip()
            low = input("Low mark (empty = no low): ").strip()
            high = input("High mark (empty = no high): ").strip()
            low_val = float(low) if low else None
            high_val = float(high) if high else None
            pretty_print_students(mgr.search_by_subject_range(subject, low_val, high_val))

        elif ch == "9":
            fn = input("CSV filename (default students_export.csv): ").strip() or "students_export.csv"
            mgr.export_csv(fn)
            print("Exported to", fn)

        elif ch == "10":
            fn = input("JSON filename to import: ").strip()
            try:
                mgr.import_json(fn)
                print("Imported.")
            except Exception as exc:
                print("Import failed:", exc)

        elif ch == "0":
            print("Bye — data saved.")
            break

        else:
            print("Invalid choice.")


if __name__ == "__main__":
    cli()