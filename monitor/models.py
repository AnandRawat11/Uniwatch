from django.db import models


class Server(models.Model):
    """
    Represents a user's server/instance that we monitor.
    SSH key is NOT stored — it's used once during setup and then discarded.
    """

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Setup Running'),
        ('success', 'Setup Successful'),
        ('failed', 'Setup Failed'),
    ]

    name = models.CharField(max_length=100, help_text="e.g., Production-Server-1")
    ip_address = models.GenericIPAddressField(unique=True)
    ssh_user = models.CharField(max_length=50, default='ubuntu')
    has_containers = models.BooleanField(
        default=False,
        help_text="If True, cAdvisor will also be installed for container monitoring"
    )
    setup_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    setup_logs = models.TextField(blank=True, default='', help_text="Logs from the setup process")
    is_active = models.BooleanField(default=False, help_text="True if monitoring agents are running")
    node_exporter_port = models.IntegerField(default=9100)
    cadvisor_port = models.IntegerField(default=8080)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.ip_address})"

    @property
    def status_emoji(self):
        return {
            'pending': '⏳',
            'running': '🔄',
            'success': '✅',
            'failed': '❌',
        }.get(self.setup_status, '❓')