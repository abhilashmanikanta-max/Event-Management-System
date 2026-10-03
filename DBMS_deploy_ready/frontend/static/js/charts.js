/**
 * EVENT MANAGEMENT SYSTEM - Dashboard Charts (Chart.js Integration)
 */

const AppCharts = {
  instances: {},

  destroyCharts() {
    Object.keys(this.instances).forEach(key => {
      if (this.instances[key]) {
        this.instances[key].destroy();
        delete this.instances[key];
      }
    });
  },

  renderDashboardCharts(chartData) {
    if (typeof Chart === 'undefined') {
      console.warn("Chart.js not loaded, skipping chart rendering.");
      return;
    }

    this.destroyCharts();

    // 1. Events by Category
    const catCanvas = document.getElementById('chartCategory');
    if (catCanvas && chartData.events_by_category) {
      const labels = chartData.events_by_category.map(item => item.category);
      const data = chartData.events_by_category.map(item => item.count);

      this.instances.category = new Chart(catCanvas, {
        type: 'bar',
        data: {
          labels,
          datasets: [{
            label: 'Total Events',
            data,
            backgroundColor: [
              '#3b82f6', '#10b981', '#8b5cf6', '#f59e0b', '#ec4899', '#06b6d4'
            ],
            borderRadius: 6
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false }
          },
          scales: {
            y: {
              beginAtZero: true,
              ticks: { stepSize: 1 }
            }
          }
        }
      });
    }

    // 2. Registrations per Event
    const regCanvas = document.getElementById('chartRegistrations');
    if (regCanvas && chartData.registrations_per_event) {
      const labels = chartData.registrations_per_event.map(item => item.event_name.length > 20 ? item.event_name.substring(0, 18) + '...' : item.event_name);
      const data = chartData.registrations_per_event.map(item => item.registrations);

      this.instances.registrations = new Chart(regCanvas, {
        type: 'bar',
        data: {
          labels,
          datasets: [{
            label: 'Confirmed Registrations',
            data,
            backgroundColor: '#6366f1',
            borderRadius: 6
          }]
        },
        options: {
          indexAxis: 'y',
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false }
          },
          scales: {
            x: {
              beginAtZero: true,
              ticks: { stepSize: 1 }
            }
          }
        }
      });
    }

    // 3. Payment Status Breakdown
    const payCanvas = document.getElementById('chartPaymentStatus');
    if (payCanvas && chartData.payment_status) {
      const labels = chartData.payment_status.map(item => item.status);
      const data = chartData.payment_status.map(item => item.count);

      this.instances.payments = new Chart(payCanvas, {
        type: 'doughnut',
        data: {
          labels,
          datasets: [{
            data,
            backgroundColor: ['#10b981', '#f59e0b', '#ef4444', '#64748b']
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { position: 'bottom' }
          }
        }
      });
    }

    // 4. Venue Utilization
    const venueCanvas = document.getElementById('chartVenueUtil');
    if (venueCanvas && chartData.venue_utilization) {
      const labels = chartData.venue_utilization.map(item => item.venue_name.length > 18 ? item.venue_name.substring(0, 16) + '...' : item.venue_name);
      const data = chartData.venue_utilization.map(item => item.total_attendees);

      this.instances.venue = new Chart(venueCanvas, {
        type: 'bar',
        data: {
          labels,
          datasets: [{
            label: 'Attendees Registered',
            data,
            backgroundColor: '#0ea5e9',
            borderRadius: 6
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false }
          },
          scales: {
            y: {
              beginAtZero: true,
              ticks: { stepSize: 1 }
            }
          }
        }
      });
    }
  }
};
