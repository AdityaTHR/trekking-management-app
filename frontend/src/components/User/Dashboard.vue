<template>
    <Navbar></Navbar>

    <div class="container mt-4">
        <h3>Welcome, {{ dashboard.name }}!</h3>

        <div v-if="message" class="alert alert-danger mt-2">{{ message }}</div>

        <div class="d-flex justify-content-between align-items-center mt-4 mb-2">
            <h5>Available Treks</h5>
            <router-link class="btn btn-outline-primary btn-sm" to="/user/treks">Browse All Treks →</router-link>
        </div>
        <div class="row">
            <div class="col-md-4 mb-3" v-for="t in dashboard.available_treks" :key="t.id">
                <div class="card h-100">
                    <div class="card-body">
                        <h5 class="card-title">{{ t.name }}</h5>
                        <p class="card-text text-muted mb-1">{{ t.location }}</p>
                        <p class="card-text mb-1">{{ t.difficulty }} · {{ t.duration }} Days</p>
                        <p class="card-text mb-2">Slots Left: {{ t.available_slots }}</p>
                        <button class="btn btn-primary w-100" :disabled="t.available_slots === 0"
                            @click="bookTrek(t.id)">
                            {{ t.available_slots === 0 ? "Not Available" : "Book Now" }}
                        </button>
                    </div>
                </div>
            </div>
            <p v-if="dashboard.available_treks && dashboard.available_treks.length === 0" class="text-muted">
                No treks are currently open for booking.
            </p>
        </div>

        <h5 class="mt-4">My Bookings</h5>
        <div class="card mb-5">
            <div class="card-body">
                <table class="table border align-middle">
                    <thead>
                        <tr><th>Trek Name</th><th>Booking Date</th><th>Status</th><th>Action</th></tr>
                    </thead>
                    <tbody>
                        <tr v-for="b in dashboard.my_bookings" :key="b.id">
                            <td>{{ b.trek_name }}</td>
                            <td>{{ b.booking_date }}</td>
                            <td>{{ b.booking_status }}</td>
                            <td>
                                <button class="btn btn-sm btn-outline-danger" @click="cancelBooking(b.id)">
                                    Cancel
                                </button>
                            </td>
                        </tr>
                        <tr v-if="dashboard.my_bookings && dashboard.my_bookings.length === 0">
                            <td colspan="4" class="text-center text-muted">No active bookings</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <div class="card-footer text-end">
                <router-link to="/user/history">View All Bookings / History →</router-link>
            </div>
        </div>
    </div>
</template>

<script>
import Navbar from '../Navbar.vue';

export default {
    name: "UserDashboard",
    components: { Navbar },
    data() {
        return {
            dashboard: { name: "", available_treks: [], my_bookings: [] },
            message: null
        }
    },
    methods: {
        authHeaders() {
            return { "Content-Type": "application/json", "Authentication-Token": localStorage.getItem("token") }
        },
        async loadDashboard() {
            const response = await fetch("http://localhost:5000/user/dashboard", { headers: this.authHeaders() })
            if (response.status == 401 || response.status == 403) { this.$router.push("/login"); return }
            this.dashboard = await response.json()
        },
        async bookTrek(trekId) {
            this.message = null
            const response = await fetch(`http://localhost:5000/user/treks/${trekId}/book`, {
                method: "POST", headers: this.authHeaders()
            })
            const data = await response.json()
            if (response.status == 200) {
                this.loadDashboard()
            } else {
                this.message = data.message
            }
        },
        async cancelBooking(bookingId) {
            if (!confirm("Cancel this booking?")) return
            await fetch(`http://localhost:5000/user/bookings/${bookingId}/cancel`, {
                method: "PUT", headers: this.authHeaders()
            })
            this.loadDashboard()
        }
    },
    mounted() {
        this.loadDashboard()
    }
}
</script>
