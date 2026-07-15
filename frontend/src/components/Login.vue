<template>
    <div class="auth-page d-flex justify-content-center align-items-center">

        <div class="card auth-card">
            <div class="card-body">
                <h5 class="card-title text-center mb-3">Trekking Management</h5>

                <div v-if="message" class="alert alert-danger" role="alert">
                    {{ message }}
                </div>

                <div class="form-floating mb-3">
                    <input type="email" class="form-control" v-model="formdata.email" id="floatingInput"
                        placeholder="name@example.com">
                    <label for="floatingInput">Email address</label>
                </div>
                <div class="form-floating">
                    <input type="password" class="form-control" v-model="formdata.password" id="floatingPassword"
                        placeholder="Password">
                    <label for="floatingPassword">Password</label>
                </div>
                <div class="d-flex justify-content-center mt-3">
                    <button class="btn btn-primary" @click="login">Login</button>
                </div>
                <p class="text-center mt-3 mb-0">
                    <router-link to="/register">Register as User (Trekker)</router-link>
                </p>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: "LoginComp",
    data() {
        return {
            formdata: {
                email: "",
                password: "",
            },
            message: null
        }
    },
    methods: {
        async login() {
            try {
                const response = await fetch("http://localhost:5000/login", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(this.formdata)
                })
                const data = await response.json()
                if (response.status == 200) {
                    localStorage.setItem("token", data.token)
                    localStorage.setItem("role", data.role)
                    localStorage.setItem("name", data.name)
                    if (data.role == "admin") {
                        this.$router.push("/admin/dashboard")
                    }
                    else if (data.role == "staff") {
                        this.$router.push("/staff/dashboard")
                    }
                    else if (data.role == "trekker") {
                        this.$router.push("/user/dashboard")
                    }
                }
                else if (response.status == 401) {
                    this.message = data.message
                }
                else if (response.status == 403) {
                    this.message = data.message
                }
                else if (response.status == 404) {
                    this.message = data.message
                }
            }
            catch (error) {
                console.log(error.message)
            }
        }
    }
}
</script>

<style scoped>
.auth-page {
    min-height: 100vh;
    padding: 1.5rem;
    background: linear-gradient(135deg, #eef5ff, #f8fbff);
}

.auth-card {
    width: min(100%, 23rem);
}
</style>
