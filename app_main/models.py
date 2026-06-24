from django.db import models


class Post(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title[:50]
    
    class Meta:
        ordering = ["-created"]
        verbose_name = "Post"
        verbose_name_plural = "Postlar"