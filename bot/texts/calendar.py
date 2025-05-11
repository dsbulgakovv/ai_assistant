from html import escape as h


def build_event_full_info(title, start_date, end_date, category, info, description):
    return (
        f"<b>{h(title)}</b>\n"
        "━━━━━━━━━━━━━━\n"
        f"🕒 <b>Дата начала:</b> <code>{h(start_date)}</code>\n"
        f"🕓 <b>Дата завершения:</b> <code>{h(end_date)}</code>\n"
        f"🏷️ <b>Категория:</b> {h(category)}\n"
        "━━━━━━━━━━━━━━\n"
        f"ℹ️ <i>{h(info)}</i>\n"
        f"{h(description)}"
    )
