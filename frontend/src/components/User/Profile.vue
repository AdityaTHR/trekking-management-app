<template>
    <Navbar></Navbar>

    <div class="d-flex justify-content-center mt-5">
        <div class="card" style="width: 22rem;">
            <div class="card-body">
                <h5 class="card-title mb-3">My Profile</h5>

                <div v-if="message" class="alert alert-info">{{ message }}</div>

                <div class="form-floating mb-3">
                    <input type="text" class="form-control" v-model="profile.name" id="floatingName">
                    <label for="floatingName">Full Name</label>
                </div>
                <div class="form-floating mb-3">
                    <input type="email" class="form-control" :value="profile.email" disabled id="floatingEmail">
                    <label for="floatingEmail">Email (cannot be changed)</label>
                </div>
                <div class="form-floating mb-3">
                    <input type="tel" class="form-control" v-model="profile.contact_number" id="floatingContact">
                    <label for="floatingContact">Contact Number</label>
                </div>

                <button class="btn btn-primary w-100" @click="saveProfile">Save Changes</button>
            </div>
        </div>
    </div>
</template>

<script>
import Navbar from '../Navbar.vue';

export default {
    name: "UserProfile",
    components: { Navbar },
    data() {
        return {
            profile: { name: "", email: "", contact_number: "" },
            message: null
        }
    },
    methods: {
        authHeaders() {
            return { "Content-Type": "application/json", "Authentication-Token": localStorage.getItem("token") }
        },
        async loadProfile() {
            const response = await fetch("http://localhost:5000/user/profile", { headers: this.authHeaders() })
            if (response.status == 401 || response.status == 403) { this.$router.push("/login"); return }
            this.profile = await response.json()
        },
        async saveProfile() {
            const response = await fetch("http://localhost:5000/user/profile", {
                method: "PUT", headers: this.authHeaders(),
                body: JSON.stringify({ name: this.profile.name, contact_number: this.profile.contact_number })
            })
            if (response.status == 200) {
                this.message = "Profile updated successfully"
                localStorage.setItem("name", this.profile.name)
            } else {
                const data = await response.json()
                this.message = data.message || "Could not update profile"
            }
        }
    },
    mounted() {
        this.loadProfile()
    }
}
</script>
