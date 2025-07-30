"""
# File       : api_会员类型管理.py
# Time       ：2024/12/20
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：会员类型管理API - 安全版本
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from svc_user_auth_zxw.db.models import MembershipType, Role, App, User
from svc_user_auth_zxw.db.get_db import get_db
from svc_user_auth_zxw.SDK_jwt.jwt import get_current_user
from svc_user_auth_zxw.apis.schemas import (
    会员类型创建请求, 会员类型响应, 会员类型更新请求, 通用响应
)
from app_tools_zxw.Errors.api_errors import HTTPException_AppToolsSZXW
from svc_user_auth_zxw.tools.error_code import ErrorCode

router = APIRouter(prefix="/membership-types", tags=["会员类型管理"])


async def _check_admin_permission(user: User, db: AsyncSession) -> bool:
    """检查用户是否有管理员权限"""
    # 检查用户是否有admin角色
    has_admin_role = any(
        role.name == "admin" for role in user.roles
    )
    return has_admin_role


async def _require_admin_permission(user: User, db: AsyncSession):
    """要求管理员权限，如果没有则抛出异常"""
    if not await _check_admin_permission(user, db):
        raise HTTPException_AppToolsSZXW(
            error_code=ErrorCode.权限不足,
            detail="需要管理员权限",
            http_status_code=403
        )


# ==================== 内部函数 (不直接暴露API) ====================

async def internal_get_membership_types(
        skip: int = 0,
        limit: int = 100,
        include_disabled: bool = False,
        db: AsyncSession = None
) -> List[会员类型响应]:
    """
    内部获取会员类型列表函数

    Args:
        skip: 跳过的记录数
        limit: 限制返回的记录数
        include_disabled: 是否包含已停用的类型
        db: 数据库会话

    Returns:
        会员类型响应列表
    """
    try:
        query = select(MembershipType)
        if not include_disabled:
            query = query.where(MembershipType.is_active == True)

        result = await db.execute(
            query.offset(skip)
            .limit(limit)
            .order_by(MembershipType.created_at.desc())
        )
        membership_types = result.scalars().all()

        return [会员类型响应.model_validate(mt) for mt in membership_types]

    except Exception as e:
        raise HTTPException_AppToolsSZXW(
            error_code=ErrorCode.系统异常,
            detail=f"获取会员类型列表失败: {str(e)}",
            http_status_code=500
        )


async def internal_get_membership_type_by_id(
        membership_type_id: int,
        include_disabled: bool = False,
        db: AsyncSession = None
) -> 会员类型响应:
    """
    内部获取会员类型详情函数

    Args:
        membership_type_id: 会员类型ID
        include_disabled: 是否包含已停用的类型
        db: 数据库会话

    Returns:
        会员类型响应对象
    """
    try:
        query = select(MembershipType).options(selectinload(MembershipType.roles))

        if include_disabled:
            query = query.where(MembershipType.id == membership_type_id)
        else:
            query = query.where(
                MembershipType.id == membership_type_id,
                MembershipType.is_active == True
            )

        result = await db.execute(query)
        membership_type = result.scalar_one_or_none()

        if not membership_type:
            error_msg = "会员类型不存在" if include_disabled else "会员类型不存在或已停用"
            raise HTTPException_AppToolsSZXW(
                error_code=ErrorCode.参数错误,
                detail=error_msg,
                http_status_code=404
            )

        return 会员类型响应.model_validate(membership_type)

    except Exception as e:
        if isinstance(e, HTTPException_AppToolsSZXW):
            raise
        raise HTTPException_AppToolsSZXW(
            error_code=ErrorCode.系统异常,
            detail=f"获取会员类型详情失败: {str(e)}",
            http_status_code=500
        )


async def internal_create_membership_type(
        request: 会员类型创建请求,
        db: AsyncSession = None
) -> 会员类型响应:
    """
    内部创建会员类型函数

    Args:
        request: 会员类型创建请求
        db: 数据库会话

    Returns:
        会员类型响应对象
    """
    try:
        # 检查会员类型名称是否已存在
        result = await db.execute(
            select(MembershipType).where(MembershipType.name == request.name)
        )
        if result.scalar_one_or_none():
            raise HTTPException_AppToolsSZXW(
                error_code=ErrorCode.参数错误,
                detail="会员类型名称已存在",
                http_status_code=400
            )

        # 创建会员类型
        membership_type = MembershipType(
            name=request.name,
            description=request.description,
            duration_days=request.duration_days,
            price=request.price
        )

        # 如果有角色关联，处理角色关联
        if request.role_names and request.app_name:
            # 查找应用
            app_result = await db.execute(
                select(App).where(App.name == request.app_name)
            )
            app = app_result.scalar_one_or_none()
            if not app:
                # 创建应用
                app = App(name=request.app_name)
                db.add(app)
                await db.flush()

            # 查找或创建角色
            for role_name in request.role_names:
                role_result = await db.execute(
                    select(Role).where(
                        Role.name == role_name,
                        Role.app_id == app.id
                    )
                )
                role = role_result.scalar_one_or_none()
                if not role:
                    role = Role(name=role_name, app_id=app.id)
                    db.add(role)
                    await db.flush()

                membership_type.roles.append(role)

        db.add(membership_type)
        await db.commit()
        await db.refresh(membership_type)

        return 会员类型响应.model_validate(membership_type)

    except Exception as e:
        await db.rollback()
        if isinstance(e, HTTPException_AppToolsSZXW):
            raise
        raise HTTPException_AppToolsSZXW(
            error_code=ErrorCode.系统异常,
            detail=f"会员类型创建失败: {str(e)}",
            http_status_code=500
        )


async def internal_update_membership_type(
        membership_type_id: int,
        request: 会员类型更新请求,
        db: AsyncSession = None
) -> 会员类型响应:
    """
    内部更新会员类型函数

    Args:
        membership_type_id: 会员类型ID
        request: 会员类型更新请求
        db: 数据库会话

    Returns:
        会员类型响应对象
    """
    try:
        result = await db.execute(
            select(MembershipType)
            .options(selectinload(MembershipType.roles))
            .where(MembershipType.id == membership_type_id)
        )
        membership_type = result.scalar_one_or_none()

        if not membership_type:
            raise HTTPException_AppToolsSZXW(
                error_code=ErrorCode.参数错误,
                detail="会员类型不存在",
                http_status_code=404
            )

        # 更新基本信息
        if request.name is not None:
            # 检查名称是否重复
            name_check = await db.execute(
                select(MembershipType).where(
                    MembershipType.name == request.name,
                    MembershipType.id != membership_type_id
                )
            )
            if name_check.scalar_one_or_none():
                raise HTTPException_AppToolsSZXW(
                    error_code=ErrorCode.参数错误,
                    detail="会员类型名称已存在",
                    http_status_code=400
                )
            membership_type.name = request.name

        if request.description is not None:
            membership_type.description = request.description
        if request.duration_days is not None:
            membership_type.duration_days = request.duration_days
        if request.price is not None:
            membership_type.price = request.price
        if request.is_active is not None:
            membership_type.is_active = request.is_active

        # 更新角色关联
        if request.role_names is not None and request.app_name:
            # 清除现有角色关联
            membership_type.roles.clear()

            # 查找应用
            app_result = await db.execute(
                select(App).where(App.name == request.app_name)
            )
            app = app_result.scalar_one_or_none()
            if not app:
                app = App(name=request.app_name)
                db.add(app)
                await db.flush()

            # 添加新的角色关联
            for role_name in request.role_names:
                role_result = await db.execute(
                    select(Role).where(
                        Role.name == role_name,
                        Role.app_id == app.id
                    )
                )
                role = role_result.scalar_one_or_none()
                if not role:
                    role = Role(name=role_name, app_id=app.id)
                    db.add(role)
                    await db.flush()

                membership_type.roles.append(role)

        await db.commit()
        await db.refresh(membership_type)

        return 会员类型响应.model_validate(membership_type)

    except Exception as e:
        await db.rollback()
        if isinstance(e, HTTPException_AppToolsSZXW):
            raise
        raise HTTPException_AppToolsSZXW(
            error_code=ErrorCode.系统异常,
            detail=f"会员类型更新失败: {str(e)}",
            http_status_code=500
        )


async def internal_delete_membership_type(
        membership_type_id: int,
        db: AsyncSession = None
) -> bool:
    """
    内部删除会员类型函数

    Args:
        membership_type_id: 会员类型ID
        db: 数据库会话

    Returns:
        删除成功返回True
    """


    try:
        result = await db.execute(
            select(MembershipType)
            .options(selectinload(MembershipType.memberships))
            .where(MembershipType.id == membership_type_id)
        )
        membership_type = result.scalar_one_or_none()

        if not membership_type:
            raise HTTPException_AppToolsSZXW(
                error_code=ErrorCode.参数错误,
                detail="会员类型不存在",
                http_status_code=404
            )

        # 检查是否有用户使用此会员类型
        if membership_type.memberships:
            raise HTTPException_AppToolsSZXW(
                error_code=ErrorCode.参数错误,
                detail="该会员类型下还有用户会员记录，无法删除",
                http_status_code=400
            )

        await db.delete(membership_type)
        await db.commit()

        return True

    except Exception as e:
        await db.rollback()
        if isinstance(e, HTTPException_AppToolsSZXW):
            raise
        raise HTTPException_AppToolsSZXW(
            error_code=ErrorCode.参数错误,
            detail=f"会员类型删除失败: {str(e)}",
            http_status_code=500
        )


# ==================== 公开查询API (无需管理员权限) ====================

@router.get("/", response_model=通用响应[List[会员类型响应]])
async def 获取会员类型列表(
        skip: int = 0,
        limit: int = 100,
        db: AsyncSession = Depends(get_db)
):
    """获取会员类型列表（只返回启用的类型）"""
    membership_types = await internal_get_membership_types(
        skip=skip,
        limit=limit,
        include_disabled=False,
        db=db
    )

    return 通用响应(
        data=membership_types,
        message="获取成功"
    )


@router.get("/{membership_type_id}", response_model=通用响应[会员类型响应])
async def 获取会员类型详情(
        membership_type_id: int,
        db: AsyncSession = Depends(get_db)
):
    """获取会员类型详情（只返回启用的类型）"""
    membership_type = await internal_get_membership_type_by_id(
        membership_type_id=membership_type_id,
        include_disabled=False,
        db=db
    )

    return 通用响应(
        data=membership_type,
        message="获取成功"
    )


# ==================== 管理员专用API ====================

@router.post("/admin/", response_model=通用响应[会员类型响应])
async def 管理员创建会员类型(
        request: 会员类型创建请求,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    await _require_admin_permission(current_user, db)

    """管理员创建会员类型"""
    membership_type = await internal_create_membership_type(
        request=request,
        db=db
    )

    return 通用响应(
        data=membership_type,
        message="会员类型创建成功"
    )


@router.get("/admin/all", response_model=通用响应[List[会员类型响应]])
async def 管理员获取所有会员类型(
        skip: int = 0,
        limit: int = 100,
        include_disabled: bool = False,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """管理员获取所有会员类型列表（包括已停用的）"""
    # 验证管理员权限
    await _require_admin_permission(current_user, db)

    membership_types = await internal_get_membership_types(
        skip=skip,
        limit=limit,
        include_disabled=include_disabled,
        db=db
    )

    return 通用响应(
        data=membership_types,
        message="获取成功"
    )


@router.get("/admin/{membership_type_id}", response_model=通用响应[会员类型响应])
async def 管理员获取会员类型详情(
        membership_type_id: int,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """管理员获取会员类型详情（包括已停用的）"""
    # 验证管理员权限
    await _require_admin_permission(current_user, db)

    membership_type = await internal_get_membership_type_by_id(
        membership_type_id=membership_type_id,
        include_disabled=True,
        db=db
    )

    return 通用响应(
        data=membership_type,
        message="获取成功"
    )


@router.put("/admin/{membership_type_id}", response_model=通用响应[会员类型响应])
async def 管理员更新会员类型(
        membership_type_id: int,
        request: 会员类型更新请求,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    # 验证管理员权限
    await _require_admin_permission(current_user, db)

    """管理员更新会员类型"""
    membership_type = await internal_update_membership_type(
        membership_type_id=membership_type_id,
        request=request,
        db=db
    )

    return 通用响应(
        data=membership_type,
        message="会员类型更新成功"
    )


@router.delete("/admin/{membership_type_id}", response_model=通用响应[dict])
async def 管理员删除会员类型(
        membership_type_id: int,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    # 验证管理员权限
    await _require_admin_permission(current_user, db)

    """管理员删除会员类型"""
    deleted = await internal_delete_membership_type(
        membership_type_id=membership_type_id,
        db=db
    )

    return 通用响应(
        data={"deleted": deleted},
        message="会员类型删除成功"
    )
