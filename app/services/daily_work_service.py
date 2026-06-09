
from app.repository import daily_work_repo
from sqlalchemy.orm import Session

def submit_task(db:Session, user_id:int, task_description:str, project_ids:list[int]):
    task_data_list = [{
        "description": task_description,
        "user_id": user_id,
        "project_id": project_id,
    }
    for project_id in project_ids
    ]
    return daily_work_repo.create_task_bulk(db, task_data_list)
def get_user_tasks(db:Session, user_id:int):
    return daily_work_repo.get_tasks_by_user(db, user_id)
def get_last_10_user_tasks(db:Session, user_id:int, supervisor_id:int=None):
    if supervisor_id is not None:
        return daily_work_repo.get_last_10_tasks_by_supervisor(db, user_id, supervisor_id)
    return daily_work_repo.get_last_10_tasks(db, user_id)
def get_yesterday_tasks(db:Session):
    return daily_work_repo.get_yesterday_tasks_all_users(db)
def get_tasks_by_user_date_range(db:Session,user_id:int,from_date,to_date):
    return daily_work_repo.get_tasks_by_user_date_range(db,user_id,from_date,to_date)
    

        