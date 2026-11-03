(function () {
    function initialize() {
        const moduleField = document.getElementById('id_module');
        const parentField = document.getElementById('id_parent');

        if (!moduleField || !parentField) {
            return;
        }

        const lessons = JSON.parse(
            parentField.dataset.parentLessons || '[]'
        );

        function updateParents() {
            const selectedParent = parentField.value;
            const selectedModule = moduleField.value;

            parentField.replaceChildren(
                new Option('---------', '')
            );

            lessons.forEach(function (lesson) {
                if (String(lesson.module_id) === selectedModule) {
                    parentField.add(
                        new Option(lesson.title, lesson.id)
                    );
                }
            });

            // Сохраняем родителя, только если он есть
            // среди уроков выбранного модуля.
            const canKeepParent = Array.from(
                parentField.options
            ).some(function (option) {
                return option.value === selectedParent;
            });

            parentField.value = canKeepParent
                ? selectedParent
                : '';

            parentField.disabled = !selectedModule;
        }

        moduleField.addEventListener('change', updateParents);

        updateParents();
    }

    if (document.readyState === 'loading') {
        document.addEventListener(
            'DOMContentLoaded',
            initialize
        );
    } else {
        initialize();
    }
})();