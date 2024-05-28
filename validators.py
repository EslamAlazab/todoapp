from password_validator import PasswordValidator
from pydantic import BaseModel, EmailStr, ValidationError
from models import User


class Email(BaseModel):
    email: EmailStr


async def username_validator(username: str, db):
    errors = []
    if db.query(User).filter(User.username == username).first():
        errors.append('Username used before!')
    return errors


async def email_validator(email, db):
    errors = []
    if db.query(User).filter(User.email == email).first():
        errors.append('email used before!')

    try:
        email = Email(email=email)
    except ValidationError as ex:
        errors.append(ex.errors()[0]['msg'])
    return errors


async def password_validator(password: str) -> list[str]:
    schema = PasswordValidator
    errors = []

    if not schema().min(8).validate(password):
        errors.append('Password must be at least 8 characters.')
    if not schema().max(50).validate(password):
        errors.append('Password must not exceed 50 characters.')
    if not schema().has().uppercase().validate(password):
        errors.append('Password must contain at least one uppercase letter.')
    if not schema().has().lowercase().validate(password):
        errors.append('Password must contain at least one lowercase letter.')
    if not schema().has().digits().validate(password):
        errors.append('Password must contain at least one digit.')
    if not schema().has().no().spaces().validate(password):
        errors.append('Password must not contain spaces.')
    if not schema().has().symbols().validate(password):
        errors.append('Password must contain at least one symbol.')

    return errors


async def password2_validator(x, y): return [
    'Please make sure to use the same password'] if x != y else []


async def user_validation(email: str, username: str, password: str, password2: str, firstname, lastname, db) -> dict[str, list]:
    errors = {}
    username_err = await username_validator(username, db)
    if username_err:
        errors['username'] = username_err
    email_err = await email_validator(email, db)
    if email_err:
        errors['email'] = email_err
    password_err = await password_validator(password)
    if password_err:
        errors['password'] = password_err
    password2_err = await password2_validator(password, password2)
    if password2_err:
        errors['password2'] = password2_err

    return errors
