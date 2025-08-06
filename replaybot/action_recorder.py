import os
import ssl
import certifi

# Исправление SSL
os.environ["SSL_CERT_FILE"] = certifi.where()

from playwright.sync_api import sync_playwright
import time


def record_actions():
    """Записывает все ваши действия в браузере"""
    print("🎬 ЗАПИСЬ ДЕЙСТВИЙ В БРАУЗЕРЕ")
    print("=" * 40)
    print("📝 Все ваши действия будут записаны в консоль")
    print("🖱️ Кликайте, вводите текст, переходите по страницам")
    print("🛑 Закройте браузер когда закончите")
    print()

    with sync_playwright() as p:
        # Запускаем браузер с вашей авторизацией
        context = p.chromium.launch_persistent_context(
            "auth",  # Папка с вашей авторизацией
            headless=False,  # Видимый браузер
            args=["--no-sandbox"],
        )

        page = context.pages[0] if context.pages else context.new_page()

        # ЗАПИСЫВАЕМ ВСЕ СОБЫТИЯ

        # Клики
        page.on("click", lambda: print(f"🖱️ КЛИК на {page.url}"))

        # Навигация
        page.on("load", lambda: print(f"🌐 ЗАГРУЖЕНА СТРАНИЦА: {page.url}"))
        page.on("domcontentloaded", lambda: print(f"📄 DOM ЗАГРУЖЕН: {page.url}"))

        # Ввод текста
        def log_input(selector, text):
            print(f"⌨️ ВВОД ТЕКСТА в [{selector}]: '{text}'")

        # Переопределяем методы ввода для логирования
        original_fill = page.fill
        original_type = page.type
        original_click = page.click
        original_goto = page.goto

        def logged_fill(selector, value, **kwargs):
            print(f"⌨️ ЗАПОЛНЕНИЕ [{selector}]: '{value}'")
            return original_fill(selector, value, **kwargs)

        def logged_type(selector, text, **kwargs):
            print(f"⌨️ НАБОР ТЕКСТА [{selector}]: '{text}'")
            return original_type(selector, text, **kwargs)

        def logged_click(selector, **kwargs):
            print(f"🖱️ КЛИК НА [{selector}]")
            return original_click(selector, **kwargs)

        def logged_goto(url, **kwargs):
            print(f"🌐 ПЕРЕХОД НА: {url}")
            return original_goto(url, **kwargs)

        # Заменяем методы
        page.fill = logged_fill
        page.type = logged_type
        page.click = logged_click
        page.goto = logged_goto

        # Отслеживаем скроллинг
        page.add_init_script(
            """
            let lastScrollTop = 0;
            window.addEventListener('scroll', () => {
                const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
                if (Math.abs(scrollTop - lastScrollTop) > 100) {
                    console.log('📜 СКРОЛЛ до позиции:', scrollTop);
                    lastScrollTop = scrollTop;
                }
            });
        """
        )

        # Слушаем консоль браузера
        page.on(
            "console",
            lambda msg: (
                print(f"🖥️ КОНСОЛЬ: {msg.text}") if "СКРОЛЛ" in msg.text else None
            ),
        )

        try:
            # Стартовая страница
            print("🚀 Запуск браузера...")
            page.goto("https://x.com/home")
            print("✅ Браузер готов к записи!")
            print()
            print("📋 ИНСТРУКЦИЯ:")
            print("1. Делайте что хотите в браузере")
            print("2. Все действия записываются в консоль")
            print("3. Закройте браузер когда закончите")
            print()
            print("🎬 НАЧАЛО ЗАПИСИ:")
            print("-" * 40)

            # Ждем пока пользователь работает
            while True:
                try:
                    # Проверяем, открыт ли еще браузер
                    page.url  # Это вызовет ошибку если страница закрыта
                    time.sleep(1)
                except:
                    break

        except KeyboardInterrupt:
            print("\n🛑 Запись остановлена пользователем")
        except Exception as e:
            print(f"💥 Ошибка: {e}")
        finally:
            print("\n🏁 КОНЕЦ ЗАПИСИ")
            try:
                context.close()
            except:
                pass


def interactive_recorder():
    """Интерактивный режим с дополнительными функциями"""
    print("🎬 ИНТЕРАКТИВНАЯ ЗАПИСЬ ДЕЙСТВИЙ")
    print("=" * 40)

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            "auth", headless=False, args=["--no-sandbox"]
        )

        page = context.pages[0] if context.pages else context.new_page()

        def log_element_info(selector):
            """Логирует информацию об элементе"""
            try:
                element = page.locator(selector)
                if element.count() > 0:
                    text = element.first.inner_text()[:50]
                    print(f"📋 ЭЛЕМЕНТ [{selector}] содержит: '{text}...'")
                else:
                    print(f"❌ ЭЛЕМЕНТ [{selector}] не найден")
            except Exception as e:
                print(f"⚠️ Ошибка получения информации об элементе: {e}")

        # Улучшенное логирование
        original_click = page.click
        original_fill = page.fill

        def enhanced_click(selector, **kwargs):
            print(f"\n🖱️ КЛИК НА: {selector}")
            log_element_info(selector)
            result = original_click(selector, **kwargs)
            print(f"✅ Клик выполнен")
            return result

        def enhanced_fill(selector, value, **kwargs):
            print(f"\n⌨️ ЗАПОЛНЕНИЕ: {selector}")
            print(f"📝 Значение: '{value}'")
            log_element_info(selector)
            result = original_fill(selector, value, **kwargs)
            print(f"✅ Заполнение выполнено")
            return result

        page.click = enhanced_click
        page.fill = enhanced_fill

        # Отслеживаем изменения URL
        current_url = ""

        def check_url_change():
            nonlocal current_url
            new_url = page.url
            if new_url != current_url:
                print(f"\n🌐 URL ИЗМЕНЕН: {new_url}")
                current_url = new_url

        try:
            page.goto("https://x.com/home")
            current_url = page.url

            print("✅ Браузер готов!")
            print("\n📋 КОМАНДЫ В КОНСОЛИ:")
            print("- Все клики и ввод текста логируются автоматически")
            print("- URL изменения отслеживаются")
            print("- Информация об элементах показывается при взаимодействии")
            print("\n🎬 ЗАПИСЬ НАЧАЛАСЬ:")
            print("-" * 50)

            while True:
                try:
                    check_url_change()
                    time.sleep(0.5)
                except:
                    break

        except KeyboardInterrupt:
            print("\n🛑 Запись остановлена")
        except Exception as e:
            print(f"💥 Ошибка: {e}")
        finally:
            print("\n🏁 Запись завершена")
            try:
                context.close()
            except:
                pass


def element_inspector():
    """Инспектор элементов - показывает селекторы при клике"""
    print("🔍 ИНСПЕКТОР ЭЛЕМЕНТОВ")
    print("=" * 30)
    print("🖱️ Кликайте на элементы - увидите их селекторы")

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            "auth", headless=False, args=["--no-sandbox"]
        )

        page = context.pages[0] if context.pages else context.new_page()

        # Добавляем скрипт для инспекции
        page.add_init_script(
            """
            document.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                
                const element = e.target;
                const tagName = element.tagName.toLowerCase();
                const id = element.id ? `#${element.id}` : '';
                const className = element.className ? `.${element.className.replace(/\\s+/g, '.')}` : '';
                const testId = element.getAttribute('data-testid') ? `[data-testid="${element.getAttribute('data-testid')}"]` : '';
                
                let selector = tagName + id + className + testId;
                
                const text = element.innerText ? element.innerText.substring(0, 30) + '...' : '';
                
                console.log('🎯 СЕЛЕКТОР:', selector);
                console.log('📝 ТЕКСТ:', text);
                console.log('🏷️ ТЕГ:', tagName);
                if (testId) console.log('🔖 DATA-TESTID:', testId);
                console.log('---');
                
                return false;
            }, true);
        """
        )

        page.on("console", lambda msg: print(f"🔍 {msg.text}"))

        try:
            page.goto("https://x.com/home")

            print("✅ Инспектор готов!")
            print("🖱️ Кликайте на любые элементы")
            print("📋 Селекторы будут показаны в консоли")
            print()

            while True:
                try:
                    time.sleep(1)
                except:
                    break

        except KeyboardInterrupt:
            print("\n🛑 Инспекция остановлена")
        finally:
            try:
                context.close()
            except:
                pass


if __name__ == "__main__":
    print("🎬 ВЫБЕРИТЕ РЕЖИМ ЗАПИСИ:")
    print("1. Простая запись действий")
    print("2. Интерактивная запись с подробностями")
    print("3. Инспектор элементов (показывает селекторы)")
    print("0. Выход")

    choice = input("\nВыбор [0-3]: ").strip()

    if choice == "1":
        record_actions()
    elif choice == "2":
        interactive_recorder()
    elif choice == "3":
        element_inspector()
    elif choice == "0":
        print("👋 До свидания!")
    else:
        print("❌ Неверный выбор")
