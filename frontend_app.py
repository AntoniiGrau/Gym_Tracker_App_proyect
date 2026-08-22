# frontend_app.py
import flet as ft
import requests

# Local address of Django backend
URL_API = "http://127.0.0.1:8000/"


def main(page: ft.Page):
    page.title = "Multi-platform Gym"
    page.theme_mode = ft.ThemeMode.DARK
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.ADAPTIVE

    # DYNAMIC LOCAL STATE VARIABLES
    current_username = "Guest"
    current_token = None
    is_login_view = True

    # VISUAL COMPONENTS OF THE DASHBOARD
    welcome_text = ft.Text(
        f"Hello {current_username}, Welcome back!", size=20, weight=ft.FontWeight.BOLD)
    stat_catalog = ft.Text(
        "0", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_200)
    stat_sets = ft.Text(
        "0", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_200)
    stat_workouts = ft.Text(
        "0", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_200)

    progress_bar = ft.ProgressBar(
        value=0.0, width=280, color=ft.Colors.BLUE_400, bgcolor=ft.Colors.GREY_700)
    progress_text = ft.Text("Completion Rate: 0%",
                            size=14, color=ft.Colors.GREY_400)

    def load_dashboard_metrics():
        try:
            answer = requests.get(f"{URL_API}api/dashboard/")
            if answer.status_code == 200:
                data = answer.json()
                stat_catalog.value = str(data.get("catalog_exercises", 0))
                stat_sets.value = str(data.get("total_sets", 0))
                stat_workouts.value = str(data.get("completed_workouts", 0))
        except requests.exceptions.ConnectionError:
            print("Error parsing dashboard metrics. Server offline.")

    # Layout of the new Dashboard view
    view_dashboard = ft.Column([
        welcome_text,
        ft.Container(height=10),
        ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("NEXT WORKOUT", size=12,
                            color=ft.Colors.BLUE_100, weight=ft.FontWeight.BOLD),
                    ft.Text("Today", size=28, weight=ft.FontWeight.BOLD),
                    ft.Text("Active Session Progress",
                            size=14, color=ft.Colors.GREY_300),
                ]),
                padding=20,
                width=300,
                bgcolor=ft.Colors.BLUE_900,
                border_radius=18
            )
        ),
        ft.Container(height=15),
        ft.Text("Performance Metric:", size=16,
                weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_100),
        progress_text,
        progress_bar,
        ft.Container(height=15),
        ft.Row([
            ft.Column([stat_catalog, ft.Text("catalog", size=12, color=ft.Colors.GREY_400)],
                      horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            ft.Column([stat_sets, ft.Text("total sets", size=12, color=ft.Colors.GREY_400)],
                      horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            ft.Column([stat_workouts, ft.Text("workouts", size=12, color=ft.Colors.GREY_400)],
                      horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=30)
    ], alignment=ft.MainAxisAlignment.START, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    input_name = ft.TextField(
        label="Exercise Name (e.g., Bench Press)", width=280, border_radius=20)
    input_muscle = ft.TextField(
        label="Muscle Group (e.g., Chest)", width=280, border_radius=20)
    message_label = ft.Text("", size=14, weight=ft.FontWeight.BOLD)
    exercises_list_ui = ft.ListView(expand=1, spacing=10, padding=20)

    # Connect to the Backend (Django)
    def load_exercises_from_django():
        headers = {}
        if current_token:
            headers["Authorization"] = f"token {current_token}"

        try:
            answer = requests.get(f"{URL_API}api/exercises/", headers=headers)
            if answer.status_code == 200:
                exercises = answer.json()
                exercises_list_ui.controls.clear()
                dropdown_workout_exercise.options.clear()
                for exercise in exercises:
                    video_button = ft.Container()
                    if exercise.get('video_url'):
                        video_button = ft.TextButton(
                            "Watch Example",
                            icon=ft.Icons.PLAY_ARROW,
                            on_click=lambda e, url=exercise['video_url']: page.launch_url(
                                url)
                        )

                    exercises_list_ui.controls.append(
                        ft.Card(
                            content=ft.Container(
                                content=ft.Column([
                                    ft.Text(
                                        exercise['name'], size=18, weight=ft.FontWeight.BOLD),
                                    ft.Text(
                                        f"group: {exercise['muscle_group']}", color=ft.Colors.GREY_400),
                                    video_button
                                ]),
                                padding=15
                            ),
                            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                            border_radius=15
                        )
                    )
                    dropdown_workout_exercise.options.append(
                        ft.dropdown.Option(
                            key=str(exercises['id']), text=exercise['name'])
                    )
                page.update()
        except requests.exceptions.ConnectionError:
            print("Django offline.")

    # LOGIC: POST REQUEST
    def save_exercise_to_django(e):
        if not input_name.value or not input_muscle.value:
            message_label.value = "Please fill in all fields!"
            message_label.color = ft.Colors.RED_400
            page.update()
            return

        payload = {
            "name": input_name.value,
            "muscle_group": input_muscle.value
        }
        headers = {
            "Authorization": f"Token {current_token}"}if current_token else {}

        try:
            answer = requests.post(f"{URL_API}api/exercises/", json=payload)
            if answer.status_code == 201:
                message_label.value = f"Successfully added: {input_name.value}"
                message_label.color = ft.Colors.GREEN_400
                input_name.value = ""
                input_muscle.value = ""
                load_exercises_from_django()
                load_dashboard_metrics()
        except requests.exceptions.ConnectionError:
            page.update()

    btn_save = ft.ElevatedButton(
        "Save New Exercise",
        icon=ft.Icons.ADD_CIRCLE_OUTLINED,
        on_click=save_exercise_to_django,
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.BLUE_700,
            shape=ft.RoundedRectangleBorder(radius=25),
            padding=ft.Padding.symmetric(horizontal=20, vertical=15)
        )
    )

    btn_connect = ft.ElevatedButton(
        "Synchronize with Django",
        icon=ft.Icons.SYNC_ROUNDED,
        on_click=lambda e: load_exercises_from_django(),
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            shape=ft.RoundedRectangleBorder(radius=25),
            padding=ft.Padding.symmetric(horizontal=20, vertical=15)
        )
    )

    # Assembled view for the Exercises screen
    view_exercises = ft.Column([
        ft.Text("Add New Exercise:", size=16,
                weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_100),
        input_name,
        input_muscle,
        btn_save,
        message_label,
        ft.Divider(),
        btn_connect,
        ft.Text("Exercises Available in the Backend:",
                size=16, color=ft.Colors.BLUE_100),
        exercises_list_ui
    ], alignment=ft.MainAxisAlignment.START, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    is_login_view = True

    # Customer registrations componets
    reg_username = ft.TextField(label="Username", width=280, border_radius=20)
    reg_email = ft.TextField(label="Email Address",
                             width=280, keyboard_type=ft.KeyboardType.EMAIL, border_radius=20)
    reg_password = ft.TextField(
        label="Password", width=280, password=True, can_reveal_password=True, border_radius=20)
    reg_message = ft.Text("", size=14, weight=ft.FontWeight.BOLD)

    def register_user_to_django(e):
        if not reg_username.value or not reg_email.value or not reg_password.value:
            reg_message.value = "All fields are required!"
            reg_message.color = ft.Colors.RED_400
            page.update()
            return

        payload = {
            "username": reg_username.value,
            "email": reg_email.value,
            "password": reg_password.value
        }

        try:
            answer = requests.post(f"{URL_API}api/register/", json=payload)
            if answer.status_code == 201:
                reg_message.value = "Client account created successfully!"
                reg_message.color = ft.Colors.GREEN_400
                current_username = reg_username.value
                welcome_text.value = f"Hello {current_username}, Welcome back!"
                reg_username.value = ""
                reg_email.value = ""
                reg_password.value = ""
                load_dashboard_metrics()
                page.update()
            elif answer.status_code == 400:
                error_data = answer.json()
                reg_message.value = f"Error: {error_data.get('error', 'Invalid data')}"
                reg_message.color = ft.Colors.RED_400
                page.update()
            else:
                reg_message.value = f"Server rejected request (Status: {answer.status_code})"
                reg_message.color = ft.Colors.RED_400
                page.update()
        except requests.exceptions.ConnectionError:
            reg_message.value = "Error: Server is offline."
            reg_message.color = ft.Colors.RED_400
            page.update()
        except requests.exceptions.JSONDecodeError:
            reg_message.value = "Error: Server sent an invalid response."
            reg_message.color = ft.Colors.RED_400
            page.update()

    btn_register = ft.ElevatedButton(
        "Create Client Account",
        icon=ft.Icons.PERSON_ADD_ROUNDED,
        on_click=register_user_to_django,
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.BLUE_700,
            shape=ft.RoundedRectangleBorder(radius=25),
            padding=ft.Padding.symmetric(horizontal=25, vertical=15)
        )
    )

    # Login components
    login_username = ft.TextField(
        label="Your Username", width=280, border_radius=20)
    login_password = ft.TextField(
        label="Your Password", width=280, password=True, can_reveal_password=True, border_radius=20)
    login_message = ft.Text("", size=14, weight=ft.FontWeight.BOLD)

    def login_user_to_django(e):
        nonlocal current_username, current_token
        if not login_username.value or not login_password.value:
            login_message.value = "Please fill in all login fields!"
            login_message.color = ft.Colors.RED_400
            page.update()
            return

        payload = {
            "username": str(login_username.value).strip(),
            "password": str(login_password.value)
        }

        try:
            answer = requests.post(f"{URL_API}api/login/", json=payload)
            if answer.status_code == 200:
                response_data = answer.json()
                current_token = response_data.get("token")
                current_username = login_username.value
                login_message.value = "login successful!"
                login_message.color = ft.Colors.GREEN_400
                welcome_text.value = f"Hello {current_username}, Welcome back!"
                login_username.value = ""
                login_password.value = ""
                page.navigation_bar.selected_index = 0
                main_container.content = view_dashboard
                load_dashboard_metrics()
                page.update()
            else:
                login_message.value = "Error: Invalid username or password."
                login_message.color = ft.Colors.RED_400
                page.update()
        except requests.exceptions.ConnectionError:
            login_message.value = "Error: Server is offline."
            login_message.color = ft.Colors.RED_400
            page.update()

    btn_login = ft.ElevatedButton(
        "Sign In / Login",
        icon=ft.Icons.LOGIN_ROUNDED,
        on_click=login_user_to_django,
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.GREEN_700,
            shape=ft.RoundedRectangleBorder(radius=25),
            padding=ft.Padding.symmetric(horizontal=30, vertical=15)
        )
    )
    dropdown_workout_exercise = ft.Dropdown(
        label="Select Exercises", width=280, border_radius=20)
    input_sets = ft.TextField(label="Sets", width=80,
                              keyboard_type=ft.KeyboardType.NUMBER, border_radius=20)
    input_reps = ft.TextField(label="Reps", width=80,
                              keyboard_type=ft.KeyboardType.NUMBER, border_radius=20)
    input_weight = ft.TextField(
        label="Weight (kg)", width=100, keyboard_type=ft.KeyboardType.NUMBER, border_radius=20)
    workout_message = ft.Text("", size=14, weight=ft.FontWeight.BOLD)
    history_list_ui = ft.ListView(expand=1, spacing=10, padding=20)

    def load_history_from_django():
        if not current_token:
            return
        headers = {"Authorization": f"Token {current_token}"}
        try:
            answer = requests.get(f"{URL_API}api/history", headers=headers)
            if answer.status_code == 200:
                history_data = answer.json()
                history_list_ui.controls.clear()
                for record in history_data:
                    history_list_ui.controls.append(
                        ft.Card(
                            content=ft.Container(
                                content=ft.Column([
                                    ft.Text(
                                        record['exercises_name'], size=16, weight=ft.FontWeight.BOLD),
                                    ft.Text(
                                        f"{record['series']} sets x {record['reps']} reps @ {record['weight_kg']} kg", color=ft.Colors.BLUE_100),
                                    ft.Text(
                                        f"Date: {record['date']}", size=12, color=ft.Colors_GREY_500)
                                ]), padding=12
                            )
                        )
                    )
                page.update()
        except requests.exceptions.ConnectionError:
            print("History load offline.")

    def save_workout_to_django(e):
        if not dropdown_workout_exercise.value or not input_sets.value or not input_reps.value or not input_weight.value:
            workout_message.value = "Please fill in all training fields!"
            workout_message.color = ft.Colors.RED_400
            page.update()
            return
        payload = {
            "excercise": int(dropdown_workout_exercise.value),
            "series": int(input_sets.value),
            "reps": int(input_reps.value),
            "weight_kg": float(input_weight.value)
        }
        headers = {"Authorizations": f"Token {current_token}"}
        try:
            answer = requests.post(
                f"{URL_API}api/history/", json=payload, headers=headers)
            if answer.status_code == 201:
                workout_message.value = "Workout set logged successfully!"
                workout_message.color = ft = Colors.GREEN_400
                input_sets.value = ""
                input_reps.value = ""
                input_weight.value = ""
                load_history_from_django()
                load_dashboard_metrics()
            else:
                workout_message.value = "Error saving workout."
                workout_message.color = ft.Colors.RED_400
                page.update()
        except requests.exceptions.ConnectionError:
            page.update()
    btn_save_workout = ft.ElevatedButton(
        "Log Workout Set", icon=ft.Icons.DASHBOARD, on_click=save_workout_to_django)

    # Assembled view for the Training screen
    view_workout = ft.Column([
        ft.Text("Log New Training Entry:", size=16,
                weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE),
        dropdown_workout_exercise,
        ft.Row([input_sets, input_reps, input_weight],
               alignment=ft.MainAxisAlignment.CENTER),
        btn_save_workout,
        workout_message,
        ft.Divider(),
        ft.Text("Your Logged Session Progress:",
                size=16, color=ft.Colors.BLUE_100),
        history_list_ui
    ], alignment=ft.MainAxisAlignment.START, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    # We consolidated both views in an organized manner within the same tab.
    view_register = ft.Column([], alignment=ft.MainAxisAlignment.START,
                              horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    def toggle_auth_view(e):
        nonlocal is_login_view
        is_login_view = not is_login_view
        build_auth_screen()
        page.update()

    def build_auth_screen():
        # We clear the previous controls from the column
        view_register.controls.clear()
        # We are building only the login screen.
        if is_login_view:
            view_register.controls.extend([
                ft.Text("Already have an account? Sign in:", size=16,
                        weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_100),
                login_username, login_password, btn_login, login_message,
                ft.Container(height=10),
                ft.TextButton("Don't have an account? Register here",
                              on_click=toggle_auth_view)
            ])
        else:
            # We are building only the registration screen.
            view_register.controls.extend([
                ft.Text("Register New Client:", size=16,
                        weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_100),
                reg_username, reg_email, reg_password, btn_register, reg_message,
                ft.Container(height=10),
                ft.TextButton("Already have an account? log In",
                              on_click=toggle_auth_view)
            ])

    build_auth_screen()

    # Central container that starts by displaying the exercises.
    main_container = ft.Container(content=view_dashboard, expand=True)

    def on_navigation_change(e):
        if not current_token and e.control.selected_index != 2:
            page.navigation_bar.selected_index = 2
            main_container.content = view_register
            login_message.value = "Please Sign In first to unlock the app!"
            login_message.color = ft.Colors.RED_400
            page.update()
            return
        if e.control.selected_index == 0:
            main_container.content = view_dashboard
            load_dashboard_metrics()
        elif e.control.selected_index == 1:
            main_container.content = view_exercises
            load_exercises_from_django
        elif e.control.selected_index == 2:
            main_container.content = view_workout
            load_history_from_django()
        elif e.control.selected_index == 3:
            main_container.content = view_register
            page.update()

    # Native bottom navigation bar
    page.navigation_bar = ft.NavigationBar(
        selected_index=3,
        on_change=on_navigation_change,
        destinations=[
            ft.NavigationBarDestination(
                icon=ft.Icons.ANALYTICS, label="Dashboard"),
            ft.NavigationBarDestination(
                icon=ft.Icons.FITNESS_CENTER, label="Exercises"),
            ft.NavigationBarDestination(
                icon=ft.Icons.DASHBOARD, label="Log Workout"),
            ft.NavigationBarDestination(
                icon=ft.Icons.PERSON_ADD_ALT_1, label="Account"),
        ]
    )

    title = ft.Text("My Gym Tracker", size=28,
                    weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_200)

    # We render the fixed structure in the mobile app.
    page.add(
        ft.Container(height=20),
        title,
        ft.Divider(),
        main_container  # Muestra dinámicamente la pantalla elegida
    )

    load_exercises_from_django()


# Launch the visual app
ft.run(main, view=ft.AppView.WEB_BROWSER)
