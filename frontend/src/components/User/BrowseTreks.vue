<template>
    <Navbar></Navbar>

    <div class="container mt-4">
        <h3>Browse Treks</h3>

        <div class="card mb-4">
            <div class="card-body">
                <div class="row g-2">
                    <div class="col-md-4">
                        <input class="form-control" placeholder="Location" v-model="filters.location" @input="loadTreks">
                    </div>
                    <div class="col-md-3">
                        <select class="form-select" v-model="filters.difficulty" @change="loadTreks">
                            <option value="">Difficulty: All</option>
                            <option>Easy</option>
                            <option>Moderate</option>
                            <option>Hard</option>
                        </select>
                    </div>
                    <div class="col-md-3">
                        <input type="number" class="form-control" placeholder="Duration (days)"
                            v-model="filters.duration" @input="loadTreks">
                    </div>
                    <div class="col-md-2">
                        <button class="btn btn-primary w-100" @click="loadTreks">Search</button>
                    </div>
                </div>
            </div>
        </div>

        <div v-if="message" class="alert alert-danger">{{ message }}</div>

        <div class="row">
            <div class="col-md-4 mb-3" v-for="t in treks" :key="t.id">
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
            <p v-if="treks.length === 0" class="text-muted">No treks match your search.</p>
        </div>
    </div>
</template>

<script>
import Navbar from '../Navbar.vue';

export default {
    name: "UserBrowseTreks",
    components: { Navbar },
    data() {
        return {
            treks: [],
            filters: { location: "", difficulty: "", duration: "" },
            message: null
        }
    },
    methods: {
        authHeaders() {
            return { "Content-Type": "application/json", "Authentication-Token": localStorage.getItem("token") }
        },
        async loadTreks() {
            const params = new URLSearchParams()
            if (this.filters.location) params.append("location", this.filters.location)
            if (this.filters.difficulty) params.append("difficulty", this.filters.difficulty)
            if (this.filters.duration) params.append("duration", this.filters.duration)

            const response = await fetch(`http://localhost:5000/user/treks?${params.toString()}`, {
                headers: this.authHeaders()
            })
            if (response.status == 401 || response.status == 403) { this.$router.push("/login"); return }
            this.treks = await response.json()
        },
        async bookTrek(trekId) {
            this.message = null
            const response = await fetch(`http://localhost:5000/user/treks/${trekId}/book`, {
                method: "POST", headers: this.authHeaders()
            })
            const data = await response.json()
            if (response.status == 200) {
                this.loadTreks()
            } else {
                this.message = data.message
            }
        }
    },
    mounted() {
        this.loadTreks()
    }
}
</script>
