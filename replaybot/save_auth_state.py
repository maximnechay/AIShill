from playwright.sync_api import sync_playwright


def save_auth_state():
    """Сохраняет состояние авторизации в файл для codegen"""
    with sync_playwright() as p:
        # Используем ваш persistent context
        context = p.chromium.launch_persistent_context(
            "auth", headless=False, args=["--no-sandbox"]
        )

        page = context.pages[0] if context.pages else context.new_page()

        # Проверяем что авторизованы
        page.goto("https://x.com/home")
        input("Убедитесь что авторизованы и нажмите Enter...")

        # Сохраняем состояние
        context.storage_state(path="auth_state.json")
        print("✅ Состояние сохранено в auth_state.json")

        context.close()


if __name__ == "__main__":
    save_auth_state()
