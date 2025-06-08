from html import escape as h


def build_event_full_info(title, start_date, end_date, category, link, description):
    return (
        f"<b>{h(title)}</b>\n"
        "━━━━━━━━━━━━━━\n"
        f"🕒 <b>Дата начала:</b> <code>{h(start_date)}</code>\n"
        f"🕓 <b>Дата завершения:</b> <code>{h(end_date)}</code>\n"
        f"🏷️ <b>Категория:</b> {h(category)}\n"
        "━━━━━━━━━━━━━━\n"
        f"<i>{h(link)}</i>\n"
        f"{h(description)}"
    )


def build_event_reminder_info(title, min_left, link, description):
    return (
        f"🔔 <b>Напоминание</b> — через <code>{min_left} мин</code> '\n"
        f"<b>{h(title)}</b>\n"
        "━━━━━━━━━━━━━━\n"
        f"<i>{h(link)}</i>\n"
        f"{h(description)}"
    )


def build_event_small_info(num, title, start_date, end_date, category):
    return (
        f"<b>{num} {h(title)}</b> ({h(category)})\n"
        f"С <code>{h(start_date)}</code> до <code>{h(end_date)}</code>\n"
    )


splitter = "━━━━━━━━━━━━━━\n"
