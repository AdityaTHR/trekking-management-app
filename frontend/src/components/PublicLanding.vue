<template>
  <div class="landing-page">
    <nav class="navbar bg-white border-bottom shadow-sm">
      <div class="container-xl">
        <router-link class="navbar-brand fw-bold" to="/">
          Trekking Management
        </router-link>

        <div class="d-flex gap-2">
          <router-link class="btn btn-outline-primary" to="/login">
            Login
          </router-link>

          <router-link class="btn btn-primary" to="/register">
            Register
          </router-link>
        </div>
      </div>
    </nav>

    <main class="hero-section">
      <div class="container-xl">
        <div class="row g-5 align-items-stretch">
          <!-- Left card -->
          <div class="col-lg-5">
            <div class="content-card h-100">
              <span class="badge bg-primary rounded-pill">
                Trekking Management Application
              </span>

              <h1 class="hero-title">
                Discover and manage your next trek
              </h1>

              <p class="hero-description">
                Browse available treks, make bookings, track your history,
                and receive upcoming trek reminders — all from one platform.
              </p>

              <div class="d-flex flex-wrap gap-3 mt-4">
                <router-link
                  class="btn btn-primary btn-lg px-4"
                  to="/register"
                >
                  Start Exploring
                </router-link>

                <router-link
                  class="btn btn-outline-secondary btn-lg px-4"
                  to="/login"
                >
                  Login
                </router-link>
              </div>
            </div>
          </div>

          <!-- Right section -->
          <div class="col-lg-7 d-flex flex-column">            
            <div class="row g-3 ">
              <div class="col-4">
                <div class="stat-card">
                  <div class="stat-number">
                    {{ stats.total_treks }}
                  </div>
                  <div class="stat-label">
                    Total Treks
                  </div>
                </div>
              </div>

              <div class="col-4">
                <div class="stat-card">
                  <div class="stat-number">
                    {{ openTreks }}
                  </div>
                  <div class="stat-label">
                    Open Treks
                  </div>
                </div>
              </div>

              <div class="col-4">
                <div class="stat-card">
                  <div class="stat-number">
                    {{ stats.total_completed_treks }}
                  </div>
                  <div class="stat-label">
                    Completed
                  </div>
                </div>
              </div>
            </div>

            <div class="chart-card mt-4">              
              <h4 class="fw-bold mb-3">
                Treks by Difficulty
              </h4>

              <div class="chart-container">
                <canvas ref="chartCanvas"></canvas>
              </div>

              <p
                v-if="!hasData"
                class="text-muted text-center mb-0"
              >
                No trek data is currently available.
              </p>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import { Chart } from "chart.js/auto";

export default {
  name: "PublicLanding",

  data() {
    return {
      stats: {
        total_treks: 0,
        total_completed_treks: 0,
        difficulty_distribution: {},
        status_distribution: {},
      },
      chart: null,
    };
  },

  computed: {
    hasData() {
      return this.stats.total_treks > 0;
    },

    openTreks() {
      return this.stats.status_distribution?.Open || 0;
    },
  },

  methods: {
    async loadStats() {
      try {
        const response = await fetch(
          "http://localhost:5000/public/stats"
        );

        if (!response.ok) {
          throw new Error("Unable to load public statistics");
        }

        this.stats = await response.json();
        this.renderChart();
      } catch (error) {
        console.error("Public statistics error:", error);
      }
    },

    renderChart() {
      const distribution =
        this.stats.difficulty_distribution || {};

      const values = [
        distribution.Easy || 0,
        distribution.Moderate || 0,
        distribution.Hard || 0,
      ];

      if (this.chart) {
        this.chart.destroy();
      }

      this.chart = new Chart(this.$refs.chartCanvas, {
        type: "bar",

        data: {
          labels: ["Easy", "Moderate", "Hard"],

          datasets: [
            {
              label: "Number of Treks",
              data: values,
              backgroundColor: [
                "#198754",
                "#f0ad4e",
                "#dc3545",
              ],
              borderRadius: 8,
              maxBarThickness: 70,
            },
          ],
        },

        options: {
          responsive: true,
          maintainAspectRatio: false,

          plugins: {
            legend: {
              display: false,
            },
          },

          scales: {
            x: {
              grid: {
                display: false,
              },
            },

            y: {
              beginAtZero: true,
              suggestedMax: Math.max(...values, 1) + 1,

              ticks: {
                stepSize: 1,
                precision: 0,
              },
            },
          },
        },
      });
    },
  },

  mounted() {
    this.loadStats();
  },

  beforeUnmount() {
    if (this.chart) {
      this.chart.destroy();
    }
  },
};
</script>

<style scoped>
.landing-page {
  min-height: 100vh;
  background: #f8f9fa;
}

.navbar {
  min-height: 78px;
}

.navbar-brand {
  color: #22314a;
  font-size: 1.8rem;
}

.hero-section {
  min-height: calc(100vh - 78px);
  display: flex;
  align-items: center;
  padding: 28px 0;
  background: url("../assets/trek-bg.jpg") center / cover no-repeat;
}

.content-card,
.stat-card,
.chart-card {
  background: #ffffff;
  border: 1px solid #dee2e6;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.14);
}

.content-card {
  min-height: 430px;
  max-width: 500px;
  padding: 40px;
  border-radius: 18px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.content-card .badge {
  width: fit-content;
  padding: 11px 22px;
  margin-bottom: 28px;
  font-size: 1rem;
}

.hero-title {
  color: #22314a;
  font-size: 2.8rem;
  font-weight: 700;
  line-height: 1.15;
}

.hero-description {
  margin-top: 20px;
  margin-bottom: 0;
  color: #49576a;
  font-size: 1.1rem;
  line-height: 1.65;
}

.stat-card {
  min-height: 92px;
  padding: 14px 6px;
  border-radius: 14px;
  text-align: center;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.stat-number {
  color: #0d6efd;
  font-size: 1.7rem;
  font-weight: 700;
  line-height: 1;
}

.stat-label {
  margin-top: 7px;
  color: #4f5d70;
  font-size: 0.9rem;
}

.chart-card {
  min-height: 270px;
  padding: 20px;
  border-radius: 16px;
}

.chart-container {
  position: relative;
  height: 205px;
}

.btn {
  border-radius: 10px;
}

@media (max-width: 992px) {
  .hero-section {
    align-items: flex-start;
  }

  .content-card {
    max-width: none;
    min-height: auto;
  }

  .hero-title {
    font-size: 2.4rem;
  }
}

@media (max-width: 576px) {
  .navbar-brand {
    font-size: 1.3rem;
  }

  .content-card {
    padding: 26px;
  }

  .hero-title {
    font-size: 2rem;
  }

  .hero-description {
    font-size: 1rem;
  }

  .content-card .badge {
    padding: 8px 14px;
    font-size: 0.8rem;
  }

  .stat-card {
    min-height: 88px;
  }

  .stat-number {
    font-size: 1.4rem;
  }

  .stat-label {
    font-size: 0.75rem;
  }

  .chart-container {
    height: 190px;
  }
}
.chart-card {
  min-height: 310px;
  padding: 22px;
}

.chart-container {
  height: 240px;
}
</style>