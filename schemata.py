from pydantic import EmailStr
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Index
from typing import Optional, List
from datetime import datetime, timezone
from enum import Enum

# ---------------------------
# Role
# ---------------------------
class Role(str, Enum):
    ADMIN = "admin"
    MEMBER = "member"

# ---------------------------
# User
# ---------------------------
class UserBase(SQLModel):
    username: str = Field(index=True, unique=True, nullable=False)
    email: EmailStr = Field(unique=True, nullable=False)
    password_hash: str

#create
class UserCreate(UserBase):
    pass

#table
class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    projects: List["Project"] = Relationship(back_populates="owner")
    tasks_assigned: List["Task"] = Relationship(back_populates="assignee")
    comments: List["Comment"] = Relationship(back_populates="author")
    activity_logs: List["ActivityLog"] = Relationship(back_populates="user")
    token: "RT" = Relationship(back_populates="user")

# ---------------------------
# Project
# ---------------------------
class ProjectBase(SQLModel):
    name: str
    description: Optional[str] = None


class Project(ProjectBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    owner_id: int = Field(foreign_key="user.id", nullable=False)

    owner: Optional[User] = Relationship(back_populates="projects")
    members: List["ProjectMember"] = Relationship(back_populates="project")
    tasks: List["Task"] = Relationship(back_populates="project")

# ---------------------------
# ProjectMember
# ---------------------------
class ProjectMemberBase(SQLModel):
    role: Role = Field(default=Role.MEMBER, description="enum: admin/member")


class ProjectMember(ProjectMemberBase, table=True):
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    project_id: int = Field(foreign_key="project.id", primary_key=True)

    user: Optional[User] = Relationship()
    project: Optional[Project] = Relationship(back_populates="members")

    __table_args__ = (
        Index('ix_UserId_ProjectId', 'user_id', 'project_id'),
    )


# ---------------------------
# Task
# ---------------------------
class TaskBase(SQLModel):
    title: str
    description: Optional[str] = None
    status: Optional[str] = Field(default="todo", description="enum: todo/in_progress/done")
    due_date: Optional[datetime] = None


class Task(TaskBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="project.id", nullable=False)
    assignee_id: Optional[int] = Field(foreign_key="user.id")

    project: Optional[Project] = Relationship(back_populates="tasks")
    assignee: Optional[User] = Relationship(back_populates="tasks_assigned")
    comments: List["Comment"] = Relationship(back_populates="task")

    __table_args__ = (
        Index('ix_ProjectId_AssigneeId', 'project_id', 'assignee_id'),
    )


# ---------------------------
# Comment
# ---------------------------
class CommentBase(SQLModel):
    content: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Comment(CommentBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="task.id", nullable=False)
    author_id: int = Field(foreign_key="user.id", nullable=False)

    task: Optional[Task] = Relationship(back_populates="comments")
    author: Optional[User] = Relationship(back_populates="comments")

    __table_args__ = (
        Index("ix_TaskId", "task_id"),
    )
# ---------------------------
# ActivityLog
# ---------------------------
class ActivityLogBase(SQLModel):
    action: str
    target_type: str = Field(description="enum: project/task/comment")
    target_id: Optional[int] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ActivityLog(ActivityLogBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", nullable=False)

    user: Optional[User] = Relationship(back_populates="activity_logs")

    __table_args__ = (Index("ix_UserId", "user_id", "target_id"),)

#refresh_token
class RT(SQLModel, table=True):
    id: int = Field(primary_key=True, default=None)
    token: str = Field()
    user_id: int = Field(foreign_key="user.id")

    user: User = Relationship(back_populates="token")

    __table_args__= (Index("ix_Token", "token"),)