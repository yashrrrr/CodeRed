"""
Nudge Content Templates for Professional Learners
Implements personalized, career-focused messaging
"""

from typing import Dict, Any, List
import random

class NudgeTemplates:
    """
    Manages nudge content templates with personalization
    Focuses on professional value and career progression
    """

    def __init__(self):
        self.templates = self._initialize_templates()

    def _initialize_templates(self) -> Dict[str, List[str]]:
        """
        Initialize all nudge templates
        Multiple variations for each template to avoid repetition
        """
        return {
            # Inactivity nudges
            'inactivity_gentle': [
                "Ready to get back on track, {name}? Here's a quick 5-minute review quiz to refresh your memory on {last_topic}. 🎯",
                "Hi {name}! We've missed seeing you in the course. Jump back in with this short video recap of where you left off.",
                "Hey {name}, your learning journey is waiting! Pick up where you left off with just one click.",
                "Welcome back, {name}! Let's make this week count. Start with a quick win - complete one short module today."
            ],

            'inactivity_social_proof': [
                "Hi {name}, {cohort_active_pct}% of your cohort has already completed this week's module. You're just {modules_behind} modules away from catching up!",
                "{name}, your study group misses you! {peer_name} just completed the {current_module} module. Ready to join them?",
                "You're not alone, {name}! {similar_learners} professionals like you are studying {program} right now. Let's learn together.",
                "{name}, did you know that learners who return after a break often perform better? Your fresh perspective could be an advantage!"
            ],

            'instructor_check_in': [
                "Hi {name}, this is {instructor_name}. I noticed you haven't been active recently. Is there anything I can help you with? Reply to schedule a quick call.",
                "{name}, I wanted to personally check in. Sometimes work gets overwhelming - would a 1-week extension help you get back on track?",
                "Hi {name}, as your instructor, I want to ensure you succeed. Let's discuss how to adjust your learning plan to fit your schedule better."
            ],

            # Quiz failure nudges
            'quiz_review_suggestion': [
                "That quiz was challenging, {name}! {percent_struggled}% of learners found it difficult too. Review Section {section_number} - it has the key concepts you need.",
                "Don't worry {name}, mastery takes practice. Students who reviewed {suggested_resource} improved their scores by {improvement_pct}% on average.",
                "Tough quiz, {name}? Here's a pro tip: The concept of {key_concept} is crucial. Check out the supplementary video for a different explanation.",
                "{name}, that quiz tests advanced concepts. Try the practice problems in {resource_name} - they build up to the quiz level gradually."
            ],

            'bonus_materials_unlock': [
                "Hi {name}, we've unlocked bonus study materials to help with {topic}. These alternative explanations have helped {success_rate}% of learners master this concept.",
                "{name}, struggling with {topic}? We've prepared a special case study that explains it from a practical, real-world perspective.",
                "Exclusive for you, {name}: Access to our {topic} masterclass recording. This 30-minute session breaks down complex concepts into simple steps.",
                "{name}, here's a different approach to {topic}. This industry expert's explanation has been a game-changer for many professionals."
            ],

            'advisor_tutoring_offer': [
                "{name}, let's tackle {topic} together. I'm offering you a free 30-minute 1-on-1 tutoring session. Click here to book a convenient time.",
                "Hi {name}, {advisor_name} here. I specialize in helping professionals master {topic}. Let's schedule a personalized session to get you past this hurdle.",
                "{name}, you're not alone in this. Our success advisor team is here to help. Book a free session to create a personalized study plan for {topic}."
            ],

            # Video engagement nudges
            'video_key_concept': [
                "Don't miss out, {name}! The last 5 minutes of '{video_title}' covers {key_concept} - crucial for your next assignment.",
                "{name}, quick tip: '{video_title}' at timestamp {timestamp} explains exactly what you need for the upcoming quiz.",
                "Hi {name}, '{video_title}' has a real-world case study that {company_name} used to {achievement}. Worth watching!",
                "{name}, investing 15 minutes in '{video_title}' now will save you hours on the project. It demos the exact technique you'll need."
            ],

            'video_quiz_challenge': [
                "{name}, test your understanding! We've created an interactive quiz based on '{video_title}'. Complete it to earn {points} career points.",
                "Make it stick, {name}! Try this 5-question challenge about '{video_title}'. {peer_count} of your peers already aced it!",
                "Active learning alert, {name}! Transform watching into understanding with our new interactive exercises for '{video_title}'.",
                "{name}, here's a fun way to review: Our AI created a personalized quiz based on the videos you haven't watched yet. Ready to test yourself?"
            ],

            'peer_study_session': [
                "{name}, {peer_name} is hosting a study session on '{topic}' tomorrow at {time}. Join 3 other professionals for collaborative learning!",
                "Study together, succeed together! {name}, you're invited to a peer-led review of this week's videos. RSVP for {day} at {time}.",
                "{name}, struggling with videos alone? Join our 'Watch & Discuss' session where {group_size} learners review content together.",
                "Community learning opportunity! {name}, your cohort is meeting virtually to discuss '{topic}'. Your insights would be valuable!"
            ],

            # Deadline nudges
            'deadline_friendly': [
                "Hi {name}, friendly reminder: Your {assignment_type} is due in 48 hours. You've got this! 💪",
                "{name}, just a heads up - {assignment_type} deadline is approaching. {percent_submitted}% of your cohort has already submitted.",
                "Quick reminder, {name}: 48 hours left for {assignment_type}. Need any clarification? Check the FAQ or ask in the forum.",
                "{name}, weekend warrior time! You have 48 hours to complete {assignment_type}. Set aside {estimated_time} hours to ace it."
            ],

            'deadline_urgent_help': [
                "⏰ {name}, 24 hours remaining for {assignment_type}! If you're stuck, here's a direct link to the most helpful resources: {resource_link}",
                "Crunch time, {name}! {assignment_type} due in 24 hours. Pro tip: Focus on {priority_sections} for maximum points.",
                "{name}, final day for {assignment_type}! Join our emergency help session at {time} or check the pinned solution approach in the forum.",
                "Last 24 hours, {name}! Remember: partial submission is better than none. Focus on completing {min_requirements} first."
            ],

            'extension_offer': [
                "{name}, need more time? You can request a 24-hour extension for {assignment_type}. No penalty for your first extension request.",
                "Life happens, {name}. If you need extra time for {assignment_type}, request an extension here. We're here to support your success.",
                "{name}, quality over rush. If you need an extension for {assignment_type} to do your best work, click here to request one.",
                "Hi {name}, we understand busy schedules. You're eligible for a {extension_hours}-hour extension on {assignment_type}. Use it if needed!"
            ],

            # Risk-based nudges
            'risk_encouragement': [
                "{name}, every expert was once a beginner. Your persistence is already impressive. Let's focus on small wins this week!",
                "You're on a journey, {name}. {success_story_name} from your program struggled initially too, but is now a {role} at {company}.",
                "{name}, your potential is clear. Let's adjust your learning approach - sometimes a small change makes a big difference.",
                "Hi {name}, challenging periods lead to the biggest growth. You're developing problem-solving skills that will serve you throughout your career."
            ],

            'risk_resources': [
                "{name}, we've curated resources specifically for your learning style. These materials have helped {success_rate}% of similar learners succeed.",
                "Personalized support for you, {name}: Access to study guides, video summaries, and practice problems tailored to your needs.",
                "{name}, unlock your exclusive resource pack: Quick-reference guides, cheat sheets, and focused practice materials for busy professionals.",
                "Special access granted, {name}: Our 'Accelerated Learning Toolkit' designed for professionals who need to optimize their study time."
            ],

            'mentor_reach_out': [
                "Hi {name}, I'm {mentor_name}, your assigned mentor. I've helped {mentee_count} professionals complete this program. Let's chat about your goals.",
                "{name}, this is {mentor_name}. I've reviewed your progress and have specific suggestions to help you succeed. When can we connect?",
                "Personal message for {name}: I'm here as your mentor to ensure you achieve your career goals through this program. Let's create a success plan together.",
                "{name}, you have tremendous potential. As your mentor, I want to understand your challenges and help you overcome them. Please reach out."
            ],

            # Weekly goal nudges
            'weekly_goal_reminder': [
                "{name}, you're {hours_remaining} hours away from your weekly learning goal. {hours_needed} more hours this week will keep your streak alive!",
                "Week's not over yet, {name}! Complete {modules_remaining} more module(s) to hit your weekly target. You've got this!",
                "{name}, maintain your {streak_weeks}-week streak! Just {hours_needed} hours of study before Sunday to keep it going.",
                "Streak alert, {name}! Your {streak_weeks}-week record is at stake. Invest {hours_needed} hours to keep your momentum!"
            ],

            # Performance improvement nudges
            'performance_improvement': [
                "Great progress, {name}! Your scores improved by {improvement_pct}% this week. Keep up the momentum!",
                "{name}, you're getting stronger! Your understanding of {topic} has clearly improved. Ready for the next challenge?",
                "Comeback story alert! {name}, you've turned things around beautifully. Your recent performance puts you on track for success.",
                "{name}, your dedication is paying off! You've moved from the {old_percentile}th to {new_percentile}th percentile in your cohort."
            ],

            # Achievement celebration nudges
            'achievement_earned': [
                "🎉 Congratulations {name}! You've earned the '{achievement_name}' badge. Share it on LinkedIn to showcase your new skills!",
                "Achievement unlocked, {name}! '{achievement_name}' is yours. You're now among the top {top_percent}% of learners!",
                "Fantastic work, {name}! Your '{achievement_name}' achievement is ready to add to your professional profile.",
                "You did it, {name}! '{achievement_name}' earned. This demonstrates {skill_demonstrated} - a valuable career asset!"
            ]
        }

    def generate(self, template_key: str, context: Dict[str, Any]) -> str:
        """
        Generate personalized nudge content

        Args:
            template_key: Template identifier
            context: Personalization context

        Returns:
            Personalized nudge content
        """
        templates = self.templates.get(template_key, ["Default nudge message"])

        # Select random template variation
        template = random.choice(templates)

        # Add default values for common placeholders
        default_context = {
            'name': context.get('name', 'Learner'),
            'instructor_name': context.get('instructor_name', 'Your Instructor'),
            'mentor_name': context.get('mentor_name', 'Your Mentor'),
            'advisor_name': context.get('advisor_name', 'Success Advisor'),
            'program': context.get('program', 'this program'),
            'cohort_active_pct': context.get('cohort_active_pct', 75),
            'percent_struggled': context.get('percent_struggled', 60),
            'improvement_pct': context.get('improvement_pct', 25),
            'success_rate': context.get('success_rate', 85),
            'percent_submitted': context.get('percent_submitted', 70),
            'estimated_time': context.get('estimated_time', 2),
            'hours_needed': context.get('hours_needed', 3),
            'modules_remaining': context.get('modules_remaining', 1),
            'streak_weeks': context.get('streak_weeks', 4),
            'points': context.get('points', 100),
            'peer_count': context.get('peer_count', 12),
            'group_size': context.get('group_size', 5),
            'mentee_count': context.get('mentee_count', 50),
            'top_percent': context.get('top_percent', 10),
            'extension_hours': context.get('extension_hours', 24),
            'topic': context.get('topic', 'this topic'),
            'last_topic': context.get('last_topic', 'the last module'),
            'current_module': context.get('current_module', 'current module'),
            'video_title': context.get('video_title', 'the video'),
            'assignment_type': context.get('assignment_type', 'assignment'),
            'key_concept': context.get('key_concept', 'a key concept'),
            'section_number': context.get('section_number', '3.2'),
            'resource_name': context.get('resource_name', 'the study guide'),
            'resource_link': context.get('resource_link', '#'),
            'timestamp': context.get('timestamp', '12:45'),
            'time': context.get('time', '7 PM'),
            'day': context.get('day', 'Saturday'),
            'company_name': context.get('company_name', 'a Fortune 500 company'),
            'achievement': context.get('achievement', 'increase efficiency by 40%'),
            'peer_name': context.get('peer_name', 'A fellow learner'),
            'success_story_name': context.get('success_story_name', 'An alumni'),
            'role': context.get('role', 'Senior Data Scientist'),
            'company': context.get('company', 'top tech company'),
            'achievement_name': context.get('achievement_name', 'Skills Master'),
            'skill_demonstrated': context.get('skill_demonstrated', 'advanced expertise'),
            'modules_behind': context.get('modules_behind', 2),
            'similar_learners': context.get('similar_learners', 15),
            'suggested_resource': context.get('suggested_resource', 'the concept review'),
            'priority_sections': context.get('priority_sections', 'sections 1 and 3'),
            'min_requirements': context.get('min_requirements', 'Part A'),
            'hours_remaining': context.get('hours_remaining', 48),
            'old_percentile': context.get('old_percentile', 45),
            'new_percentile': context.get('new_percentile', 72)
        }

        # Merge with provided context (provided values override defaults)
        full_context = {**default_context, **context}

        # Format template with context
        try:
            return template.format(**full_context)
        except KeyError as e:
            # Return template with error indication if formatting fails
            return f"{template} [Error: Missing {e}]"

    def get_subject_line(self, template_key: str, context: Dict[str, Any]) -> str:
        """
        Generate email subject line for nudge

        Args:
            template_key: Template identifier
            context: Context data

        Returns:
            Subject line string
        """
        subject_lines = {
            'inactivity_gentle': "Ready to continue your learning journey?",
            'inactivity_social_proof': "Your cohort is making progress!",
            'instructor_check_in': "Personal message from your instructor",
            'quiz_review_suggestion': "Tips to master {topic}",
            'bonus_materials_unlock': "Exclusive resources unlocked for you",
            'advisor_tutoring_offer': "Free 1-on-1 tutoring session available",
            'video_key_concept': "Don't miss this key concept",
            'video_quiz_challenge': "Test your knowledge - earn points!",
            'peer_study_session': "You're invited to a study session",
            'deadline_friendly': "48 hours until {assignment_type} deadline",
            'deadline_urgent_help': "⏰ 24 hours remaining - we're here to help",
            'extension_offer': "Extension available for {assignment_type}",
            'risk_encouragement': "You're doing better than you think",
            'risk_resources': "Personalized resources ready for you",
            'mentor_reach_out': "Message from your mentor",
            'weekly_goal_reminder': "Keep your {streak_weeks}-week streak alive!",
            'performance_improvement': "Celebrating your progress!",
            'achievement_earned': "🎉 New achievement unlocked!"
        }

        subject_template = subject_lines.get(template_key, "Important update about your learning")

        try:
            return subject_template.format(**context)
        except:
            return subject_template