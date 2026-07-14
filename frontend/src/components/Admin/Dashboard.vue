<template>
    <Navbar></Navbar>

    <div class="container mt-4">
        <div class="d-flex justify-content-between align-items-center flex-wrap gap-2">
            <h3>Dashboard</h3>
            <div>
                <button class="btn btn-outline-secondary btn-sm me-2" @click="triggerReminders" :disabled="jobRunning">
                    Send Daily Reminders Now
                </button>
                <button class="btn btn-outline-secondary btn-sm" @click="triggerReport" :disabled="jobRunning">
                    Generate Monthly Report Now
                </button>
            </div>
        </div>
        <div v-if="jobMessage" class="alert alert-info py-2 mt-2">{{ jobMessage }}</div>

        <div class="row mt-3 mb-4">
            <div class="col-md-3">
                <div class="card text-center">
                    <div class="card-body">
                        <h6 class="text-muted">Total Treks</h6>
                        <h2>{{ stats.total_treks }}</h2>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-center">
                    <div class="card-body">
                        <h6 class="text-muted">Total Users</h6>
                        <h2>{{ stats.total_users }}</h2>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-center">
                    <div class="card-body">
                        <h6 class="text-muted">Total Staff</h6>
                        <h2>{{ stats.total_staff }}</h2>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-center">
                    <div class="card-body">
                        <h6 class="text-muted">Total Bookings</h6>
                        <h2>{{ stats.total_bookings }}</h2>
                    </div>
                </div>
            </div>
        </div>

        <div class="card mb-5">
            <div class="card-header">Recent Bookings</div>
            <div class="card-body">
                <table class="table border">
                    <thead>
                        <tr>
                            <th>Booking ID</th>
                            <th>User</th>
                            <th>Trek</th>
                            <th>Date</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="b in stats.recent_bookings" :key="b.id">
                            <td>{{ b.id }}</td>
                            <td>{{ b.user_name }}</td>
                            <td>{{ b.trek_name }}</td>
                            <td>{{ b.booking_date }}</td>
                            <td>{{ b.booking_status }}</td>
                        </tr>
                        <tr v-if="stats.recent_bookings && stats.recent_bookings.length === 0">
                            <td colspan="5" class="text-center text-muted">No bookings yet</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</template>

<script>
import Navbar from '../Navbar.vue';

export default {
    name: "AdminDashboard",
    components: { Navbar },
    data() {
        return {
            stats: {
                total_treks: 0,
                total_users: 0,
                total_staff: 0,
                total_bookings: 0,
                recent_bookings: []
            },
            jobMessage: null,
            jobRunning: false
        }
    },
    methods: {
        async loadDashboard() {
            try {
                const response = await fetch("http://localhost:5000/admin/dashboard", {
                    headers: { "Authentication-Token": localStorage.getItem("token") }
                })
                const data = await response.json()
                if (response.status == 200) {
                    this.stats = data
                }
                else if (response.status == 401 || response.status == 403) {
                    this.$router.push("/login")
                }
            }
            catch (error) {
                console.log(error.message)
            }
        },
        async queueAdminJob(url) {
            this.jobRunning = true
            this.jobMessage = null
            try {
                const response = await fetch(url, {
                    method: "POST",
                    headers: { "Authentication-Token": localStorage.getItem("token") }
                })
                const data = await response.json()
                this.jobMessage = data.message || "Unable to queue the job"
                if (response.status == 401 || response.status == 403) this.$router.push("/login")
            } catch (error) {
                this.jobMessage = "Could not contact the backend"
            } finally {
                this.jobRunning = false
            }
        },
        triggerReminders() {
            return this.queueAdminJob("http://localhost:5000/admin/trigger-daily-reminders")
        },
        triggerReport() {
            return this.queueAdminJob("http://localhost:5000/admin/trigger-monthly-report")
        }
    },
    mounted() {
        this.loadDashboard()
    }
}
</script>
