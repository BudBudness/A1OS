
from fastapi import APIRouter

router = APIRouter(prefix='/v1/security',tags=['security'])

@router.get('/status')
def status():
    return {
        'security':'active',
        'authentication':'enabled',
        'audit':'enabled',
        'rbac':'enabled'
    }

@router.get('/permissions/{role}')
def permissions(role:str):
    matrix={
        'director':['all'],
        'head_mistress':['students','staff','reports'],
        'teacher':['attendance','classes'],
        'staff':['assigned_tasks'],
        'parent':['children','payments']
    }
    return {
        'role':role,
        'permissions':matrix.get(role,[])
    }
