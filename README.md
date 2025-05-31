# TamaOd
Analyze addresses for possible construction

## How to Run

Set the enviroment (production / test) before starting up the application
`export DJANGO_ENV=production`


To run this app:
```pdm run manage.py runserver```

## Testing and Mocking

To change app_state to use mock apis - Uncomment the API varaibles in tamaod/settings.py

To run tests, run `pytest` from the project root.