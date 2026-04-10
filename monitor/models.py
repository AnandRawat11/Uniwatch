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


class AlertRule(models.Model):
    """
    Defines a monitoring threshold. When a metric crosses this threshold,
    an Alert is created with a suggested fix action.
    """

    METRIC_CHOICES = [
        ('cpu_usage', 'CPU Usage (%)'),
        ('memory_usage', 'Memory Usage (%)'),
        ('disk_usage', 'Disk Usage (%)'),
        ('node_exporter_down', 'Node Exporter Down'),
        ('cadvisor_down', 'cAdvisor Down'),
    ]

    SEVERITY_CHOICES = [
        ('warning', 'Warning'),
        ('critical', 'Critical'),
    ]

    name = models.CharField(max_length=150, help_text="e.g., High CPU Alert")
    metric = models.CharField(max_length=30, choices=METRIC_CHOICES)
    threshold = models.FloatField(
        default=90.0,
        help_text="Threshold value. For CPU/Memory/Disk this is percentage. For 'down' alerts, set to 0."
    )
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default='warning')
    is_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['metric', 'severity']

    def __str__(self):
        return f"{self.name} ({self.metric} > {self.threshold}%)"

    @property
    def severity_emoji(self):
        return '⚠️' if self.severity == 'warning' else '🔴'


class Alert(models.Model):
    """
    A triggered alert instance. Created when a metric crosses a threshold.
    Can be fixed by executing a remote SSH command.
    """

    STATUS_CHOICES = [
        ('open', 'Open'),
        ('fixing', 'Fix In Progress'),
        ('fixed', 'Fixed'),
        ('failed', 'Fix Failed'),
        ('dismissed', 'Dismissed'),
    ]

    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name='alerts')
    rule = models.ForeignKey(AlertRule, on_delete=models.SET_NULL, null=True, blank=True, related_name='alerts')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    metric_name = models.CharField(max_length=50)
    metric_value = models.FloatField(null=True, blank=True)
    threshold_value = models.FloatField(null=True, blank=True)
    severity = models.CharField(max_length=10, choices=[('warning', 'Warning'), ('critical', 'Critical')], default='warning')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='open')
    fix_command = models.TextField(
        blank=True, default='',
        help_text="The SSH command that will be executed to fix this issue"
    )
    fix_description = models.CharField(
        max_length=200, blank=True, default='',
        help_text="Human-readable description of what the fix does"
    )
    fix_logs = models.TextField(blank=True, default='', help_text="Output from executing the fix command")
    created_at = models.DateTimeField(auto_now_add=True)
    fixed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.severity.upper()}] {self.title} on {self.server.name}"

    @property
    def severity_emoji(self):
        return '⚠️' if self.severity == 'warning' else '🔴'

    @property
    def status_emoji(self):
        return {
            'open': '🚨',
            'fixing': '🔧',
            'fixed': '✅',
            'failed': '❌',
            'dismissed': '🔕',
        }.get(self.status, '❓')

    @property
    def has_fix(self):
        return bool(self.fix_command.strip())