
from datetime import date, timedelta

import pytest
from playwright.sync_api import Page, expect


def fill_valid_form(page: Page):
    tomorrow = (date.today() + timedelta(days=1)).isoformat()

    page.locator('[name="room"]').select_option("small")
    page.locator("#date").fill(tomorrow)
    page.locator('[name="startTime"]').fill("10:00")
    page.locator('[name="endTime"]').fill("11:00")
    page.locator('[name="participants"]').fill("3")
    page.locator('[name="name"]').fill("Иван Иванов")
    page.locator('[name="email"]').fill("ivan@company.com")

# 1. Позитивный тест: успешное бронирование
def test_successful_booking(page: Page, base_url: str):
    page.goto(base_url)

    fill_valid_form(page)

    page.locator('#booking-form button[type="submit"]').click()

    status = page.locator("#form-status")

    expect(status).to_contain_text("Бронирование создано.")
    expect(status).to_contain_text("Малая")
    expect(status).to_contain_text("Иван Иванов")
    expect(status).to_have_class("form-status success")

# 2. Негативный тест: превышена вместимость комнаты
def test_invalid_booking(page: Page, base_url: str):
    page.goto(base_url)

    fill_valid_form(page)

    # Малая комната рассчитана максимум на 4 участников
    page.locator('[name="participants"]').fill("5")

    page.locator('#booking-form button[type="submit"]').click()

    status = page.locator("#form-status")

    # Проверяем, что бронирование не создано
    expect(status).to_contain_text(
        "Проверьте, пожалуйста, заполнение формы."
    )

    # Проверяем сообщение об ошибке
    expect(
        page.locator('[data-error-for="participants"]')
    ).to_contain_text(
        "В комнате максимум 4 участника."
    )

    # Убеждаемся, что успешное сообщение отсутствует
    expect(status).not_to_contain_text(
        "Бронирование создано."
    )

# 3. Проверка известного дефекта
@pytest.mark.xfail(
    strict=True,
    reason="Допускается бронирование с одинаковым временем начала и окончания",
    raises=AssertionError
)
def test_discovered_defect(page: Page, base_url: str):
    page.goto(base_url)

    fill_valid_form(page)

    page.locator('[name="startTime"]').fill("10:00")
    page.locator('[name="endTime"]').fill("10:00")

    page.locator('#booking-form button[type="submit"]').click()

    status = page.locator("#form-status")

    # Ожидаемое поведение:
    # бронирование должно быть отклонено.
    expect(status).to_contain_text(
        "Проверьте, пожалуйста, заполнение формы."
    )

    expect(status).not_to_contain_text(
        "Бронирование создано."
    )
