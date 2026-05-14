from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = "001_add_tests_system"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():

    # =========================
    # TEST FOLDERS
    # =========================

    op.create_table(
        "test_folders",

        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
        ),

        sa.Column(
            "name",
            sa.String(length=255),
            nullable=False,
        ),

        sa.Column(
            "parent_id",
            sa.Integer(),
            sa.ForeignKey(
                "test_folders.id",
                ondelete="CASCADE",
            ),
            nullable=True,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
        ),
    )

    # =========================
    # CERTIFICATE TEMPLATES
    # =========================

    op.create_table(
        "certificate_templates",

        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
        ),

        sa.Column(
            "name",
            sa.String(length=255),
            nullable=False,
        ),

        sa.Column(
            "background_image_file_id",
            sa.String(length=500),
            nullable=False,
        ),

        sa.Column(
            "signature_image_file_id",
            sa.String(length=500),
            nullable=False,
        ),

        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default="true",
        ),

        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
        ),
    )

    # =========================
    # TESTS
    # =========================

    op.create_table(
        "tests",

        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
        ),

        sa.Column(
            "folder_id",
            sa.Integer(),
            sa.ForeignKey(
                "test_folders.id",
                ondelete="CASCADE",
            ),
            nullable=False,
        ),

        sa.Column(
            "certificate_template_id",
            sa.Integer(),
            sa.ForeignKey(
                "certificate_templates.id",
            ),
            nullable=False,
        ),

        sa.Column(
            "title",
            sa.String(length=255),
            nullable=False,
        ),

        sa.Column(
            "telegram_file_id",
            sa.String(length=1000),
            nullable=False,
        ),

        sa.Column(
            "answer_key_json",
            sa.JSON(),
            nullable=False,
        ),

        sa.Column(
            "question_count",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default="true",
        ),

        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
        ),
    )

    # =========================
    # TEST ATTEMPTS
    # =========================

    op.create_table(
        "test_attempts",

        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
        ),

        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey(
                "users.id",
                ondelete="CASCADE",
            ),
            nullable=False,
        ),

        sa.Column(
            "test_id",
            sa.Integer(),
            sa.ForeignKey(
                "tests.id",
                ondelete="CASCADE",
            ),
            nullable=False,
        ),

        sa.Column(
            "submitted_answers",
            sa.JSON(),
            nullable=False,
        ),

        sa.Column(
            "correct_answers",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "wrong_answers",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "score_percent",
            sa.Float(),
            nullable=False,
        ),

        sa.Column(
            "duration_seconds",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "attempt_number",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "certificate_generated",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),

        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
        ),
    )

    # =========================
    # CERTIFICATES
    # =========================

    op.create_table(
        "certificates",

        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
        ),

        sa.Column(
            "attempt_id",
            sa.Integer(),
            sa.ForeignKey(
                "test_attempts.id",
                ondelete="CASCADE",
            ),
            nullable=False,
        ),

        sa.Column(
            "certificate_number",
            sa.String(length=255),
            nullable=False,
            unique=True,
        ),

        sa.Column(
            "telegram_file_id",
            sa.String(length=1000),
            nullable=False,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
        ),
    )


def downgrade():

    op.drop_table(
        "certificates"
    )

    op.drop_table(
        "test_attempts"
    )

    op.drop_table(
        "tests"
    )

    op.drop_table(
        "certificate_templates"
    )

    op.drop_table(
        "test_folders"
    )