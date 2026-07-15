from __future__ import annotations

from django.db import models
from django.utils import timezone


class SoftDeleteQuerySet(models.QuerySet):
    def delete(self) -> int:
        return self.update(is_deleted=True, deleted_at=timezone.now())

    def hard_delete(self) -> int:
        return super().delete()

    def alive(self) -> "SoftDeleteQuerySet":
        return self.filter(is_deleted=False)

    def deleted(self) -> "SoftDeleteQuerySet":
        return self.filter(is_deleted=True)


class SoftDeleteManager(models.Manager):
    def get_queryset(self) -> SoftDeleteQuerySet:
        return SoftDeleteQuerySet(self.model, using=self._db).filter(is_deleted=False)

    def hard_delete(self) -> int:
        return self.get_queryset().hard_delete()


class AllObjectsManager(models.Manager):
    def get_queryset(self) -> SoftDeleteQuerySet:
        return SoftDeleteQuerySet(self.model, using=self._db)
