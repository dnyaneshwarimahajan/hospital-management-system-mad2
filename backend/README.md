# hospital-management-system-mad2
This is Hospital Management System MAD-2 Project.

Commands to run this project : 

starting with : python -m venv venv
                venv/Scripts/activate
                pip install -r requirements.txt 
                pip install redis


Terminal 1 :  cd backend
              python app.py

Terminal 2 : cd backend
             celery -A backend_jobs.celery_config worker --loglevel=info --pool=solo

Terminal 3 : cd backend
             celery -A backend_jobs.celery_config beat --loglevel=info

Ternimal 4 : cd frontend
             npm install
             npm run dev

## Test Credentials
- Admin: admin / admin123
- Doctor: created by admin
- Patient: self register

# mailhog

http://localhost:8025

             


             
             
              


