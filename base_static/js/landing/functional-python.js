(function () {
    'use strict';
    const menu = document.querySelector('[data-fp-menu]');
    const desktop = window.matchMedia('(min-width: 961px)');
    if (menu) {
        const syncMenu = function () { menu.open = desktop.matches; };
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
    const lab = document.querySelector('[data-fp-lab]');
    if (!lab) return;
    // Fixed educational examples, never evaluate user-supplied code.
    const examples = {
        squares: {
            code: 'def is_even(number):\n    return number % 2 == 0\n\ndef square(number):\n    return number ** 2\n\ndata = [1, 2, 3, 4, 5, 6]\nevens = filter(is_even, data)\nresult = list(map(square, evens))',
            labels: ['Входные данные', 'filter → чётные', 'map → квадрат числа'],
            values: ['[1, 2, 3, 4, 5, 6]', '[2, 4, 6]', '[4, 16, 36]'],
            note: 'filter выбирает элементы, map применяет функцию. Исходный список остаётся прежним.'
        },
        discount: {
            code: 'def discounted(price):\n    return price * 80 // 100\n\nprices = [100, 200, 300]\nnew_prices = list(map(discounted, prices))\ntotal = sum(new_prices)',
            labels: ['Цены до скидки', 'map → скидка 20%', 'sum → итоговая сумма'],
            values: ['[100, 200, 300]', '[80, 160, 240]', '480'],
            note: 'Функция описывает одно преобразование цены. map применяет её ко всей последовательности.'
        },
        lazy: {
            code: 'def squares(numbers):\n    for number in numbers:\n        yield number ** 2\n\nstream = squares(range(1, 7))\nfirst = next(stream)\nsecond = next(stream)\nthird = next(stream)',
            labels: ['Источник значений', 'Генератор squares', 'Три вызова next(stream)'],
            values: ['range(1, 7)', 'yield number ** 2', '1 → 4 → 9'],
            note: 'Генератор приостанавливается после yield. Следующий вызов next продолжает вычисление; весь список заранее не создаётся.'
        }
    };
    const buttons = lab.querySelectorAll('[data-preset]');
    buttons.forEach(function (button) {
        button.disabled = false;
        button.addEventListener('click', function () {
            const example = examples[button.dataset.preset];
            lab.querySelector('[data-lab-code]').textContent = example.code;
            example.labels.forEach(function (label, index) {
                lab.querySelector('[data-step-label="' + index + '"]').textContent = label;
                lab.querySelector('[data-step-value="' + index + '"]').textContent = example.values[index];
            });
            lab.querySelector('[data-lab-note]').textContent = example.note;
            buttons.forEach(function (item) { item.setAttribute('aria-pressed', String(item === button)); });
        });
    });
})();
