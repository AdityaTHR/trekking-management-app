<template>
    <nav class="navbar navbar-expand-lg bg-body-tertiary">
        <div class="container-fluid">
            <router-link class="navbar-brand fw-semibold" :to="homePath">🏔️ Trekking Management</router-link>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav"
                aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item" v-if="role === 'admin'">
                        <router-link class="nav-link" to="/admin/dashboard">Dashboard</router-link>
                    </li>
                    <li class="nav-item" v-if="role === 'admin'">
                        <router-link class="nav-link" to="/admin/treks">Treks</router-link>
                    </li>
                    <li class="nav-item" v-if="role === 'admin'">
                        <router-link class="nav-link" to="/admin/staff">Trekking Staff</router-link>
                    </li>
                    <li class="nav-item" v-if="role === 'admin'">
                        <router-link class="nav-link" to="/admin/users">Users</router-link>
                    </li>
                    <li class="nav-item" v-if="role === 'admin'">
                        <router-link class="nav-link" to="/admin/search">Search</router-link>
                    </li>
                    <li class="nav-item" v-if="role === 'admin'">
                        <router-link class="nav-link" to="/admin/bookings">All Bookings</router-link>
                    </li>
                    <li class="nav-item" v-if="role === 'staff'">
                        <router-link class="nav-link" to="/staff/dashboard">My Dashboard</router-link>
                    </li>
                    <li class="nav-item" v-if="role === 'trekker'">
                        <router-link class="nav-link" to="/user/dashboard">Dashboard</router-link>
                    </li>
                    <li class="nav-item" v-if="role === 'trekker'">
                        <router-link class="nav-link" to="/user/treks">Browse Treks</router-link>
                    </li>
                    <li class="nav-item" v-if="role === 'trekker'">
                        <router-link class="nav-link" to="/user/history">History</router-link>
                    </li>
                    <li class="nav-item" v-if="role === 'trekker'">
                        <router-link class="nav-link" to="/user/profile">Profile</router-link>
                    </li>
                    <li class="nav-item">
                        <router-link class="nav-link" to="/login" @click="logout">Logout</router-link>
                    </li>
                </ul>
            </div>
        </div>
    </nav>
</template>

<script>
export default {
    name: "NavBar",
    data() {
        return { role: localStorage.getItem("role") }
    },
    computed: {
        homePath() {
            if (this.role === "admin") return "/admin/dashboard"
            if (this.role === "staff") return "/staff/dashboard"
            return "/user/dashboard"
        }
    },
    methods: {
        logout() {
            localStorage.removeItem("token")
            localStorage.removeItem("role")
            localStorage.removeItem("name")
        }
    }
}
</script>
