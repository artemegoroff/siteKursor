from django.db import migrations


def copy_lesson_content_to_blocks(apps, schema_editor):
    Lesson = apps.get_model('courses', 'Lesson')
    LessonBlock = apps.get_model('courses', 'LessonBlock')
    db_alias = schema_editor.connection.alias

    # Перенос рассчитан на ещё не заполненную таблицу блоков.
    # Останавливаемся, чтобы не создать дубликаты вручную введённых данных.
    if LessonBlock.objects.using(db_alias).exists():
        raise RuntimeError(
            'Таблица LessonBlock уже содержит данные. '
            'Перед переносом необходимо проверить существующие блоки.'
        )

    lessons = (
        Lesson.objects.using(db_alias)
        .all()
        .iterator(chunk_size=500)
    )

    for lesson in lessons:
        blocks = []

        if lesson.youtube_id or lesson.rutube_id:
            blocks.append(
                LessonBlock(
                    lesson_id=lesson.pk,
                    kind='video',
                    sort_order=10,
                    youtube_id=lesson.youtube_id or '',
                    rutube_id=lesson.rutube_id or '',
                )
            )

        if lesson.article:
            blocks.append(
                LessonBlock(
                    lesson_id=lesson.pk,
                    kind='text',
                    sort_order=20,
                    content=lesson.article,
                )
            )

        if lesson.stepik:
            blocks.append(
                LessonBlock(
                    lesson_id=lesson.pk,
                    kind='practice',
                    sort_order=30,
                    practice_url=lesson.stepik,
                )
            )

        if blocks:
            LessonBlock.objects.using(db_alias).bulk_create(blocks)


class Migration(migrations.Migration):
    dependencies = [
        ('courses', '0005_add_lesson_blocks_and_parent'),
    ]

    operations = [
        migrations.RunPython(copy_lesson_content_to_blocks),
    ]