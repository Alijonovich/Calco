import pandas as pd
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner  # Для выпадающего списка
from kivy.core.window import Window

# Устанавливаем цвет фона окна (RGB + Alpha)
Window.clearcolor = (0.95, 0.95, 0.95, 1)  # Светло-серый фон

# Загружаем Excel-файл
try:
    df = pd.read_excel("tovar.xlsx")
    df["Плотность"] = df["Плотность"].astype(float)  # Преобразуем в число
    df["Длина"] = df["Длина"].astype(float)
    df["Ширина"] = df["Ширина"].astype(float)
    df["Высота"] = df["Высота"].astype(float)
except Exception as e:
    print(f"Ошибка загрузки Excel: {e}")
    df = None  # Если не загрузился, работаем без файла

# Список возможных плотностей
DENSITY_VALUES = [20, 30, 40, 50, 60, 70, 80, 90, 100, 105, 110, 120, 125, 130]

def round_density(density):
    """Округляет плотность к ближайшему значению из списка DENSITY_VALUES."""
    return min(DENSITY_VALUES, key=lambda x: abs(x - density))

def find_product(rounded_density, length, width, height):
    """Ищет товар в Excel-файле по округлённой плотности + габаритам."""
    if df is not None:
        filtered_df = df[
            (df["Плотность"] == rounded_density) &
            (df["Длина"] == length) &
            (df["Ширина"] == width) &
            (df["Высота"] == height)
        ]
        products = filtered_df["Наименование"].tolist()
        return ", ".join(products) if products else "Товар не найден"
    else:
        return "Excel не загружен"

def calculate_density(mass, length, width, height):
    """Вычисляет плотность материала."""
    volume = length * width * height
    if volume == 0:
        return None
    return mass / volume

def calculate_mass(density, length, width, height):
    """Вычисляет массу материала."""
    volume = length * width * height
    return density * volume

class DensityCalculator(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=20, spacing=10, **kwargs)

        # Заголовок
        self.add_widget(Label(
            text="Калькулятор плотности и массы",
            font_size=24,
            size_hint_y=None,
            height=50,
            color=(0.1, 0.1, 0.1, 1)  # Темно-серый текст
        ))

        # Выбор режима
        self.mode_spinner = Spinner(
            text="Расчёт плотности",  # Текст по умолчанию
            values=("Расчёт плотности", "Расчёт массы"),  # Доступные варианты
            size_hint_y=None,
            height=40
        )
        self.add_widget(self.mode_spinner)

        # Поля ввода
        self.input_1 = TextInput(
            hint_text="Масса (кг) или Плотность (кг/м³)",
            multiline=False,
            input_filter='float',
            input_type='number',  # Числовая клавиатура
            size_hint_y=None,
            height=40
        )
        self.length_input = TextInput(
            hint_text="Длина (м)",
            multiline=False,
            input_filter='float',
            input_type='number',  # Числовая клавиатура
            size_hint_y=None,
            height=40
        )
        self.width_input = TextInput(
            hint_text="Ширина (м)",
            multiline=False,
            input_filter='float',
            input_type='number',  # Числовая клавиатура
            size_hint_y=None,
            height=40
        )
        self.height_input = TextInput(
            hint_text="Высота (м)",
            multiline=False,
            input_filter='float',
            input_type='number',  # Числовая клавиатура
            size_hint_y=None,
            height=40
        )

        # Кнопка
        self.calculate_button = Button(
            text="Рассчитать",
            size_hint_y=None,
            height=50,
            background_color=(0.2, 0.6, 1, 1),  # Голубой цвет кнопки
            color=(1, 1, 1, 1)  # Белый текст
        )
        self.calculate_button.bind(on_press=self.calculate)

        # Результат
        self.result_label = Label(
            text="",
            size_hint_y=None,
            height=100,
            color=(0.1, 0.1, 0.1, 1),  # Темно-серый текст
            halign="center",
            valign="middle"
        )
        self.result_label.bind(size=self.result_label.setter('text_size'))  # Для многострочного текста

        # Добавляем все элементы
        self.add_widget(self.input_1)
        self.add_widget(self.length_input)
        self.add_widget(self.width_input)
        self.add_widget(self.height_input)
        self.add_widget(self.calculate_button)
        self.add_widget(self.result_label)

    def calculate(self, instance):
        try:
            mode = self.mode_spinner.text  # Получаем выбранный режим

            # Заменяем запятую на точку и преобразуем в число
            value_1 = float(self.input_1.text.replace(',', '.'))
            length = float(self.length_input.text.replace(',', '.'))
            width = float(self.width_input.text.replace(',', '.'))
            height = float(self.height_input.text.replace(',', '.'))

            # Проверяем, что все значения положительные
            if value_1 <= 0 or length <= 0 or width <= 0 or height <= 0:
                self.result_label.text = "Ошибка: значения должны быть положительными числами."
                return

            if mode == "Расчёт плотности":
                density = calculate_density(value_1, length, width, height)
                if density is None:
                    self.result_label.text = "Ошибка: объём не может быть 0."
                    return
                rounded_density = round_density(density)
                product_name = find_product(rounded_density, length, width, height)
                self.result_label.text = (
                    f"Плотность: {density:.2f} кг/м³\n"
                    f"Округлённая: {rounded_density} кг/м³\n"
                    f"Товар: {product_name}"
                )

            elif mode == "Расчёт массы":
                mass = calculate_mass(value_1, length, width, height)
                product_name = find_product(value_1, length, width, height)  # Находим товар по плотности
                self.result_label.text = (
                    f"Масса: {mass:.2f} кг\n"
                    f"Товар: {product_name}"
                )

        except ValueError:
            self.result_label.text = "Ошибка: пожалуйста, введите корректные числа."

class DensityApp(App):
    def build(self):
        self.title = "Калькулятор плотности и массы"  # Название приложения
        self.icon = "icon.png"  # Иконка приложения (добавьте файл icon.png в папку с проектом)
        return DensityCalculator()

if __name__ == "__main__":
    DensityApp().run()