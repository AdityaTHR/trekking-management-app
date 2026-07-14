<template>
    <Navbar></Navbar>

    <div class="container mt-4">
        <h3 class="mb-3">Users (Trekkers)</h3>

        <div class="card mb-5">
            <div class="card-body">
                <table class="table border align-middle">
                    <thead>
                        <tr>
                            <th>ID</th><th>Name</th><th>Email</th><th>Contact</th><th>Status</th><th>Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="u in users" :key="u.id">
                            <td>{{ u.id }}</td>
                            <td>{{ u.name }}</td>
                            <td>{{ u.email }}</td>
                            <td>{{ u.contact_number }}</td>
                            <td>
                                <span :class="u.status === 'active' ? 'badge bg-success' : 'badge bg-danger'">
                                    {{ u.status }}
                                </span>
                            </td>
                            <td>
                                <button v-if="u.status === 'active'" class="btn btn-sm btn-danger"
                                    @click="toggleStatus(u, 'blacklisted')">Blacklist</button>
                                <button v-else class="btn btn-sm btn-success"
                                    @click="toggleStatus(u, 'active')">Whitelist</button>
                            </td>
                        </tr>
                        <tr v-if="users.length === 0">
                            <td colspan="6" class="text-center text-muted">No users yet</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
        <p class="text-muted" style="font-size: 0.85rem;">Blacklisted users cannot log in or book treks.</p>
    </div>
</template>

<script>
import Navbar from '../Navbar.vue';

export default {
    name: "AdminManageUsers",
    components: { Navbar },
    data() {
        return { users: [] }
    },
    methods: {
        authHeaders() {
            return { "Content-Type": "application/json", "Authentication-Token": localStorage.getItem("token") }
        },
        async loadUsers() {
            const response = await fetch("http://localhost:5000/admin/users", { headers: this.authHeaders() })
            if (response.status == 401 || response.status == 403) { this.$router.push("/login"); return }
            this.users = await response.json()
        },
        async toggleStatus(user, newStatus) {
            await fetch(`http://localhost:5000/admin/users/${user.id}/status`, {
                method: "PUT", headers: this.authHeaders(), body: JSON.stringify({ status: newStatus })
            })
            this.loadUsers()
        }
    },
    mounted() {
        this.loadUsers()
    }
}
</script>
