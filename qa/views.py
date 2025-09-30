import pandas as pd
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_datetime
from django.shortcuts import render
from .models import Sprint, UserStory, Defect, TestCase, Effort, DefectStatus, Comment, TestResult
from django.http import JsonResponse, HttpResponse
from datetime import datetime
from django.db import transaction


def home(request):
    return render(request, "home.html", {
        "sprints": Sprint.objects.all(),
        "all_stories": UserStory.objects.all(),
        "defect_status": DefectStatus.values,
    })

def userstories_view(request):
    sprint_id = request.GET.get("sprint")
    qs = UserStory.objects.all()
    if sprint_id:
        qs = qs.filter(sprint_id=sprint_id)
    return render(request, "qa/partials/userstories_table.html", {"userstories": qs})

def defects_view(request):
    sprint_id = request.GET.get("sprint")
    story_id = request.GET.get("user_story")
    status = request.GET.get("status")
    qs = Defect.objects.all()
    if sprint_id:
        qs = qs.filter(user_story__sprint_id=sprint_id)
    if story_id:
        qs = qs.filter(user_story_id=story_id)
    if status:
        qs = qs.filter(status=status)
    return render(request, "qa/partials/defects_table.html", {"defects": qs})

def testcases_view(request):
    story_id = request.GET.get("user_story")
    qs = TestCase.objects.all()
    if story_id:
        qs = qs.filter(user_story_id=story_id)
    return render(request, "qa/partials/testcases_table.html", {"testcases": qs})

def efforts_view(request):
    story_id = request.GET.get("user_story")
    qs = Effort.objects.all()
    if story_id:
        qs = qs.filter(user_story_id=story_id)
    return render(request, "qa/partials/efforts_table.html", {"efforts": qs})

def userstories_for_sprint(request):
    sprint_id = request.GET.get("sprint_id")
    qs = UserStory.objects.all()
    if sprint_id:
        qs = qs.filter(sprint_id=sprint_id)
    data = [{"id": s.id, "title": s.title} for s in qs]
    return JsonResponse(data, safe=False)

def safe_date(val, only_date=False):
    """Normalize Excel/Pandas date/time values into Python datetime/date or None."""
    if val is None or pd.isna(val):
        return None

    import numpy as np

    if isinstance(val, pd.Timestamp):
        return val.to_pydatetime().date() if only_date else val.to_pydatetime()

    if isinstance(val, (np.datetime64,)):
        dt = pd.to_datetime(val).to_pydatetime()
        return dt.date() if only_date else dt

    if isinstance(val, (int, float)):
        try:
            dt = pd.to_datetime(val, unit="D", origin="1899-12-30")
            return dt.date() if only_date else dt.to_pydatetime()
        except Exception:
            return None

    if isinstance(val, datetime):
        return val.date() if only_date else val

    if isinstance(val, str):
        try:
            dt = datetime.fromisoformat(val)
            return dt.date() if only_date else dt
        except Exception:
            try:
                dt = pd.to_datetime(val).to_pydatetime()
                return dt.date() if only_date else dt
            except Exception:
                return None

    return None


def upload_file(request):
    if request.method == "POST" and request.FILES.get("file"):
        file = request.FILES["file"]
        try:
            xl = pd.ExcelFile(file)

            # --- Helper: bulk insert or update ---
            def bulk_upsert(model, objs, fields, batch_size = 1000):
                """Insert new objects and update existing ones."""
                if not objs:
                    return
                # Separate new and existing
                ids = [obj.id for obj in objs if obj.id is not None]
                existing = model.objects.filter(id__in=ids).values_list("id", flat=True)

                to_create = [obj for obj in objs if obj.id not in existing]
                to_update = [obj for obj in objs if obj.id in existing]

                if to_create:
                    model.objects.bulk_create(to_create, ignore_conflicts=True)
                if to_update:
                    model.objects.bulk_update(to_update, fields)

            # --- Sprints ---
            if "sprints" in xl.sheet_names:
                df = xl.parse("sprints")
                objs = []
                for _, row in df.iterrows():
                    objs.append(Sprint(
                        id=row["id"],
                        name=row["name"],
                        start_date=safe_date(row.get("start_date"), only_date=True),
                        end_date=safe_date(row.get("end_date"), only_date=True),
                        goal=row.get("goal"),
                    ))
                bulk_upsert(Sprint, objs, ["name", "start_date", "end_date", "goal"])

            # --- User Stories ---
            if "userstories" in xl.sheet_names:
                df = xl.parse("userstories")
                objs = []
                for _, row in df.iterrows():
                    sprint = Sprint.objects.filter(id=row.get("sprint_id")).first()
                    objs.append(UserStory(
                        id=row["id"],
                        sprint=sprint,
                        title=row["title"],
                        description=row.get("description"),
                        created_by=row.get("created_by"),
                        status=row.get("status"),
                        story_points=row.get("story_points"),
                    ))
                bulk_upsert(UserStory, objs, ["sprint", "title", "description", "created_by", "status", "story_points"])

            # --- Test Cases ---
            if "testcases" in xl.sheet_names:
                df = xl.parse("testcases")
                objs = []
                for _, row in df.iterrows():
                    story = UserStory.objects.filter(id=row.get("user_story_id")).first()
                    objs.append(TestCase(
                        id=row["id"],
                        user_story=story,
                        title=row["title"],
                        description=row.get("description"),
                        created_by=row.get("created_by"),
                    ))
                bulk_upsert(TestCase, objs, ["user_story", "title", "description", "created_by"])

            # --- Defects ---
            if "defects" in xl.sheet_names:
                df = xl.parse("defects")
                objs = []
                for _, row in df.iterrows():
                    story = UserStory.objects.filter(id=row.get("user_story_id")).first()
                    tc = TestCase.objects.filter(id=row.get("test_case_id")).first()
                    objs.append(Defect(
                        id=row["id"],
                        user_story=story,
                        test_case=tc,
                        title=row.get("title"),
                        description=row.get("description"),
                        status=row.get("status"),
                        severity=row.get("severity"),
                        priority=row.get("priority"),
                        reported_by=row.get("reported_by"),
                        assigned_to=row.get("assigned_to"),
                    ))
                bulk_upsert(Defect, objs, ["user_story", "test_case", "title", "description",
                                           "status", "severity", "priority", "reported_by", "assigned_to"])

            # --- Efforts ---
            if "efforts" in xl.sheet_names:
                df = xl.parse("efforts")
                objs = []
                for _, row in df.iterrows():
                    story = UserStory.objects.filter(id=row.get("user_story_id")).first()
                    objs.append(Effort(
                        id=row["id"],
                        user_story=story,
                        user=row.get("user_name"),
                        effort_type=row.get("effort_type"),
                        hours=row.get("hours"),
                        logged_at=safe_date(row.get("logged_at")),
                    ))
                bulk_upsert(Effort, objs, ["user_story", "user", "effort_type", "hours", "logged_at"])

            return JsonResponse({"success": True, "message": "All sheets uploaded successfully"})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "No file uploaded"})