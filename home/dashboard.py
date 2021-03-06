"""
To add a new dashboard section, there are three steps:

- Define a function that takes a request and returns a context
  value. If the value evaluates false, like False, None, [], or {},
  then this section will be skipped.

- The name of that function determines what template renders this
  section. For example, the function named "approval_status" gets
  the template named "home/dashboard/approval_status.html". Within
  the template, the section's context value is available under
  the name "section".

- Add the function name to the DASHBOARD_SECTIONS list at the end of
  this file. The order in which functions appear in that list
  determines the order that sections will be displayed on the
  dashboard, so you can reorder them easily.

The context value can be any type. Here are some examples:

- If the function returns {'x': ...}, the template can access that
  as "section.x".

- If it returns a list, then "{% for x in section %}" will loop over
  that list.
"""

from collections import defaultdict
import datetime

from .models import ApplicantApproval
from .models import ApprovalStatus
from .models import Community
from .models import Comrade
from .models import DASHBOARD_MODELS
from .models import MentorApproval
from .models import MentorRelationship
from .models import Participation
from .models import Role
from .models import RoundPage
from .models import get_deadline_date_for
from .models import has_deadline_passed

__all__ = ('get_dashboard_sections',)

def get_dashboard_sections(request):
    sections = []
    for section in DASHBOARD_SECTIONS:
        context = section(request)
        if context:
            template_name = "home/dashboard/{}.html".format(section.__name__)
            sections.append((template_name, context))
    return sections


def intern_announcement(request):
    now = datetime.datetime.now(datetime.timezone.utc)
    today = get_deadline_date_for(now)
    try:
        # Find the newest round whose intern announcement date has passed.
        current_round = RoundPage.objects.filter(
            internannounce__lte=today,
        ).latest('internannounce')
    except RoundPage.DoesNotExist:
        return None

    # Hide this message once the next round starts, where "starts" is defined
    # by pingnew, and "next round" means it has a later intern announcement
    # date than this one.
    later_open_rounds = RoundPage.objects.filter(
        pingnew__lte=today,
        internannounce__gt=current_round.internannounce,
    )
    if later_open_rounds.exists():
        return None

    roles = []
    if current_round.is_coordinator(request.user):
        roles.append("coordinator")
    if current_round.is_mentor(request.user):
        roles.append("mentor")
    if request.user.is_staff:
        roles.append("organizer")

    if not roles:
        return None

    return {
        'current_round': current_round,
        'role': ' and '.join(roles),
    }


def coordinator_reminder(request):
    now = datetime.datetime.now(datetime.timezone.utc)
    today = get_deadline_date_for(now)

    # It's possible that some intern selections may not work out, and a mentor
    # will have to select another intern after the intern announcement date.
    # Show coordinator's communities until the day after their mentors' interns
    # start.
    try:
        current_round = RoundPage.objects.filter(
            internstarts__gt=today,
        ).earliest('internstarts')
    except RoundPage.DoesNotExist:
        return None

    role = Role(request.user, current_round)
    if not role.approved_coordinator_communities:
        return None

    return role


def application_summary(request):
    now = datetime.datetime.now(datetime.timezone.utc)
    today = get_deadline_date_for(now)
    try:
        current_round = RoundPage.objects.get(
            appsopen__lte=today,
            internannounce__gt=today,
        )
    except RoundPage.DoesNotExist:
        return None

    try:
        if not request.user.is_staff and not current_round.is_reviewer(request.user):
            return None
    except Comrade.DoesNotExist:
        return None

    pending_revisions_count = ApplicantApproval.objects.filter(
            application_round = current_round,
            approval_status = ApprovalStatus.PENDING,
            barrierstoparticipation__applicant_should_update=True).count() + ApplicantApproval.objects.filter(
                    application_round = current_round,
                    approval_status = ApprovalStatus.PENDING,
                    schoolinformation__applicant_should_update=True).count()

    pending_applications_count = ApplicantApproval.objects.filter(
            application_round = current_round,
            approval_status = ApprovalStatus.PENDING).count() - pending_revisions_count

    rejected_applications_count = ApplicantApproval.objects.filter(
            application_round = current_round,
            approval_status = ApprovalStatus.REJECTED).count()
    approved_applications_count = ApplicantApproval.objects.filter(
            application_round = current_round,
            approval_status = ApprovalStatus.APPROVED).count()

    return {
        'pending_applications_count': pending_applications_count,
        'pending_revisions_count': pending_revisions_count,
        'rejected_applications_count': rejected_applications_count,
        'approved_applications_count': approved_applications_count,
    }


def staff_subscriptions(request):
    # This template doesn't need any data, it just needs to be
    # hidden for non-staff.
    return request.user.is_staff


# This is a list of all reminders that staff need at different times in the
# round. Each entry is of the form:
#   (field, delta, template, duration)
# where:
# - field is the name of a DateField on a RoundPage,
# - delta is a datetime.timedelta,
# - the template is supposed to be displayed on the date of field + delta,
# - and duration is a datetime.timedelta for how long the reminder stays
#   relevant.
#
# These templates are in home/dashboard/email/{name}.html
#
# It doesn't matter what order this list is in, but I think it's less confusing
# if we keep it sorted by when in the round each event occurs.
all_round_events = (
    ('appsclose', datetime.timedelta(weeks=-2), 'deadline-review'),
    ('appsclose', datetime.timedelta(weeks=-2, days=3), 'deadline-reminder'),
    ('appsclose', datetime.timedelta(weeks=-1), 'contributor-deadline-reminder'),
    ('appsclose', datetime.timedelta(weeks=-1), 'mentor-application-deadline-reminder-early'),
    ('appsclose', datetime.timedelta(days=-1), 'contributor-deadline-reminder'),
    ('appsclose', datetime.timedelta(), 'mentor-application-deadline-reminder-final'),
    ('appsclose', datetime.timedelta(), 'mentor-intern-selection-reminder'),
    ('appslate', datetime.timedelta(days=-1), 'contributor-deadline-reminder'),
    ('appslate', datetime.timedelta(), 'coordinator-intern-selection-reminder'),
    ('appslate', datetime.timedelta(), 'application-period-ended'),
    ('internannounce', datetime.timedelta(), 'intern-welcome'),
    ('internstarts', datetime.timedelta(weeks=0), 'internship-week-one'),
    ('initialfeedback', datetime.timedelta(weeks=-1), 'initial-feedback-instructions', datetime.timedelta(weeks=5)),
    ('internstarts', datetime.timedelta(weeks=2), 'internship-week-three'),
    ('internstarts', datetime.timedelta(weeks=4), 'internship-week-five'),
    ('internstarts', datetime.timedelta(weeks=6), 'internship-week-seven'),
    ('midfeedback', datetime.timedelta(weeks=-1), 'midpoint-feedback-instructions', datetime.timedelta(weeks=5)),
    ('finalfeedback', datetime.timedelta(weeks=-1), 'final-feedback-instructions', datetime.timedelta(weeks=5)),
)

def round_events(request):
    if not request.user.is_staff:
        return None

    now = datetime.datetime.now(datetime.timezone.utc)
    today = get_deadline_date_for(now)

    # How long before and after the ideal date should we display each reminder?
    early = datetime.timedelta(weeks=2)
    late = datetime.timedelta(weeks=1)

    events = []
    for field, delta, template, *rest in all_round_events:
        if rest:
            duration = rest[0]
        else:
            duration = datetime.timedelta()

        # We're looking for rounds where:
        #   target = field + delta
        #   target >= today - early
        #   target <= today + duration + late
        # but we can only query against field, so we do a little algebra to
        # shift the rest of each left-hand side over to the right.
        rounds = RoundPage.objects.filter(**{
            field + '__gte': today - delta - early,
            field + '__lte': today - delta + duration + late,
        })

        for current_round in rounds:
            events.append({
                'template': 'home/dashboard/email/{}.html'.format(template),
                'current_round': current_round,
                'due': getattr(current_round, field) + delta,
                'duration': duration,
            })

    if events:
        events.sort(key=lambda d: d['due'])
        return {
            'events': events,
            'today': today,
        }


def sponsor_statistics(request):
    if not request.user.is_staff:
        return None

    now = datetime.datetime.now(datetime.timezone.utc)
    today = get_deadline_date_for(now)
    try:
        return RoundPage.objects.filter(
            appsopen__lte=today,
        ).latest('appsopen')
    except RoundPage.DoesNotExist:
        return None


def staff_intern_progress(request):
    if not request.user.is_staff:
        return None

    now = datetime.datetime.now(datetime.timezone.utc)
    today = get_deadline_date_for(now)
    try:
        return RoundPage.objects.get(
            initialfeedback__lte=today + datetime.timedelta(days=7),
            finalfeedback__gt=today - datetime.timedelta(days=30),
        )
    except RoundPage.DoesNotExist:
        return None


def staff_intern_selection(request):
    if not request.user.is_staff:
        return None

    now = datetime.datetime.now(datetime.timezone.utc)
    today = get_deadline_date_for(now)
    try:
        return RoundPage.objects.get(
            appsopen__lte=today,
            initialfeedback__gt=today + datetime.timedelta(days=7),
        )
    except RoundPage.DoesNotExist:
        return None


def staff_community_progress(request):
    if not request.user.is_staff:
        return None

    now = datetime.datetime.now(datetime.timezone.utc)
    today = get_deadline_date_for(now)
    try:
        current_round = RoundPage.objects.get(
            appsopen__lte=today,
            internannounce__gt=today,
        )
    except RoundPage.DoesNotExist:
        return None

    pending_participations = Participation.objects.filter(
            participating_round = current_round,
            approval_status = ApprovalStatus.PENDING).order_by('community__name')
    approved_participations = Participation.objects.filter(
            participating_round = current_round,
            approval_status = ApprovalStatus.APPROVED).order_by('community__name')
    participations = list(pending_participations) + list(approved_participations)

    if not participations:
        return None

    return {
        'current_round': current_round,
        'participations': participations,
    }


def selected_intern(request):
    try:
        intern_selection = request.user.comrade.get_intern_selection()
    except Comrade.DoesNotExist:
        return None
    if not intern_selection:
        return None

    # No peeking! Wait for the announcement!
    if not intern_selection.round().has_intern_announcement_deadline_passed():
        return None

    # We could check here how long ago this intern's round was, and
    # maybe remove this section from their dashboard, if desired.

    return intern_selection


def intern(request):
    # TODO: move this function somewhere common
    # or TODO: merge with selected_intern above
    # This import can't be at top-level because views.py imports this
    # file so that would be a circular dependency.
    from .views import intern_in_good_standing
    return intern_in_good_standing(request.user)


def eligibility_prompts(request):
    now = datetime.datetime.now(datetime.timezone.utc)
    today = get_deadline_date_for(now)
    try:
        current_round = RoundPage.objects.get(
            appsopen__lte=today,
            appslate__gt=today,
        )
    except RoundPage.DoesNotExist:
        return None

    role = Role(request.user, current_round)

    return {
        'current_round': current_round,
        'role': role,
    }


def unselected_intern(request):
    """
    Display a message for people who filled out the eligibility form
    but didn't get selected. But only display it once the
    internannounce deadline has passed, and make the sad message go
    away a few weeks later when the selected interns start working on
    their internships.
    """
    now = datetime.datetime.now(datetime.timezone.utc)
    today = get_deadline_date_for(now)
    try:
        return ApplicantApproval.objects.exclude(
            internselection__organizer_approved=True,
        ).get(
            applicant__account=request.user,
            application_round__internannounce__lte=today,
            application_round__internstarts__gte=today,
        )
    except ApplicantApproval.DoesNotExist:
        return None


def mentor(request):
    return MentorRelationship.objects.filter(mentor__mentor__account=request.user)


def mentor_projects(request):
    try:
        comrade = request.user.comrade
    except Comrade.DoesNotExist:
        return None

    now = datetime.datetime.now(datetime.timezone.utc)
    today = get_deadline_date_for(now)

    # It's possible that some intern selections may not work out,
    # and a mentor will have to select another intern
    # after the intern announcement date.
    # Show their project until the day after their intern starts.
    try:
        current_round = RoundPage.objects.filter(
            internstarts__gt=today,
        ).earliest('internstarts')
    except RoundPage.DoesNotExist:
        return None

    # Get all projects where they're an approved mentor
    # XXX: previous comment said "where the project is pending," but this is not true; should it be?
    # and the community is approved or pending for the current round.
    # Don't count withdrawn or rejected communities.
    mentored_projects = comrade.get_mentored_projects().filter(
        project_round__participating_round=current_round,
        project_round__approval_status__in=(ApprovalStatus.PENDING, ApprovalStatus.APPROVED),
    )
    if not mentored_projects:
        return None

    # Communities where this person is an approved mentor for at least one
    # approved project, and the community is approved to participate in the
    # current round.

    mentored_communities = Community.objects.filter(
        participation__participating_round=current_round,
        participation__approval_status=ApprovalStatus.APPROVED,
        participation__project__approval_status=ApprovalStatus.APPROVED,
        participation__project__mentorapproval__mentor=comrade,
        participation__project__mentorapproval__approval_status=ApprovalStatus.APPROVED,
    ).distinct()

    return {
        'current_round': current_round,
        'mentored_projects': mentored_projects,
        'mentored_communities': mentored_communities,
    }


def approval_status(request):
    """
    Find objects for which the current user is either an approver or a
    submitter, and list them all in one place.
    """
    by_status = defaultdict(list)
    for model in DASHBOARD_MODELS:
        by_model = defaultdict(list)
        for obj in model.objects_for_dashboard(request.user).distinct():
            if obj.approval_status == ApprovalStatus.APPROVED or not has_deadline_passed(obj.submission_and_approval_deadline()):
                by_model[obj.approval_status].append(obj)

        label = model._meta.verbose_name
        for status, objects in by_model.items():
            by_status[status].append((label, objects))

    groups = []
    for status, label in ApprovalStatus.APPROVAL_STATUS_CHOICES:
        group = by_status.get(status)
        if group:
            groups.append((label, group))

    # If this person has nothing to do, groups will be an empty
    # list, which will cause this section to be skipped.
    return groups


DASHBOARD_SECTIONS = (
    intern_announcement,
    coordinator_reminder,
    application_summary,
    staff_subscriptions,
    round_events,
    sponsor_statistics,
    staff_intern_progress,
    staff_intern_selection,
    staff_community_progress,
    selected_intern,
    intern,
    eligibility_prompts,
    unselected_intern,
    mentor,
    mentor_projects,
    approval_status,
)
