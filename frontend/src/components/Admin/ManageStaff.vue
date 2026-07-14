<template>
    <Navbar></Navbar>

    <div class="container mt-4">
        <div class="d-flex justify-content-between align-items-center mb-3">
            <h3>Trekking Staff</h3>
            <button class="btn btn-primary" @click="showCreateForm = !showCreateForm">
                + Create New Trekking Staff
            </button>
        </div>

        <div v-if="message" class="alert alert-danger">{{ message }}</div>

        <div class="card mb-4" v-if="showCreateForm">
            <div class="card-header">Create New Trekking Staff</div>
            <div class="card-body">
                <div class="row g-2">
                    <div class="col-md-4"><input class="form-control" placeholder="Full Name" v-model="form.name"></div>
                    <div class="col-md-4"><input class="form-control" placeholder="Email Address" v-model="form.email"></div>
                    <div class="col-md-4"><input class="form-control" placeholder="Contact Number" v-model="form.contact_number"></div>
                    <div class="col-md-4"><input type="password" class="form-control" placeholder="Password" v-model="form.password"></div>
                    <div class="col-md-4"><input type="number" class="form-control" placeholder="Experience (years)" v-model="form.experience_years"></div>
                    <div class="col-md-4"><input class="form-control" placeholder="Specialization e.g. High Altitude, First Aid" v-model="form.specialization"></div>
                    <div class="col-md-12 mt-2">
                        <button class="btn btn-primary" @click="createStaff">Create Staff</button>
                        <button class="btn btn-secondary ms-2" @click="showCreateForm = false">Cancel</button>
                    </div>
                </div>
                <p class="text-muted mt-2 mb-0" style="font-size: 0.85rem;">
                    The staff member will receive their login credentials directly (email/password shown above).
                </p>
            </div>
        </div>

        <div class="card mb-5">
            <div class="card-body">
                <table class="table border align-middle">
                    <thead>
                        <tr>
                            <th>ID</th><th>Name</th><th>Email</th><th>Contact</th>
                            <th>Experience</th><th>Specialization</th><th>Status</th><th>Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="s in staffList" :key="s.id">
                            <td>{{ s.id }}</td>
                            <td>{{ s.name }}</td>
                            <td>{{ s.email }}</td>
                            <td>{{ s.contact_number }}</td>
                            <td>{{ s.experience_years }}</td>
                            <td>{{ s.specialization }}</td>
                            <td>
                                <span :class="s.status === 'active' ? 'badge bg-success' : 'badge bg-danger'">
                                    {{ s.status }}
                                </span>
                            </td>
                            <td>
                                <button v-if="s.status === 'active'" class="btn btn-sm btn-danger"
                                    @click="toggleStatus(s, 'blacklisted')">Blacklist</button>
                                <button v-else class="btn btn-sm btn-success"
                                    @click="toggleStatus(s, 'active')">Whitelist</button>
                            </td>
                        </tr>
                        <tr v-if="staffList.length === 0">
                            <td colspan="8" class="text-center text-muted">No trekking staff yet</td>
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
    name: "AdminManageStaff",
    components: { Navbar },
    data() {
        return {
            staffList: [],
            showCreateForm: false,
            message: null,
            form: { name: "", email: "", password: "", contact_number: "", experience_years: "", specialization: "" }
        }
    },
    methods: {
        authHeaders() {
            return { "Content-Type": "application/json", "Authentication-Token": localStorage.getItem("token") }
        },
        async loadStaff() {
            const response = await fetch("http://localhost:5000/admin/staff", { headers: this.authHeaders() })
            if (response.status == 401 || response.status == 403) { this.$router.push("/login"); return }
            this.staffList = await response.json()
        },
        async createStaff() {
            this.message = null
            try {
                const response = await fetch("http://localhost:5000/admin/staff", {
                    method: "POST", headers: this.authHeaders(), body: JSON.stringify(this.form)
                })
                const data = await response.json()
                if (response.status == 200) {
                    this.showCreateForm = false
                    this.form = { name: "", email: "", password: "", contact_number: "", experience_years: "", specialization: "" }
                    this.loadStaff()
                } else {
                    this.message = data.message
                }
            } catch (error) { console.log(error.message) }
        },
        async toggleStatus(staffMember, newStatus) {
            await fetch(`http://localhost:5000/admin/users/${staffMember.id}/status`, {
                method: "PUT", headers: this.authHeaders(), body: JSON.stringify({ status: newStatus })
            })
            this.loadStaff()
        }
    },
    mounted() {
        this.loadStaff()
    }
}
</script>
