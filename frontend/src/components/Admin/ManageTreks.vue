<template>
    <Navbar></Navbar>

    <div class="container mt-4">
        <div class="d-flex justify-content-between align-items-center mb-3">
            <h3>Treks</h3>
            <button class="btn btn-warning" @click="showCreateForm = !showCreateForm">
                + Add New Trek
            </button>
        </div>

        <div v-if="message" class="alert alert-danger">{{ message }}</div>

        <div class="card mb-4" v-if="showCreateForm">
            <div class="card-header">Create Trek</div>
            <div class="card-body">
                <div class="row g-2">
                    <div class="col-md-3">
                        <input class="form-control" placeholder="Name" v-model="form.name">
                    </div>
                    <div class="col-md-3">
                        <input class="form-control" placeholder="Location" v-model="form.location">
                    </div>
                    <div class="col-md-2">
                        <select class="form-select" v-model="form.difficulty">
                            <option disabled value="">Difficulty</option>
                            <option>Easy</option>
                            <option>Moderate</option>
                            <option>Hard</option>
                        </select>
                    </div>
                    <div class="col-md-2">
                        <input type="number" class="form-control" placeholder="Duration (days)" v-model="form.duration">
                    </div>
                    <div class="col-md-2">
                        <input type="number" class="form-control" placeholder="Slots" v-model="form.available_slots">
                    </div>
                    <div class="col-md-3">
                        <input type="date" class="form-control" v-model="form.start_date">
                    </div>
                    <div class="col-md-3">
                        <input type="date" class="form-control" v-model="form.end_date">
                    </div>
                    <div class="col-md-3 d-flex align-items-end">
                        <button class="btn btn-primary w-100" @click="createTrek">Create</button>
                    </div>
                </div>
            </div>
        </div>

        <div class="card mb-5">
            <div class="card-body">
                <table class="table border align-middle">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Name</th>
                            <th>Location</th>
                            <th>Difficulty</th>
                            <th>Slots</th>
                            <th>Status</th>
                            <th>Assigned Staff</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="trek in treks" :key="trek.id">
                            <td>{{ trek.id }}</td>
                            <td>{{ trek.name }}</td>
                            <td>{{ trek.location }}</td>
                            <td>{{ trek.difficulty }}</td>
                            <td>{{ trek.available_slots }}</td>
                            <td>
                                <select class="form-select form-select-sm" v-model="trek.status"
                                    @change="updateTrek(trek)">
                                    <option>Pending</option>
                                    <option>Approved</option>
                                    <option>Open</option>
                                    <option>Closed</option>
                                    <option>Completed</option>
                                </select>
                            </td>
                            <td>
                                <select class="form-select form-select-sm"
                                    v-model="trek.assigned_staff_id" @change="updateTrek(trek)">
                                    <option :value="null">Unassigned</option>
                                    <option v-for="s in staffList" :key="s.id" :value="s.id">{{ s.name }}</option>
                                </select>
                            </td>
                            <td>
                                <button class="btn btn-sm btn-danger" @click="deleteTrek(trek.id)">Delete</button>
                            </td>
                        </tr>
                        <tr v-if="treks.length === 0">
                            <td colspan="8" class="text-center text-muted">No treks yet</td>
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
    name: "AdminManageTreks",
    components: { Navbar },
    data() {
        return {
            treks: [],
            staffList: [],
            showCreateForm: false,
            message: null,
            form: {
                name: "", location: "", difficulty: "", duration: "",
                available_slots: "", start_date: "", end_date: ""
            }
        }
    },
    methods: {
        authHeaders() {
            return {
                "Content-Type": "application/json",
                "Authentication-Token": localStorage.getItem("token")
            }
        },
        async loadTreks() {
            const response = await fetch("http://localhost:5000/admin/treks", { headers: this.authHeaders() })
            if (response.status == 401 || response.status == 403) { this.$router.push("/login"); return }
            this.treks = await response.json()
        },
        async loadStaff() {
            const response = await fetch("http://localhost:5000/admin/staff", { headers: this.authHeaders() })
            if (response.status == 200) this.staffList = await response.json()
        },
        async createTrek() {
            this.message = null
            try {
                const response = await fetch("http://localhost:5000/admin/treks", {
                    method: "POST", headers: this.authHeaders(), body: JSON.stringify(this.form)
                })
                const data = await response.json()
                if (response.status == 200) {
                    this.showCreateForm = false
                    this.form = { name: "", location: "", difficulty: "", duration: "", available_slots: "", start_date: "", end_date: "" }
                    this.loadTreks()
                } else {
                    this.message = data.message
                }
            } catch (error) { console.log(error.message) }
        },
        async updateTrek(trek) {
            try {
                await fetch(`http://localhost:5000/admin/treks/${trek.id}`, {
                    method: "PUT", headers: this.authHeaders(),
                    body: JSON.stringify({ status: trek.status, assigned_staff_id: trek.assigned_staff_id })
                })
                this.loadTreks()
            } catch (error) { console.log(error.message) }
        },
        async deleteTrek(id) {
            if (!confirm("Delete this trek?")) return
            await fetch(`http://localhost:5000/admin/treks/${id}`, { method: "DELETE", headers: this.authHeaders() })
            this.loadTreks()
        }
    },
    mounted() {
        this.loadTreks()
        this.loadStaff()
    }
}
</script>
