#!/usr/bin/env python3
"""
Простой скрипт для авторизации в Twitter
Запуск:
    AUTH_PATH=auth_account1 python login.py
    AUTH_PATH=auth_account2 python login.py
"""

import os
import ssl
import certifi
import asyncio
from playwright.async_api import async_playwright

# Исправление SSL
os.environ["SSL_CERT_FILE"] = certifi.where()


async def login_to_twitter():
    """Простая авторизация в Twitter"""
    print("🔐 АВТОРИЗАЦИЯ В TWITTER")
    print("=" * 25)

    try:
        async with async_playwright() as p:
            # Запускаем браузер с сохранением сессии
            auth_path = os.environ.get("AUTH_PATH", "auth")
            context = await p.chromium.launch_persistent_context(
                auth_path,
                # Папка для сохранения сессии
                headless=False,  # Видимый браузер
                args=["--no-sandbox"],
            )

            page = await context.new_page()

            try:
                # Сначала проверим, не авторизованы ли уже
                print("🔍 Проверяем текущую авторизацию...")
                await page.goto("https://x.com/home", timeout=15000)
                await asyncio.sleep(3)

                current_url = page.url
                nav_count = await page.locator("nav").count()

                if "home" in current_url and nav_count > 0:
                    print("✅ УЖЕ АВТОРИЗОВАНЫ!")
                    print("🎉 Можете запускать бота")
                    return True

                # Если не авторизованы, переходим к входу
                print("❌ Не авторизован, переходим к входу...")
                await page.goto("https://x.com/i/flow/login", timeout=15000)
                await asyncio.sleep(3)

                print("\n📋 ИНСТРУКЦИЯ:")
                print("1. В открывшемся браузере введите логин/email")
                print("2. Введите пароль")
                print("3. Пройдите все проверки (2FA, капча)")
                print("4. Дождитесь перехода на главную страницу")
                print("5. НЕ ЗАКРЫВАЙТЕ браузер!")
                print()

                # Ждем пока пользователь войдет
                input("⏸ Нажмите Enter ПОСЛЕ входа в аккаунт: ")

                # Проверяем результат
                print("🔍 Проверяем результат...")
                await page.goto("https://x.com/home", timeout=15000)
                await asyncio.sleep(3)

                final_url = page.url
                final_nav = await page.locator("nav").count()

                print(f"📍 Финальный URL: {final_url}")
                print(f"🧭 Nav элементы: {final_nav}")

                if "home" in final_url and final_nav > 0:
                    print("\n✅ АВТОРИЗАЦИЯ УСПЕШНА!")
                    print("🎉 Теперь можете запускать автоответчик")

                    # Дополнительный тест
                    try:
                        await page.goto("https://x.com/elonmusk", timeout=10000)
                        await asyncio.sleep(2)
                        articles = await page.locator("article").count()
                        if articles > 0:
                            print("✅ Доступ к профилям подтвержден")
                        else:
                            print("⚠️ Возможны проблемы с доступом к профилям")
                    except:
                        print("⚠️ Не удалось проверить доступ к профилям")

                    return True
                else:
                    print("\n❌ АВТОРИЗАЦИЯ НЕ УДАЛАСЬ")
                    print("💡 Попробуйте еще раз")
                    return False

            except Exception as e:
                print(f"💥 Ошибка авторизации: {e}")
                return False
            finally:
                await context.close()

    except Exception as e:
        print(f"💥 Критическая ошибка: {e}")
        return False


async def main():
    """Главная функция"""
    success = await login_to_twitter()

    if success:
        print("\n🚀 ВСЕ ГОТОВО!")
        print("Запустите: python botai.py")
    else:
        print("\n❌ ПРОБЛЕМЫ С АВТОРИЗАЦИЕЙ")
        print("Попробуйте запустить скрипт еще раз")

    input("\nНажмите Enter для выхода...")


if __name__ == "__main__":
    print("🔐 Скрипт авторизации Twitter")
    asyncio.run(main())
