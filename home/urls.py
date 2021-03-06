from . import views
from .models import ApprovalStatus

from django.views.generic import TemplateView
from django.conf.urls import include, url

# To see all URL patterns at once, run:
#   ./manage.py show_urls
# or to see just the patterns from this file:
#   ./manage.py show_urls | grep -Fw home.urls

# These views all take a community_slug.
community_cfp_patterns = [
    url(r'^edit/$', views.CommunityUpdate.as_view(), name='community-update'),
    url(r'^notify/$', views.CommunityNotificationUpdate.as_view(), name='notify-me'),
    url(r'^coordinator/preview/(?P<username>[^/]+)/$', views.CoordinatorApprovalPreview.as_view(), name='coordinatorapproval-preview'),
    url(r'^coordinator/(?P<action>[^/]+)/(?:(?P<username>[^/]+)/)?$', views.CoordinatorApprovalAction.as_view(), name='coordinatorapproval-action'),
    url(r'^$', views.community_read_only_view, name='community-read-only'),
]

# These views all take a round_slug, a community_slug, and a project_slug.
round_community_project_patterns = [
    url(r'^intern-agreement/$', views.InternAgreementSign.as_view(), name='intern-agreement'),
    url(r'^alum-standing/(?P<applicant_username>[^/]+)/(?P<standing>[^/]+)$', views.AlumStanding.as_view(), name='alum-standing'),
    url(r'^final-application/(?P<applicant_username>[^/]+)/select/$', views.InternSelectionUpdate.as_view(), name='select-intern'),
    url(r'^final-application/(?P<applicant_username>[^/]+)/remove/$', views.InternRemoval.as_view(), name='remove-intern'),
    url(r'^final-application/(?P<applicant_username>[^/]+)/resign/$', views.MentorResignation.as_view(), name='resign-as-mentor'),
    url(r'^final-application/(?P<applicant_username>[^/]+)/project-timeline/$', views.project_timeline, name='project-timeline'),
    url(r'^mentor-contract-export/(?P<applicant_username>[^/]+)/$', views.MentorContractExport.as_view(), name='mentor-contract'),
    url(r'^final-application/fund/(?P<applicant_username>[^/]+)/(?P<funding>[^/]+)$', views.InternFund.as_view(), name='intern-fund'),
    url(r'^final-application/organizer-approval/(?P<applicant_username>[^/]+)/(?P<approval>[^/]+)$', views.InternApprove.as_view(), name='intern-approval'),
    url(r'^final-application/(?P<action>[^/]+)/(?:(?P<username>[^/]+)/)?$', views.FinalApplicationAction.as_view(), name='application-action'),
    url(r'^final-application/rate/(?P<username>[^/]+)/(?P<rating>[^/]+)$', views.FinalApplicationRate.as_view(), name='application-rate'),
    url(r'^contributions/add/$', views.ContributionUpdate.as_view(), name='contributions-add'),
    url(r'^contributions/(?P<contribution_slug>[^/]+)/$', views.ContributionUpdate.as_view(), name='contributions-edit'),
    url(r'^contributions/$', views.ProjectContributions.as_view(), name='contributions'),
    url(r'^applicants/$', views.ProjectApplicants.as_view(), name='project-applicants'),
    url(r'^cfp/mentor/preview/(?P<username>[^/]+)/$', views.MentorApprovalPreview.as_view(), name='mentorapproval-preview'),
    url(r'^cfp/mentor/(?P<action>[^/]+)/(?:(?P<username>[^/]+)/)?$', views.MentorApprovalAction.as_view(), name='mentorapproval-action'),
    url(r'^cfp/skills/$', views.ProjectSkillsEditPage.as_view(), name='project-skills-edit'),
    url(r'^cfp/channels/$', views.CommunicationChannelsEditPage.as_view(), name='communication-channels-edit'),
    url(r'^cfp/$', views.project_read_only_view, name='project-read-only'),
]

# These views all take a round_slug and a community_slug.
round_community_patterns = [
    url(r'^(?P<project_slug>[^/]+)/', include(round_community_project_patterns)),
    url(r'^applicants/$', views.community_applicants, name='community-applicants'),
    url(r'^(?P<action>[^/]+)-project/(?:(?P<project_slug>[^/]+)/)?$', views.ProjectAction.as_view(), name='project-action'),
    url(r'^(?P<action>[^/]+)/$', views.ParticipationAction.as_view(), name='participation-action'),
    url(r'^$', views.community_landing_view, name='community-landing'),
]

# These views all take a round_slug.
round_patterns = [
    url(r'^communities/(?P<community_slug>[^/]+)/', include(round_community_patterns)),
    url(r'^contract-export/$', views.contract_export_view, name='contract-export'),
    url(r'^initial-feedback-export/$', views.initial_mentor_feedback_export_view, name='initial-feedback-export'),
    url(r'^initial-feedback-summary/$', views.initial_feedback_summary, name='initial-feedback-summary'),
    url(r'^midpoint-feedback-export/$', views.midpoint_mentor_feedback_export_view, name='midpoint-feedback-export'),
    url(r'^midpoint-feedback-summary/$', views.midpoint_feedback_summary, name='midpoint-feedback-summary'),
    url(r'^final-feedback-export/$', views.final_mentor_feedback_export_view, name='final-feedback-export'),
    url(r'^final-feedback-summary/$', views.final_feedback_summary, name='final-feedback-summary'),
    url(r'^email/application-deadline-review/$', views.MentorCheckDeadlinesReminder.as_view(), name='email-deadline-review'),
    url(r'^email/application-period-ended/$', views.ContributorsApplicationPeriodEndedReminder.as_view(), name='email-application-period-ended'),
    url(r'^email/application-deadline-reminder/$', views.ApplicantsDeadlinesReminder.as_view(), name='email-deadline-reminder'),
    url(r'^email/contributor-deadline-reminder/$', views.ContributorsDeadlinesReminder.as_view(), name='email-contributor-deadline-reminder'),
    url(r'^email/mentor-application-deadline-reminder/$', views.MentorApplicationDeadlinesReminder.as_view(), name='email-mentor-application-deadline-reminder'),
    url(r'^email/mentor-intern-selection-reminder/$', views.MentorInternSelectionReminder.as_view(), name='email-mentor-intern-selection-reminder'),
    url(r'^email/coordinator-intern-selection-reminder/$', views.CoordinatorInternSelectionReminder.as_view(), name='email-coordinator-intern-selection-reminder'),
    url(r'^email/intern-welcome/$', views.InternNotification.as_view(), name='email-intern-welcome'),
    url(r'^email/internship-week-(?P<week>[^/]+)/$', views.InternWeek.as_view(), name='email-internship-week'),
    url(r'^email/initial-feedback-instructions/$', views.InitialFeedbackInstructions.as_view(), name='email-initial-feedback-instructions'),
    url(r'^email/midpoint-feedback-instructions/$', views.MidpointFeedbackInstructions.as_view(), name='email-midpoint-feedback-instructions'),
    url(r'^email/final-feedback-instructions/$', views.FinalFeedbackInstructions.as_view(), name='email-final-feedback-instructions'),
]

urlpatterns = [
    url(r'^communities/cfp/add/$', views.CommunityCreate.as_view(), name='community-add'),
    url(r'^communities/cfp/(?P<community_slug>[^/]+)/', include(community_cfp_patterns)),
    url(r'^communities/cfp/$', views.community_cfp_view, name='community-cfp'),
    url(r'^(?P<round_slug>[^/]+)/', include(round_patterns)),
    url(r'^intern-contract-export/$', views.intern_contract_export_view, name='intern-contract-export'),
    url(r'^generic-intern-contract-export/$', views.generic_intern_contract_export_view, name='generic-intern-contract-export'),
    url(r'^generic-mentor-contract-export/$', views.generic_mentor_contract_export_view, name='generic-mentor-contract-export'),
    url(r'^alums/$', views.alums_page, name='alums'),
    url(r'^dashboard/$', views.dashboard, name='dashboard'),
    url(r'^dashboard/pending-applications/$', views.applicant_review_summary, name='pending-applicants-summary', kwargs={'status': ApprovalStatus.PENDING}),
    url(r'^dashboard/rejected-applications/$', views.applicant_review_summary, name='rejected-applicants-summary', kwargs={'status': ApprovalStatus.REJECTED}),
    url(r'^dashboard/approved-applications/$', views.applicant_review_summary, name='approved-applicants-summary', kwargs={'status': ApprovalStatus.APPROVED}),
    url(r'^dashboard/delete-application/(?P<applicant_username>[^/]+)/$', views.DeleteApplication.as_view(), name='delete-application'),
    url(r'^dashboard/review-applications/(?P<applicant_username>[^/]+)/$', views.ViewInitialApplication.as_view(), name='applicant-review-detail'),
    url(r'^dashboard/review-applications/update-comment/(?P<applicant_username>[^/]+)/$', views.ReviewCommentUpdate.as_view(), name='update-comment'),
    url(r'^dashboard/review-applications/(?P<action>[^/]+)/(?P<applicant_username>[^/]+)/$', views.ApplicantApprovalUpdate.as_view(), name='application-action'),
    url(r'^dashboard/review-applications/rate-essay/(?P<rating>[^/]+)/(?P<applicant_username>[^/]+)/$', views.EssayRating.as_view(), name='essay-rating'),
    url(r'^dashboard/review-applications/change-red-flag/(?P<flag>[^/]+)/(?P<flag_value>[^/]+)/(?P<applicant_username>[^/]+)/$', views.ChangeRedFlag.as_view(), name='change-red-flag'),
    url(r'^dashboard/review-applications/set-owner/(?P<owner>[^/]+)/(?P<applicant_username>[^/]+)/$', views.SetReviewOwner.as_view(), name='set-review-owner'),
    url(r'^dashboard/feedback/mentor/initial/(?P<username>[^/]+)/$', views.InitialMentorFeedbackUpdate.as_view(), name='initial-mentor-feedback'),
    url(r'^dashboard/feedback/intern/initial/$', views.InitialInternFeedbackUpdate.as_view(), name='initial-intern-feedback'),
    url(r'^dashboard/feedback/mentor/midpoint/(?P<username>[^/]+)/$', views.MidpointMentorFeedbackUpdate.as_view(), name='midpoint-mentor-feedback'),
    url(r'^dashboard/feedback/intern/midpoint/$', views.MidpointInternFeedbackUpdate.as_view(), name='midpoint-intern-feedback'),
    url(r'^dashboard/feedback/mentor/final/(?P<username>[^/]+)/$', views.FinalMentorFeedbackUpdate.as_view(), name='final-mentor-feedback'),
    url(r'^dashboard/feedback/intern/final/$', views.FinalInternFeedbackUpdate.as_view(), name='final-intern-feedback'),
    url(r'^dashboard/trusted-volunteers/$', views.TrustedVolunteersListView.as_view(), name='trusted-volunteers-list'),
    url(r'^eligibility/$', views.EligibilityUpdateView.as_view(), name='eligibility'),
    url(r'^eligibility/essay-revision/(?P<applicant_username>[^/]+)/$', views.BarriersToParticipationUpdate.as_view(), name='essay-revision'),
    url(r'^eligibility/school-revision/(?P<applicant_username>[^/]+)/$', views.SchoolInformationUpdate.as_view(), name='school-revision'),
    url(r'^eligibility/request-essay-revision/(?P<applicant_username>[^/]+)/$', views.NotifyEssayNeedsUpdating.as_view(), name='request-essay-revision'),
    url(r'^eligibility/request-school-info-revision/(?P<applicant_username>[^/]+)/$', views.NotifySchoolInformationUpdating.as_view(), name='request-school-info-revision'),
    url(r'^eligibility-results/$', views.EligibilityResults.as_view(), name='eligibility-results'),
    url(r'^longitudinal-survey/2018-initiate/$', views.Survey2018Notification.as_view(), name='longitudinal-survey-2018-initiate'),
    url(r'^longitudinal-survey/2018/(?P<survey_slug>[^/]+)/$', views.AlumSurveyUpdate.as_view(), name='longitudinal-survey-2018'),
    url(r'^longitudinal-survey/2018-completed/$', TemplateView.as_view(template_name='home/survey_confirmation.html'), name='longitudinal-survey-2018-completed'),
    url(r'^longitudinal-survey/2018-opt-out/(?P<survey_slug>[^/]+)/$', views.survey_opt_out, name='longitudinal-survey-2018-opt-out'),
    url(r'^account/$', views.ComradeUpdate.as_view(), name='account'),
    url(r'^apply/project-selection/$', views.current_round_page, name='project-selection'),
    url(r'^past-projects/$', views.past_rounds_page, name='past-rounds'),
    url(r'^apply/make-contributions/$', views.contribution_tips, name='contribution-tips'),
    url(r'^apply/eligibility/$', views.eligibility_information, name='eligibility-information'),
    url(r'^register/$', views.RegisterUser.as_view(), name='register'),
    url(r'^register/sent/$', views.PendingRegisterUser.as_view(), name='registration_complete'),
    url(r'^register/activate/(?P<activation_key>[-.:\w]+)/$', views.ActivationView.as_view(), name='registration_activate'),
    url(r'^register/activate/$', views.ActivationCompleteView.as_view(), name='registration_activation_complete'),
    url(r'^travel-stipend/$', views.travel_stipend, name='travel-stipend'),
    url(r'^blog/(?P<round_slug>[^/]+)/application-period-statistics/$', views.round_statistics, name='blog-application-period-statistics'),
    url(r'^privacy-policy/$', views.privacy_policy, name='privacy-policy'),
]
