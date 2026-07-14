<template>
    <Navbar></Navbar>

    <div class="container mt-4" v-if="trek">
        <div class="d-flex justify-content-between align-items-start">
            <div>
                <h3>{{ trek.name }}</h3>
                <p class="text-muted mb-0">
                    {{ trek.location }} · {{ trek.difficulty }} · {{ trek.duration }} days
                </p>
                <p class="text-muted">{{ trek.start_date }} — {{ trek.end_date }}</p>
            </div>
            <router-link class="btn btn-outline-secondary" to="/staff/dashboard">← Back to My Treks</router-link>
        </div>

        <div v-if="message" class="alert alert-danger mt-2">{{ message }}</div>

        <div class="row mt-3">
            <div class="col-md-4">
                <label class="form-label">Available Slots</label>
                <div class="input-group">
                    <input type="number" class="form-control" v-model="slotsInput">
                    <button class="btn btn-primary" @click="updateSlots">Update</button>
                </div>
            </div>
            <div class="col-md-4">
                <label class="form-label">Trek Status</label>
                <select class="form-select" v-model="trek.status" @change="updateStatus">
                    <option>Open</option>
                    <option>Closed</option>
                    <option>Ongoing</option>
                    <option>Completed</option>
                </select>
            </div>
        </div>

        <div class="card mt-4 mb-5">
            <div class="card-header">Participants ({{ trek.participants.length }})</div>
            <div class="card-body">
                <table class="table border">
                    <thead>
                        <tr><th>Name</th><th>Email</th><th>Booking Date</th><th>Status</th></tr>
                    </thead>
                    <tbody>
                        <tr v-for="p in trek.participants" :key="p.booking_id">
                            <td>{{ p.name }}</td>
                            <td>{{ p.email }}</td>
                            <td>{{ p.booking_date }}</td>
                            <td>{{ p.booking_status }}</td>
                        </tr>
                        <tr v-if="trek.participants.length === 0">
                            <td colspan="4" class="text-center text-muted">No participants yet</td>
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
    name: "StaffManageTrek",
    components: { Navbar },
    data() {
        return {
            trekId: null,
            trek: null,
            slotsInput: null,
            message: null
        }
    },
    methods: {
        authHeaders() {
            return { "Content-Type": "application/json", "Authentication-Token": localStorage.getItem("token") }
        },
        async loadTrek() {
            const response = await fetch(`http://localhost:5000/staff/treks/${this.trekId}`, { headers: this.authHeaders() })
            const data = await response.json()
            if (response.status == 200) {
                this.trek = data
                this.slotsInput = data.available_slots
            } else if (response.status == 401 || response.status == 403) {
                this.message = data.message
            } else {
                this.message = data.message
            }
        },
        async updateSlots() {
            const response = await fetch(`http://localhost:5000/staff/treks/${this.trekId}/slots`, {
                method: "PUT", headers: this.authHeaders(),
                body: JSON.stringify({ available_slots: Number(this.slotsInput) })
            })
            const data = await response.json()
            if (response.status == 200) this.trek = { ...this.trek, ...data.trek, participants: this.trek.participants }
            else this.message = data.message
        },
        async updateStatus() {
            const response = await fetch(`http://localhost:5000/staff/treks/${this.trekId}/status`, {
                method: "PUT", headers: this.authHeaders(),
                body: JSON.stringify({ status: this.trek.status })
            })
            const data = await response.json()
            if (response.status != 200) this.message = data.message
        }
    },
    mounted() {
        this.trekId = this.$route.params.trek_id
        this.loadTrek()
    }
}
</script>
