<template>
    <Navbar></Navbar>

    <div class="container mt-4">
        <h3>My Dashboard</h3>

        <div class="row mt-3 mb-4">
            <div class="col-md-4">
                <div class="card text-center">
                    <div class="card-body">
                        <h6 class="text-muted">Assigned Treks</h6>
                        <h2>{{ dashboard.assigned_trek_count }}</h2>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card text-center">
                    <div class="card-body">
                        <h6 class="text-muted">Total Participants</h6>
                        <h2>{{ dashboard.total_participants }}</h2>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card text-center">
                    <div class="card-body">
                        <h6 class="text-muted">Ongoing Treks</h6>
                        <h2>{{ dashboard.ongoing_trek_count }}</h2>
                    </div>
                </div>
            </div>
        </div>

        <div class="card mb-5">
            <div class="card-header">My Assigned Treks</div>
            <div class="card-body">
                <table class="table border align-middle">
                    <thead>
                        <tr>
                            <th>Trek Name</th><th>Location</th><th>Participants</th>
                            <th>Slots Left</th><th>Status</th><th>Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="t in dashboard.treks" :key="t.id">
                            <td>{{ t.name }}</td>
                            <td>{{ t.location }}</td>
                            <td>{{ t.registered_count }}</td>
                            <td>{{ t.available_slots }}</td>
                            <td>{{ t.status }}</td>
                            <td>
                                <router-link class="btn btn-sm btn-primary" :to="`/staff/treks/${t.id}`">
                                    Manage
                                </router-link>
                            </td>
                        </tr>
                        <tr v-if="dashboard.treks && dashboard.treks.length === 0">
                            <td colspan="6" class="text-center text-muted">No treks assigned to you yet</td>
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
    name: "StaffDashboard",
    components: { Navbar },
    data() {
        return {
            dashboard: { assigned_trek_count: 0, total_participants: 0, ongoing_trek_count: 0, treks: [] }
        }
    },
    methods: {
        async loadDashboard() {
            const response = await fetch("http://localhost:5000/staff/dashboard", {
                headers: { "Authentication-Token": localStorage.getItem("token") }
            })
            if (response.status == 401 || response.status == 403) { this.$router.push("/login"); return }
            this.dashboard = await response.json()
        }
    },
    mounted() {
        this.loadDashboard()
    }
}
</script>
