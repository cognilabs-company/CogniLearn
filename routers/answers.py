from fastapi import APIRouter, Depends, status, HTTPException, Path
from typing import Annotated


from sqlalchemy import func
from utils import is_admin
from auth.auth import get_current_user
from database import db_dependency
from model.model import Users, Roles, Answers, StudentQuizAttempts, Questions, Results, Quizzes
from routers.scheme import AnswerRequestModel, EditAnswerRequestModel, Submission

router = APIRouter(
    prefix='/answers',
    tags=['answers']
)

user_dependency = Annotated[dict, Depends(get_current_user)]



    

@router.get("/get-all", status_code=status.HTTP_200_OK)
async def get_all_answers(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")
    
    current_user = db.query(Users).filter(Users.id == user.get('id')).first()
    user_role = db.query(Roles).filter(Roles.id == current_user.role_id).first()

    if is_admin(db, user):
        return db.query(Answers).all()
    
    if user_role.role_name == "student":
        student_attempts = db.query(StudentQuizAttempts).filter(StudentQuizAttempts.student_id == current_user.id).all()

        quiz_ids = [attempt.quiz_id for attempt in student_attempts]

        question_ids = db.query(Questions.id).filter(Questions.quiz_id.in_(quiz_ids)).subquery()

        student_answers = db.query(Answers).filter(Answers.question_id.in_(question_ids)).all()

        return student_answers

    

    raise HTTPException(status_code=403, detail="You do not have permissions")


@router.get("/get-answers/{id}", status_code=status.HTTP_200_OK)
async def get_answers(user: user_dependency, db: db_dependency,
                     id: int):

    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    current_user = db.query(Users).filter(Users.id == user.get('id')).first()
    user_role = db.query(Roles).filter(Roles.id == current_user.role_id).first()

    if is_admin(db, user):
        answer = db.query(Answers).filter(Answers.id == id).all()
        if answer is None:
            raise HTTPException(status_code=404, detail="Not found")
        return answer
        
    if user_role.role_name == "student":
        student_attempt = db.query(StudentQuizAttempts).filter(StudentQuizAttempts.student_id == current_user.id).all()
    
        quiz_ids = [attempt.quiz_id for attempt in student_attempt]

        question_ids = db.query(Questions.id).filter(Questions.quiz_id.in_(quiz_ids)).subquery()

        student_answer = db.query(Answers).filter(Answers.question_id.in_(question_ids) and Answers.id == id).all()

        if student_answer is None:
            raise HTTPException(status_code=404, detail="Not found")

        return student_answer


    raise HTTPException(status_code=403, detail="You do not have permissions")
           
                



@router.post("/add-answer_for_teachers", status_code=status.HTTP_201_CREATED)
async def add_answer(user: user_dependency, db: db_dependency,
                     request_model: AnswerRequestModel):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    current_user = db.query(Users).filter(Users.id == user.get('id')).first()
    user_role = db.query(Roles).filter(Roles.id == current_user.role_id).first()
    answer_check = db.query(Answers).filter(Answers.question_id == request_model.question_id).first()
    
    if answer_check is None:
        if user_role.role_name == "admin" or user_role.role_name == "super_admin":
            answer_model = Answers(**request_model.model_dump())
            db.add(answer_model)
            db.commit()
            return {"message": "Answer added successfully"}
        
        raise HTTPException(status_code=403, detail="You do not have permissions")

    else:
        return {"message": "answer already exist for this lesson"}
    


@router.post("/submit", status_code=status.HTTP_201_CREATED)
async def submit_answers(submission: Submission, db: db_dependency, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    current_user = db.query(Users).filter(Users.id == user.get('id')).first()
    user_role = db.query(Roles).filter(Roles.id == current_user.role_id).first()

    if user_role.role_name == "student":

        results = []
        correct_answers = 0
        total_questions = len(submission.answers)
        
        for answer in submission.answers:
            question = db.query(Questions).filter(Questions.id == answer.question_id).first()
            if not question:
                raise HTTPException(status_code=404, detail=f"Question {answer.question_id} not found")
            correct = question.correct_answer == answer.answer
            result = Results(student_id=current_user.id, quiz_id=question.quiz_id, question_id=answer.question_id, correct=int(correct))
            db.add(result)
            if correct:
                correct_answers += 1
            results.append({"question_id": answer.question_id, "correct": correct})
        
        score = (correct_answers / total_questions) * 100
        quiz = db.query(Quizzes).filter(Quizzes.id == question.quiz_id).first()
        passed = score >= quiz.passing_score
        quiz_attempt = StudentQuizAttempts(student_id=submission.student_id, quiz_id=question.quiz_id, score=score, passed=passed)
        db.add(quiz_attempt)
        
        db.commit()
        return {"student_id": submission.student_id, "results": results, "score": score, "passed": passed}
    
    raise HTTPException(status_code=403, detail="You do not have permission")


@router.put("/edit-answer/{answer_id}")
async def edit_answer(user: user_dependency, db: db_dependency,
                      answer_text:str, answer_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    current_user = db.query(Users).filter(Users.id == user.get('id')).first()
    user_role = db.query(Roles).filter(Roles.id == current_user.role_id).first()

    if user_role.role_name == "teacher":
        raise HTTPException(status_code=403, detail="You are not a student or an admin") 

    answer_model = db.query(Answers).filter(Answers.id == answer_id).first()

        
    if answer_model is None:
        raise HTTPException(status_code=404, detail="Not Found")

    answer_model.answers_text = answer_text
    db.add(answer_model)
    db.commit()
    return {"message": "answer changed successfully"}

    raise HTTPException(status_code=403, detail="You do not have permissions")


@router.delete("/delete_qanswer/{answer_id}")
async def delete_answer(user: user_dependency, db: db_dependency, answer_id: int = Path(gt=0)):

    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    if is_admin(db, user):
        answer_model = db.query(Answers).filter(Answers.id == answer_id).first()
        if answer_model is None:
            raise HTTPException(status_code=404, detail="Not Found")

        
        db.delete(answer_model)
        db.commit()
        return {"message": "deleted successfully"}

    raise HTTPException(status_code=403, detail="You do not have permissions")
