# django-nifty-layout Demo App

## Setting up the demo app

1. `cd` into the `demo_app` directory.
    ```bash
    cd demo_app  # assuming the cwd is the project root
    ```

2. Create the sqlite database.
    ```bash
    python manage.py makemigrations reports && python manage.py migrate reports
    ```

3. Use the provided `seed_report` management command to populate the database with a report.
    ```bash
    python manage.py seed_report
    ```
   
4. Run the demo server.
    ```bash
    python manage.py runserver
    ```

5.  Visit [localhost:8000](localhost:8000) (*change port if applicable*) to view the rendered report!