import re
from typing import List, Dict, Tuple, Optional, Set

class MessageGenerator:
    def __init__(self, subject_template: str, body_template: str):
        self.subject_template = subject_template
        self.body_template = body_template

    def generate(self, df) -> Tuple[Optional[List[Dict]], Optional[str]]:
        used_tags, invalid = self._extract_used_tags()
        if invalid:
            return None, f"В шаблоне используются недопустимые метки: {', '.join(invalid)}"

        tag_to_column = {
            "*имя*": "имя",
            "*дата*": "дата",
            "*время*": "время",
            "*место*": "место",
            "*задание*": "задание",
        }
        # Проверка наличия столбцов для используемых меток
        missing_cols = []
        for tag in used_tags:
            col = tag_to_column.get(tag)
            if col not in df.columns:
                missing_cols.append(tag)
        if missing_cols:
            return None, f"В шаблоне используются метки {missing_cols}, но в таблице нет соответствующих столбцов."

        # Проверка пустых ячеек
        error_rows = []
        for idx, row in df.iterrows():
            for tag in used_tags:
                col = tag_to_column[tag]
                if not row[col]:
                    error_rows.append((idx+2, tag, row.get("почта", "неизвестно")))
        if error_rows:
            msg = "В следующих строках отсутствуют данные для меток:\n"
            for row_num, tag, email in error_rows:
                msg += f"  Строка {row_num}, метка {tag}, адрес {email}\n"
            return None, msg

        # Генерация писем
        emails = []
        for idx, row in df.iterrows():
            body = self._process_gender_alternatives(self.body_template, row.get("пол", ""))
            subject = self._process_gender_alternatives(self.subject_template, row.get("пол", ""))
            body = self._substitute_tags(body, row, tag_to_column)
            subject = self._substitute_tags(subject, row, tag_to_column)
            emails.append({
                "to": row["почта"],
                "subject": subject,
                "body": body,
            })
        return emails, None

    def _extract_used_tags(self) -> Tuple[Set[str], Set[str]]:
        pattern = r"\*[а-яё]+\*"
        found = set(re.findall(pattern, self.subject_template + self.body_template))
        allowed = {"*имя*", "*дата*", "*время*", "*место*", "*задание*"}
        invalid = found - allowed
        return allowed.intersection(found), invalid

    def _process_gender_alternatives(self, text: str, gender: str) -> str:
        def repl(match):
            base = match.group(1)
            alt = match.group(2)
            g = gender.strip().lower()
            if g in ("ж", "жен", "женский"):
                return alt
            return base
        pattern = r"([а-яё-]+)\(([а-яё-]+)\)"
        return re.sub(pattern, repl, text, flags=re.IGNORECASE)

    def _substitute_tags(self, text: str, row, tag_to_column: dict) -> str:
        for tag, col in tag_to_column.items():
            text = text.replace(tag, row[col])
        return text