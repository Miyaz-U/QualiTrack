import pandas as pd
from django.core.management.base import BaseCommand
from qa.models import Sprint, UserStory, Defect, TestCase, Effort

class Command(BaseCommand):
    help = "Load sample data from Test Sample Data.xlsx into the database"

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=str,
            default="TestSampleData.xlsx",
            help="Path to the Excel file",
        )

    def handle(self, *args, **options):
        file_path = options["file"]

        self.stdout.write(self.style.NOTICE(f"Reading Excel file: {file_path}"))

        # ---- Load Sprints ----
        try:
            df_sprints = pd.read_excel(file_path, sheet_name="sprints")
            for _, row in df_sprints.iterrows():
                Sprint.objects.get_or_create(
                    id=row.get("ID"),
                    defaults={
                        "name": row.get("name"),
                        "start_date": row.get("start_date"),
                        "end_date": row.get("end_date"),
                        "goal": row.get("goal"),
                    },
                )
            self.stdout.write(self.style.SUCCESS("Loaded Sprints"))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"No Sprints sheet found ({e})"))

        # ---- Load User Stories ----
        try:
            df_stories = pd.read_excel(file_path, sheet_name="userstories")
            for _, row in df_stories.iterrows():
                sprint = None
                if not pd.isna(row.get("sprint_id")):
                    sprint = Sprint.objects.filter(id=int(row["sprint_id"])).first()

                UserStory.objects.get_or_create(
                    id=row.get("ID"),
                    defaults={
                        "sprint": sprint,
                        "title": row.get("title"),
                        "description": row.get("description"),
                        "created_by": row.get("created_by"),
                        "status": row.get("status"),
                        "story_points": row.get("story_points"),
                    },
                )
            self.stdout.write(self.style.SUCCESS("Loaded User Stories"))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"No UserStories sheet found ({e})"))

        # ---- Load Test Cases ----
        try:
            df_tc = pd.read_excel(file_path, sheet_name="testcases")
            for _, row in df_tc.iterrows():
                story = None
                if not pd.isna(row.get("userstory_id")):
                    story = UserStory.objects.filter(id=int(row["userstory_id"])).first()

                TestCase.objects.get_or_create(
                    id=row.get("ID"),
                    defaults={
                        "user_story": story,
                        "title": row.get("title"),
                        "description": row.get("description"),
                        "created_by": row.get("created_by"),
                    },
                )
            self.stdout.write(self.style.SUCCESS("Loaded Test Cases"))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"No TestCases sheet found ({e})"))

        # ---- Load Defects ----
        try:
            df_defects = pd.read_excel(file_path, sheet_name="defects")
            for _, row in df_defects.iterrows():
                story = None
                if not pd.isna(row.get("userstory_id")):
                    story = UserStory.objects.filter(id=int(row["userstory_id"])).first()
                test_case = None
                if not pd.isna(row.get("testcase_id")):
                    test_case = TestCase.objects.filter(id=int(row["testcase_id"])).first()

                Defect.objects.get_or_create(
                    id=row.get("ID"),
                    defaults={
                        "user_story": story,
                        "test_case": test_case,
                        "title": row.get("title"),
                        "description": row.get("description"),
                        "status": row.get("status"),
                        "severity": row.get("severity"),
                        "priority": row.get("priority"),
                        "reported_by": row.get("reported_by"),
                        "assigned_to": row.get("assigned_to"),
                    },
                )
            self.stdout.write(self.style.SUCCESS("Loaded Defects"))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"No Defects sheet found ({e})"))

        # ---- Load Efforts ----
        try:
            df_efforts = pd.read_excel(file_path, sheet_name="efforts")
            for _, row in df_efforts.iterrows():
                story = None
                if not pd.isna(row.get("userstory_id")):
                    story = UserStory.objects.filter(id=int(row["userstory_id"])).first()

                Effort.objects.get_or_create(
                    id=row.get("ID"),
                    defaults={
                        "user_story": story,
                        "user": row.get("user_name"),
                        "effort_type": row.get("effort_type"),
                        "hours": row.get("hours"),
                    },
                )
            self.stdout.write(self.style.SUCCESS("Loaded Efforts"))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"No Efforts sheet found ({e})"))
