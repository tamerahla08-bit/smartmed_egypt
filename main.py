"""Entry point. Run:  python main.py"""
import os
import hospital_database as db

if __name__ == "__main__":
    if not os.path.exists(db.DB_PATH):  # rebuild if hospitals.db is missing
        db.seed_database()
    import gui
    gui.run()
