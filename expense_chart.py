#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Expense Chart - Консольное приложение для учета расходов с построением графиков
Автор: Иван Иванов
"""

import json
import os
from datetime import datetime, timedelta
from collections import defaultdict
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Для совместимости с различными системами


class Expense:
    """Класс расхода с инкапсуляцией"""

    def __init__(self, amount, category, date):
        self._amount = amount
        self._category = category
        self._date = date

    @property
    def amount(self):
        return self._amount

    @property
    def category(self):
        return self._category

    @property
    def date(self):
        return self._date

    def to_dict(self):
        """Преобразование в словарь для JSON"""
        return {
            'amount': self._amount,
            'category': self._category,
            'date': self._date
        }

    @classmethod
    def from_dict(cls, data):
        """Создание из словаря"""
        return cls(data['amount'], data['category'], data['date'])

    def __str__(self):
        return f"{self._date} | {self._category:12} | {self._amount:8.2f} руб."


class ExpenseCategory(Expense):
    """Наследование: класс для категории расходов с дополнительной информацией"""

    def __init__(self, amount, category, date, subcategory=None):
        super().__init__(amount, category, date)
        self.subcategory = subcategory

    def get_category_info(self):
        return f"{self.category}" + (f" ({self.subcategory})" if self.subcategory else "")


class ExpenseManager:
    """Менеджер для управления расходами"""

    def __init__(self):
        self.expenses = []
        self.data_file = "expenses.json"
        self.categories = ['Еда', 'Транспорт', 'Жилье', 'Развлечения', 'Здоровье', 'Одежда', 'Другое']
        self.load_data()

    def add_expense(self, amount, category, date):
        """Добавление расхода с валидацией"""
        # Валидация суммы
        if amount <= 0:
            raise ValueError("Сумма расхода должна быть положительной!")

        # Валидация категории
        if category not in self.categories:
            raise ValueError(f"Категория должна быть из списка: {', '.join(self.categories)}")

        # Валидация даты
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Неверный формат даты! Используйте ГГГГ-ММ-ДД (например, 2024-03-15)")

        expense = Expense(amount, category, date)
        self.expenses.append(expense)
        self.save_data()
        return True

    def get_expenses(self, category=None, start_date=None, end_date=None):
        """Получение расходов с фильтрацией"""
        filtered = self.expenses

        if category:
            filtered = [e for e in filtered if e.category == category]

        if start_date:
            filtered = [e for e in filtered if e.date >= start_date]

        if end_date:
            filtered = [e for e in filtered if e.date <= end_date]

        return filtered

    def delete_expense(self, index):
        """Удаление расхода по индексу"""
        if 0 <= index < len(self.expenses):
            deleted = self.expenses.pop(index)
            self.save_data()
            return deleted
        return None

    def get_total_by_period(self, start_date=None, end_date=None):
        """Подсчет суммы расходов за период"""
        expenses = self.get_expenses(start_date=start_date, end_date=end_date)
        total = sum(e.amount for e in expenses)
        return total

    def get_category_totals(self, start_date=None, end_date=None):
        """Получение сумм по категориям за период"""
        expenses = self.get_expenses(start_date=start_date, end_date=end_date)
        totals = defaultdict(float)
        for expense in expenses:
            totals[expense.category] += expense.amount
        return dict(totals)

    def plot_expenses(self, start_date=None, end_date=None):
        """Построение графика расходов по категориям"""
        totals = self.get_category_totals(start_date, end_date)

        if not totals:
            print("\n❌ Нет данных для построения графика за выбранный период!")
            return False

        # Подготовка данных
        categories = list(totals.keys())
        amounts = list(totals.values())

        # Создание графика
        plt.figure(figsize=(10, 6))

        # Столбчатая диаграмма
        bars = plt.bar(categories, amounts, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#F0E68C'])

        # Настройка графика
        plt.xlabel('Категории расходов', fontsize=12, fontweight='bold')
        plt.ylabel('Сумма (руб.)', fontsize=12, fontweight='bold')

        # Заголовок с периодом
        if start_date and end_date:
            title = f'Расходы по категориям за период: {start_date} - {end_date}'
        elif start_date:
            title = f'Расходы по категориям с {start_date}'
        elif end_date:
            title = f'Расходы по категориям до {end_date}'
        else:
            title = 'Расходы по категориям (все время)'

        plt.title(title, fontsize=14, fontweight='bold')

        # Добавление значений на столбцы
        for bar, amount in zip(bars, amounts):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                     f'{amount:.0f} руб.',
                     ha='center', va='bottom', fontsize=10, fontweight='bold')

        # Поворот подписей оси X для лучшей читаемости
        plt.xticks(rotation=45, ha='right')

        # Добавление сетки
        plt.grid(axis='y', alpha=0.3, linestyle='--')

        plt.tight_layout()

        # Сохранение графика
        filename = f"expense_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(filename, dpi=100, bbox_inches='tight')
        print(f"\n✅ График сохранен как: {filename}")

        # Показ графика
        plt.show()
        return True

    def save_data(self):
        """Сохранение данных в JSON"""
        try:
            data = [expense.to_dict() for expense in self.expenses]
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ Ошибка сохранения: {e}")
            return False

    def load_data(self):
        """Загрузка данных из JSON"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.expenses = [Expense.from_dict(item) for item in data]
                print(f"✅ Загружено {len(self.expenses)} записей")
                return True
            except Exception as e:
                print(f"❌ Ошибка загрузки: {e}")
                return False
        return False


class ConsoleUI:
    """Консольный интерфейс пользователя"""

    def __init__(self):
        self.manager = ExpenseManager()

    def display_menu(self):
        """Отображение главного меню"""
        print("\n" + "="*60)
        print("         💰 EXPENSE CHART - Учет расходов 💰")
        print("="*60)
        print("1. 📝 Добавить расход")
        print("2. 📋 Просмотреть все расходы")
        print("3. 🔍 Фильтровать расходы")
        print("4. 📊 Статистика расходов")
        print("5. 📈 Построить график расходов")
        print("6. 🗑️ Удалить расход")
        print("7. 💾 Сохранить данные")
print("8. 📂 Загрузить данные")
        print("0. 🚪 Выход")
        print("="*60)

    def add_expense_ui(self):
        """Интерфейс добавления расхода"""
        print("\n--- Добавление нового расхода ---")

        # Ввод суммы
        while True:
            try:
                amount = float(input("💰 Сумма (руб.): "))
                break
            except ValueError:
                print("❌ Ошибка: Введите число!")

        # Ввод категории
        print(f"\n📂 Доступные категории: {', '.join(self.manager.categories)}")
        category = input("📂 Категория: ").strip()

        # Ввод даты
        date = input("📅 Дата (ГГГГ-ММ-ДД): ").strip()
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")

        try:
            if self.manager.add_expense(amount, category, date):
                print(f"\n✅ Расход успешно добавлен!")
                print(f"   Сумма: {amount} руб.")
                print(f"   Категория: {category}")
                print(f"   Дата: {date}")
        except ValueError as e:
            print(f"\n❌ Ошибка: {e}")

    def view_expenses(self, expenses=None):
        """Отображение расходов в таблице"""
        if expenses is None:
            expenses = self.manager.expenses

        if not expenses:
            print("\n📭 Нет записей о расходах.")
            return

        print("\n" + "="*70)
        print(f"{'№':<4} {'Дата':<12} {'Категория':<15} {'Сумма (руб.)':<15}")
        print("-"*70)

        for i, expense in enumerate(expenses):
            print(f"{i+1:<4} {expense.date:<12} {expense.category:<15} {expense.amount:<15.2f}")

        print("="*70)
        total = sum(e.amount for e in expenses)
        print(f"📊 ИТОГО: {total:.2f} руб.")

    def filter_expenses_ui(self):
        """Интерфейс фильтрации расходов"""
        print("\n--- Фильтрация расходов ---")
        print("Оставьте поле пустым, чтобы пропустить фильтр")

        category = input("📂 Категория: ").strip()
        if category and category not in self.manager.categories:
            print(f"❌ Категория '{category}' не найдена!")
            return

        start_date = input("📅 Начальная дата (ГГГГ-ММ-ДД): ").strip()
        end_date = input("📅 Конечная дата (ГГГГ-ММ-ДД): ").strip()

        # Валидация дат
        try:
            if start_date:
                datetime.strptime(start_date, "%Y-%m-%d")
            if end_date:
                datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            print("❌ Ошибка: Неверный формат даты!")
            return

        filtered = self.manager.get_expenses(
            category=category if category else None,
            start_date=start_date if start_date else None,
            end_date=end_date if end_date else None
        )

        print(f"\n🔍 Найдено записей: {len(filtered)}")
        self.view_expenses(filtered)

    def statistics_ui(self):
        """Интерфейс статистики расходов"""
        print("\n--- Статистика расходов ---")
        print("Выберите период:")
        print("1. Все время")
        print("2. Текущий месяц")
        print("3. Текущий год")
        print("4. Произвольный период")

        choice = input("Выберите (1-4): ").strip()

        start_date = None
        end_date = None
        now = datetime.now()

        if choice == '2':
            start_date = now.replace(day=1).strftime("%Y-%m-%d")
            end_date = now.strftime("%Y-%m-%d")
            print(f"\n📅 Период: {start_date} - {end_date}")

        elif choice == '3':
            start_date = now.replace(month=1, day=1).strftime("%Y-%m-%d")
            end_date = now.strftime("%Y-%m-%d")
            print(f"\n📅 Период: {start_date} - {end_date}")

        elif choice == '4':
            start_date = input("📅 Начальная дата (ГГГГ-ММ-ДД): ").strip()
            end_date = input("📅 Конечная дата (ГГГГ-ММ-ДД): ").strip()
            if start_date:
                try:
                    datetime.strptime(start_date, "%Y-%m-%d")
                except ValueError:
                    print("❌ Неверный формат даты!")
                    return
            if end_date:
                try:
                    datetime.strptime(end_date, "%Y-%m-%d")
                except ValueError:
                    print("❌ Неверный формат даты!")
                    return

        total = self.manager.get_total_by_period(start_date, end_date)
        category_totals = self.manager.get_category_totals(start_date, end_date)

        print("\n" + "="*50)
        print("📊 СТАТИСТИКА РАСХОДОВ")
        print("="*50)
        print(f"\n💰 Общая сумма: {total:.2f} руб.")

        if category_totals:
            print("\n📂 Расходы по категориям:")
            print("-"*50)
            sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
            for cat, amt in sorted_categories:
                percentage = (amt / total * 100) if total > 0 else 0
                print(f"   {cat:<15} {amt:>10.2f} руб. ({percentage:>5.1f}%)")
        else:
            print("\n📭 Нет расходов за выбранный период")

    def plot_ui(self):
        """Интерфейс построения графика"""
        print("\n--- Построение графика расходов ---")
        print("Выберите период для графика:")
        print("1. Все время")
        print("2. Текущий месяц")
        print("3. Текущий год")
        print("4. Произвольный период")

        choice = input("Выберите (1-4): ").strip()

        start_date = None
        end_date = None
        now = datetime.now()

        if choice == '2':
            start_date = now.replace(day=1).strftime("%Y-%m-%d")
            end_date = now.strftime("%Y-%m-%d")

        elif choice == '3':
            start_date = now.replace(month=1, day=1).strftime("%Y-%m-%d")
            end_date = now.strftime("%Y-%m-%d")

        elif choice == '4':
            start_date = input("📅 Начальная дата (ГГГГ-ММ-ДД): ").strip() or None
            end_date = input("📅 Конечная дата (ГГГГ-ММ-ДД): ").strip() or None

        self.manager.plot_expenses(start_date, end_date)

    def delete_expense_ui(self):
        """Интерфейс удаления расхода"""
        if not self.manager.expenses:
            print("\n📭 Нет записей для удаления.")
            return

        self.view_expenses()

        try:
            index = int(input("\n🗑️ Введите номер расхода для удаления: ")) - 1
            deleted = self.manager.delete_expense(index)
            if deleted:
                print(f"\n✅ Удален расход: {deleted}")
            else:
                print("\n❌ Неверный номер!")
        except ValueError:
            print("\n❌ Ошибка: Введите число!")

    def run(self):
        """Запуск приложения"""
        print("\n🎯 Добро пожаловать в Expense Chart!")

        while True:
            self.display_menu()
            choice = input("Выберите действие: ").strip()

            if choice == '0':
                print("\n👋 До свидания! Спасибо за использование Expense Chart!")
                break

            elif choice == '1':
                self.add_expense_ui()

            elif choice == '2':
                self.view_expenses()

            elif choice == '3':
                self.filter_expenses_ui()

            elif choice == '4':
                self.statistics_ui()

            elif choice == '5':
                self.plot_ui()

            elif choice == '6':
                self.delete_expense_ui()

            elif choice == '7':
                if self.manager.save_data():
                    print("\n✅ Данные сохранены успешно!")

            elif choice == '8':
                if self.manager.load_data():
                    print("\n✅ Данные загружены успешно!")

            else:
                print("\n❌ Неверный выбор! Попробуйте снова.")


def main():
    """Главная функция"""
    try:
        app = ConsoleUI()
        app.run()
    except KeyboardInterrupt:
        print("\n\n👋 Программа прервана. До свидания!")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")


if __name__ == "__main__":
    main()
