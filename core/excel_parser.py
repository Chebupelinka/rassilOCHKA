import pandas as pd
from typing import Tuple, Optional, List

# Ожидаемые столбцы и их порядок в шаблоне
EXPECTED_COLUMNS_SET = {"почта", "имя", "пол", "дата", "время", "место", "задание"}
EXPECTED_COLUMNS_ORDER = ["почта", "имя", "пол", "дата", "время", "место", "задание"]


class ExcelParser:
    @staticmethod
    def load_excel(file_path: str) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
        try:
            df = pd.read_excel(file_path, dtype=str).fillna('')
        except Exception as e:
            return None, f"Ошибка чтения файла: {e}"

        df.columns = df.columns.str.strip().str.lower()
        cols_set = set(df.columns)
        extra = cols_set - EXPECTED_COLUMNS_SET
        if extra:
            return None, f"Найдены лишние столбцы: {', '.join(extra)}"

        missing = EXPECTED_COLUMNS_SET - cols_set
        if missing:
            # Предупреждение, но не ошибка
            return df, f"Отсутствуют столбцы: {', '.join(missing)}. Они могут понадобиться, если будут использованы соответствующие метки."
        return df, None

    @staticmethod
    def generate_template(save_path: str):
        """Создаёт шаблон Excel с правильным порядком столбцов"""
        df = pd.DataFrame(columns=EXPECTED_COLUMNS_ORDER)
        df.to_excel(save_path, index=False)