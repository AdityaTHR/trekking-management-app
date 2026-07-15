<template>
    <Navbar></Navbar>

    <div class="container mt-4 mb-5">
        <div class="d-flex justify-content-between align-items-center mb-3">
            <div>
                <h3>All Bookings</h3>
                <p class="text-muted mb-0">Complete booking and trekking history</p>
            </div>

            <input
                v-model="searchText"
                class="form-control"
                style="max-width: 300px"
                placeholder="Search user, trek or status"
            />
        </div>

        <div v-if="loading" class="alert alert-info">
            Loading booking records...
        </div>

        <div v-else-if="errorMessage" class="alert alert-danger">
            {{ errorMessage }}
        </div>

        <div v-else class="card">
            <div class="card-header">
                Total Records: {{ filteredBookings.length }}
            </div>

            <div class="card-body table-responsive">
                <table class="table table-bordered table-hover align-middle">
                    <thead>
                        <tr>
                            <th>Booking ID</th>
                            <th>User</th>
                            <th>Trek</th>
                            <th>Booking Date</th>
                            <th>Booking Status</th>
                            <th>Payment Status</th>
                        </tr>
                    </thead>

                    <tbody>
                        <tr v-for="booking in filteredBookings" :key="booking.id">
                            <td>{{ booking.id }}</td>
                            <td>{{ booking.user_name }}</td>
                            <td>{{ booking.trek_name }}</td>
                            <td>{{ formatDate(booking.booking_date) }}</td>
                            <td>
                                <span class="badge text-bg-primary">
                                    {{ booking.booking_status }}
                                </span>
                            </td>
                            <td>
                                <span class="badge text-bg-secondary">
                                    {{ booking.payment_status }}
                                </span>
                            </td>
                        </tr>

                        <tr v-if="filteredBookings.length === 0">
                            <td colspan="6" class="text-center text-muted">
                                No booking records found
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</template>

<script>
import Navbar from "../Navbar.vue"

export default {
    name: "AdminBookings",
    components: { Navbar },

    data() {
        return {
            bookings: [],
            searchText: "",
            loading: true,
            errorMessage: ""
        }
    },

    computed: {
        filteredBookings() {
            const query = this.searchText.trim().toLowerCase()

            if (!query) return this.bookings

            return this.bookings.filter((booking) => {
                return (
                    String(booking.id).includes(query) ||
                    (booking.user_name || "").toLowerCase().includes(query) ||
                    (booking.trek_name || "").toLowerCase().includes(query) ||
                    (booking.booking_status || "").toLowerCase().includes(query) ||
                    (booking.payment_status || "").toLowerCase().includes(query)
                )
            })
        }
    },

    methods: {
        async loadBookings() {
            this.loading = true
            this.errorMessage = ""

            try {
                const response = await fetch(
                    "http://localhost:5000/admin/bookings",
                    {
                        headers: {
                            "Authentication-Token":
                                localStorage.getItem("token")
                        }
                    }
                )

                const data = await response.json()

                if (response.status === 200) {
                    this.bookings = data
                } else if (
                    response.status === 401 ||
                    response.status === 403
                ) {
                    this.$router.push("/login")
                } else {
                    this.errorMessage =
                        data.message || "Unable to load bookings"
                }
            } catch (error) {
                this.errorMessage = "Could not contact the backend"
            } finally {
                this.loading = false
            }
        },

        formatDate(value) {
            if (!value) return "-"

            return new Date(value).toLocaleString()
        }
    },

    mounted() {
        this.loadBookings()
    }
}
</script>
