import pandas as pd
from typing import Tuple, Optional

EXPECTED_COLUMNS = {"почта", "имя", "пол", "дата", "время", "место", "задание"}


class ExcelParser:
    @staticmethod
    def load_excel(file_path: str) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
        try:
            df = pd.read_excel(file_path, dtype=str).fillna('')
        except Exception as e:
            return None, f"Ошибка чтения файла: {e}"

        df.columns = df.columns.str.strip().str.lower()
        cols_set = set(df.columns)
        extra = cols_set - EXPECTED_COLUMNS
        if extra:
            return None, f"Найдены лишние столбцы: {', '.join(extra)}"

        missing = EXPECTED_COLUMNS - cols_set
        if missing:
            # Предупреждение, но не ошибка
            return df, f"Отсутствуют столбцы: {', '.join(missing)}. Они могут понадобиться, если будут использованы соответствующие метки."
        return df, None

    @staticmethod
    def generate_template(save_path: str):
        df = pd.DataFrame(columns=list(EXPECTED_COLUMNS))
        df.to_excel(save_path, index=False)