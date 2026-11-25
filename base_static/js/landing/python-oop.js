(function () {
    'use strict';
    const menu = document.querySelector('[data-oop-menu]');
    const desktop = window.matchMedia('(min-width: 1025px)');
    if (menu) {
        function syncMenu() { menu.open = desktop.matches; }
        syncMenu();
        desktop.addEventListener('change', syncMenu);
        menu.addEventListener('click', function (event) {
            if (event.target.closest('a') && !desktop.matches) menu.open = false;
        });
        document.addEventListener('keydown', function (event) {
            if (event.key === 'Escape' && menu.open && !desktop.matches) {
                menu.open = false;
                menu.querySelector('summary').focus();
            }
        });
    }
    const lab = document.querySelector('[data-oop-lab]');
    if (!lab) return;
    // Fixed model of two independent objects, not a Python interpreter or course progress.
    const state = {first: false, second: false};
    function render() {
        lab.querySelectorAll('[data-object-toggle]').forEach(function (button) {
            const key = button.dataset.objectToggle;
            const done = state[key];
            const output = lab.querySelector('[data-object-state="' + key + '"]');
            output.textContent = 'done = ' + (done ? 'True' : 'False');
            output.classList.toggle('is-complete', done);
            button.textContent = done ? 'Вернуть в работу' : 'Выполнить';
            button.setAttribute('aria-pressed', String(done));
        });
        // Include the whole current state so the shown code also reproduces a reset.
        const calls = ['first', 'second'].filter(function (key) { return state[key]; }).map(function (key) {
            return (key === 'first' ? 'task_1' : 'task_2') + '.complete()';
        });
        lab.querySelector('[data-oop-output]').textContent = 'task_1 = Task("Разобраться в классах")\ntask_2 = Task("Написать свой метод")\n\n' + (calls.length ? calls.join('\n') + '\n\n' : '') + 'print(task_1.done)  # ' + (state.first ? 'True' : 'False') + '\nprint(task_2.done)  # ' + (state.second ? 'True' : 'False');
    }
    lab.querySelectorAll('[data-object-toggle]').forEach(function (button) {
        button.disabled = false;
        button.addEventListener('click', function () {
            const key = button.dataset.objectToggle;
            state[key] = !state[key];
            render();
        });
    });
    render();
})();
