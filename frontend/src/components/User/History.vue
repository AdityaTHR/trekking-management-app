<template>
    <Navbar></Navbar>

    <div class="container mt-4">
        <h3>Trekking History</h3>

        <div class="card mb-4">
            <div class="card-body">
                <table class="table border align-middle">
                    <thead>
                        <tr><th>Trek Name</th><th>Booking Date</th><th>Status</th></tr>
                    </thead>
                    <tbody>
                        <tr v-for="b in history" :key="b.id">
                            <td>{{ b.trek_name }}</td>
                            <td>{{ b.booking_date }}</td>
                            <td>
                                <span :class="statusBadgeClass(b.booking_status)">{{ b.booking_status }}</span>
                            </td>
                        </tr>
                        <tr v-if="history.length === 0">
                            <td colspan="3" class="text-center text-muted">No trekking history yet</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
        <p class="text-muted" style="font-size: 0.85rem;">
            History shows all your booked, completed, and cancelled treks.
        </p>
    </div>
</template>

<script>
import Navbar from '../Navbar.vue';

export default {
    name: "UserHistory",
    components: { Navbar },
    data() {
        return { history: [] }
    },
    methods: {
        statusBadgeClass(status) {
            if (status === "Completed") return "badge bg-success"
            if (status === "Cancelled") return "badge bg-secondary"
            return "badge bg-primary"
        },
        async loadHistory() {
            const response = await fetch("http://localhost:5000/user/history", {
                headers: { "Authentication-Token": localStorage.getItem("token") }
            })
            if (response.status == 401 || response.status == 403) { this.$router.push("/login"); return }
            this.history = await response.json()
        }
    },
    mounted() {
        this.loadHistory()
    }
}
</script>
