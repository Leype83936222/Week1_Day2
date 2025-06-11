import flet as ft

def main(page: ft.Page):
    page.title = "Simple App with Bottom Nav"
    page.theme_mode = "dark"

    def on_nav_change(e):
        print(f"Selected index: {e.control.selected_index}")

    # Top AppBar with logo and app name
    page.appbar = ft.AppBar(
        leading=ft.Icon(name="account_circle"),  # Use string name instead of ft.icons
        leading_width=40,
        title=ft.Text("Regil"),
        center_title=False,
        bgcolor=ft.Colors.SURFACE,  # ✅ replaced SURFACE_VARIANT
    )

    # Bottom Navigation Bar
    page.navigation_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.HOME, label="Home"),
            ft.NavigationBarDestination(icon=ft.Icons.CHAT, label="Chat"),
            ft.NavigationBarDestination(icon=ft.Icons.SETTINGS, label="Settings"),
        ],
        selected_index=0,
        on_change=on_nav_change,
    )

    # Main content
    page.add(
        ft.Container(
            content=ft.Text("Select an option from the bottom navigation."),
            alignment=ft.alignment.center,
            expand=True,
        )
    )

# ✅ Launch with asset directory + mobile access
ft.app(
    target=main,
    view=ft.WEB_BROWSER,
    port=8550,
    host="0.0.0.0",
    assets_dir="assets"  # ✅ tells Flet where to find reg.png
)
