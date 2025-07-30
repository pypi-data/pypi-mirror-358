import uuid
from datetime import (
    datetime,
)

from django.db.models import (
    CASCADE,
    PROTECT,
    SET_NULL,
    DateTimeField,
    FileField,
    ForeignKey,
    JSONField,
    PositiveSmallIntegerField,
    UUIDField,
)
from django.utils import (
    timezone,
)
from m3.db import (
    BaseObjectModel,
)

from educommon.django.db.mixins import (
    ReprStrPreModelMixin,
)
from educommon.utils.date import (
    get_today_max_datetime,
    get_today_min_datetime,
)
from function_tools.models import (
    Entity,
)
from m3_db_utils.models import (
    ModelEnumValue,
    TitledModelEnum,
)

from edu_rdm_integration.core.enums import (
    CommandType,
)
from edu_rdm_integration.core.utils import (
    get_data_command_progress_attachment_path,
)


class CollectingDataStageStatus(TitledModelEnum):
    """Статус этапа сбора данных."""

    CREATED = ModelEnumValue(
        title='Создан',
    )

    IN_PROGRESS = ModelEnumValue(
        title='В процессе сбора',
    )

    FAILED = ModelEnumValue(
        title='Завершено с ошибками',
    )

    FINISHED = ModelEnumValue(
        title='Завершено',
    )

    class Meta:
        db_table = 'rdm_collecting_data_stage_status'
        verbose_name = 'Модель-перечисление статусов этапа сбора данных'
        verbose_name_plural = 'Модели-перечисления статусов этапов сбора данных'


class CollectingExportedDataStage(ReprStrPreModelMixin, BaseObjectModel):
    """Этап подготовки данных в рамках Функций. За работу Функции отвечает ранер менеджер."""

    manager = ForeignKey(
        to='function_tools.Entity',
        verbose_name='Менеджер ранера Функции',
        on_delete=PROTECT,
        null=True,
        blank=True,
    )

    logs_period_started_at = DateTimeField(
        'Левая граница периода обрабатываемых логов',
        db_index=True,
        default=get_today_min_datetime,
    )

    logs_period_ended_at = DateTimeField(
        'Правая граница периода обрабатываемых логов',
        db_index=True,
        default=get_today_max_datetime,
    )

    started_at = DateTimeField(
        'Время начала сбора данных',
        auto_now_add=True,
        db_index=True,
    )

    ended_at = DateTimeField(
        'Время завершения сбора данных',
        null=True,
        blank=True,
        db_index=True,
    )

    status = ForeignKey(
        to='edu_rdm_integration_collect_data_stage.CollectingDataStageStatus',
        verbose_name='Статус',
        on_delete=PROTECT,
        default=CollectingDataStageStatus.CREATED.key,
    )

    class Meta:
        db_table = 'rdm_collecting_exported_data_stage'
        verbose_name = 'Этап формирования данных для выгрузки'
        verbose_name_plural = 'Этапы формирования данных для выгрузки'

    @property
    def attrs_for_repr_str(self):
        """Список атрибутов для отображения экземпляра модели."""
        return ['manager_id', 'logs_period_started_at', 'logs_period_ended_at', 'started_at', 'ended_at', 'status_id']

    def save(self, *args, **kwargs):
        """Сохранение этапа сбора данных модели РВД."""
        if (
            self.status_id in (CollectingDataStageStatus.FAILED.key, CollectingDataStageStatus.FINISHED.key)
            and not self.ended_at
        ):
            self.ended_at = datetime.now()

        super().save(*args, **kwargs)


class CollectingDataSubStageStatus(TitledModelEnum):
    """Статус этапа сбора данных."""

    CREATED = ModelEnumValue(
        title='Создан',
    )

    IN_PROGRESS = ModelEnumValue(
        title='В процессе сбора',
    )

    READY_TO_EXPORT = ModelEnumValue(
        title='Готово к выгрузке',
    )

    FAILED = ModelEnumValue(
        title='Завершено с ошибками',
    )

    EXPORTED = ModelEnumValue(
        title='Выгружено',
    )

    NOT_EXPORTED = ModelEnumValue(
        title='Не выгружено',
    )

    class Meta:
        db_table = 'rdm_collecting_data_sub_stage_status'
        verbose_name = 'Модель-перечисление статусов подэтапа сбора данных'
        verbose_name_plural = 'Модели-перечисления статусов подэтапов сбора данных'


class CollectingExportedDataSubStage(ReprStrPreModelMixin, BaseObjectModel):
    """Подэтап сбора данных для сущностей в рамках функции."""

    stage = ForeignKey(
        to=CollectingExportedDataStage,
        verbose_name='Этап подготовки данных для экспорта',
        on_delete=PROTECT,
    )

    function = ForeignKey(
        to=Entity,
        verbose_name='Функция',
        on_delete=PROTECT,
    )

    started_at = DateTimeField(
        'Время начала сбора данных',
        auto_now_add=True,
        db_index=True,
    )

    ended_at = DateTimeField(
        'Время завершения сбора данных',
        null=True,
        blank=True,
        db_index=True,
    )

    previous = ForeignKey(
        'self',
        null=True,
        blank=True,
        verbose_name='Предыдущий сбор данных',
        on_delete=CASCADE,
    )

    status = ForeignKey(
        to='edu_rdm_integration_collect_data_stage.CollectingDataSubStageStatus',
        verbose_name='Статус',
        on_delete=PROTECT,
        default=CollectingDataSubStageStatus.CREATED.key,
    )

    class Meta:
        db_table = 'rdm_collecting_exported_data_sub_stage'
        verbose_name = 'Подэтап формирования данных для выгрузки'
        verbose_name_plural = 'Подэтапы формирования данных для выгрузки'

    @property
    def attrs_for_repr_str(self):
        """Список атрибутов для отображения экземпляра модели."""
        return ['stage_id', 'function_id', 'started_at', 'ended_at', 'previous_id', 'status_id']

    def save(self, *args, **kwargs):
        """Сохранение подэтапа сбора данных."""
        if (
            self.status_id
            in (CollectingDataSubStageStatus.FAILED.key, CollectingDataSubStageStatus.READY_TO_EXPORT.key)
            and not self.ended_at
        ):
            self.ended_at = datetime.now()

        super().save(*args, **kwargs)


class AbstractCollectDataCommandProgress(ReprStrPreModelMixin, BaseObjectModel):
    """Модель, хранящая данные для формирования и отслеживания асинхронных задач по сбору данных.

    В реализации необходимо определить поля:
        1. Ссылку на асинхронную задачу, например:
            task = ForeignKey(
                to=RunningTask,
                verbose_name='Асинхронная задача',
                blank=True, null=True,
                on_delete=SET_NULL,
            )
        2. Поле хранения лога:
            logs_link = FileField(
                upload_to=upload_file_handler,
                max_length=255,
                verbose_name='Ссылка на файл логов',
            )
    """

    task = ...

    logs_link = ...

    stage = ForeignKey(
        to='edu_rdm_integration_collect_data_stage.CollectingExportedDataStage',
        verbose_name='Этап формирования данных для выгрузки',
        blank=True,
        null=True,
        on_delete=SET_NULL,
    )
    model = ForeignKey(
        to='edu_rdm_integration_models.RegionalDataMartModelEnum',
        verbose_name='Модель РВД',
        on_delete=PROTECT,
    )
    created = DateTimeField(
        verbose_name='Дата создания',
        default=timezone.now,
    )
    logs_period_started_at = DateTimeField(
        'Левая граница периода обрабатываемых логов',
    )
    logs_period_ended_at = DateTimeField(
        'Правая граница периода обрабатываемых логов',
    )
    generation_id = UUIDField(
        'Идентификатор генерации',
        default=uuid.uuid4,
    )
    institute_ids = JSONField(
        'id учебного заведения',
        blank=True,
        null=True,
        default=list,
    )

    class Meta:
        abstract = True
        db_table = 'rdm_collecting_data_command_progress'
        verbose_name = 'Задача по сбору данных'
        verbose_name_plural = 'Задачи по сбору данных'


class EduRdmCollectDataCommandProgress(AbstractCollectDataCommandProgress):
    """Модель, хранящая данные для формирования и отслеживания асинхронных задач по сбору данных."""

    task = ForeignKey(
        to='async_task.RunningTask',
        verbose_name='Асинхронная задача',
        blank=True,
        null=True,
        on_delete=SET_NULL,
    )
    logs_link = FileField(
        upload_to=get_data_command_progress_attachment_path,
        max_length=255,
        verbose_name='Ссылка на файл логов',
    )
    type = PositiveSmallIntegerField(  # noqa: A003
        verbose_name='Тип команды',
        choices=CommandType.get_choices(),
    )

    class Meta(AbstractCollectDataCommandProgress.Meta):
        db_table = 'edu_rdm_collecting_data_command_progress'
