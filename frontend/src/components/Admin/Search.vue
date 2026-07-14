<template>
    <Navbar></Navbar>

    <div class="d-flex justify-content-center mt-5">
        <div class="card" style="width: 26rem;">
            <div class="card-body">
                <div class="d-flex gap-3">
                    <div class="form-check">
                        <input class="form-check-input" type="radio" v-model="formdata.query_type" value="trek"
                            name="radioDefault" id="radioTrek">
                        <label class="form-check-label" for="radioTrek">Trek</label>
                    </div>
                    <div class="form-check">
                        <input class="form-check-input" type="radio" v-model="formdata.query_type" value="staff"
                            name="radioDefault" id="radioStaff">
                        <label class="form-check-label" for="radioStaff">Staff</label>
                    </div>
                    <div class="form-check">
                        <input class="form-check-input" type="radio" v-model="formdata.query_type" value="user"
                            name="radioDefault" id="radioUser">
                        <label class="form-check-label" for="radioUser">User</label>
                    </div>
                </div>
                <div class="d-flex gap-3 mt-3">
                    <div class="form-floating flex-grow-1">
                        <input class="form-control" v-model="formdata.query" id="floatingInput" placeholder="Search">
                        <label for="floatingInput">Search by name or ID</label>
                    </div>
                    <button class="btn btn-primary" @click="search">Search</button>
                </div>
            </div>
        </div>
    </div>

    <div v-if="results" class="card mt-5 ms-5 me-5 mb-5">
        <div class="card-header text-capitalize">{{ formdata.query_type }} Results</div>
        <div class="card-body">
            <table class="table border">
                <thead>
                    <tr>
                        <th>ID</th><th>Name</th><th>{{ formdata.query_type === 'trek' ? 'Location' : 'Email' }}</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="r in results" :key="r.id">
                        <td>{{ r.id }}</td>
                        <td>{{ r.name }}</td>
                        <td>{{ formdata.query_type === 'trek' ? r.location : r.email }}</td>
                    </tr>
                    <tr v-if="results.length === 0">
                        <td colspan="3" class="text-center text-muted">No matches</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</template>

<script>
import Navbar from '../Navbar.vue';

export default {
    name: "AdminSearch",
    components: { Navbar },
    data() {
        return {
            formdata: { query_type: "trek", query: "" },
            results: null
        }
    },
    methods: {
        async search() {
            try {
                const response = await fetch(
                    `http://localhost:5000/admin/search?type=${this.formdata.query_type}&q=${encodeURIComponent(this.formdata.query)}`,
                    { headers: { "Authentication-Token": localStorage.getItem("token") } }
                )
                if (response.status == 401 || response.status == 403) { this.$router.push("/login"); return }
                this.results = await response.json()
            } catch (error) { console.log(error.message) }
        }
    }
}
</script>
