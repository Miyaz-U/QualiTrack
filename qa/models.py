from django.db import models
from django.db.models import Q

# --- ENUMS OUTSIDE MODELS ---

class UserStoryStatus(models.TextChoices):
    NEW = "New"
    IN_PROGRESS = "In Progress"
    DONE = "Done"
    CLOSED = "Closed"


class TestResultStatus(models.TextChoices):
    PASS_ = "Pass"
    FAIL = "Fail"
    BLOCKED = "Blocked"
    SKIPPED = "Skipped"


class DefectStatus(models.TextChoices):
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    RESOLVED = "Resolved"
    CLOSED = "Closed"


class DefectSeverity(models.TextChoices):
    CRITICAL = "Critical"
    MAJOR = "Major"
    MINOR = "Minor"


class DefectPriority(models.TextChoices):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class EffortType(models.TextChoices):
    CREATION = "Creation"
    TESTING = "Testing"
    ANALYSIS = "Analysis"
    FIXING = "Fixing"

# --- MODELS ---

class Sprint(models.Model):
    name = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    goal = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class UserStory(models.Model):
    sprint = models.ForeignKey("Sprint", on_delete=models.CASCADE, related_name="user_stories",
                               blank=True, null=True)
    title = models.TextField()
    description = models.TextField(blank=True, null=True)
    created_by = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.TextField(choices=UserStoryStatus.choices, blank=True, null=True)
    story_points = models.IntegerField(blank=True, null=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=Q(status__in=UserStoryStatus.values) | Q(status__isnull=True),
                name="user_stories_status_check",
            )
        ]


class TestCase(models.Model):
    user_story = models.ForeignKey("UserStory", on_delete=models.CASCADE,
                                   related_name="test_cases", blank=True, null=True)
    title = models.TextField()
    description = models.TextField(blank=True, null=True)
    created_by = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"TC-{self.pk}: {self.title}"


class TestResult(models.Model):
    test_case = models.ForeignKey("TestCase", on_delete=models.CASCADE, related_name="results")
    executed_by = models.TextField(blank=True, null=True)
    executed_at = models.DateTimeField(auto_now_add=True)
    result = models.TextField(choices=TestResultStatus.choices, blank=True, null=True)
    environment = models.TextField(blank=True, null=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=Q(result__in=TestResultStatus.values) | Q(result__isnull=True),
                name="test_results_result_check",
            )
        ]


class Defect(models.Model):
    user_story = models.ForeignKey("UserStory", on_delete=models.CASCADE, related_name="defects",
                                   blank=True, null=True)
    test_case = models.ForeignKey("TestCase", on_delete=models.SET_NULL, related_name="defects",
                                  blank=True, null=True)
    title = models.TextField()
    description = models.TextField(blank=True, null=True)
    status = models.TextField(choices=DefectStatus.choices, blank=True, null=True)
    severity = models.TextField(choices=DefectSeverity.choices, blank=True, null=True)
    priority = models.TextField(choices=DefectPriority.choices, blank=True, null=True)
    reported_by = models.TextField(blank=True, null=True)
    assigned_to = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=Q(status__in=DefectStatus.values) | Q(status__isnull=True),
                name="defects_status_check",
            ),
            models.CheckConstraint(
                check=Q(severity__in=DefectSeverity.values) | Q(severity__isnull=True),
                name="defects_severity_check",
            ),
            models.CheckConstraint(
                check=Q(priority__in=DefectPriority.values) | Q(priority__isnull=True),
                name="defects_priority_check",
            ),
        ]


class Comment(models.Model):
    defect = models.ForeignKey("Defect", on_delete=models.CASCADE,
                               related_name="comments", blank=True, null=True)
    user_story = models.ForeignKey("UserStory", on_delete=models.CASCADE,
                                   related_name="comments", blank=True, null=True)
    author = models.TextField(blank=True, null=True)
    comment_text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Effort(models.Model):
    user_story = models.ForeignKey("UserStory", on_delete=models.CASCADE, related_name="efforts", blank=True, null=True)
    user = models.TextField(db_column="user")  # keeps DB column name "user"
    effort_type = models.TextField(choices=EffortType.choices)
    hours = models.FloatField()
    logged_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=Q(effort_type__in=EffortType.values),
                name="efforts_effort_type_check",
            )
        ]