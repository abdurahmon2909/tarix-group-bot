from __future__ import annotations

from sqlalchemy import (
    select,
)

from app.database.db import (
    async_session,
)

from app.database.models.test_folder import (
    TestFolder,
)

from app.database.models.test import (
    Test,
)


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