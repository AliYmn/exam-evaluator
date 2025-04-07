from typing import List, Optional, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from fit_service.api.v1.workout.workout_schemas import (
    WorkoutCategoryCreate,
    WorkoutCategoryUpdate,
    WorkoutCategoryResponse,
    WorkoutCreate,
    WorkoutUpdate,
    WorkoutResponse,
    WorkoutSetCreate,
    WorkoutSetUpdate,
    WorkoutSetResponse,
    WorkoutProgramCreate,
    WorkoutProgramUpdate,
    WorkoutProgramResponse,
    WorkoutProgramDayCreate,
    WorkoutProgramDayUpdate,
    WorkoutProgramDayResponse,
)
from libs import ErrorCode, ExceptionBase
from libs.models.workout import (
    WorkoutCategory,
    Workout,
    WorkoutSet,
    WorkoutProgram,
    WorkoutProgramDay,
)


class WorkoutService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ===== Workout Category Methods =====
    async def create_workout_category(self, category_data: WorkoutCategoryCreate) -> WorkoutCategoryResponse:
        """Create a new workout category"""
        new_category = WorkoutCategory(
            name=category_data.name,
            description=category_data.description,
        )
        self.db.add(new_category)
        await self.db.commit()
        await self.db.refresh(new_category)

        return WorkoutCategoryResponse.model_validate(new_category)

    async def get_workout_category(self, category_id: int) -> WorkoutCategoryResponse:
        """Get a specific workout category by ID"""
        result = await self.db.execute(
            select(WorkoutCategory).where(WorkoutCategory.id == category_id, WorkoutCategory.deleted_date.is_(None))
        )
        category = result.scalars().first()
        if not category:
            raise ExceptionBase(ErrorCode.NOT_FOUND)

        return WorkoutCategoryResponse.model_validate(category)

    async def list_workout_categories(
        self, skip: int = 0, limit: int = 100
    ) -> Tuple[List[WorkoutCategoryResponse], int]:
        """List all workout categories with pagination"""
        # Get total count
        count_query = select(WorkoutCategory).where(WorkoutCategory.deleted_date.is_(None))
        count_result = await self.db.execute(count_query)
        total_count = len(count_result.scalars().all())

        # Get paginated records
        result = await self.db.execute(
            select(WorkoutCategory)
            .where(WorkoutCategory.deleted_date.is_(None))
            .order_by(WorkoutCategory.name)
            .offset(skip)
            .limit(limit)
        )
        categories = result.scalars().all()

        return [WorkoutCategoryResponse.model_validate(category) for category in categories], total_count

    async def update_workout_category(
        self, category_id: int, category_data: WorkoutCategoryUpdate
    ) -> WorkoutCategoryResponse:
        """Update a specific workout category"""
        result = await self.db.execute(
            select(WorkoutCategory).where(WorkoutCategory.id == category_id, WorkoutCategory.deleted_date.is_(None))
        )
        category = result.scalars().first()
        if not category:
            raise ExceptionBase(ErrorCode.NOT_FOUND)

        # Update fields if provided
        if category_data.name is not None:
            category.name = category_data.name
        if category_data.description is not None:
            category.description = category_data.description

        await self.db.commit()
        await self.db.refresh(category)

        return WorkoutCategoryResponse.model_validate(category)

    async def delete_workout_category(self, category_id: int) -> None:
        """Soft delete a specific workout category"""
        result = await self.db.execute(
            select(WorkoutCategory).where(WorkoutCategory.id == category_id, WorkoutCategory.deleted_date.is_(None))
        )
        category = result.scalars().first()
        if not category:
            raise ExceptionBase(ErrorCode.NOT_FOUND)

        category.soft_delete()
        await self.db.commit()

    # ===== Workout Methods =====
    async def create_workout(self, user_id: int, workout_data: WorkoutCreate) -> WorkoutResponse:
        """Create a new workout with optional sets"""
        new_workout = Workout(
            name=workout_data.name,
            description=workout_data.description,
            category_id=workout_data.category_id,
            difficulty_level=workout_data.difficulty_level,
            equipment_needed=workout_data.equipment_needed,
            muscle_groups=workout_data.muscle_groups,
            instructions=workout_data.instructions,
            video_url=workout_data.video_url,
            image_url=workout_data.image_url,
            user_id=user_id,
            is_custom=workout_data.is_custom,
        )
        self.db.add(new_workout)
        await self.db.commit()
        await self.db.refresh(new_workout)

        # Create workout sets if provided
        if workout_data.sets:
            for set_data in workout_data.sets:
                new_set = WorkoutSet(
                    workout_id=new_workout.id,
                    set_number=set_data.set_number,
                    reps=set_data.reps,
                    weight=set_data.weight,
                    duration_seconds=set_data.duration_seconds,
                    rest_seconds=set_data.rest_seconds,
                    notes=set_data.notes,
                )
                self.db.add(new_set)

            await self.db.commit()
            await self.db.refresh(new_workout)

        # Load the workout with relationships for response
        result = await self.db.execute(
            select(Workout)
            .options(joinedload(Workout.sets), joinedload(Workout.category))
            .where(Workout.id == new_workout.id)
        )
        workout_with_relations = result.scalars().first()

        return WorkoutResponse.model_validate(workout_with_relations)

    async def get_workout(self, workout_id: int) -> WorkoutResponse:
        """Get a specific workout by ID with its sets and category"""
        result = await self.db.execute(
            select(Workout)
            .options(joinedload(Workout.sets), joinedload(Workout.category))
            .where(Workout.id == workout_id, Workout.deleted_date.is_(None))
        )
        workout = result.scalars().first()
        if not workout:
            raise ExceptionBase(ErrorCode.NOT_FOUND)

        return WorkoutResponse.model_validate(workout)

    async def list_workouts(
        self,
        user_id: Optional[int] = None,
        category_id: Optional[int] = None,
        difficulty_level: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[WorkoutResponse], int]:
        """List workouts with optional filtering by user_id and category_id"""
        # Build base query
        base_query = select(Workout).where(Workout.deleted_date.is_(None))

        # Apply filters
        if user_id is not None:
            base_query = base_query.where(Workout.user_id == user_id)
        if category_id is not None:
            base_query = base_query.where(Workout.category_id == category_id)
        if difficulty_level is not None:
            base_query = base_query.where(Workout.difficulty_level == difficulty_level)

        # Get total count
        count_result = await self.db.execute(base_query)
        total_count = len(count_result.scalars().all())

        # Get paginated records with relationships
        result = await self.db.execute(
            base_query.options(joinedload(Workout.sets), joinedload(Workout.category))
            .order_by(Workout.name)
            .offset(skip)
            .limit(limit)
        )
        workouts = result.unique().scalars().all()

        return [WorkoutResponse.model_validate(workout) for workout in workouts], total_count

    async def update_workout(self, workout_id: int, user_id: int, workout_data: WorkoutUpdate) -> WorkoutResponse:
        """Update a specific workout"""
        # Get the workout with ownership check
        result = await self.db.execute(
            select(Workout).where(Workout.id == workout_id, Workout.user_id == user_id, Workout.deleted_date.is_(None))
        )
        workout = result.scalars().first()
        if not workout:
            raise ExceptionBase(ErrorCode.NOT_FOUND)

        # Update fields if provided
        if workout_data.name is not None:
            workout.name = workout_data.name
        if workout_data.description is not None:
            workout.description = workout_data.description
        if workout_data.category_id is not None:
            workout.category_id = workout_data.category_id
        if workout_data.difficulty_level is not None:
            workout.difficulty_level = workout_data.difficulty_level
        if workout_data.equipment_needed is not None:
            workout.equipment_needed = workout_data.equipment_needed
        if workout_data.muscle_groups is not None:
            workout.muscle_groups = workout_data.muscle_groups
        if workout_data.instructions is not None:
            workout.instructions = workout_data.instructions
        if workout_data.video_url is not None:
            workout.video_url = workout_data.video_url
        if workout_data.image_url is not None:
            workout.image_url = workout_data.image_url
        if workout_data.is_custom is not None:
            workout.is_custom = workout_data.is_custom

        await self.db.commit()

        # Load the workout with relationships for response
        result = await self.db.execute(
            select(Workout)
            .options(joinedload(Workout.sets), joinedload(Workout.category))
            .where(Workout.id == workout_id)
        )
        updated_workout = result.scalars().first()

        return WorkoutResponse.model_validate(updated_workout)

    async def delete_workout(self, workout_id: int, user_id: int) -> None:
        """Soft delete a specific workout with ownership check"""
        result = await self.db.execute(
            select(Workout).where(Workout.id == workout_id, Workout.user_id == user_id, Workout.deleted_date.is_(None))
        )
        workout = result.scalars().first()
        if not workout:
            raise ExceptionBase(ErrorCode.NOT_FOUND)

        workout.soft_delete()
        await self.db.commit()

    # ===== Workout Set Methods =====
    async def create_workout_set(self, workout_id: int, user_id: int, set_data: WorkoutSetCreate) -> WorkoutSetResponse:
        """Create a new workout set for a specific workout"""
        # Verify workout exists and belongs to user
        result = await self.db.execute(
            select(Workout).where(Workout.id == workout_id, Workout.user_id == user_id, Workout.deleted_date.is_(None))
        )
        workout = result.scalars().first()
        if not workout:
            raise ExceptionBase(ErrorCode.NOT_FOUND)

        new_set = WorkoutSet(
            workout_id=workout_id,
            set_number=set_data.set_number,
            reps=set_data.reps,
            weight=set_data.weight,
            duration_seconds=set_data.duration_seconds,
            rest_seconds=set_data.rest_seconds,
            notes=set_data.notes,
        )
        self.db.add(new_set)
        await self.db.commit()
        await self.db.refresh(new_set)

        return WorkoutSetResponse.model_validate(new_set)

    async def update_workout_set(self, set_id: int, user_id: int, set_data: WorkoutSetUpdate) -> WorkoutSetResponse:
        """Update a specific workout set with user ownership check"""
        # Get the set with workout and user check
        result = await self.db.execute(
            select(WorkoutSet)
            .join(Workout)
            .where(WorkoutSet.id == set_id, Workout.user_id == user_id, WorkoutSet.deleted_date.is_(None))
        )
        workout_set = result.scalars().first()
        if not workout_set:
            raise ExceptionBase(ErrorCode.NOT_FOUND)

        # Update fields if provided
        if set_data.set_number is not None:
            workout_set.set_number = set_data.set_number
        if set_data.reps is not None:
            workout_set.reps = set_data.reps
        if set_data.weight is not None:
            workout_set.weight = set_data.weight
        if set_data.duration_seconds is not None:
            workout_set.duration_seconds = set_data.duration_seconds
        if set_data.rest_seconds is not None:
            workout_set.rest_seconds = set_data.rest_seconds
        if set_data.notes is not None:
            workout_set.notes = set_data.notes

        await self.db.commit()
        await self.db.refresh(workout_set)

        return WorkoutSetResponse.model_validate(workout_set)

    async def delete_workout_set(self, set_id: int, user_id: int) -> None:
        """Soft delete a specific workout set with user ownership check"""
        result = await self.db.execute(
            select(WorkoutSet)
            .join(Workout)
            .where(WorkoutSet.id == set_id, Workout.user_id == user_id, WorkoutSet.deleted_date.is_(None))
        )
        workout_set = result.scalars().first()
        if not workout_set:
            raise ExceptionBase(ErrorCode.NOT_FOUND)

        workout_set.soft_delete()
        await self.db.commit()

    # ===== Workout Program Methods =====
    async def create_workout_program(self, user_id: int, program_data: WorkoutProgramCreate) -> WorkoutProgramResponse:
        """Create a new workout program with optional days and workouts"""
        new_program = WorkoutProgram(
            name=program_data.name,
            description=program_data.description,
            user_id=user_id,
            group_name=program_data.group_name,
            difficulty_level=program_data.difficulty_level,
            duration_weeks=program_data.duration_weeks,
            goal=program_data.goal,
            is_public=program_data.is_public,
        )
        self.db.add(new_program)
        await self.db.commit()
        await self.db.refresh(new_program)

        # Create program days if provided
        if program_data.days:
            for day_data in program_data.days:
                new_day = WorkoutProgramDay(
                    program_id=new_program.id,
                    day_number=day_data.day_number,
                    name=day_data.name,
                    description=day_data.description,
                )
                self.db.add(new_day)
                await self.db.commit()
                await self.db.refresh(new_day)

                # Associate workouts with the day
                if day_data.workout_ids:
                    for workout_id in day_data.workout_ids:
                        # Verify workout exists
                        workout_result = await self.db.execute(
                            select(Workout).where(Workout.id == workout_id, Workout.deleted_date.is_(None))
                        )
                        workout = workout_result.scalars().first()
                        if workout:
                            # Add association
                            new_day.workouts.append(workout)

                    await self.db.commit()

        # Load the program with relationships for response
        result = await self.db.execute(
            select(WorkoutProgram)
            .options(
                joinedload(WorkoutProgram.days)
                .joinedload(WorkoutProgramDay.workouts)
                .options(joinedload(Workout.sets), joinedload(Workout.category))
            )
            .where(WorkoutProgram.id == new_program.id)
        )
        program_with_relations = result.unique().scalars().first()

        return WorkoutProgramResponse.model_validate(program_with_relations)

    async def get_workout_program(self, program_id: int, user_id: Optional[int] = None) -> WorkoutProgramResponse:
        """Get a specific workout program by ID with its days and workouts"""
        query = (
            select(WorkoutProgram)
            .options(
                joinedload(WorkoutProgram.days)
                .joinedload(WorkoutProgramDay.workouts)
                .options(joinedload(Workout.sets), joinedload(Workout.category))
            )
            .where(WorkoutProgram.id == program_id, WorkoutProgram.deleted_date.is_(None))
        )

        # If user_id is provided, check ownership or public status
        if user_id is not None:
            query = query.where((WorkoutProgram.user_id == user_id) | (WorkoutProgram.is_public == 1))

        result = await self.db.execute(query)
        program = result.unique().scalars().first()
        if not program:
            raise ExceptionBase(ErrorCode.NOT_FOUND)

        return WorkoutProgramResponse.model_validate(program)

    async def list_workout_programs(
        self,
        user_id: Optional[int] = None,
        group_name: Optional[str] = None,
        include_public: bool = False,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[WorkoutProgramResponse], int]:
        """List workout programs with optional filtering"""
        # Build base query
        base_query = select(WorkoutProgram).where(WorkoutProgram.deleted_date.is_(None))

        # Apply filters
        if user_id is not None:
            if include_public:
                base_query = base_query.where((WorkoutProgram.user_id == user_id) | (WorkoutProgram.is_public == 1))
            else:
                base_query = base_query.where(WorkoutProgram.user_id == user_id)

        if group_name is not None:
            base_query = base_query.where(WorkoutProgram.group_name == group_name)

        # Get total count
        count_result = await self.db.execute(base_query)
        total_count = len(count_result.scalars().all())

        # Get paginated records with relationships
        result = await self.db.execute(
            base_query.options(
                joinedload(WorkoutProgram.days)
                .joinedload(WorkoutProgramDay.workouts)
                .options(joinedload(Workout.sets), joinedload(Workout.category))
            )
            .order_by(WorkoutProgram.name)
            .offset(skip)
            .limit(limit)
        )
        programs = result.unique().scalars().all()

        return [WorkoutProgramResponse.model_validate(program) for program in programs], total_count

    async def update_workout_program(
        self, program_id: int, user_id: int, program_data: WorkoutProgramUpdate
    ) -> WorkoutProgramResponse:
        """Update a specific workout program"""
        # Get the program with ownership check
        result = await self.db.execute(
            select(WorkoutProgram).where(
                WorkoutProgram.id == program_id,
                WorkoutProgram.user_id == user_id,
                WorkoutProgram.deleted_date.is_(None),
            )
        )
        program = result.scalars().first()
        if not program:
            raise ExceptionBase(ErrorCode.NOT_FOUND)

        # Update fields if provided
        if program_data.name is not None:
            program.name = program_data.name
        if program_data.description is not None:
            program.description = program_data.description
        if program_data.group_name is not None:
            program.group_name = program_data.group_name
        if program_data.difficulty_level is not None:
            program.difficulty_level = program_data.difficulty_level
        if program_data.duration_weeks is not None:
            program.duration_weeks = program_data.duration_weeks
        if program_data.goal is not None:
            program.goal = program_data.goal
        if program_data.is_public is not None:
            program.is_public = program_data.is_public

        await self.db.commit()

        # Load the program with relationships for response
        result = await self.db.execute(
            select(WorkoutProgram)
            .options(joinedload(WorkoutProgram.days).joinedload(WorkoutProgramDay.workouts))
            .where(WorkoutProgram.id == program_id)
        )
        updated_program = result.scalars().first()

        return WorkoutProgramResponse.model_validate(updated_program)

    async def delete_workout_program(self, program_id: int, user_id: int) -> None:
        """Soft delete a specific workout program with ownership check"""
        result = await self.db.execute(
            select(WorkoutProgram).where(
                WorkoutProgram.id == program_id,
                WorkoutProgram.user_id == user_id,
                WorkoutProgram.deleted_date.is_(None),
            )
        )
        program = result.scalars().first()
        if not program:
            raise ExceptionBase(ErrorCode.NOT_FOUND)

        program.soft_delete()
        await self.db.commit()

    # ===== Workout Program Day Methods =====
    async def create_workout_program_day(
        self, program_id: int, user_id: int, day_data: WorkoutProgramDayCreate
    ) -> WorkoutProgramDayResponse:
        """Create a new workout program day for a specific program"""
        # Verify program exists and belongs to user
        result = await self.db.execute(
            select(WorkoutProgram).where(
                WorkoutProgram.id == program_id,
                WorkoutProgram.user_id == user_id,
                WorkoutProgram.deleted_date.is_(None),
            )
        )
        program = result.scalars().first()
        if not program:
            raise ExceptionBase(ErrorCode.NOT_FOUND)

        new_day = WorkoutProgramDay(
            program_id=program_id,
            day_number=day_data.day_number,
            name=day_data.name,
            description=day_data.description,
        )
        self.db.add(new_day)
        await self.db.commit()
        await self.db.refresh(new_day)

        # Associate workouts with the day
        if day_data.workout_ids:
            for workout_id in day_data.workout_ids:
                # Verify workout exists
                workout_result = await self.db.execute(
                    select(Workout).where(Workout.id == workout_id, Workout.deleted_date.is_(None))
                )
                workout = workout_result.scalars().first()
                if workout:
                    # Add association
                    new_day.workouts.append(workout)

            await self.db.commit()
            await self.db.refresh(new_day)

        # Load the day with relationships for response
        result = await self.db.execute(
            select(WorkoutProgramDay)
            .options(joinedload(WorkoutProgramDay.workouts))
            .where(WorkoutProgramDay.id == new_day.id)
        )
        day_with_relations = result.scalars().first()

        return WorkoutProgramDayResponse.model_validate(day_with_relations)

    async def update_workout_program_day(
        self, day_id: int, user_id: int, day_data: WorkoutProgramDayUpdate
    ) -> WorkoutProgramDayResponse:
        """Update a specific workout program day with user ownership check"""
        # Get the day with program and user check
        result = await self.db.execute(
            select(WorkoutProgramDay)
            .join(WorkoutProgram)
            .where(
                WorkoutProgramDay.id == day_id,
                WorkoutProgram.user_id == user_id,
                WorkoutProgramDay.deleted_date.is_(None),
            )
        )
        day = result.scalars().first()
        if not day:
            raise ExceptionBase(ErrorCode.NOT_FOUND)

        # Update fields if provided
        if day_data.day_number is not None:
            day.day_number = day_data.day_number
        if day_data.name is not None:
            day.name = day_data.name
        if day_data.description is not None:
            day.description = day_data.description

        # Update workout associations if provided
        if day_data.workout_ids is not None:
            # Clear existing associations
            day.workouts = []

            # Add new associations
            for workout_id in day_data.workout_ids:
                workout_result = await self.db.execute(
                    select(Workout).where(Workout.id == workout_id, Workout.deleted_date.is_(None))
                )
                workout = workout_result.scalars().first()
                if workout:
                    day.workouts.append(workout)

        await self.db.commit()

        # Load the day with relationships for response
        result = await self.db.execute(
            select(WorkoutProgramDay)
            .options(joinedload(WorkoutProgramDay.workouts))
            .where(WorkoutProgramDay.id == day_id)
        )
        updated_day = result.scalars().first()

        return WorkoutProgramDayResponse.model_validate(updated_day)

    async def delete_workout_program_day(self, day_id: int, user_id: int) -> None:
        """Soft delete a specific workout program day with user ownership check"""
        result = await self.db.execute(
            select(WorkoutProgramDay)
            .join(WorkoutProgram)
            .where(
                WorkoutProgramDay.id == day_id,
                WorkoutProgram.user_id == user_id,
                WorkoutProgramDay.deleted_date.is_(None),
            )
        )
        day = result.scalars().first()
        if not day:
            raise ExceptionBase(ErrorCode.NOT_FOUND)

        day.soft_delete()
        await self.db.commit()
