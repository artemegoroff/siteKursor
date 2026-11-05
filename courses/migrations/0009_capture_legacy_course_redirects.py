from django.db import migrations


# These are the paths exposed by the retired videos.urls, not current slugs.
LEGACY_COURSES = {
    'PYT': ('python', 'python'),
    'TUR': ('turtle', 'turtle'),
    'PGA': ('pygame', 'pygame'),
    'OOP': ('oop-python', 'oop-python'),
    'TKN': ('tkinter', 'tkinter'),
    'DJA': ('django', 'django'),
}


def capture_redirects(apps, schema_editor):
    database = schema_editor.connection.alias
    OldCourse = apps.get_model('videos', 'Course')
    Course = apps.get_model('courses', 'LearningCourse')
    Lesson = apps.get_model('courses', 'Lesson')
    Redirect = apps.get_model('courses', 'LegacyCourseRedirect')

    known_courses = dict(
        Course.objects.using(database)
        .filter(slug__in=[slug for _, slug in LEGACY_COURSES.values()])
        .values_list('slug', 'pk')
    )
    observed_courses = {language: set() for language in LEGACY_COURSES}
    paths = {}
    numbered_paths = {}
    unmatched = 0

    for old in OldCourse.objects.using(database).order_by('pk').iterator():
        if old.language not in LEGACY_COURSES:
            continue
        prefix, original_course_slug = LEGACY_COURSES[old.language]
        original_course_id = known_courses.get(original_course_slug)
        candidates = Lesson.objects.using(database).filter(
            slug=old.slug or f'lesson-{old.pk}',
        ).select_related('module')

        matches = []
        if original_course_id is not None:
            matches = list(candidates.filter(
                module__course_id=original_course_id,
            )[:2])
        if not matches:
            # A lesson may have been moved to another module or course.
            matches = list(candidates[:2])

        lesson = matches[0] if len(matches) == 1 else None
        if lesson is not None:
            course_id = lesson.module.course_id
            observed_courses[old.language].add(course_id)
        else:
            course_id = original_course_id
            unmatched += 1

        destination = {
            'course_id': course_id,
            'lesson_id': lesson.pk if lesson is not None else None,
        }
        if old.slug:
            paths[f'{prefix}/{old.slug}/'] = destination
        if old.number_theme is not None and old.number_theme >= 0:
            numbered_paths[f'{prefix}/{old.number_theme}/'] = destination

    # The original URLconf matched numeric lesson numbers before slugs.
    paths.update(numbered_paths)
    for language, (prefix, original_slug) in LEGACY_COURSES.items():
        course_id = known_courses.get(original_slug)
        if course_id is None and len(observed_courses[language]) == 1:
            course_id = next(iter(observed_courses[language]))
        paths[f'{prefix}/'] = {'course_id': course_id, 'lesson_id': None}

    for old_path, destination in paths.items():
        Redirect.objects.using(database).update_or_create(
            old_path=old_path,
            defaults=destination,
        )

    if unmatched:
        print(
            f' Legacy redirects: {unmatched} archived lessons have no unique '
            'current match; their URLs will lead to the course or catalogue.'
        )


class Migration(migrations.Migration):
    dependencies = [
        ('courses', '0008_legacy_course_redirects'),
        ('videos', '0024_alter_course_youtube_id'),
    ]

    operations = [
        migrations.RunPython(capture_redirects, migrations.RunPython.noop),
    ]
