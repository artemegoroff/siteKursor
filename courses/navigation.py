def build_lesson_tree(modules, current_id=None):
    flattened = []
    root_number = 0

    for module in modules:
        lessons = list(module.lessons.all())
        by_id = {lesson.pk: lesson for lesson in lessons}
        roots = []

        for lesson in lessons:
            lesson.children_for_menu = []
            lesson.is_current = lesson.pk == current_id
            lesson.is_on_current_path = False

            # Используем загруженный модуль без дополнительных запросов.
            lesson.module = module

        for lesson in lessons:
            if lesson.parent_id is None:
                roots.append(lesson)

            elif lesson.parent_id in by_id:
                parent = by_id[lesson.parent_id]
                parent.children_for_menu.append(lesson)

            else:
                raise ValueError(
                    'Родитель урока отсутствует в его модуле.'
                )

        module.lessons_for_menu = roots
        module.lesson_count = len(lessons)
        module.is_on_current_path = current_id in by_id

        visited = set()

        for root in roots:
            root_number += 1
            stack = [(root, str(root_number), ())]

            while stack:
                lesson, number, ancestors = stack.pop()

                if lesson.pk in visited:
                    raise ValueError(
                        'Обнаружен цикл в структуре уроков.'
                    )

                visited.add(lesson.pk)

                lesson.menu_number = number
                lesson.ancestors_for_menu = ancestors
                flattened.append(lesson)

                if lesson.is_current:
                    for ancestor in (*ancestors, lesson):
                        ancestor.is_on_current_path = True

                children = lesson.children_for_menu

                for index in range(len(children) - 1, -1, -1):
                    stack.append((
                        children[index],
                        f'{number}.{index + 1}',
                        (*ancestors, lesson),
                    ))

        if len(visited) != len(lessons):
            raise ValueError(
                'Обнаружен цикл в структуре уроков.'
            )

    return flattened