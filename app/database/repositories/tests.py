from __future__ import annotations

from sqlalchemy import (
    select,
)
from sqlalchemy.orm import (
    selectinload,
)
from app.database.models.certificate_template import (
    CertificateTemplate,
)
from app.database.models.test_attempt import (
    TestAttempt,
)
from app.database.db import (
    async_session,
)
from app.database.models.certificate import (
    Certificate,
)
from app.database.models.test_folder import (
    TestFolder,
)

from app.database.models.test import (
    Test,
)
from app.database.models.test_attempt import (
    TestAttempt,
)

from app.database.models.user import (
    User,
)

from sqlalchemy import func

# =========================
# CREATE FOLDER
# =========================

async def create_test_folder(
    name: str,
    parent_id: int | None = None,
):

    async with async_session() as session:

        folder = TestFolder(
            name=name,
            parent_id=parent_id,
        )

        session.add(folder)

        await session.commit()

        await session.refresh(folder)

        return folder


# =========================
# GET ROOT FOLDERS
# =========================

async def get_root_test_folders():

    async with async_session() as session:

        result = await session.execute(
            select(TestFolder).where(
                TestFolder.parent_id == None
            )
        )

        return result.scalars().all()


# =========================
# GET CHILD FOLDERS
# =========================

async def get_child_folders(
    parent_id: int,
):

    async with async_session() as session:

        result = await session.execute(
            select(TestFolder).where(
                TestFolder.parent_id == parent_id
            )
        )

        return result.scalars().all()


# =========================
# GET FOLDER BY ID
# =========================

async def get_folder_by_id(
    folder_id: int,
):

    async with async_session() as session:

        result = await session.execute(
            select(TestFolder).where(
                TestFolder.id == folder_id
            )
        )

        return result.scalar_one_or_none()


# =========================
# CREATE TEST
# =========================

async def create_test(
    folder_id: int,
    certificate_template_id: int,
    title: str,
    telegram_file_id: str,
    answer_key_json: dict,
    question_count: int,
):

    async with async_session() as session:

        test = Test(
            folder_id=folder_id,
            certificate_template_id=(
                certificate_template_id
            ),
            title=title,
            telegram_file_id=telegram_file_id,
            answer_key_json=answer_key_json,
            question_count=question_count,
        )

        session.add(test)

        await session.commit()

        await session.refresh(test)

        return test


# =========================
# GET TESTS BY FOLDER
# =========================

async def get_tests_by_folder(
    folder_id: int,
):

    async with async_session() as session:

        result = await session.execute(
            select(Test).where(
                Test.folder_id == folder_id
            )
        )

        return result.scalars().all()


# =========================
# GET TEST BY ID
# =========================

async def get_test_by_id(
    test_id: int,
):

    async with async_session() as session:

        result = await session.execute(
            select(Test).where(
                Test.id == test_id
            )
        )

        return result.scalar_one_or_none()


# =========================
# DELETE TEST
# =========================

async def delete_test_by_id(
    test_id: int,
):

    async with async_session() as session:

        result = await session.execute(
            select(Test).where(
                Test.id == test_id
            )
        )

        test = result.scalar_one_or_none()

        if not test:
            return False

        await session.delete(test)

        await session.commit()

        return True

# =========================
# GET USER DB ID
# =========================

async def get_user_db_id(
    telegram_id: int,
):

    async with async_session() as session:

        result = await session.execute(
            select(User).where(
                User.telegram_id == telegram_id
            )
        )

        user = result.scalar_one_or_none()

        if not user:
            return None

        return user.id


# =========================
# GET ATTEMPTS COUNT
# =========================

async def get_attempts_count(
    user_id: int,
    test_id: int,
):

    async with async_session() as session:

        result = await session.execute(
            select(
                func.count(
                    TestAttempt.id
                )
            ).where(
                TestAttempt.user_id
                == user_id,

                TestAttempt.test_id
                == test_id,
            )
        )

        return result.scalar() or 0


# =========================
# CREATE TEST ATTEMPT
# =========================

async def create_test_attempt(
    user_id: int,
    test_id: int,
    submitted_answers: dict,
    correct_answers: int,
    wrong_answers: int,
    score_percent: float,
    duration_seconds: int,
    attempt_number: int,
    certificate_generated: bool,
):

    async with async_session() as session:

        attempt = TestAttempt(
            user_id=user_id,
            test_id=test_id,
            submitted_answers=(
                submitted_answers
            ),
            correct_answers=(
                correct_answers
            ),
            wrong_answers=wrong_answers,
            score_percent=score_percent,
            duration_seconds=(
                duration_seconds
            ),
            attempt_number=attempt_number,
            certificate_generated=(
                certificate_generated
            ),
        )

        session.add(attempt)

        await session.commit()

        await session.refresh(attempt)

        await session.refresh(
            attempt
        )

        return attempt

# =========================
# CREATE CERTIFICATE
# =========================

async def create_certificate(
    attempt_id: int,
    certificate_number: str,
    telegram_file_id: str,
):

    async with async_session() as session:

        certificate = Certificate(
            attempt_id=attempt_id,
            certificate_number=(
                certificate_number
            ),
            telegram_file_id=(
                telegram_file_id
            ),
        )

        session.add(certificate)

        await session.commit()

        await session.refresh(certificate)

        return certificate

# =========================
# GET TEST RESULTS
# =========================

async def get_test_results(
    test_id: int,
):

    async with async_session() as session:

        result = await session.execute(
            select(TestAttempt)
            .options(
                selectinload(
                    TestAttempt.user
                )
            )
            .where(
                TestAttempt.test_id
                == test_id
            )
            .order_by(
                TestAttempt.score_percent.desc()
            )
        )

        return result.scalars().all()

# =========================
# COUNT TEST ATTEMPTS
# =========================

async def count_test_attempts(
    test_id: int,
):

    async with async_session() as session:

        result = await session.execute(
            select(
                func.count(
                    TestAttempt.id
                )
            ).where(
                TestAttempt.test_id
                == test_id
            )
        )

        return result.scalar() or 0

# =========================
# CREATE CERTIFICATE TEMPLATE
# =========================

async def create_certificate_template(
    name: str,
    background_image_file_id: str,
    signature_image_file_id: str,
):

    async with async_session() as session:

        template = CertificateTemplate(
            name=name,
            background_image_file_id=(
                background_image_file_id
            ),
            signature_image_file_id=(
                signature_image_file_id
            ),
        )

        session.add(template)

        await session.commit()

        await session.refresh(template)

        return template


# =========================
# GET CERTIFICATE TEMPLATES
# =========================

async def get_certificate_templates():

    async with async_session() as session:

        result = await session.execute(
            select(
                CertificateTemplate
            )
        )

        return result.scalars().all()


# =========================
# GET TEMPLATE BY ID
# =========================

async def get_certificate_template_by_id(
    template_id: int,
):

    async with async_session() as session:

        result = await session.execute(
            select(
                CertificateTemplate
            ).where(
                CertificateTemplate.id
                == template_id
            )
        )

        return result.scalar_one_or_none()