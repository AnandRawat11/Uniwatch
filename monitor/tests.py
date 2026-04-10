from unittest.mock import patch

from django.test import Client, TestCase
from django.urls import reverse

from .models import Alert, AlertRule, Server


class SmokeTests(TestCase):
	def setUp(self):
		self.client = Client()
		self.server = Server.objects.create(
			name='Test Server',
			ip_address='10.10.10.10',
			ssh_user='ubuntu',
			has_containers=True,
			setup_status='success',
			is_active=True,
		)

	def test_core_pages_render(self):
		with patch('monitor.views.get_server_metrics', return_value={'cpu_usage': 12.5}):
			response = self.client.get(reverse('dashboard'))
			self.assertEqual(response.status_code, 200)

			response = self.client.get(reverse('alerts_list'))
			self.assertEqual(response.status_code, 200)

			response = self.client.get(reverse('add_server'))
			self.assertEqual(response.status_code, 200)

			response = self.client.get(reverse('server_detail', args=[self.server.id]))
			self.assertEqual(response.status_code, 200)


class AlertFlowTests(TestCase):
	def setUp(self):
		self.client = Client()
		self.server = Server.objects.create(
			name='Container Host',
			ip_address='10.10.20.20',
			ssh_user='ubuntu',
			has_containers=True,
			setup_status='success',
			is_active=True,
		)
		self.rule = AlertRule.objects.create(
			name='cAdvisor Down',
			metric='cadvisor_down',
			threshold=0,
			severity='critical',
			is_enabled=True,
		)

	@patch('monitor.views.get_server_metrics', return_value={})
	@patch('monitor.views.check_prometheus_health', return_value=True)
	@patch('monitor.views.query_prometheus', return_value=[{'value': ['0', '0']}])
	def test_check_alerts_creates_cadvisor_down_alert(self, mocked_query, mocked_health, mocked_metrics):
		response = self.client.post(reverse('check_alerts'))

		self.assertEqual(response.status_code, 302)
		self.assertEqual(Alert.objects.count(), 1)

		alert = Alert.objects.get()
		self.assertEqual(alert.server, self.server)
		self.assertEqual(alert.metric_name, 'cadvisor_down')
		self.assertEqual(alert.status, 'open')
